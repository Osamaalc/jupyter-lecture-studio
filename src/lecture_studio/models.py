"""Validated content and theme models. All text is plain text by default.

Models are immutable, accept nested dictionaries (so JSON maps directly onto
them) and validate eagerly: an invalid component never reaches a deck.
Interface labels left as ``None`` come from the deck's locale.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import MISSING, dataclass, field, fields
import re
from typing import Any, ClassVar

from .themes import get_theme, validate_tokens

__all__ = [
    'RichText', 'Theme', 'Brand', 'Card', 'Node', 'Diagram', 'Activity', 'CoverSection',
    'Component', 'Cover', 'Slide', 'Note', 'Table', 'Callout', 'Compare', 'CodeExample',
    'Quiz', 'TraceStep', 'Trace', 'Exercise', 'Agenda', 'Figure', 'Divider',
]


def text(value, name):
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")


def optional_text(value, name):
    if value is not None:
        text(value, name)


def choice(value, values, name):
    if value not in values:
        raise ValueError(f"{name} must be one of: {', '.join(values)}")


def flag(value, name):
    if not isinstance(value, bool):
        raise TypeError(f'{name} must be a bool')


@dataclass(frozen=True)
class RichText:
    """Explicitly trusted author HTML. Never use for untrusted student input."""
    html: str

    def __post_init__(self):
        text(self.html, 'RichText.html')

    def __bool__(self):
        return bool(self.html.strip())


Content = str | RichText


def content(value, name):
    """Plain text or trusted HTML; JSON spells trusted HTML as {"html": "..."}."""
    if isinstance(value, Mapping) and set(value) == {'html'}:
        return RichText(value['html'])
    if not isinstance(value, (str, RichText)):
        raise TypeError(f'{name} must be str or RichText')
    return value


def coerce(value, cls):
    if isinstance(value, cls):
        return value
    if isinstance(value, Mapping):
        return cls(**value)
    raise TypeError(f'Expected {cls.__name__} or a dictionary')


def strings(values, name):
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise TypeError(f'{name} must be a list of strings')
    for value in values:
        text(value, name)
    return tuple(values)


def _set(obj, name, value):
    object.__setattr__(obj, name, value)


@dataclass(frozen=True)
class Theme:
    """Visual settings. ``direction=None`` follows the deck's locale."""
    preset: str = 'gold'
    accent: str | None = None
    background: str | None = None
    motion: bool = True
    direction: str | None = None
    max_width: int = 1280
    notebook_style: bool = False
    external_fonts: bool = False
    tokens: Mapping[str, str] | None = None

    def __post_init__(self):
        get_theme(self.preset)
        if self.direction is not None:
            choice(self.direction, ('rtl', 'ltr'), 'direction')
        for name in ('accent', 'background'):
            value = getattr(self, name)
            if value is not None and not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
                raise ValueError(f'{name} must be a six-digit hex color, e.g. #ECD29A')
        if isinstance(self.max_width, bool) or not isinstance(self.max_width, int) or not 320 <= self.max_width <= 2400:
            raise ValueError('max_width must be an integer between 320 and 2400')
        for name in ('motion', 'notebook_style', 'external_fonts'):
            flag(getattr(self, name), name)
        if self.tokens is not None:
            _set(self, 'tokens', validate_tokens(self.tokens))

    @property
    def palette(self) -> str:
        preset = get_theme(self.preset)
        if preset.palette == 'original' and (self.accent or self.background):
            return 'custom'
        return preset.palette


@dataclass(frozen=True)
class Brand:
    """Course identity shown on every slide. ``None`` uses the locale default."""
    course: str | None = None
    series: str | None = None
    lesson: str = ''
    footer: str | None = None
    language: str = 'python'

    def __post_init__(self):
        for name in ('course', 'series', 'footer'):
            optional_text(getattr(self, name), name)
        for name in ('lesson', 'language'):
            text(getattr(self, name), name)


@dataclass(frozen=True)
class Card:
    title: str
    explanation: Content = ''
    code: str = ''
    reason: Content = ''
    language: str | None = None

    def __post_init__(self):
        text(self.title, 'Card.title')
        text(self.code, 'Card.code')
        _set(self, 'explanation', content(self.explanation, 'Card.explanation'))
        _set(self, 'reason', content(self.reason, 'Card.reason'))
        optional_text(self.language, 'Card.language')


@dataclass(frozen=True)
class Node:
    value: str
    note: str = ''
    selected: bool = False

    def __post_init__(self):
        text(self.value, 'Node.value')
        text(self.note, 'Node.note')
        if not isinstance(self.selected, bool):
            raise TypeError('Node.selected must be bool')


@dataclass(frozen=True)
class Diagram:
    title: str
    nodes: Sequence[Node] = field(default_factory=list)
    caption: str = ''
    direction: str = 'ltr'
    arrows: bool = True
    kind: str = 'flow'

    def __post_init__(self):
        text(self.title, 'Diagram.title')
        text(self.caption, 'Diagram.caption')
        choice(self.direction, ('rtl', 'ltr'), 'Diagram.direction')
        if isinstance(self.nodes, (str, bytes)) or not isinstance(self.nodes, Sequence):
            raise ValueError('Diagram.nodes requires at least one Node')
        nodes = [coerce(n, Node) if isinstance(n, Mapping) else n for n in self.nodes]
        if not nodes or not all(isinstance(n, Node) for n in nodes):
            raise ValueError('Diagram.nodes requires at least one Node')
        _set(self, 'nodes', nodes)
        if not isinstance(self.arrows, bool):
            raise TypeError('Diagram.arrows must be bool')
        if not isinstance(self.kind, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', self.kind):
            raise ValueError('Diagram.kind must be a lowercase CSS identifier')


def coerce_diagram(value):
    if value is None or isinstance(value, Diagram):
        return value
    if isinstance(value, str):
        from .presets import preset_diagram
        return preset_diagram(value)
    return coerce(value, Diagram)


@dataclass(frozen=True)
class Activity:
    question: str
    answer: Content
    code: str = ''
    language: str | None = None
    label: str | None = None
    reveal: str | None = None

    def __post_init__(self):
        for name in ('question', 'code'):
            text(getattr(self, name), f'Activity.{name}')
        _set(self, 'answer', content(self.answer, 'Activity.answer'))
        for name in ('language', 'label', 'reveal'):
            optional_text(getattr(self, name), f'Activity.{name}')


@dataclass(frozen=True)
class CoverSection:
    title: str
    description: str = ''

    def __post_init__(self):
        text(self.title, 'CoverSection.title')
        text(self.description, 'CoverSection.description')


# --------------------------------------------------------------------------
# Components: everything a deck can contain. ``kind`` is the JSON "type".


def _is_default(item, value):
    if item.default is not MISSING:
        return value == item.default
    if item.default_factory is not MISSING:
        return not value
    return False


def _plain(value):
    if isinstance(value, RichText):
        return {'html': value.html}
    if hasattr(value, '__dataclass_fields__'):
        return {f.name: _plain(getattr(value, f.name)) for f in fields(value)
                if not _is_default(f, getattr(value, f.name))}
    if isinstance(value, Mapping):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


@dataclass(frozen=True)
class Component:
    """Base class for deck components; register new ones in ``components``."""
    kind: ClassVar[str] = ''
    numbered: ClassVar[bool] = False

    def to_dict(self) -> dict[str, Any]:
        """A JSON-ready dictionary that ``LectureDeck.render`` accepts again."""
        data = _plain(self)
        return {'type': self.kind, **data}


def _notes(obj):
    text(obj.notes, f'{type(obj).__name__}.notes')


@dataclass(frozen=True)
class Cover(Component):
    kind: ClassVar[str] = 'cover'
    title: str
    description: Content = ''
    kicker: str = ''
    tags: Sequence[str] = ()
    sections: Sequence[CoverSection] = ()
    hero_code: str = ''
    hero_result: str = ''
    hero_label: str | None = None
    footer_label: str | None = None
    notes: str = ''

    def __post_init__(self):
        text(self.title, 'title')
        _set(self, 'description', content(self.description, 'description'))
        for name in ('kicker', 'hero_code', 'hero_result'):
            text(getattr(self, name), name)
        for name in ('hero_label', 'footer_label'):
            optional_text(getattr(self, name), name)
        _set(self, 'tags', strings(self.tags, 'tags'))
        _set(self, 'sections', tuple(coerce(s, CoverSection) for s in self.sections))
        _notes(self)


@dataclass(frozen=True)
class Slide(Component):
    kind: ClassVar[str] = 'slide'
    numbered: ClassVar[bool] = True
    title: str
    description: Content = ''
    cards: Sequence[Card] = ()
    subtitle: str = ''
    diagram: Diagram | None = None
    activity: Activity | None = None
    notes: str = ''

    def __post_init__(self):
        text(self.title, 'title')
        text(self.subtitle, 'subtitle')
        _set(self, 'description', content(self.description, 'description'))
        _set(self, 'cards', tuple(coerce(c, Card) for c in self.cards))
        _set(self, 'diagram', coerce_diagram(self.diagram))
        if self.activity is not None:
            _set(self, 'activity', coerce(self.activity, Activity))
        _notes(self)


@dataclass(frozen=True)
class Note(Component):
    kind: ClassVar[str] = 'note'
    title: str
    body: Content = ''
    notes: str = ''

    def __post_init__(self):
        text(self.title, 'title')
        _set(self, 'body', content(self.body, 'body'))
        _notes(self)


@dataclass(frozen=True)
class Table(Component):
    kind: ClassVar[str] = 'table'
    title: str
    headers: Sequence[Any]
    rows: Sequence[Sequence[Any]]
    notes: str = ''

    def __post_init__(self):
        text(self.title, 'title')
        columns = tuple(self.headers)
        if not columns:
            raise ValueError('Table needs at least one header')
        values = tuple(tuple(row) for row in self.rows)
        if any(len(row) != len(columns) for row in values):
            raise ValueError('Each table row must match the number of headers')
        _set(self, 'headers', columns)
        _set(self, 'rows', values)
        _notes(self)


CALLOUT_STYLES = ('info', 'tip', 'warning', 'mistake', 'success', 'key')


@dataclass(frozen=True)
class Callout(Component):
    """A highlighted remark: tip, warning, common mistake, key idea..."""
    kind: ClassVar[str] = 'callout'
    body: Content
    title: str | None = None
    style: str = 'info'
    notes: str = ''

    def __post_init__(self):
        _set(self, 'body', content(self.body, 'body'))
        optional_text(self.title, 'title')
        choice(self.style, CALLOUT_STYLES, 'style')
        _notes(self)


@dataclass(frozen=True)
class Compare(Component):
    """Two code versions side by side: wrong/right or before/after."""
    kind: ClassVar[str] = 'compare'
    title: str
    before: str
    after: str
    mode: str = 'wrong-right'
    before_label: str | None = None
    after_label: str | None = None
    before_note: Content = ''
    after_note: Content = ''
    description: Content = ''
    language: str | None = None
    notes: str = ''

    def __post_init__(self):
        for name in ('title', 'before', 'after'):
            text(getattr(self, name), name)
        choice(self.mode, ('wrong-right', 'before-after'), 'mode')
        for name in ('before_label', 'after_label', 'language'):
            optional_text(getattr(self, name), name)
        for name in ('before_note', 'after_note', 'description'):
            _set(self, name, content(getattr(self, name), name))
        _notes(self)


def _lines(values, name):
    result = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f'{name} must contain line numbers starting at 1')
        result.append(value)
    return tuple(sorted(set(result)))


@dataclass(frozen=True)
class CodeExample(Component):
    """Code with an optional result panel, highlighted lines and line numbers."""
    kind: ClassVar[str] = 'code'
    code: str
    title: str = ''
    output: str = ''
    language: str | None = None
    highlight: Sequence[int] = ()
    line_numbers: bool = False
    description: Content = ''
    caption: str = ''
    notes: str = ''

    def __post_init__(self):
        for name in ('code', 'title', 'output', 'caption'):
            text(getattr(self, name), name)
        if not self.code:
            raise ValueError('code must not be empty')
        optional_text(self.language, 'language')
        _set(self, 'highlight', _lines(self.highlight, 'highlight'))
        flag(self.line_numbers, 'line_numbers')
        _set(self, 'description', content(self.description, 'description'))
        _notes(self)


@dataclass(frozen=True)
class Quiz(Component):
    """Multiple choice. ``answer`` is the option index (from 0) or its text.

    Works without JavaScript: choosing an option marks it right or wrong.
    """
    kind: ClassVar[str] = 'quiz'
    question: str
    options: Sequence[str]
    answer: int | str
    explanation: Content = ''
    code: str = ''
    language: str | None = None
    title: str | None = None
    notes: str = ''

    def __post_init__(self):
        text(self.question, 'question')
        _set(self, 'options', strings(self.options, 'options'))
        if not 2 <= len(self.options) <= 8:
            raise ValueError('A quiz needs between 2 and 8 options')
        if isinstance(self.answer, str):
            if self.answer not in self.options:
                raise ValueError('answer must be one of the options')
            _set(self, 'answer', self.options.index(self.answer))
        elif isinstance(self.answer, bool) or not isinstance(self.answer, int) or not 0 <= self.answer < len(self.options):
            raise ValueError('answer must be an option index starting at 0')
        _set(self, 'explanation', content(self.explanation, 'explanation'))
        text(self.code, 'code')
        optional_text(self.language, 'language')
        optional_text(self.title, 'title')
        _notes(self)


@dataclass(frozen=True)
class TraceStep:
    line: int
    variables: Mapping[str, Any] = field(default_factory=dict)
    output: str = ''
    note: str = ''

    def __post_init__(self):
        if isinstance(self.line, bool) or not isinstance(self.line, int) or self.line < 1:
            raise ValueError('TraceStep.line must be a line number starting at 1')
        if not isinstance(self.variables, Mapping) or not all(isinstance(k, str) for k in self.variables):
            raise TypeError('TraceStep.variables must map names to values')
        _set(self, 'variables', {k: v if isinstance(v, str) else repr(v) for k, v in self.variables.items()})
        text(self.output, 'TraceStep.output')
        text(self.note, 'TraceStep.note')


@dataclass(frozen=True)
class Trace(Component):
    """Step through code line by line, showing variables and output."""
    kind: ClassVar[str] = 'trace'
    code: str
    steps: Sequence[TraceStep]
    title: str = ''
    language: str | None = None
    description: Content = ''
    notes: str = ''

    def __post_init__(self):
        text(self.code, 'code')
        text(self.title, 'title')
        optional_text(self.language, 'language')
        steps = tuple(coerce(s, TraceStep) for s in self.steps)
        if not steps:
            raise ValueError('A trace needs at least one step')
        if len(steps) > 60:
            raise ValueError('A trace supports at most 60 steps; split long programs')
        count = len(self.code.splitlines())
        if any(step.line > count for step in steps):
            raise ValueError(f'Trace steps must refer to lines 1-{count}')
        _set(self, 'steps', steps)
        _set(self, 'description', content(self.description, 'description'))
        _notes(self)


@dataclass(frozen=True)
class Exercise(Component):
    kind: ClassVar[str] = 'exercise'
    title: str
    task: Content
    starter: str = ''
    hints: Sequence[str] = ()
    solution: str = ''
    explanation: Content = ''
    language: str | None = None
    notes: str = ''

    def __post_init__(self):
        for name in ('title', 'starter', 'solution'):
            text(getattr(self, name), name)
        _set(self, 'task', content(self.task, 'task'))
        _set(self, 'hints', strings(self.hints, 'hints'))
        _set(self, 'explanation', content(self.explanation, 'explanation'))
        optional_text(self.language, 'language')
        _notes(self)


@dataclass(frozen=True)
class Agenda(Component):
    """Learning goals at the start of a lecture, or a recap at the end."""
    kind: ClassVar[str] = 'agenda'
    items: Sequence[str]
    title: str | None = None
    mode: str = 'goals'
    notes: str = ''

    def __post_init__(self):
        _set(self, 'items', strings(self.items, 'items'))
        if not self.items:
            raise ValueError('An agenda needs at least one item')
        optional_text(self.title, 'title')
        choice(self.mode, ('goals', 'recap'), 'mode')
        _notes(self)


@dataclass(frozen=True)
class Figure(Component):
    """An image from a local file (embedded at render time) or an https URL."""
    kind: ClassVar[str] = 'figure'
    src: str
    caption: str = ''
    alt: str = ''
    title: str = ''
    width: int | None = None
    notes: str = ''

    def __post_init__(self):
        for name in ('src', 'caption', 'alt', 'title'):
            text(getattr(self, name), name)
        width = self.width
        if width is not None and (isinstance(width, bool) or not isinstance(width, int) or not 40 <= width <= 2400):
            raise ValueError('width must be an integer between 40 and 2400 pixels')
        _notes(self)


@dataclass(frozen=True)
class Divider(Component):
    """A section break between parts of a long lecture."""
    kind: ClassVar[str] = 'divider'
    title: str
    subtitle: str = ''
    label: str | None = None
    notes: str = ''

    def __post_init__(self):
        text(self.title, 'title')
        text(self.subtitle, 'subtitle')
        optional_text(self.label, 'label')
        _notes(self)
