"""LectureDeck: an ordered collection of components with a brand, a theme and
a locale, displayed in Jupyter and exported to standalone HTML or PDF.

The deck stores validated component models, not HTML. Rendering happens on
display and again on export, so slide numbers in an export always follow the
final order even after cells were re-run out of order.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import html
import json
from pathlib import Path
from typing import Any

from . import notebook
from .components import RenderContext, get_component
from .i18n import Locale, get_locale
from .models import (
    Activity,
    Agenda,
    Brand,
    Callout,
    Card,
    CodeExample,
    Compare,
    Component,
    Content,
    Cover,
    CoverSection,
    Diagram,
    Divider,
    Exercise,
    Figure,
    Note,
    Quiz,
    Slide,
    Table,
    Theme,
    Trace,
    TraceStep,
    coerce,
    coerce_diagram,
)
from .styles import asset, bundled_fonts, font_styles, stylesheet  # noqa: F401  (public helpers)
from .themes import get_theme
from .visuals import Array, Chart, Equation, Graph, Matrix, Memory, Network, Schema, Tree

__all__ = ['LectureDeck']

_JSON_KEYS = {'$schema', 'version', 'brand', 'theme', 'locale', 'markup', 'components'}


@dataclass
class _Entry:
    key: str
    component: Component
    cell: str | None = None


class LectureDeck:
    """A course brand, a visual theme, a locale and the lecture's components.

    Component methods display immediately in Jupyter; ``show=False`` returns
    standalone HTML instead (use it in scripts). Re-running a notebook cell
    replaces what that cell added. ``export()`` saves every component.
    """

    def __init__(self, course: str | None = None, *, series: str | None = None, lesson: str = '',
                 language: str = 'python', theme: str | Theme | Mapping[str, Any] = 'gold',
                 brand: Brand | Mapping[str, Any] | None = None, locale: str | Locale | None = None,
                 markup: str = 'markdown', **theme_options):
        self.brand = coerce(brand, Brand) if brand is not None else Brand(course, series, lesson, language=language)
        if isinstance(theme, Theme):
            if theme_options:
                raise TypeError('Pass options inside Theme when supplying a Theme instance')
            self.theme = theme
        elif isinstance(theme, Mapping):
            self.theme = Theme(**{**theme, **theme_options})
        else:
            self.theme = Theme(preset=theme, **theme_options)
        if locale is None:
            locale = 'en' if self.theme.direction == 'ltr' else 'ar'
        self.locale = get_locale(locale)
        if markup not in ('markdown', 'text'):
            raise ValueError('markup must be "markdown" or "text"')
        self.markup = markup
        self.base_dir = Path.cwd()
        self._entries: list[_Entry] = []
        self._cells: dict[str, list] = {}
        self._auto = 0

    # ------------------------------------------------------------------ state
    @property
    def direction(self) -> str:
        return self.theme.direction or self.locale.direction

    @property
    def components(self) -> tuple[Component, ...]:
        return tuple(entry.component for entry in self._entries)

    @property
    def _components(self) -> list[str]:
        """Rendered component bodies (kept for code written against 0.x)."""
        return [self._render(i) for i in range(len(self._entries))]

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[Component]:
        return iter(self.components)

    def __repr__(self) -> str:
        return (f'<LectureDeck {self.brand.course or self.locale["course"]!r}: {len(self)} components, '
                f'theme={self.theme.preset!r}, locale={self.locale.code!r}>')

    def clear(self) -> None:
        """Remove every component and restart numbering."""
        self._entries.clear()
        self._cells.clear()
        self._auto = 0

    # -------------------------------------------------------------- rendering
    def _context(self, index: int, *, include_answers: bool = True, include_notes: bool = False) -> RenderContext:
        entry = self._entries[index]
        kind = entry.component.kind
        ordinal = sum(1 for e in self._entries[:index + 1] if e.component.kind == kind)
        digest = hashlib.sha1((entry.key + json.dumps(entry.component.to_dict(), ensure_ascii=False, sort_keys=True,
                                                     default=str)).encode('utf-8')).hexdigest()[:10]
        return RenderContext(self.brand, self.theme, self.locale, self.direction, self.markup, ordinal,
                             'ls-' + digest, include_answers, include_notes, self.base_dir)

    def _render(self, index: int, **options) -> str:
        component = self._entries[index].component
        return get_component(component.kind).render(component, self._context(index, **options))

    def _wrapper(self, body: str, *, present: bool = False, fragments: bool = False) -> str:
        preset = get_theme(self.theme.preset)
        variables = {
            'accent': self.theme.accent or preset.accent,
            'background': self.theme.background or preset.background,
            'width': f'{self.theme.max_width}px',
            'dir': self.direction,
            **preset.tokens,
            **(self.theme.tokens or {}),
        }
        style = ';'.join(f'--ls-{name}:{value}' for name, value in variables.items())
        mode = ' ls-present' if present else ''
        steps = ' data-fragments="true"' if present and fragments else ''
        return (f'<div class="lecture-studio{mode}"{steps} dir="{self.direction}" lang="{self.locale.code}" '
                f'data-theme="{self.theme.preset}" data-palette="{self.theme.palette}" '
                f'data-motion="{str(self.theme.motion).lower()}" data-notebook-style="{str(self.theme.notebook_style).lower()}" '
                f'style="{html.escape(style)}">{body}</div>')

    def _styles(self, *, fonts: bool = True, present: bool = False) -> str:
        css = stylesheet(self.theme.notebook_style, present)
        if fonts or self.theme.external_fonts:
            css = font_styles(self.theme.external_fonts) + '\n' + css
        return f'<style>{css}</style>'

    def html(self, *, include_answers: bool = True, notes: bool = False) -> str:
        """Every component as one standalone HTML fragment (styles included)."""
        bodies = ''.join(self._render(i, include_answers=include_answers, include_notes=notes)
                         for i in range(len(self._entries)))
        return self._styles() + self._wrapper(bodies)

    def _repr_html_(self) -> str:
        return self.html()

    def styles(self, *, show: bool = True) -> str | None:
        """Display fonts and styles once, e.g. in the first cell of a notebook.

        Later outputs then omit the embedded fonts. Useful when the first
        lecture output is far down the notebook or was cleared.
        """
        if not show:
            return self._styles()
        cell = notebook.current_cell()
        notebook.reset_fonts(cell[0] if cell else None)
        notebook.display_html(self._styles())
        return None

    # ------------------------------------------------------------- collection
    def _insert(self, component: Component, id: str | None) -> int:
        cell = notebook.current_cell()
        cell_id = None
        position = None
        if cell is not None:
            cell_id, count = cell
            state = self._cells.get(cell_id)
            if state is None or state[0] != count:
                # A new execution of this cell replaces what it added before.
                old = [i for i, e in enumerate(self._entries) if e.cell == cell_id]
                state = [count, old[0] if old else None, 0]
                self._entries = [e for e in self._entries if e.cell != cell_id]
                self._cells[cell_id] = state
            key = f'cell:{cell_id}:{state[2]}'
            state[2] += 1
            position = state[1]
            if position is not None:
                state[1] += 1
        else:
            self._auto += 1
            key = f'auto:{self._auto}'
        if id is not None:
            if not isinstance(id, str) or not id:
                raise TypeError('id must be a non-empty string')
            key = 'id:' + id
            for i, entry in enumerate(self._entries):
                if entry.key == key:
                    entry.component, entry.cell = component, cell_id
                    return i
        entry = _Entry(key, component, cell_id)
        if position is None or position > len(self._entries):
            self._entries.append(entry)
            return len(self._entries) - 1
        self._entries.insert(position, entry)
        return position

    def add(self, component: Component, *, id: str | None = None, show: bool = True) -> str | None:
        """Add any registered component (including plugin components)."""
        if not isinstance(component, Component):
            raise TypeError('add() expects a component such as Slide(...) or Quiz(...)')
        if get_component(component.kind).model is not type(component):
            raise TypeError(f'{type(component).__name__} is not the registered model for {component.kind!r}')
        index = self._insert(component, id)
        try:
            body = self._render(index)
        except Exception:
            del self._entries[index]
            raise
        if show:
            cell = self._entries[index].cell
            fonts = notebook.claim_fonts(cell)
            notebook.display_html(self._styles(fonts=fonts) + self._wrapper(body))
            return None
        return self._styles() + self._wrapper(body)

    # ------------------------------------------------------------- components
    def cover(self, title: str, description: Content = '', *, kicker: str = '', tags: Sequence[str] = (),
              sections: Sequence[CoverSection | Mapping] = (), hero_code: str = '', hero_result: str = '',
              hero_label: str | None = None, footer_label: str | None = None, notes: str = '',
              id: str | None = None, show: bool = True):
        """Lecture cover with tags, section cards and an optional code emblem."""
        parts = [coerce(s, CoverSection) for s in sections]
        return self.add(Cover(title, description, kicker, tags, parts, hero_code, hero_result, hero_label,
                              footer_label, notes), id=id, show=show)

    def slide(self, title: str, description: Content = '', *, cards: Sequence[Card | Mapping] = (),
              subtitle: str = '', diagram: Diagram | Mapping | str | None = None,
              activity: Activity | Mapping | None = None, notes: str = '', id: str | None = None, show: bool = True):
        """Numbered concept slide: explanation cards, a diagram and an activity."""
        items = [coerce(c, Card) for c in cards]
        check = coerce(activity, Activity) if activity is not None else None
        return self.add(Slide(title, description, items, subtitle, coerce_diagram(diagram), check, notes), id=id, show=show)

    def note(self, title: str, body: Content = '', *, notes: str = '', id: str | None = None, show: bool = True):
        """A light reading panel for summaries and remarks."""
        return self.add(Note(title, body, notes), id=id, show=show)

    def table(self, title: str, headers: Sequence[Any], rows: Iterable[Sequence[Any]], *, notes: str = '',
              id: str | None = None, show: bool = True):
        """A comparison table. Cells are plain text."""
        return self.add(Table(title, headers, list(rows), notes), id=id, show=show)

    def callout(self, body: Content, *, style: str = 'info', title: str | None = None, notes: str = '',
                id: str | None = None, show: bool = True):
        """A highlighted remark: info, tip, warning, mistake, success or key."""
        return self.add(Callout(body, title, style, notes), id=id, show=show)

    def compare(self, title: str, before: str, after: str, *, mode: str = 'wrong-right',
                before_label: str | None = None, after_label: str | None = None, before_note: Content = '',
                after_note: Content = '', description: Content = '', language: str | None = None,
                notes: str = '', id: str | None = None, show: bool = True):
        """Two code versions side by side (``wrong-right`` or ``before-after``)."""
        return self.add(Compare(title, before, after, mode, before_label, after_label, before_note, after_note,
                                description, language, notes), id=id, show=show)

    def code(self, code: str, *, title: str = '', output: str = '', language: str | None = None,
             highlight: Sequence[int] = (), line_numbers: bool = False, description: Content = '',
             caption: str = '', notes: str = '', id: str | None = None, show: bool = True):
        """Displayed code with its expected output, highlighted lines and numbers."""
        return self.add(CodeExample(code, title, output, language, highlight, line_numbers, description, caption,
                                    notes), id=id, show=show)

    def quiz(self, question: str, options: Sequence[str], answer: int | str, *, explanation: Content = '',
             code: str = '', language: str | None = None, title: str | None = None, notes: str = '',
             id: str | None = None, show: bool = True):
        """Multiple-choice check that marks the chosen option, without JavaScript."""
        return self.add(Quiz(question, options, answer, explanation, code, language, title, notes), id=id, show=show)

    def trace(self, code: str, steps: Sequence[TraceStep | Mapping], *, title: str = '',
              language: str | None = None, description: Content = '', notes: str = '',
              id: str | None = None, show: bool = True):
        """Step-by-step execution: the current line, variables and output."""
        timeline = [coerce(s, TraceStep) for s in steps]
        return self.add(Trace(code, timeline, title, language, description, notes), id=id, show=show)

    def exercise(self, title: str, task: Content, *, starter: str = '', hints: Sequence[str] = (),
                 solution: str = '', explanation: Content = '', language: str | None = None, notes: str = '',
                 id: str | None = None, show: bool = True):
        """A practice task with progressive hints and a hidden solution."""
        return self.add(Exercise(title, task, starter, hints, solution, explanation, language, notes),
                        id=id, show=show)

    def agenda(self, items: Sequence[str], *, title: str | None = None, mode: str = 'goals', notes: str = '',
               id: str | None = None, show: bool = True):
        """Learning goals (``mode='goals'``) or key takeaways (``mode='recap'``)."""
        return self.add(Agenda(items, title, mode, notes), id=id, show=show)

    def recap(self, items: Sequence[str], *, title: str | None = None, notes: str = '',
              id: str | None = None, show: bool = True):
        """Key takeaways at the end of a lecture."""
        return self.agenda(items, title=title, mode='recap', notes=notes, id=id, show=show)

    def figure(self, src: str, *, caption: str = '', alt: str = '', title: str = '', width: int | None = None,
               notes: str = '', id: str | None = None, show: bool = True):
        """An image; local files are embedded so the lecture stays self-contained."""
        return self.add(Figure(src, caption, alt, title, width, notes), id=id, show=show)

    def divider(self, title: str, subtitle: str = '', *, label: str | None = None, notes: str = '',
                id: str | None = None, show: bool = True):
        """A section break between parts of a lecture."""
        return self.add(Divider(title, subtitle, label, notes), id=id, show=show)

    # ---------------------------------------------------------------- visuals
    def math(self, latex: str | Sequence[str], *, title: str = '', legend: Mapping[str, str] | None = None,
             description: Content = '', caption: str = '', notes: str = '', id: str | None = None, show: bool = True):
        """Display formulas written in LaTeX; ``legend`` explains the symbols."""
        return self.add(Equation(latex, title, dict(legend or {}), description, caption, notes), id=id, show=show)

    def array(self, values: Sequence[Any], *, title: str = '', name: str = '', highlight: Sequence[int] = (),
              pointers: Mapping[str, int] | None = None, slice: Sequence[int] | None = None, negative: bool = False,
              description: Content = '', caption: str = '', notes: str = '', id: str | None = None, show: bool = True):
        """A list drawn as indexed cells, with pointers (``{'i': 0}``) and a slice ``[start, stop]``."""
        return self.add(Array(values, title, name, highlight, dict(pointers or {}), slice, negative, description,
                              caption, notes), id=id, show=show)

    def matrix(self, rows: Sequence[Sequence[Any]], *, title: str = '', name: str = '', row_labels: Sequence[str] = (),
               col_labels: Sequence[str] = (), row_title: str = '', col_title: str = '', heatmap: bool = False,
               highlight: Sequence[Sequence[int]] = (), brackets: bool = False, metrics: Mapping[str, Any] | None = None,
               description: Content = '', caption: str = '', notes: str = '', id: str | None = None, show: bool = True):
        """A grid of values; ``heatmap=True`` shades cells, ``brackets=True`` draws a math matrix."""
        return self.add(Matrix(rows, title, name, row_labels, col_labels, row_title, col_title, heatmap, highlight,
                               brackets, dict(metrics or {}), description, caption, notes), id=id, show=show)

    def confusion_matrix(self, counts: Sequence[Sequence[int]], labels: Sequence[str], *, title: str = '',
                         description: Content = '', caption: str = '', notes: str = '', id: str | None = None,
                         show: bool = True):
        """A classifier's confusion matrix: actual classes by row, predictions by column, with accuracy."""
        grid = [list(row) for row in counts]
        size = min(len(grid), len(grid[0])) if grid else 0
        total = sum(sum(row) for row in grid)
        metrics = {self.locale['matrix.accuracy']: f'{sum(grid[i][i] for i in range(size)) / total:.1%}'} if total else {}
        return self.matrix(grid, title=title, row_labels=labels, col_labels=labels,
                           row_title=self.locale['matrix.actual'], col_title=self.locale['matrix.predicted'],
                           heatmap=True, highlight=[(i, i) for i in range(size)], metrics=metrics,
                           description=description, caption=caption, notes=notes, id=id, show=show)

    def chart(self, series: Any, *, mode: str = 'line', labels: Sequence[str] = (), title: str = '',
              x_label: str = '', y_label: str = '', y_min: float | None = None, y_max: float | None = None,
              description: Content = '', caption: str = '', notes: str = '', id: str | None = None, show: bool = True):
        """A line, bar or scatter chart.

        ``series`` is a list of numbers, ``{'loss': [...], 'accuracy': [...]}``
        or a list of ``{'name', 'values', 'x'}`` dictionaries.
        """
        if isinstance(series, Mapping) and 'values' not in series:
            series = [{'name': name, 'values': list(values)} for name, values in series.items()]
        elif isinstance(series, Mapping):
            series = [series]
        elif isinstance(series, Sequence) and series and all(isinstance(v, (int, float)) for v in series):
            series = [{'name': '', 'values': list(series)}]
        return self.add(Chart(list(series), mode, labels, title, x_label, y_label, y_min, y_max, description, caption,
                              notes), id=id, show=show)

    def network(self, layers: Sequence[int], *, labels: Sequence[str] = (), title: str = '', description: Content = '',
                caption: str = '', notes: str = '', id: str | None = None, show: bool = True):
        """A feed-forward neural network, e.g. ``[4, 6, 3]`` neurons per layer."""
        return self.add(Network(layers, labels, title, description, caption, notes), id=id, show=show)

    def tree(self, root: Any, *, title: str = '', description: Content = '', caption: str = '', notes: str = '',
             id: str | None = None, show: bool = True):
        """A rooted tree: ``{'value': '8', 'children': [{'value': '3'}, None]}``."""
        return self.add(Tree(root, title, description, caption, notes), id=id, show=show)

    def graph(self, nodes: Sequence[Any], edges: Sequence[Any] = (), *, directed: bool = False, title: str = '',
              description: Content = '', caption: str = '', notes: str = '', id: str | None = None, show: bool = True):
        """Nodes and edges: ``graph(['A', 'B'], [('A', 'B', 4)], directed=True)``."""
        return self.add(Graph(list(nodes), list(edges), directed, title, description, caption, notes), id=id, show=show)

    def memory(self, frames: Any, objects: Any = (), *, title: str = '', stack_label: str | None = None,
               heap_label: str | None = None, description: Content = '', caption: str = '', notes: str = '',
               id: str | None = None, show: bool = True):
        """Frames, variables and the objects they reference (``"@id"`` draws an arrow).

        ``memory({'main': {'x': 5, 'nums': '@a'}}, {'a': [1, 2]})``
        """
        if isinstance(frames, Mapping):
            frames = [{'name': name, 'variables': dict(variables)} for name, variables in frames.items()]
        if isinstance(objects, Mapping):
            objects = [{'id': key, 'value': value} for key, value in objects.items()]
        return self.add(Memory(list(frames), list(objects), title, stack_label, heap_label, description, caption, notes),
                        id=id, show=show)

    def schema(self, tables: Any, *, title: str = '', per_row: int = 3, description: Content = '', caption: str = '',
               notes: str = '', id: str | None = None, show: bool = True):
        """Database tables and relationships: ``{'students': ['id INT PK', 'name TEXT'], ...}``."""
        if isinstance(tables, Mapping):
            tables = [{'name': name, 'columns': list(columns)} for name, columns in tables.items()]
        return self.add(Schema(list(tables), title, per_row, description, caption, notes), id=id, show=show)

    # ------------------------------------------------------------------- JSON
    def render(self, content: Mapping[str, Any] | Sequence[Mapping[str, Any]], *, show: bool = True):
        """Render a component dictionary (``{"type": "slide", ...}``) or a list."""
        if isinstance(content, Mapping):
            data = dict(content)
            kind = data.pop('type', 'slide')
            id = data.pop('id', None)
            spec = get_component(kind)
            return self.add(spec.model(**data), id=id, show=show)
        if isinstance(content, (str, bytes)):
            raise TypeError('Content must be a component dictionary or a list')
        results = [self.render(item, show=show) for item in content]
        return None if show else results

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], *, show: bool = True, base_dir: str | Path | None = None) -> LectureDeck:
        """Build a deck from the portable course format (see ``to_dict``)."""
        if not isinstance(data, Mapping) or set(data) - _JSON_KEYS:
            raise ValueError('Course JSON supports only brand, theme, locale, markup and components')
        deck = cls(brand=Brand(**data.get('brand', {})), theme=Theme(**data.get('theme', {})),
                   locale=data.get('locale'), markup=data.get('markup', 'markdown'))
        if base_dir is not None:
            deck.base_dir = Path(base_dir)
        deck.render(data.get('components', []), show=show)
        return deck

    @classmethod
    def from_file(cls, path: str | Path, *, show: bool = True) -> LectureDeck:
        """Load one portable JSON course file and render its components."""
        path = Path(path)
        data = json.loads(path.read_text(encoding='utf-8'))
        return cls.from_dict(data, show=show, base_dir=path.resolve().parent)

    def to_dict(self) -> dict[str, Any]:
        """The deck in the portable JSON course format."""
        brand = {k: v for k, v in vars(self.brand).items() if v not in (None, '') and not (k == 'language' and v == 'python')}
        theme = {k: v for k, v in vars(self.theme).items() if v != getattr(Theme, k, None) and v is not None}
        return {'brand': brand, 'theme': theme, 'locale': self.locale.code,
                'components': [e.component.to_dict() | ({'id': e.key[3:]} if e.key.startswith('id:') else {})
                               for e in self._entries]}

    def save(self, path: str | Path) -> Path:
        """Write the deck as a JSON course file that ``from_file`` reads back."""
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return destination.resolve()

    # ----------------------------------------------------------------- export
    def export(self, path: str | Path, *, title: str | None = None, include_answers: bool = True,
               present: bool = False, notes: bool | None = None, fragments: bool = False) -> Path:
        """Save a standalone HTML file with embedded styles and fonts.

        ``include_answers=False`` removes activity answers, quiz keys and
        exercise solutions from the file (a student copy). ``present=True``
        adds a slideshow mode: arrow keys, fullscreen (F) and speaker notes (S);
        ``fragments=True`` then reveals cards one at a time. Speaker notes are
        only included in presentation exports unless ``notes`` says otherwise.
        """
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        notes = present if notes is None else notes
        bodies = ''.join(self._render(i, include_answers=include_answers, include_notes=notes)
                         for i in range(len(self._entries)))
        page_title = html.escape(title or self.brand.course or self.locale['course'])
        script = ''
        if present:
            labels = {k: self.locale[k] for k in self.locale.labels if k.startswith('present.')}
            script = ('<script>window.LECTURE_STUDIO_LABELS=' + json.dumps(labels, ensure_ascii=False)
                      .replace('<', '\\u003c') + ';' + asset('present.js') + '</script>')
        result = (f'<!doctype html><html lang="{self.locale.code}" dir="{self.direction}"><head><meta charset="utf-8">'
                  f'<meta name="viewport" content="width=device-width,initial-scale=1">'
                  f'<meta name="generator" content="Lecture Studio"><title>{page_title}</title>'
                  f'<style>body{{margin:0;padding:24px;background:#e9e9e5}}@media(max-width:600px){{body{{padding:8px}}}}</style>'
                  f'</head><body>{self._styles(present=present)}'
                  f'{self._wrapper(bodies, present=present, fragments=fragments)}{script}</body></html>')
        destination.write_text(result, encoding='utf-8')
        return destination.resolve()

    def export_pdf(self, path: str | Path, *, width: int | None = None, scale: int = 2, mode: str = 'faithful',
                   include_answers: bool = True, title: str | None = None, timeout: int = 60,
                   audit_dir: str | Path | None = None, browser_path: str | Path | None = None) -> Path:
        """Save the deck as a PDF using the optional pdf extra.

        Faithful mode preserves screen pixels as lossless images. Vector mode
        keeps selectable text. Animations become a deterministic static frame.
        Collapsible sections are open; ``include_answers=False`` hides answers.
        """
        from .pdf import export_deck_pdf
        options: dict[str, Any] = dict(scale=scale, mode=mode, include_answers=include_answers,
                                       timeout=timeout, audit_dir=audit_dir, browser_path=browser_path)
        if width is not None:
            options['width'] = width
        if title is not None:
            options['title'] = title
        return export_deck_pdf(self, path, **options)
