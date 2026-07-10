#!/usr/bin/env bash
set -e

# Gebruik parameter bij handmatige run, anders de trigger-tag
TAG="${RELEASE_TAG_PARAM}"
if [ -z "$TAG" ]; then
  # Build.SourceBranch geeft refs/tags/pub/v1.0.0 — strip het refs/tags/ prefix
  TAG="${BUILD_SOURCE_BRANCH}"
  TAG="${TAG#refs/tags/}"
fi

# Strip pub/ prefix voor de GitHub tag (pub/v1.0.0 -> v1.0.0)
GITHUB_TAG="${TAG#pub/}"

# Verifieer dat de tag bestaat
git tag | grep -q "^${TAG}$" || { echo "Tag ${TAG} niet gevonden"; exit 1; }

echo "Exporteren van tag: ${TAG}"
SNAPSHOT="${AGENT_TEMPDIRECTORY}/snapshot"
mkdir -p "${SNAPSHOT}"

# Exporteer alleen de whitelisted bestanden via git archive
# .gitattributes export-ignore regels worden automatisch toegepast
git archive "${TAG}" | tar -x -C "${SNAPSHOT}"

# Verwijder .claudesync als git archive het toch meeneemt
rm -rf "${SNAPSHOT}/docs/en/.claudesync"

# Lees originele waarden voor de sanitize (voor rapportage)
ORIG_REPO_URL=$(grep 'repo_url:' "${SNAPSHOT}/mkdocs.yml" | head -1 | sed 's/repo_url:\s*//')
ORIG_EDIT_URI=$(grep 'edit_uri:' "${SNAPSHOT}/mkdocs.yml" | head -1 | sed 's/edit_uri:\s*//')
ORIG_ICON=$(grep 'repo: fontawesome' "${SNAPSHOT}/mkdocs.yml" | head -1 | sed 's/.*repo:\s*//')
ORIG_ICON2=$(grep 'icon: fontawesome' "${SNAPSHOT}/mkdocs.yml" | head -1 | sed 's/.*icon:\s*//')

# Sanitize mkdocs.yml -- vervang interne GitLab URL door GitHub
sed -i \
  -e 's|repo_url:.*|repo_url: https://github.com/ProvincieFlevoland/IOU-architectuur|' \
  -e 's|edit_uri:.*|edit_uri: edit/main/docs/|' \
  -e 's|repo: fontawesome/brands/gitlab|repo: fontawesome/brands/github|' \
  -e 's|icon: fontawesome/brands/gitlab|icon: fontawesome/brands/github|' \
  "${SNAPSHOT}/mkdocs.yml"

# Secretscan
SCAN_HITS=$(grep -rEl '(password|secret|token|api_key|private_key)\s*[:=]\s*[^$({]' \
    "${SNAPSHOT}" \
    --include="*.yml" --include="*.yaml" --include="*.env" --include="*.tf" \
    --include="*.sh" 2>/dev/null || true)

FILE_COUNT=$(find "${SNAPSHOT}" -type f | wc -l | tr -d ' ')
FILE_LIST=$(find "${SNAPSHOT}" -type f | sed "s|${SNAPSHOT}/||" | sort)

# Manifest in pipeline log
echo "##[group]PUBLISH MANIFEST"
echo "  Tag (ADO):    ${TAG}"
echo "  Tag (GitHub): ${GITHUB_TAG}"
echo "  Bestanden:    ${FILE_COUNT}"
echo ""
echo "  Bestanden in snapshot:"
echo "${FILE_LIST}" | sed 's/^/    /'
echo ""
echo "  Gesaniteerd in mkdocs.yml:"
echo "    repo_url:  ${ORIG_REPO_URL} -> https://github.com/ProvincieFlevoland/IOU-architectuur"
echo "    edit_uri:  ${ORIG_EDIT_URI} -> edit/main/docs/"
echo "    repo icon: ${ORIG_ICON} -> fontawesome/brands/github"
echo "    icon:      ${ORIG_ICON2} -> fontawesome/brands/github"
echo ""
if [ -n "${SCAN_HITS}" ]; then
  echo "  Secretscan: GEFAALD"
  echo "${SCAN_HITS}" | sed 's/^/    /'
  echo "##[endgroup]"
  echo "##[error]Mogelijk gevoelige data gevonden -- publish afgebroken"
  exit 1
else
  echo "  Secretscan: OK (${FILE_COUNT} bestanden gescand)"
fi
echo "##[endgroup]"

# Manifest als Extensions tab
MANIFEST_FILE="${AGENT_TEMPDIRECTORY}/publish-manifest.md"
{
  echo "## Publish Manifest"
  echo ""
  echo "| | |"
  echo "|---|---|"
  echo "| **Tag (ADO)** | \`${TAG}\` |"
  echo "| **Tag (GitHub)** | \`${GITHUB_TAG}\` |"
  echo "| **Bestanden** | ${FILE_COUNT} |"
  echo ""
  echo "### Bestanden in snapshot"
  echo "\`\`\`"
  echo "${FILE_LIST}"
  echo "\`\`\`"
  echo ""
  echo "### Sanitize"
  echo "- repo_url:  ${ORIG_REPO_URL} -> https://github.com/ProvincieFlevoland/IOU-architectuur"
  echo "- edit_uri:  ${ORIG_EDIT_URI} -> edit/main/docs/"
  echo "- repo icon: ${ORIG_ICON} -> fontawesome/brands/github"
  echo "- icon:      ${ORIG_ICON2} -> fontawesome/brands/github"
  echo ""
  echo "### Secretscan"
  echo "OK -- geen gevoelige data gevonden in ${FILE_COUNT} bestanden"
} > "${MANIFEST_FILE}"

echo "##vso[task.uploadsummary]${MANIFEST_FILE}"
echo "##vso[task.setvariable variable=GITHUB_TAG;isOutput=true]${GITHUB_TAG}"
