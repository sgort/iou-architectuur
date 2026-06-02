# Getting Started

This guide gets you from nothing to a running Norm Editor and your first interpretation.

---

## Prerequisites

To run the full stack locally you need:

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose, **or**
- [Node.js](https://nodejs.org/) v20+ if you only want to run the frontend against an existing
  backend.

To save to or load from TriplyDB you also need a **Triply API key**.

---

## Running the full stack

1. Create a `.env` file in the project root with your Triply key:

   ```env
   TRIPLY_KEY_R=your-triply-api-key
   ```

2. Start everything:

   ```bash
   docker compose up --build
   ```

3. Open the editor at **http://localhost**.

All traffic goes through nginx on port 80. The individual services are also exposed for
debugging (backend `:3000`, nlp-api `:8081`, unwrap-api `:5001`, wrap-up-api `:5002`).

For frontend-only development with hot reload, see
[Local Development](../developer/local-development.md).

---

## The five-step workflow

The editor opens on a stepper. You move through it from left to right:

1. **Define a task** — say who you are and what you are interpreting.
2. **Collect sources** — load documents and pick the sentences in scope.
3. **Interpret sources** — highlight text and build frames.
4. **Validate interpretations** *(planned)*.
5. **Perform task** *(planned)*.

A banner at the top of the stepper lets you **save** and **load** an interpretation at any
point, so you never lose work between sessions.

---

## Your first interpretation in brief

1. On **step 1**, fill in *Editor*, *Label*, and *Description*, then click **Continue**.
2. On **step 2**, add a source, tick the sentences you care about, and click **Continue**.
3. On **step 3**, highlight a phrase, choose **Fact**, **Act**, or **Claim-duty**, and start
   building. For an act, use the role pencils to mark which fact is the actor, action, object,
   and recipient.
4. Use the **save** banner to download your interpretation as JSON or to push it to TriplyDB.

Each step has its own detailed page:

- [Defining a task](defining-a-task.md)
- [Collecting sources](collecting-sources.md)
- [Interpreting sources](interpreting-sources.md)
- [Using NLP suggestions](using-nlp-suggestions.md)
- [Saving and loading](saving-and-loading.md)
