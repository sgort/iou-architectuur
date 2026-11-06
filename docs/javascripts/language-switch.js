/* language-switch.js
 * Lets the language selector follow its own link.
 *
 * mkdocs-static-i18n points each language-selector link at the matching page in
 * the other language (on /psa/ the Dutch link is ../nl/psa/). Material for
 * MkDocs intercepts those clicks: it expects the link to point at a language
 * root and looks the current page up in that language's sitemap.xml. With
 * page-level links it fetches e.g. /nl/psa/sitemap.xml, which does not exist,
 * and then falls back to the link with its trailing slash removed (/nl/psa).
 * Every relative link on the page it lands on then resolves one level too high:
 * the footer's "next" link went to /nl/01-executive-summary/.
 *
 * A capturing listener on document runs before Material's listener on body;
 * stopping propagation there leaves the browser's default navigation to the
 * link as written, trailing slash included.
 */

(function () {
  "use strict";

  document.addEventListener(
    "click",
    function (event) {
      var target = event.target;
      if (!(target instanceof Element)) return;
      if (target.closest("a.md-select__link[hreflang]")) {
        event.stopPropagation();
      }
    },
    true
  );
})();
