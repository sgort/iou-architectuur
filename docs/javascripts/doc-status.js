/* doc-status.js
 * Fetches repo-versions.json and:
 *   1. Renders a documentation status admonition on the home page
 *      (identified by presence of #doc-status).
 *   2. Injects an ACC badge into matching What's New grid cards
 *      (identified by .whats-new-cards) for any repository whose
 *      environment is "acc".
 *   3. Renders the "last documentation patch" box under the home page's
 *      subtitle (identified by #last-patch) from the `last_patch` record —
 *      when the site was last patched, what kind of run it was, the run
 *      before it, and where the findings left open are tracked.
 *
 * Update repo-versions.json manually whenever you sync content from a
 * component repository, then rebuild the MkDocs site.
 */

(function () {
  "use strict";

  function formatDate(isoDate) {
    const d = new Date(isoDate + "T00:00:00Z");
    return d.toLocaleDateString("en-GB", {
      day: "numeric",
      month: "long",
      year: "numeric",
      timeZone: "UTC",
    });
  }

  function envBadge(environment) {
    if (!environment) return "";
    var env = environment.toLowerCase();
    if (env === "acc") {
      return '<span class="env-badge env-acc">ACC</span>';
    }
    if (env === "prod") {
      return '<span class="env-badge env-prod">PROD</span>';
    }
    return '<span class="env-badge">' + environment.toUpperCase() + "</span>";
  }

  function buildAdmonition(data) {
    const builtDate = formatDate(data.docs_built);

    const rows = data.repositories
      .map(function (repo) {
        const commitLink = repo.repo_url
          ? '<a href="' +
            repo.repo_url +
            '" target="_blank" rel="noopener">' +
            repo.commit +
            "</a>"
          : repo.commit;

        return (
          "<tr>" +
          "<td>" +
          repo.icon +
          "&nbsp;" +
          repo.name +
          "</td>" +
          "<td><code>" +
          repo.version +
          "</code></td>" +
          "<td>" +
          envBadge(repo.environment) +
          "</td>" +
          "<td>" +
          commitLink +
          "</td>" +
          "<td>" +
          formatDate(repo.commit_date) +
          "</td>" +
          "</tr>"
        );
      })
      .join("");

    return (
      "" +
      '<div class="admonition info doc-status-admonition">' +
      '<p class="admonition-title">Documentation built on ' +
      builtDate +
      "</p>" +
      "<p>The table below records the component version and commit this documentation was last synced from.</p>" +
      '<table class="doc-status-table">' +
      "<thead><tr>" +
      "<th>Component</th>" +
      "<th>Version</th>" +
      "<th>Environment</th>" +
      "<th>Commit</th>" +
      "<th>Commit date</th>" +
      "</tr></thead>" +
      "<tbody>" +
      rows +
      "</tbody>" +
      "</table>" +
      "</div>"
    );
  }

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function patchLine(patch) {
    return (
      "<strong>" +
      formatDate(patch.date) +
      "</strong> · " +
      escapeHtml(patch.kind) +
      " — " +
      escapeHtml(patch.summary)
    );
  }

  /* The last documentation patch, from repo-versions.json's `last_patch`.
   * Every run of /iou-document-patch updates the record, so the box says
   * when the site was last brought in line with the code, and links the
   * issue where the source findings of those runs wait to be fixed.
   */
  function buildLastPatch(patch) {
    var html =
      '<div class="admonition note last-patch-admonition">' +
      '<p class="admonition-title">Last documentation patch: ' +
      formatDate(patch.date) +
      " · " +
      escapeHtml(patch.kind) +
      "</p>" +
      "<p>" +
      escapeHtml(patch.summary) +
      "</p>";
    if (patch.previous) {
      html += "<p>Before that: " + patchLine(patch.previous) + "</p>";
    }
    // One issue, or a list of them when a pass covered several components.
    var findings = [].concat(patch.open_findings || []).filter(function (f) {
      return f && f.url;
    });
    if (findings.length) {
      html +=
        "<p>Open findings — what the patches found in the component repositories and left for them to fix: " +
        findings
          .map(function (f) {
            return (
              '<a href="' +
              escapeHtml(f.url) +
              '" target="_blank" rel="noopener">' +
              escapeHtml(f.label) +
              "</a>"
            );
          })
          .join(" · ") +
        "</p>";
    }
    return html + "</div>";
  }

  /* Inject ACC badges into What's New grid cards.
   *
   * Each card's first <strong> contains the component name, e.g.
   * "⚙️ RONL Business API — v2.0.1". We match repo.name as a substring
   * (case-insensitive) against that text, then prepend an ACC badge
   * inside the <strong> element before the em-dash separator.
   */
  function decorateWhatsNewCards(data) {
    var container = document.querySelector(".whats-new-cards");
    if (!container) return;

    var cards = container.querySelectorAll("li");

    data.repositories.forEach(function (repo) {
      if (!repo.environment) return;

      cards.forEach(function (card) {
        var strong = card.querySelector("p > strong, strong");
        if (!strong) return;
        // Avoid double-injection on Material instant navigation re-renders
        if (strong.querySelector(".env-badge")) return;
        if (
          strong.textContent.toLowerCase().indexOf(repo.name.toLowerCase()) ===
          -1
        )
          return;

        // Insert badge after the version token (after the last em-dash segment)
        var env = repo.environment.toLowerCase();
        var badge = document.createElement("span");
        badge.className = "env-badge env-" + env + " whats-new-env-badge";
        badge.textContent = repo.environment.toUpperCase();
        strong.appendChild(badge);
      });
    });
  }

  function render() {
    var target = document.getElementById("doc-status");
    var hasCards = document.querySelector(".whats-new-cards");
    var lastPatch = document.getElementById("last-patch");

    if (!target && !hasCards && !lastPatch) return; // not on home page

    // Resolve JSON path relative to site root regardless of language prefix
    var base = document.querySelector("base");
    var basePath = base ? base.href : "/";
    var jsonUrl = basePath.replace(/\/$/, "") + "/repo-versions.json";

    fetch(jsonUrl)
      .then(function (response) {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.json();
      })
      .then(function (data) {
        if (target) {
          target.innerHTML = buildAdmonition(data);
        }
        if (lastPatch && data.last_patch) {
          lastPatch.innerHTML = buildLastPatch(data.last_patch);
        }
        decorateWhatsNewCards(data);
      })
      .catch(function (err) {
        if (target) {
          target.innerHTML =
            "" +
            '<div class="admonition warning">' +
            '<p class="admonition-title">Documentation status unavailable</p>' +
            "<p>Could not load <code>repo-versions.json</code>: " +
            err.message +
            "</p>" +
            "</div>";
        }
      });
  }

  // MkDocs Material re-renders content on navigation without a full page reload.
  // Listen for the custom event it fires after each page change.
  document.addEventListener("DOMContentLoaded", render);
  document$.subscribe(render); // Material for MkDocs instant navigation hook
})();
