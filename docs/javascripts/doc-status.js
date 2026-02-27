/* doc-status.js
 * Fetches repo-versions.json and renders a documentation status admonition
 * on the home page only (identified by presence of #doc-status).
 * Update repo-versions.json manually whenever you sync content from a
 * component repository, then rebuild the MkDocs site.
 */

(function () {
  'use strict';

  function formatDate(isoDate) {
    const d = new Date(isoDate + 'T00:00:00Z');
    return d.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      timeZone: 'UTC'
    });
  }

  function buildAdmonition(data) {
    const builtDate = formatDate(data.docs_built);

    const rows = data.repositories.map(function (repo) {
      const commitLink = repo.repo_url
        ? '<a href="' + repo.repo_url + '" target="_blank" rel="noopener">' + repo.commit + '</a>'
        : repo.commit;

      return '<tr>'
        + '<td>' + repo.icon + '&nbsp;' + repo.name + '</td>'
        + '<td><code>' + repo.version + '</code></td>'
        + '<td>' + commitLink + '</td>'
        + '<td>' + formatDate(repo.commit_date) + '</td>'
        + '</tr>';
    }).join('');

    return ''
      + '<div class="admonition info doc-status-admonition">'
      + '<p class="admonition-title">Documentation built on ' + builtDate + '</p>'
      + '<p>The table below records the component version and commit this documentation was last synced from. '
      + '<table class="doc-status-table">'
      + '<thead><tr>'
      + '<th>Component</th>'
      + '<th>Version</th>'
      + '<th>Commit</th>'
      + '<th>Commit date</th>'
      + '</tr></thead>'
      + '<tbody>' + rows + '</tbody>'
      + '</table>'
      + '</div>';
  }

  function render() {
    var target = document.getElementById('doc-status');
    if (!target) return; // not on home page

    // Resolve JSON path relative to site root regardless of language prefix
    var base = document.querySelector('base');
    var basePath = base ? base.href : '/';
    var jsonUrl = basePath.replace(/\/$/, '') + '/repo-versions.json';

    fetch(jsonUrl)
      .then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.json();
      })
      .then(function (data) {
        target.innerHTML = buildAdmonition(data);
      })
      .catch(function (err) {
        target.innerHTML = ''
          + '<div class="admonition warning">'
          + '<p class="admonition-title">Documentation status unavailable</p>'
          + '<p>Could not load <code>repo-versions.json</code>: ' + err.message + '</p>'
          + '</div>';
      });
  }

  // MkDocs Material re-renders content on navigation without a full page reload.
  // Listen for the custom event it fires after each page change.
  document.addEventListener('DOMContentLoaded', render);
  document$.subscribe(render); // Material for MkDocs instant navigation hook
})();
