# Release notes

## 1.0.2 — Arabic bold fix

**Text:** `**bold**` attached to a one-letter Arabic proclitic (و ف ب ل ك), as in `و**الكائن**`, is now bold instead of showing the asterisks. Python operators such as `a**2` and `**kwargs` stay literal.

## 1.0.1 — Light and dark notebooks

**Dark mode:** `notebook_style=True` now follows the JupyterLab theme. Under JupyterLab Dark the notebook page, markdown cells, code editors (including edit mode) and outputs switch to a dark design matched to the gold slides; under JupyterLab Light nothing changes.

**Host-proof decks:** slides and panels look identical under light and dark hosts. Inline `` `code` ``, trace variables, matrices, confusion matrices, tables and reveal buttons no longer pick up JupyterLab's grey code chips, striped or highlighted rows, or table text colors; notebook PDFs of traces are fixed as well.

**PDF:** notebook pages group better (a short section heading travels with its content; practice cells share the page of their slide); the first real lecture went from 50 to 40 pages.

**Quality:** a real-browser test exports the same notebook with nbconvert's Light and Dark themes and checks identical deck colors and WCAG AA contrast for notebook text in both (88 tests).

## 1.0.0 — Bilingual teaching platform

**New components:** `agenda`/`recap`, `code` (output panel, highlighted lines, line numbers), `trace` (step-by-step execution with variables), `compare` (common mistake vs better approach), `quiz` (graded multiple choice without JavaScript), `exercise` (progressive hints, hidden solution), `callout` (six styles), `figure` (embedded images) and `divider`.

**Languages:** interface labels follow the lecture's locale (`ar`, `en`, or your own with `register_locale`); direction follows the locale. English lectures no longer show Arabic interface text.

**Themes:** a token-driven stylesheet where every color is a `--ls-*` variable; new `paper` (light), `violet` and `ruby` themes; per-deck `tokens=` overrides; `register_theme` for institutional identities; automatic RTL/LTR mirroring with logical properties.

**Sharing:** student copies without answers (`include_answers=False`), presentation mode (`present=True`) with keyboard navigation, fit-to-screen scaling, fullscreen, speaker notes and optional step-by-step reveal; JSON round trip with `deck.save()` and `from_dict()`; `validate`, `info`, `--student` and `--present` in the CLI.

**Notebooks:** re-running a cell replaces its components in place; embedded fonts are sent once per notebook (about 80% smaller outputs); identical content gives identical HTML.

**Subject visuals:** `math` (LaTeX to MathML, with a symbol legend, and `$...$` inside any text), `array`, `matrix` and `confusion_matrix`, `chart` (line, bar, scatter), `network`, `tree`, `graph`, `memory` (frames, objects and references) and `schema` (tables, keys and relationships). All are laid out in Python and drawn as HTML or SVG, with no JavaScript.

**Programming languages:** built-in highlighting for about twenty teaching languages, identical on every machine without Pygments; `register_highlighter` for more. Code never shows typographic ligatures.

**PDF:** execution traces print every step; short callouts share the previous page; searchable (vector) PDFs keep their layout at page boundaries and no longer show grey boxes in macOS Preview.

**Text:** inline `` `code` `` and `**bold**` in plain text; automatic bidi isolation of `C++`/`C#` in Arabic; Arabic text never receives letter spacing; Arabic comments inside code stay joined.

**Engineering:** document model with a component registry and plugin entry points (`lecture_studio.components`), typed public API (mypy clean), ruff, 84 tests including real-browser PDF checks, visual-parity tooling, CI for Linux/macOS/Windows and Python 3.10–3.13.

**Compatibility:** the gold design is unchanged (verified element by element); the public Python API, JSON format, CLI and `LuxurySlideDeck` keep working. HTML class names now use the `ls-` prefix; see the [migration guide](MIGRATION.md).

## 0.3.0.dev0 — Local PDF preview

Optional offline PDF export for decks, JSON, HTML and saved notebooks, with faithful snapshots or searchable vector output.

## 0.2.0 — PyPI distribution

- Public distribution name: `jupyter-lecture-studio`; matching import `jupyter_lecture_studio`.
- English and Arabic documentation, local search and an offline documentation command.
- Explicit Python and font license notices in the release archives.

## 0.1.1 — Design parity

Bundled fonts, original palette, cover spacing, code alignment and footer label.

## 0.1.0 — Initial local library

Course-independent covers, cards, diagrams, activities, notes, tables, themes, JSON loading and HTML export extracted from the original teaching notebook.
