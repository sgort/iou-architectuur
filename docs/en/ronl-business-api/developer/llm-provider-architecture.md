# LLM Provider Architecture

The AI Assistant decouples the agentic loop from any specific LLM SDK through a `LlmProvider` interface and a `LlmRegistry` singleton. Adding a new LLM (Mistral, Azure OpenAI, Google Gemini, etc.) requires only implementing the interface and registering the provider at startup — no changes to the chat service, routes, or frontend are needed.

See [MCP AI Assistant](mcp-ai-assistant.md) for the overall architecture and MCP source registry.

---

## Interface

`packages/backend/src/services/llm/LlmProvider.ts` defines the contract every provider must satisfy.
```typescript
export interface LlmProvider {
  readonly meta: LlmProviderMeta;
  isAvailable(): boolean;
  streamTurn(
    params: LlmStreamParams,
    onDelta: (text: string) => void,
    signal?: AbortSignal
  ): Promise<LlmTurnResult>;
}
```

`isAvailable()` returns `false` when the provider's API key is not configured. Unavailable providers are registered but their models are excluded from `GET /v1/mcp/models`.

`streamTurn()` receives a provider-agnostic `AgentMessage[]` history, a system prompt, and tool definitions. It calls `onDelta` for each text chunk and returns an `LlmTurnResult` containing the full response text, any tool use blocks, and the stop reason. The chat service (`mcpChat.service.ts`) never imports any SDK directly.

### Message types
```typescript
export type AgentMessage =
  | { role: 'user';              content: string }
  | { role: 'assistant';         content: string }
  | { role: 'assistant_tool_use'; toolUses: AgentToolUse[] }
  | { role: 'tool_results';      results: AgentToolResult[] };
```

Each provider's `streamTurn()` implementation converts these to its SDK's native format. `toAnthropicMessage()` and `toOpenAIMessage()` in the respective provider files handle the mapping.

---

## Registry

`LlmRegistry` maps model IDs to their owning provider.
```typescript
llmRegistry.register(new AnthropicLlmProvider());
llmRegistry.register(new OpenAILlmProvider());
```

`llmRegistry.getProvider(modelId)` is called by `runChatStream()` to resolve which provider handles the request. `llmRegistry.getAvailableModels()` returns all models from connected providers, used by `GET /v1/mcp/models`.

---

## Registered providers

### `AnthropicLlmProvider`

Uses `@anthropic-ai/sdk`. Enabled when `ANTHROPIC_API_KEY` is set.

| Model ID                    | Display name         |
|-----------------------------|----------------------|
| `claude-sonnet-4-20250514`  | Claude Sonnet 4      |
| `claude-opus-4-20250514`    | Claude Opus 4        |
| `claude-haiku-4-5-20251001` | Claude Haiku 4.5     |

### `OpenAILlmProvider`

Uses `openai`. Enabled when `OPENAI_API_KEY` is set.

| Model ID      | Display name  |
|---------------|---------------|
| `gpt-4o`      | GPT-4o        |
| `gpt-4o-mini` | GPT-4o Mini   |

---

## Response delivery: streaming vs. buffered

`onDelta` is called per token as the stream arrives. This produces a visible build-up effect in the assistant bubble — the user sees progress during long multi-tool queries rather than a blank wait followed by a sudden full response.

The pre-registry behavior (one emission of the full text after `stream.finalMessage()`) can be restored in `AnthropicLlmProvider.streamTurn()` by buffering and emitting once:
```typescript
// Buffered (all-at-once) variant
const response = await stream.finalMessage();
const text = response.content
  .filter((b): b is Anthropic.TextBlock => b.type === 'text')
  .map((b) => b.text)
  .join('');
if (text) onDelta(text);
```

The streaming variant is the current default. Which is preferable is subject to user feedback.

---

## Frontend — model selector

`GET /v1/mcp/models` returns all available models with their provider:
```typescript
export interface LlmModelEntry {
  id: string;
  displayName: string;
  providerId: string;
  providerDisplayName: string;
}
```

`McpChatSection` fetches this on mount and renders a `<select>` below the source toggles when more than one model is available. The selected `modelId` is sent on every `POST /v1/mcp/chat` request. When only one model is available the selector is hidden.

---

## Adding a new provider

1. Create `packages/backend/src/services/llm/YourLlmProvider.ts` implementing `LlmProvider`. Declare `meta.models` with the model IDs you want to expose. Implement `toYourMessage()` to convert `AgentMessage` to the SDK's native format and handle the `assistant_tool_use` / `tool_results` roles.
2. Add the API key to `Config` in `config.ts` and to `.env.example`.
3. Register in `packages/backend/src/index.ts`:
```typescript
   llmRegistry.register(new YourLlmProvider());
```

The new provider's models appear in `GET /v1/mcp/models` immediately after deployment, as long as `isAvailable()` returns `true`.