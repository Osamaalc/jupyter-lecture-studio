# Architecture

This page is for contributors. It explains how the package is organised and the guarantees each layer keeps.

## Layers

```text
lecture_studio/
├── models.py        Immutable, validated content models (Card, Slide, Quiz, Theme, Brand...)
├── visuals.py       Models of subject visuals (Equation, Array, Matrix, Chart, Network, Tree, Graph, Memory, Schema)
├── i18n.py          Locales: interface labels and writing direction
├── themes.py        Theme registry: palette family + design-token overrides
├── markup.py        Escaping, inline markup (`code`, **bold**, $math$) and bidi isolation
├── mathml.py        LaTeX subset -> MathML, validated when content is built
├── highlight.py     Highlight dispatch (stdlib Python, built-in grammars, then Pygments)
├── lexers.py        Built-in grammars for about twenty teaching languages; register_highlighter
├── components/
│   ├── __init__.py  Component registry and plugin loading (entry points)
│   ├── base.py      RenderContext: everything a renderer may use
│   ├── core.py      cover, slide, note, table
│   ├── teaching.py  agenda, code, trace, compare, quiz, exercise, callout, figure, divider
│   └── visuals.py   Layout in Python, output as HTML, MathML or inline SVG
├── deck.py          LectureDeck: the ordered document, notebook display, JSON and export
├── notebook.py      Jupyter integration: cell identity, display, shared fonts
├── styles.py        Stylesheet and font assembly
├── pdf.py           Optional Chromium-based PDF export
├── cli.py           Command line
├── compat.py        LuxurySlideDeck bridge for pre-library notebooks
└── assets/          studio.css (tokens + components), notebook.css, present.css/js, fonts
```

## Data flow

1. A deck method builds a **model**. Models validate eagerly and accept dictionaries, so Python and JSON share one code path. Invalid content never enters a deck.
2. The deck stores models, not HTML, keyed by notebook cell (or by `id`). Re-running a cell replaces its entries in place.
3. A **renderer** turns a model and a `RenderContext` into HTML. Renderers are pure functions: same input, same output (stable ids come from content and position, never randomness).
4. The deck wraps component HTML in a `.lecture-studio` element that carries the theme as CSS variables, the direction and the language.

## Guarantees

- **Safety:** plain text is always escaped before markup is applied; only `RichText` (explicitly trusted) bypasses escaping. Design-token values are validated. Figures accept local images, `data:image/` and `http(s)` only.
- **Determinism:** identical decks produce byte-identical HTML.
- **Isolation:** every selector starts with `.lecture-studio`; nothing leaks into the host page, and a doubled root class restates colors that notebook hosts restyle (inline code, table rows, `pre`), so decks look the same under light and dark hosts. Notebook-wide styling is opt-in (`notebook_style=True`) and follows the host theme.
- **No JavaScript** in notebook output and default exports. Interaction uses `<details>`, radio inputs and CSS. Only presentation exports include a small script.
- **Offline:** fonts and images are embedded; nothing is fetched unless you ask for external fonts or link a remote image.
- **Accessibility:** keyboard-operable disclosures and choices, visible focus rings, reduced-motion support, semantic headings and table scopes.

## Stylesheet

`studio.css` is organised as: tokens (gold) → custom palette derivations → paper palette → frames → components → teaching panels → responsive rules → motion → print. Specificity of two classes or more beats Jupyter's rendered-HTML rules without `!important`, which is reserved for motion and print switches. Frames are size containers, so components adapt to the width of the notebook output rather than the browser window. Logical properties (`inline-start`, `inline-end`) mirror layouts for each direction.

## Visual parity

The original gold design is a contract. `tools/parity/` renders reference lectures with a previous version and with the working tree, then compares the computed style of every element in Chromium at three widths:

```bash
PYTHONPATH=<previous>/src python tools/parity/sample_decks.py out/before
PYTHONPATH=src python tools/parity/sample_decks.py out/after
python tools/parity/compare.py out/before out/after
```

Run it for any change to `studio.css` or to the HTML structure of existing components.

## Quality gates

```bash
python -m pip install -e ".[dev]"
pytest
ruff check src tests tools
mypy
```

CI runs these on Linux, macOS and Windows for Python 3.10 to 3.13.
