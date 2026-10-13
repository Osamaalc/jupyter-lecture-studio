"""Subject visuals: formulas, arrays, matrices, charts, neural networks,
trees, graphs, memory diagrams and database schemas.

Each visual is a validated component model like those in ``models``; its
renderer (``components.visuals``) draws plain HTML or inline SVG laid out in
Python, so the result is deterministic, needs no JavaScript and survives HTML,
notebook and PDF export unchanged. Colors come from ``--ls-viz-*`` tokens.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
import math
import re
from typing import Any, ClassVar

from .mathml import to_mathml
from .models import Component, Content, _notes, _set, choice, coerce, content, flag, optional_text, strings, text

__all__ = [
    'Equation', 'Array', 'Matrix', 'Series', 'Chart', 'Network', 'TreeNode', 'Tree',
    'GraphNode', 'GraphEdge', 'Graph', 'Frame', 'HeapObject', 'Memory', 'Column', 'SchemaTable', 'Schema',
]


def _common(obj) -> None:
    """Title, description, caption and notes shared by every visual."""
    text(obj.title, 'title')
    _set(obj, 'description', content(obj.description, 'description'))
    text(obj.caption, 'caption')
    _notes(obj)


def _index(value, name: str, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= upper:
        raise ValueError(f'{name} must be an index between 0 and {upper}')
    return value


def _number(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name} must contain finite numbers')
    return value


def _cell(value) -> str:
    """Display text for a data value: strings as written, numbers compactly."""
    if isinstance(value, str):
        return value
    if isinstance(value, float):
        return f'{value:.6g}'
    return str(value)


@dataclass(frozen=True)
class Equation(Component):
    """Display formulas in LaTeX, with an optional legend of their symbols.

    ``legend`` maps a symbol (LaTeX) to its meaning, e.g. ``{r'\\eta': 'learning rate'}``.
    """
    kind: ClassVar[str] = 'math'
    latex: str | Sequence[str]
    title: str = ''
    legend: Mapping[str, str] = field(default_factory=dict)
    description: Content = ''
    caption: str = ''
    notes: str = ''

    def __post_init__(self):
        lines = (self.latex,) if isinstance(self.latex, str) else strings(self.latex, 'latex')
        if not lines or not all(line.strip() for line in lines):
            raise ValueError('latex needs at least one non-empty formula')
        for line in lines:
            to_mathml(line)
        _set(self, 'latex', lines[0] if len(lines) == 1 else lines)
        if not isinstance(self.legend, Mapping):
            raise TypeError('legend must map symbols to meanings')
        for symbol, meaning in self.legend.items():
            text(symbol, 'legend symbol')
            text(meaning, 'legend meaning')
            to_mathml(symbol)
        _set(self, 'legend', dict(self.legend))
        _common(self)

    @property
    def formulas(self) -> tuple[str, ...]:
        return (self.latex,) if isinstance(self.latex, str) else tuple(self.latex)


@dataclass(frozen=True)
class Array(Component):
    """A list or array drawn as cells with indices, pointers and a slice.

    ``pointers`` maps a label to an index (``len(values)`` marks the end);
    ``slice`` is ``[start, stop]`` like Python's ``values[start:stop]``.
    """
    kind: ClassVar[str] = 'array'
    values: Sequence[Any]
    title: str = ''
    name: str = ''
    highlight: Sequence[int] = ()
    pointers: Mapping[str, int] = field(default_factory=dict)
    slice: Sequence[int] | None = None
    negative: bool = False
    description: Content = ''
    caption: str = ''
    notes: str = ''

    def __post_init__(self):
        if isinstance(self.values, (str, bytes, Mapping)) or not isinstance(self.values, Sequence):
            raise TypeError('values must be a list')
        count = len(self.values)
        if not 1 <= count <= 40:
            raise ValueError('An array needs between 1 and 40 values')
        _set(self, 'values', tuple(self.values))
        text(self.name, 'name')
        _set(self, 'highlight', tuple(sorted({_index(i, 'highlight', count - 1) for i in self.highlight})))
        if not isinstance(self.pointers, Mapping):
            raise TypeError('pointers must map labels to indexes')
        for label, position in self.pointers.items():
            text(label, 'pointer label')
            _index(position, f'pointer {label!r}', count)
        _set(self, 'pointers', dict(self.pointers))
        if self.slice is not None:
            bounds = tuple(self.slice)
            if len(bounds) != 2:
                raise ValueError('slice must be [start, stop]')
            start, stop = (_index(b, 'slice', count) for b in bounds)
            if start > stop:
                raise ValueError('slice start must not be after stop')
            _set(self, 'slice', (start, stop))
        flag(self.negative, 'negative')
        _common(self)


@dataclass(frozen=True)
class Matrix(Component):
    """A grid of values: matrices, tables of weights, heatmaps, confusion matrices.

    ``heatmap=True`` shades numeric cells by value; ``highlight`` lists
    ``[row, column]`` cells; ``metrics`` adds labelled figures below the grid.
    """
    kind: ClassVar[str] = 'matrix'
    rows: Sequence[Sequence[Any]]
    title: str = ''
    name: str = ''
    row_labels: Sequence[str] = ()
    col_labels: Sequence[str] = ()
    row_title: str = ''
    col_title: str = ''
    heatmap: bool = False
    highlight: Sequence[Sequence[int]] = ()
    brackets: bool = False
    metrics: Mapping[str, str] = field(default_factory=dict)
    description: Content = ''
    caption: str = ''
    notes: str = ''

    def __post_init__(self):
        if isinstance(self.rows, (str, bytes)) or not isinstance(self.rows, Sequence):
            raise TypeError('rows must be a list of rows')
        grid = tuple(tuple(row) for row in self.rows)
        if not grid or not grid[0]:
            raise ValueError('A matrix needs at least one value')
        width = len(grid[0])
        if any(len(row) != width for row in grid):
            raise ValueError('Every matrix row must have the same length')
        if len(grid) > 24 or width > 24:
            raise ValueError('A matrix supports at most 24 rows and 24 columns')
        _set(self, 'rows', grid)
        for name in ('name', 'row_title', 'col_title'):
            text(getattr(self, name), name)
        for name, size in (('row_labels', len(grid)), ('col_labels', width)):
            labels = strings(getattr(self, name), name)
            if labels and len(labels) != size:
                raise ValueError(f'{name} must have {size} labels')
            _set(self, name, labels)
        flag(self.heatmap, 'heatmap')
        flag(self.brackets, 'brackets')
        if self.heatmap:
            for row in grid:
                for value in row:
                    _number(value, 'A heatmap')
        cells = []
        for cell in self.highlight:
            if isinstance(cell, (str, bytes)) or len(cell) != 2:
                raise ValueError('highlight cells must be [row, column] pairs')
            cells.append((_index(cell[0], 'highlight row', len(grid) - 1), _index(cell[1], 'highlight column', width - 1)))
        _set(self, 'highlight', tuple(cells))
        if not isinstance(self.metrics, Mapping):
            raise TypeError('metrics must map labels to values')
        _set(self, 'metrics', {k: _cell(v) for k, v in self.metrics.items()})
        for label in self.metrics:
            text(label, 'metric label')
        _common(self)


@dataclass(frozen=True)
class Series:
    name: str
    values: Sequence[float]
    x: Sequence[float] = ()

    def __post_init__(self):
        text(self.name, 'Series.name')
        if isinstance(self.values, (str, bytes)) or not isinstance(self.values, Sequence) or not self.values:
            raise ValueError('Series.values must be a non-empty list of numbers')
        _set(self, 'values', tuple(_number(v, 'Series.values') for v in self.values))
        _set(self, 'x', tuple(_number(v, 'Series.x') for v in self.x))
        if self.x and len(self.x) != len(self.values):
            raise ValueError('Series.x must have one value per point')


CHART_MODES = ('line', 'bar', 'scatter')


@dataclass(frozen=True)
class Chart(Component):
    """A line, bar or scatter chart drawn as inline SVG (training curves, results...)."""
    kind: ClassVar[str] = 'chart'
    series: Sequence[Series]
    mode: str = 'line'
    labels: Sequence[str] = ()
    title: str = ''
    x_label: str = ''
    y_label: str = ''
    y_min: float | None = None
    y_max: float | None = None
    description: Content = ''
    caption: str = ''
    notes: str = ''

    def __post_init__(self):
        choice(self.mode, CHART_MODES, 'mode')
        if isinstance(self.series, (str, bytes)) or not isinstance(self.series, Sequence):
            raise TypeError('series must be a list')
        series = tuple(coerce(s, Series) for s in self.series)
        if not 1 <= len(series) <= 6:
            raise ValueError('A chart needs between 1 and 6 series')
        _set(self, 'series', series)
        _set(self, 'labels', strings(self.labels, 'labels'))
        if self.mode == 'scatter':
            if not all(s.x for s in series):
                raise ValueError('Scatter series need x values')
        else:
            size = len(series[0].values)
            if any(len(s.values) != size for s in series):
                raise ValueError('Every series needs the same number of values')
            if self.labels and len(self.labels) != size:
                raise ValueError(f'labels must have {size} entries, one per value')
            if size > 60:
                raise ValueError('Line and bar charts support at most 60 points')
        for name in ('x_label', 'y_label'):
            text(getattr(self, name), name)
        for name in ('y_min', 'y_max'):
            if getattr(self, name) is not None:
                _number(getattr(self, name), name)
        if self.y_min is not None and self.y_max is not None and self.y_min >= self.y_max:
            raise ValueError('y_min must be below y_max')
        _common(self)


@dataclass(frozen=True)
class Network(Component):
    """A feed-forward neural network: neurons per layer, fully connected."""
    kind: ClassVar[str] = 'network'
    layers: Sequence[int]
    labels: Sequence[str] = ()
    title: str = ''
    description: Content = ''
    caption: str = ''
    notes: str = ''

    def __post_init__(self):
        sizes = tuple(self.layers)
        if not 2 <= len(sizes) <= 8:
            raise ValueError('A network needs between 2 and 8 layers')
        for size in sizes:
            if isinstance(size, bool) or not isinstance(size, int) or not 1 <= size <= 4096:
                raise ValueError('Layer sizes must be integers between 1 and 4096')
        _set(self, 'layers', sizes)
        labels = strings(self.labels, 'labels')
        if labels and len(labels) != len(sizes):
            raise ValueError('labels must name every layer')
        _set(self, 'labels', labels)
        _common(self)


@dataclass(frozen=True)
class TreeNode:
    value: str
    children: Sequence[TreeNode | None] = ()
    selected: bool = False
    note: str = ''

    def __post_init__(self):
        if not isinstance(self.value, str):
            _set(self, 'value', _cell(self.value))
        text(self.note, 'TreeNode.note')
        flag(self.selected, 'TreeNode.selected')
        if isinstance(self.children, (str, bytes)) or not isinstance(self.children, Sequence):
            raise TypeError('TreeNode.children must be a list')
        _set(self, 'children', tuple(None if c is None else coerce(c, TreeNode) for c in self.children))


def _tree_size(node: TreeNode | None, depth: int = 1) -> tuple[int, int]:
    if node is None:
        return 0, 0
    counts = [_tree_size(child, depth + 1) for child in node.children]
    return 1 + sum(c for c, _ in counts), max([depth] + [d for _, d in counts])


@dataclass(frozen=True)
class Tree(Component):
    """A rooted tree (search trees, parse trees, decision trees...).

    ``None`` children keep an empty slot, so binary trees keep left and right.
    """
    kind: ClassVar[str] = 'tree'
    root: TreeNode
    title: str = ''
    description: Content = ''
    caption: str = ''
    notes: str = ''

    def __post_init__(self):
        _set(self, 'root', coerce(self.root, TreeNode))
        count, depth = _tree_size(self.root)
        if count > 63 or depth > 7:
            raise ValueError('A tree supports at most 63 nodes and 7 levels')
        _common(self)


@dataclass(frozen=True)
class GraphNode:
    id: str
    label: str = ''
    x: float | None = None
    y: float | None = None
    selected: bool = False

    def __post_init__(self):
        text(self.id, 'GraphNode.id')
        text(self.label, 'GraphNode.label')
        for name in ('x', 'y'):
            value = getattr(self, name)
            if value is not None and not 0 <= _number(value, f'GraphNode.{name}') <= 100:
                raise ValueError('Graph positions use a 0-100 grid')
        flag(self.selected, 'GraphNode.selected')


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    label: str = ''
    selected: bool = False

    def __post_init__(self):
        for name in ('source', 'target', 'label'):
            if name == 'label' and not isinstance(self.label, str):
                _set(self, 'label', _cell(self.label))
            text(getattr(self, name), f'GraphEdge.{name}')
        flag(self.selected, 'GraphEdge.selected')


def _graph_node(value):
    return GraphNode(value) if isinstance(value, str) else coerce(value, GraphNode)


def _graph_edge(value):
    if isinstance(value, (list, tuple)) and 2 <= len(value) <= 3:
        return GraphEdge(*value)
    return coerce(value, GraphEdge)


@dataclass(frozen=True)
class Graph(Component):
    """Nodes and edges (search, shortest paths, networks, state machines).

    Nodes are ids or ``{"id", "label", "x", "y"}`` on a 0-100 grid; without
    positions they are placed on a circle. Edges are ``[source, target]`` or
    ``[source, target, label]``.
    """
    kind: ClassVar[str] = 'graph'
    nodes: Sequence[GraphNode]
    edges: Sequence[GraphEdge] = ()
    directed: bool = False
    title: str = ''
    description: Content = ''
    caption: str = ''
    notes: str = ''

    def __post_init__(self):
        nodes = tuple(_graph_node(n) for n in self.nodes)
        if not 1 <= len(nodes) <= 40:
            raise ValueError('A graph needs between 1 and 40 nodes')
        ids = [n.id for n in nodes]
        if len(set(ids)) != len(ids):
            raise ValueError('Graph node ids must be unique')
        positioned = [n.x is not None and n.y is not None for n in nodes]
        if any(positioned) and not all(positioned):
            raise ValueError('Give x and y to every graph node, or to none')
        edges = tuple(_graph_edge(e) for e in self.edges)
        for edge in edges:
            if edge.source not in ids or edge.target not in ids:
                raise ValueError(f'Edge {edge.source!r} -> {edge.target!r} refers to an unknown node')
        _set(self, 'nodes', nodes)
        _set(self, 'edges', edges)
        flag(self.directed, 'directed')
        _common(self)


@dataclass(frozen=True)
class Frame:
    """A stack frame (or a scope) and its variables. ``"@id"`` points to an object."""
    name: str
    variables: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        text(self.name, 'Frame.name')
        if not isinstance(self.variables, Mapping) or not all(isinstance(k, str) for k in self.variables):
            raise TypeError('Frame.variables must map names to values')
        _set(self, 'variables', dict(self.variables))


@dataclass(frozen=True)
class HeapObject:
    """An object in memory. ``value`` is text, a list (indexed slots) or a dict (fields)."""
    id: str
    value: Any = ''
    type: str = ''

    def __post_init__(self):
        text(self.id, 'HeapObject.id')
        text(self.type, 'HeapObject.type')
        if isinstance(self.value, Mapping):
            _set(self, 'value', dict(self.value))
        elif isinstance(self.value, (list, tuple)):
            _set(self, 'value', tuple(self.value))

    def slots(self) -> list[tuple[str, Any]]:
        if isinstance(self.value, dict):
            return [(str(k), v) for k, v in self.value.items()]
        if isinstance(self.value, tuple):
            return [(str(i), v) for i, v in enumerate(self.value)]
        return [('', self.value)]


def reference(value) -> str | None:
    """The object id when a value is a reference (``"@id"``)."""
    if isinstance(value, str) and re.fullmatch(r'@[\w.-]+', value):
        return value[1:]
    return None


@dataclass(frozen=True)
class Memory(Component):
    """A memory diagram: stack frames with variables and the objects they reference.

    Values written ``"@id"`` draw an arrow to the object with that id, so the
    same component shows Python names and objects, C/C++ pointers, linked
    lists and recursion (the last frame is the active one).
    """
    kind: ClassVar[str] = 'memory'
    frames: Sequence[Frame]
    objects: Sequence[HeapObject] = ()
    title: str = ''
    stack_label: str | None = None
    heap_label: str | None = None
    description: Content = ''
    caption: str = ''
    notes: str = ''

    def __post_init__(self):
        frames = tuple(coerce(f, Frame) for f in self.frames)
        objects = tuple(coerce(o, HeapObject) for o in self.objects)
        if not frames and not objects:
            raise ValueError('A memory diagram needs a frame or an object')
        if len(frames) > 12 or len(objects) > 16:
            raise ValueError('A memory diagram supports at most 12 frames and 16 objects')
        ids = [o.id for o in objects]
        if len(set(ids)) != len(ids):
            raise ValueError('Object ids must be unique')
        values = [v for f in frames for v in f.variables.values()] + [v for o in objects for _, v in o.slots()]
        for value in values:
            target = reference(value)
            if target is not None and target not in ids:
                raise ValueError(f'Reference {value!r} does not match an object id')
        _set(self, 'frames', frames)
        _set(self, 'objects', objects)
        optional_text(self.stack_label, 'stack_label')
        optional_text(self.heap_label, 'heap_label')
        _common(self)


_COLUMN = re.compile(r'(?P<name>[^\s]+)(?P<rest>.*)')


@dataclass(frozen=True)
class Column:
    """A table column. Shorthand: ``"student_id INT FK -> students.id"``."""
    name: str
    type: str = ''
    key: str = ''
    references: str = ''

    def __post_init__(self):
        for name in ('name', 'type', 'key', 'references'):
            text(getattr(self, name), f'Column.{name}')
        keys = set(self.key.lower().replace(',', ' ').split())
        if keys - {'pk', 'fk', 'uq'}:
            raise ValueError('Column.key may contain pk, fk and uq')
        if self.references and not re.fullmatch(r'[^\s.]+\.[^\s.]+', self.references):
            raise ValueError('Column.references must look like "table.column"')
        if self.references:
            keys.add('fk')
        _set(self, 'key', ' '.join(k for k in ('pk', 'fk', 'uq') if k in keys))

    @classmethod
    def parse(cls, value) -> Column:
        if not isinstance(value, str):
            return coerce(value, Column)
        words = value.replace('→', '->').split()
        if not words:
            raise ValueError('Empty column definition')
        name, rest, keys, kinds, ref = words[0], words[1:], [], [], ''
        i = 0
        while i < len(rest):
            word = rest[i]
            if word.upper() in ('PK', 'FK', 'UQ'):
                keys.append(word.lower())
            elif word == '->' and i + 1 < len(rest):
                ref = rest[i + 1]
                i += 1
            else:
                kinds.append(word)
            i += 1
        return cls(name, ' '.join(kinds), ' '.join(keys), ref)


@dataclass(frozen=True)
class SchemaTable:
    name: str
    columns: Sequence[Column]

    def __post_init__(self):
        text(self.name, 'SchemaTable.name')
        columns = tuple(Column.parse(c) for c in self.columns)
        if not 1 <= len(columns) <= 20:
            raise ValueError('A table needs between 1 and 20 columns')
        _set(self, 'columns', columns)


@dataclass(frozen=True)
class Schema(Component):
    """Database tables with keys and the relationships between them."""
    kind: ClassVar[str] = 'schema'
    tables: Sequence[SchemaTable]
    title: str = ''
    per_row: int = 3
    description: Content = ''
    caption: str = ''
    notes: str = ''

    def __post_init__(self):
        tables = tuple(coerce(t, SchemaTable) for t in self.tables)
        if not 1 <= len(tables) <= 12:
            raise ValueError('A schema needs between 1 and 12 tables')
        names = {t.name: {c.name for c in t.columns} for t in tables}
        if len(names) != len(tables):
            raise ValueError('Table names must be unique')
        for table in tables:
            for column in table.columns:
                if column.references:
                    target, _, field_name = column.references.partition('.')
                    if field_name not in names.get(target, ()):
                        raise ValueError(f'{table.name}.{column.name} references unknown column {column.references!r}')
        if isinstance(self.per_row, bool) or not isinstance(self.per_row, int) or not 1 <= self.per_row <= 4:
            raise ValueError('per_row must be between 1 and 4')
        _set(self, 'tables', tables)
        _common(self)
