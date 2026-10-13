# Extending Lecture Studio

## A custom component

A component is a frozen dataclass that subclasses `Component`, plus a renderer that returns HTML.

```python
from dataclasses import dataclass
from typing import ClassVar
from jupyter_lecture_studio import Component, LectureDeck, register_component


@dataclass(frozen=True)
class Timeline(Component):
    kind: ClassVar[str] = "timeline"      # the JSON "type"
    title: str
    events: tuple[str, ...]
    notes: str = ""

    def __post_init__(self):
        object.__setattr__(self, "events", tuple(self.events))


def render_timeline(item, ctx):
    events = "".join(f"<li>{ctx.line(event)}</li>" for event in item.events)
    body = f'<ol class="ls-agenda-list">{events}</ol>'
    return (f'<section class="ls-frame ls-panel"><header class="ls-panel-head">'
            f'<h3 class="ls-panel-title">{ctx.line(item.title)}</h3></header>{body}{ctx.notes(item)}</section>')


register_component(Timeline, render_timeline)

deck = LectureDeck(course="History of computing", locale="en")
deck.add(Timeline("Milestones", ["1843 · Lovelace", "1936 · Turing"]))
deck.render({"type": "timeline", "title": "Again", "events": ["1957 · FORTRAN"]})
```

The `RenderContext` (`ctx`) gives renderers what they need without touching global state:

| Member | Purpose |
|---|---|
| `ctx.line(text)` | One line of escaped author text with inline markup |
| `ctx.text(content)` | Multi-line text or trusted `RichText` |
| `ctx.esc(value)` | Plain HTML escaping |
| `ctx.label(key)` | An escaped locale label |
| `ctx.code(code, language, marked=(), numbers=False)` | A highlighted code block |
| `ctx.topline()` / `ctx.footer()` | The course header and footer |
| `ctx.notes(component)` | Speaker notes (only in presentation exports) |
| `ctx.ordinal` | Position among components of the same kind |
| `ctx.uid` | A stable id for form controls |
| `ctx.include_answers` | `False` for student copies; omit answers then |

Reuse existing classes (`ls-frame`, `ls-panel`, `ls-card`, `ls-code`...) and `--ls-*` tokens so your component follows every theme and direction.

## Distribute it as a plugin

Publish a package with an entry point; Lecture Studio loads it the first time an unknown component type is requested:

```toml
[project.entry-points."lecture_studio.components"]
timeline = "lecture_timeline:register"
```

```python
# lecture_timeline/__init__.py
def register():
    register_component(Timeline, render_timeline)
```

A failing plugin produces a warning and never breaks other lectures.

## Themes and languages

`register_theme(...)` and `register_locale(...)` add reusable identities and interface languages; see [Themes](themes.md) and [Languages](languages.md).

## Programming languages

`register_highlighter(names, function, label=...)` colors another language, or replaces a built-in grammar, everywhere code appears. The function receives the code and returns escaped HTML whose `<span>` classes use the Pygments short names (`k`, `s`, `m`, `c`, `nb`, `nf`...), so every theme colors it. A plugin's `register()` entry point can call it too. See [Syntax highlighting](visuals.md).

## Drawing with SVG

The built-in visuals in `lecture_studio/components/visuals.py` show the pattern for a custom figure. Compute the layout in Python, emit SVG with token classes (`ls-box`, `ls-edge`, `ls-label`...) and escape every text node. Prefix marker and gradient ids with `ctx.uid`, so two figures on one page never collide.
