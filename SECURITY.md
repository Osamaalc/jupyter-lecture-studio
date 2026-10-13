# Security policy

## Trust model

- Plain strings in every component are HTML-escaped before any markup is applied.
- `RichText` (JSON: `{"html": ...}`) inserts author HTML **without sanitization**. Use it only for content you wrote. Never pass student submissions or other untrusted text through `RichText`.
- Design-token names and values are validated so they cannot leave the style attribute.
- Figures accept local image files, `data:image/` URIs and `http(s)` URLs only.
- The renderer never executes displayed code. PDF export renders saved outputs only and blocks author scripts while rendering.
- Activity answers, quiz keys and solutions are present in teacher exports. Use `include_answers=False` for files given to students; do not rely on hidden answers for graded examinations.

## Supported versions

Security fixes are released for the latest minor version.

## Reporting a vulnerability

Please report privately through the maintainer contact listed on the PyPI project page rather than in a public issue. Include the version, a minimal reproduction and the impact you observed. You will receive an acknowledgement, and a fix will be coordinated before public disclosure.
