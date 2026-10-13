# Changelog

All notable changes are listed here. The project follows [semantic versioning](https://semver.org/).

## 1.0.2 — Arabic bold fix (2026-10-12)

### Fixed
- `**bold**` right after a one-letter Arabic proclitic (و ف ب ل ك), as in `و**الكائن**`, is now bold instead of showing the asterisks.

## 1.0.1 — Light and dark notebooks (2026-10-12)

### Added
- `notebook_style=True` follows the JupyterLab / Notebook 7 theme: under a dark theme the notebook page, markdown cells, code editors and outputs switch to a dark design matched to the gold slides; under a light theme the original design is unchanged.
- Regression test that exports the same notebook with nbconvert's Light and Dark themes and checks, in Chromium, that deck colors are identical and that notebook text meets WCAG AA contrast in both.

### Changed
- Notebook PDFs: a short section heading stays on the page of the content that follows it, short practice cells share the page of the slide before them (never the cover), and untitled pages are bookmarked under their section. The first real lecture shrank from 50 to 40 pages.
- Notebook style: input prompts are slightly darker (AA contrast); terminal colors in tracebacks are readable on the output panel.

### Fixed
- Inline `` `code` `` inside slides and panels was unreadable under the JupyterLab Light theme (a grey host chip behind pale text) and grey under the Dark theme; callout and note code went blank under Dark.
- JupyterLab striped and hover-highlighted rows inside decks: trace variable values, `matrix` and `confusion_matrix` cells were white and unreadable under Light (also in notebook PDFs), black under Dark; `table` rows turned black and their text vanished under Dark.
- Reveal buttons (answers, hints, solutions, "concept in motion") inside notebook-style lectures were dull brown on dark panels; the notebook rule for markdown `<details>` no longer reaches decks.
- Under a dark JupyterLab theme, notebook-style practice code showed white variable names on a light editor, editing flipped the editor to black with dark syntax colors, and markdown and DataFrame table headers were invisible.
- The collapsed-source line above callouts, notes and tables is hidden like the one above slides.
- Searchable (vector) PDFs no longer leave transparent margins when the page body is a fixed-height scroll container.

### Known issues
- Searchable (vector) PDFs of notebooks can still shift pages slightly; use the default faithful mode for notebooks.
- Exported PDFs are created with owner-only permissions (0600) instead of following the umask.

## 1.0.0 — Bilingual teaching platform (2026-10-11)

### Added
- Subject visuals: `math` (LaTeX to MathML with a symbol legend; `$...$` inside any text), `array`, `matrix`, `confusion_matrix`, `chart` (line, bar, scatter), `network`, `tree`, `graph`, `memory` (frames, objects, references) and `schema` (tables, keys, relationships). Drawn as HTML, MathML or inline SVG, without JavaScript.
- Built-in syntax highlighting for Python, C, C++, Java, C#, JavaScript, TypeScript, Kotlin, Go, Rust, Dart, Swift, SQL, Bash, R, MATLAB, JSON, HTML and CSS without Pygments; `register_highlighter` for more; toolbar labels such as `C++` and `C#`.
- Components: `agenda`/`recap`, `code` (output panel, highlighted lines, line numbers), `trace` (step-by-step execution), `compare` (mistake vs better approach), `quiz` (graded multiple choice), `exercise` (hints and hidden solution), `callout` (six styles), `figure` (embedded images) and `divider`. All interactive parts work without JavaScript.
- Locales: interface labels and direction follow `locale` (`ar`, `en`); `register_locale` and `Locale.with_labels` for other languages.
- Themes: token-driven stylesheet (every color is a `--ls-*` variable), `paper` light theme, `violet` and `ruby`, per-deck `tokens=`, `register_theme`.
- Sharing: `export(include_answers=False)` student copies; `export(present=True)` presentation mode with keyboard navigation, scaling, fullscreen, speaker notes (`notes=`) and `fragments=True`.
- JSON: `to_dict`, `save`, `from_dict`, trusted HTML as `{"html": ...}`, every component type available.
- CLI: `validate`, `info`, `export --student/--present/--fragments`, `init --locale`.
- Extension API: `register_component`, `RenderContext`, plugin entry points (`lecture_studio.components`), `deck.add()`.
- Inline `` `code` `` and `**bold**` in plain text; automatic bidi isolation of `C++`/`C#` in Arabic.
- Developer tooling: visual-parity harness (`tools/parity`), ruff, mypy, CI, contribution guides.

### Changed
- Re-running a notebook cell replaces the components it added; numbering and exports stay correct.
- Embedded fonts are sent once per notebook (outputs about 80% smaller); `deck.styles()` re-sends them.
- Rendering is deterministic: identical content produces identical HTML.
- HTML classes use the `ls-` prefix; Python highlighting emits Pygments token classes; f-strings are highlighted.
- Layouts use logical properties, so LTR lectures mirror correctly.
- `Brand`/`Activity` label defaults and `Theme.direction` are `None` and resolved from the locale.
- The gold design is unchanged, verified element by element against 0.3.0.dev0 and a real lecture.
- Code shows `!=`, `>=` and `<<` as typed (no font ligatures); preprocessor lines use the keyword color.
- PDF: execution traces print every step; short callouts share the page of the content before them.

### Fixed
- Arabic interface text no longer appears in English lectures.
- Arabic labels in letter-spaced slots and Arabic comments in code stay joined.
- The cover description in LTR lectures is no longer pushed to the right.
- Searchable (vector) PDF pages no longer shift when content crosses a page boundary, and no longer show grey shadow boxes in macOS Preview.

## 0.3.0.dev0 — Local PDF preview

- Optional offline PDF export for deck collections, JSON, HTML and saved notebooks.
- Faithful lossless screen snapshots; optional searchable vector output.
- Bundled fonts, deterministic animation state and fitted page heights.
- Expand every collapsible section before measuring PDF pages; `include_answers=False` / `--hide-answers` for a student version.
- Hidden notebook inputs/outputs, no code execution, atomic destination replacement, CLI and PDF guide.

## 0.2.0

- Publish under the descriptive name Jupyter Lecture Studio (`jupyter-lecture-studio`).
- Add the `jupyter_lecture_studio` import while preserving `lecture_studio` and the existing CLI.
- Add English and Arabic documentation, a searchable offline documentation site, and a `docs` CLI command.
- Add PyPI metadata, explicit MIT/OFL licensing, clean source distributions and release verification tooling.
- Preserve the original fonts, gold design and lecture compatibility from 0.1.1.

## 0.1.1

- Bundle the original Cairo and JetBrains Mono variable fonts for offline parity.
- Preserve the original gold palette, gradients, cover spacing and hero alignment.
- Restore gold Python prompts, independent cover footer labels and C++ bidi isolation.
- Omit empty reason panels and restore checkpoint code without an extra toolbar.
- Add a detailed before/extraction/fixed design audit and regression coverage.

## 0.1.0

- Extract premium Arabic teaching design into an installable, course-independent library.
- Add covers, slides, cards, flow diagrams, reveal activities, notes and tables.
- Add scoped themes, custom colors, RTL/LTR, motion control and offline HTML export.
- Add JSON content loader, starter CLI, Arabic documentation and notebooks.
- Preserve the old LuxurySlideDeck API through a migration adapter.
