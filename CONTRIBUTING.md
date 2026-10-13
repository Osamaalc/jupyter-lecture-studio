# Contributing to Jupyter Lecture Studio

Thank you for helping teachers build better lectures. Contributions in English or Arabic are welcome.

## Ways to help

- **Report a problem** with the notebook host, browser and a minimal lecture that shows it.
- **Add a locale**: copy the English labels from `src/lecture_studio/i18n.py`, translate them and open a pull request.
- **Add a theme**: propose token values for a dark or light palette, with a screenshot.
- **Add a component**: start as a plugin (see `docs/extending.md`); widely useful components can move into the core.
- **Improve documentation**: examples from real courses are especially valuable.

## Development setup

```bash
git clone <repository-url> && cd lecture-studio
python -m venv .venv-dev
.venv-dev/bin/python -m pip install -e ".[dev,notebook,highlight]"
```

## Before opening a pull request

```bash
pytest                       # unit tests
ruff check src tests tools   # lint and import order
mypy                         # types of the public package
python tools/build_docs.py   # when documentation changed (needs the docs extra)
```

If you change `studio.css` or the HTML of an existing component, run the visual-parity check described in `docs/architecture.md` and include its summary. The gold design must not change unintentionally.

## Principles

- **Safe by default.** Plain text is escaped; only `RichText` is trusted HTML.
- **Offline first.** No network access unless the author asks for it.
- **No JavaScript in notebook output.** Interaction uses HTML and CSS; only presentation exports ship a script.
- **Both directions.** Every component must work in Arabic (RTL) and English (LTR). Use logical CSS properties and never apply letter spacing to Arabic text.
- **Every color is a token.** New CSS uses `--ls-*` variables so all themes keep working.
- **Backward compatibility.** Public names, JSON fields and CLI commands follow semantic versioning; deprecate before removing.

## Commit and release

Keep commits focused and describe the user-visible effect. Maintainers update `CHANGELOG.md`, bump `src/lecture_studio/_version.py`, build with `python -m build`, verify with `python tools/verify_release.py dist/` and publish from a tagged commit.
