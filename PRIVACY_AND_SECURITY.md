# Privacy and Security Notes

## What this site is

The site is a static public directory built from an owner-supplied source list. It has no accounts, server application, database, payment feature, analytics SDK, advertising tag, geolocation call, feedback form, or persistent client-side browsing storage.

The public output contains source-derived listing content: name, district, address text, type text, source-supplied contact text, source remarks, lineage-safe identifiers, source-text classification fields, coverage semantics, and map uncertainty statements. This data should be treated as public directory content, not independently verified service information.

The raw import file is not committed. Canonical records retain a source-artifact identifier and hashes for provenance, not a copy of the original uploaded file.

## Browser behaviour and external requests

The page loads `index.html`, `app.css`, `runtime-data.js`, `app.js`, and `logo.svg` from the same site origin. It does not load map tiles, web fonts, tracking pixels, or third-party executable scripts.

The map attribution link is an ordinary user-initiated link to Bharat Atlas. It uses `rel="noopener noreferrer"` and `referrerpolicy="no-referrer"`. A visitor’s browser contacts that third party only after the visitor chooses that link.

Filters, selected entry, and list/map view are encoded in the URL only when the user changes them. The application does not use `localStorage`, `sessionStorage`, cookies, or browser geolocation. Treat a shared link as a record-selection link, not as an authorization mechanism.

## Controls in the static application

- The generated HTML uses same-origin external CSS and JavaScript files plus a restrictive meta Content Security Policy. It disallows third-party script/style origins, plugin content, forms, and external connections.
- The renderer creates record UI with DOM nodes and text content rather than interpolating record text as HTML. The deterministic validator rejects generated `innerHTML` paths.
- Source contact text is labelled as supplied and unconfirmed. The application does not convert contact text into click-to-call links.
- Public CSV export neutralizes formula-like leading characters. Exports retain the source-derived/location-uncertainty context and data version.
- The map publishes district-group counts and coverage controls, not facility coordinates. It must not be used for routing or travel decisions without independent confirmation.
- GitHub Actions uses immutable commit references for official actions. The deploy job receives Pages/OIDC permission only in the protected deployment job.

## Limits and maintainer obligations

A meta CSP is useful for a static GitHub Pages deployment but cannot replace platform response headers. GitHub Pages and the browser ultimately control transport and response-header behaviour. Review any new third-party asset, executable code, form endpoint, analytics tool, or external link before adding it.

Do not add a correction form, error-report destination, canonical public URL, verified contact/operating-status field, Panjabi translation, or access claim until the required owner approval and evidence are available. The public configuration intentionally leaves the correction route and canonical URL as `null`.

If a future source contains sensitive, personal, or non-public information, stop the import and obtain appropriate approval before it reaches canonical or generated data.
