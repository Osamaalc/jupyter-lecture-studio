# Troubleshooting and supported behavior

| Symptom | Action |
|---|---|
| Import cannot be found | Install with `%pip` in the active notebook, then restart the kernel. |
| Notebook output is unstyled | Trust the notebook or re-run its display cells. Some hosted platforms strip CSS. |
| Text uses a system font | The output carrying the fonts was cleared. Run `deck.styles()` once, or re-run the first lecture cell. |
| Old fonts or colors after upgrading | Restart the kernel and re-run the display cells. Saved outputs keep the HTML they were created with. |
| Components appear twice in an export | Your notebook host does not report cell ids. Use `id="..."` on components, or `deck.clear()` and run in order. |
| SQL / Java / C++ has no syntax colors | Install the `[highlight]` extra. Plain-text fallback remains supported. |
| Arabic text looks disconnected | Do not add letter spacing to Arabic in custom CSS; the library avoids it automatically. |
| Quiz or trace steps do not respond | Some hosts remove form controls from untrusted output. Trust the notebook or use the exported HTML. |
| Answers missing from a printed handout | Expand the answers before printing, or use `export_pdf()` which expands them. |
| `docs` says documentation is missing | In a source checkout, run `python tools/build_docs.py`. Installed releases include the built site. |

## Support scope

The core renderer runs without IPython or Pygments. Display and re-run tracking are verified in JupyterLab 4; Notebook 7 and VS Code use the same protocol. Modern CSS (container queries, `:has()`, logical properties, `color-mix()`) requires a browser from 2023 or later. Colab and other hosted services may restrict HTML; validate before teaching.

Displayed code is never executed by the renderer. Export includes only the deck's components.

## Keep your lecture reproducible

Record the package version used for a course. Before distributing a revised handout, restart the kernel, run all cells, then export.
