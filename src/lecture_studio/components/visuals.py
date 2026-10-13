"""Renderers for subject visuals (see ``lecture_studio.visuals``).

Layouts are computed here in Python and emitted as HTML or inline SVG with
token-based classes, so every theme colors them and nothing runs in the
browser. SVG text is escaped like all other author text.
"""
from __future__ import annotations

import html
import math

from ..mathml import to_mathml
from ..visuals import (
    Array,
    Chart,
    Equation,
    Graph,
    Matrix,
    Memory,
    Network,
    Schema,
    Tree,
    TreeNode,
    _cell,
    reference,
)
from . import register_component
from .base import RenderContext
from .teaching import description, panel

__all__ = ['nice_ticks']


def _e(value) -> str:
    return html.escape(str(value))


def _n(value: float) -> str:
    """Compact SVG coordinates."""
    return f'{value:.1f}'.rstrip('0').rstrip('.')


def _clip(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[:limit - 1] + '…'


def _text_width(value: str, size: float = 14, mono: bool = False) -> float:
    return len(value) * size * (0.62 if mono else 0.56)


def _caption(item, ctx: RenderContext) -> str:
    return f'<p class="ls-panel-caption">{ctx.line(item.caption)}</p>' if item.caption else ''


def _visual(name: str, item, ctx: RenderContext, figure: str, *, attrs: str = '') -> str:
    body = description(item.description, ctx) + figure + _caption(item, ctx)
    return panel(f'viz ls-viz-{name}', ctx, body, title=item.title, attrs=attrs, component=item)


def _svg(width: float, height: float, body: str, label: str, defs: str = '') -> str:
    return (f'<svg class="ls-svg" viewBox="0 0 {_n(width)} {_n(height)}" width="{_n(width)}" height="{_n(height)}" '
            f'role="img" aria-label="{_e(label)}" direction="ltr" xmlns="http://www.w3.org/2000/svg">'
            f'{"<defs>" + defs + "</defs>" if defs else ""}{body}</svg>')


def _arrow_marker(uid: str, cls: str = 'ls-arrowhead') -> str:
    # User-space units keep arrowheads the same size on thick (selected) edges.
    return (f'<marker id="{uid}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="11" markerHeight="11" '
            f'markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path class="{cls}" d="M0 0L10 5L0 10z"/></marker>')


# -- formulas ---------------------------------------------------------------

def render_equation(item: Equation, ctx: RenderContext) -> str:
    formulas = ''.join(f'<div class="ls-equation">{to_mathml(line)}</div>' for line in item.formulas)
    legend = ''
    if item.legend:
        rows = ''.join(f'<div><dt>{to_mathml(symbol, display=False)}</dt><dd>{ctx.line(meaning)}</dd></div>'
                       for symbol, meaning in item.legend.items())
        legend = f'<dl class="ls-legend"><span class="ls-legend-title">{ctx.label("math.where")}</span>{rows}</dl>'
    return _visual('math', item, ctx, f'<div class="ls-equations">{formulas}</div>{legend}')


# -- arrays and matrices ------------------------------------------------------

def render_array(item: Array, ctx: RenderContext) -> str:
    count = len(item.values)
    end_pointer = any(position == count for position in item.pointers.values())
    columns = count + (1 if end_pointer else 0)
    start, stop = item.slice if item.slice is not None else (None, None)
    cells = []
    for i in range(columns):
        ghost = i == count
        marks = [label for label, position in item.pointers.items() if position == i]
        state = ' is-marked' if i in item.highlight else ''
        if start is not None and stop is not None and start <= i < stop:
            state += ' in-slice'
        state += ' is-first' if i == 0 else ''
        state += ' is-last' if i == count - 1 else ''
        pointers = ''.join(f'<b>{_e(label)}</b>' for label in marks)
        value = '' if ghost else _e(_cell(item.values[i]))
        negative = f'<span class="ls-array-neg">{i - count}</span>' if item.negative and not ghost else ''
        cells.append(f'<div class="ls-array-cell{" is-ghost" if ghost else ""}{state}" style="grid-column:{i + 1}">'
                     f'<span class="ls-array-index">{i}</span><span class="ls-array-value">{value}</span>{negative}'
                     + (f'<span class="ls-array-pointers">{pointers}</span>' if pointers else '') + '</div>')
    bracket = ''
    if start is not None and stop is not None:
        label = f'{item.name}[{start}:{stop}]' if item.name else f'[{start}:{stop}]'
        span = f'{start + 1} / {max(stop, start + 1) + 1}'
        bracket = f'<div class="ls-array-slice" style="grid-column:{span}"><span>{_e(label)}</span></div>'
    name = f'<span class="ls-array-name">{_e(item.name)} =</span>' if item.name else ''
    figure = (f'<div class="ls-array" dir="ltr">{name}<div class="ls-array-track" style="--ls-count:{columns}">'
              f'{"".join(cells)}{bracket}</div></div>')
    return _visual('array', item, ctx, figure)


def render_matrix(item: Matrix, ctx: RenderContext) -> str:
    rows, width = item.rows, len(item.rows[0])
    low = high = 0.0
    if item.heatmap:
        values = [float(v) for row in rows for v in row]
        low, high = min(values), max(values)
    marked = set(item.highlight)
    head = ''
    corner = int(bool(item.row_title)) + int(bool(item.row_labels))
    if item.col_title:
        head += (f'<tr>{"<th></th>" * corner}<th class="ls-matrix-axis" colspan="{width}">{ctx.line(item.col_title)}</th>'
                 '</tr>')
    if item.col_labels:
        head += '<tr>' + '<th></th>' * corner + ''.join(f'<th scope="col">{ctx.line(c)}</th>' for c in item.col_labels) + '</tr>'
    body = []
    for r, row in enumerate(rows):
        cells = []
        if item.row_title and r == 0:
            cells.append(f'<th class="ls-matrix-axis ls-matrix-axis-row" rowspan="{len(rows)}"><span>'
                         f'{ctx.line(item.row_title)}</span></th>')
        if item.row_labels:
            cells.append(f'<th scope="row">{ctx.line(item.row_labels[r])}</th>')
        for c, value in enumerate(row):
            classes, style = [], ''
            if item.heatmap:
                heat = 0.0 if high == low else (float(value) - low) / (high - low)
                style = f' style="--ls-heat:{heat:.3f}"'
                classes.append('is-heat')
                if heat > .55:
                    classes.append('is-hot')
            if (r, c) in marked:
                classes.append('is-marked')
            cls = f' class="{" ".join(classes)}"' if classes else ''
            cells.append(f'<td{cls}{style}>{_e(_cell(value))}</td>')
        body.append('<tr>' + ''.join(cells) + '</tr>')
    table = (f'<table class="ls-matrix{" ls-brackets" if item.brackets else ""}">'
             + (f'<thead>{head}</thead>' if head else '') + f'<tbody>{"".join(body)}</tbody></table>')
    name = f'<span class="ls-matrix-name">{_e(item.name)} =</span>' if item.name else ''
    metrics = ''.join(f'<span><b>{ctx.line(label)}</b> <bdi dir="ltr">{_e(value)}</bdi></span>'
                      for label, value in item.metrics.items())
    figure = (f'<div class="ls-matrix-wrap" dir="ltr">{name}<div class="ls-matrix-scroll">{table}</div></div>'
              + (f'<div class="ls-metrics">{metrics}</div>' if metrics else ''))
    return _visual('matrix', item, ctx, figure)


# -- charts ----------------------------------------------------------------------

def nice_ticks(low: float, high: float, count: int = 5) -> list[float]:
    """Round axis ticks covering ``low``..``high`` (1, 2, 2.5 or 5 times a power of ten)."""
    if high == low:
        high, low = high + 1, low - 1 if low else 0
    raw = (high - low) / max(count - 1, 1)
    magnitude = 10 ** math.floor(math.log10(raw))
    step = next(m * magnitude for m in (1, 2, 2.5, 5, 10) if m * magnitude >= raw)
    start = math.floor(low / step) * step
    ticks, value = list[float](), start
    while value < high + step * 0.5 and len(ticks) < 12:
        ticks.append(round(value, 10))
        value += step
    if ticks[-1] < high:
        ticks.append(round(value, 10))
    return ticks


def _tick(value: float) -> str:
    return f'{value:g}' if abs(value) < 1e6 else f'{value:.2g}'


def render_chart(item: Chart, ctx: RenderContext) -> str:
    width, height = 720.0, 380.0
    left, right, top = 64.0, 20.0, 18.0
    bottom = 46.0 + (24 if item.x_label else 0)
    plot_w, plot_h = width - left - right, height - top - bottom
    values = [v for s in item.series for v in s.values]
    low = min(values) if item.y_min is None else item.y_min
    high = max(values) if item.y_max is None else item.y_max
    if item.mode == 'bar':
        low, high = min(low, 0.0), max(high, 0.0)
    ticks = nice_ticks(low, high)
    y_low = ticks[0] if item.y_min is None else item.y_min
    y_high = ticks[-1] if item.y_max is None else item.y_max
    ticks = [t for t in ticks if y_low - 1e-9 <= t <= y_high + 1e-9]

    def y(value: float) -> float:
        return top + plot_h - (value - y_low) / (y_high - y_low) * plot_h

    parts = []
    for t in ticks:
        parts.append(f'<line class="ls-grid" x1="{_n(left)}" x2="{_n(left + plot_w)}" y1="{_n(y(t))}" y2="{_n(y(t))}"/>'
                     f'<text class="ls-tick" x="{_n(left - 10)}" y="{_n(y(t) + 4)}" text-anchor="end">{_tick(t)}</text>')
    parts.append(f'<line class="ls-axis" x1="{_n(left)}" x2="{_n(left + plot_w)}" y1="{_n(top + plot_h)}" '
                 f'y2="{_n(top + plot_h)}"/><line class="ls-axis" x1="{_n(left)}" x2="{_n(left)}" y1="{_n(top)}" '
                 f'y2="{_n(top + plot_h)}"/>')
    base_y = top + plot_h + 20
    if item.mode == 'scatter':
        xs = [v for s in item.series for v in s.x]
        x_ticks = nice_ticks(min(xs), max(xs))
        x_low, x_high = x_ticks[0], x_ticks[-1]

        def x(value: float) -> float:
            return left + (value - x_low) / (x_high - x_low) * plot_w
        for t in x_ticks:
            parts.append(f'<line class="ls-grid" x1="{_n(x(t))}" x2="{_n(x(t))}" y1="{_n(top)}" y2="{_n(top + plot_h)}"/>'
                         f'<text class="ls-tick" x="{_n(x(t))}" y="{_n(base_y)}" text-anchor="middle">{_tick(t)}</text>')
        for i, series in enumerate(item.series, 1):
            dots = ''.join(f'<circle class="ls-point" cx="{_n(x(a))}" cy="{_n(y(b))}" r="5"/>'
                           for a, b in zip(series.x, series.values, strict=True))
            parts.append(f'<g class="ls-series" style="--ls-c:var(--ls-viz-{i})">{dots}</g>')
    else:
        size = len(item.series[0].values)
        labels = item.labels or [str(i + 1) for i in range(size)]
        band = plot_w / size
        if item.mode == 'bar':
            def x(value: float) -> float:
                return left + band * (value + 0.5)
        else:
            def x(value: float) -> float:
                return left + (plot_w / 2 if size == 1 else plot_w * value / (size - 1))
        step = max(1, math.ceil(size / 12))
        for i, label in enumerate(labels):
            if i % step == 0 or i == size - 1:
                parts.append(f'<text class="ls-tick" x="{_n(x(i))}" y="{_n(base_y)}" text-anchor="middle">'
                             f'{_e(_clip(label, 14))}</text>')
        for s, series in enumerate(item.series, 1):
            style = f' style="--ls-c:var(--ls-viz-{s})"'
            if item.mode == 'bar':
                group = band * 0.72
                bar = group / len(item.series)
                zero = y(max(min(0.0, y_high), y_low))
                rects = ''.join(
                    f'<rect class="ls-bar" x="{_n(left + band * i + (band - group) / 2 + bar * (s - 1))}" '
                    f'y="{_n(min(y(v), zero))}" width="{_n(bar - 2)}" height="{_n(abs(zero - y(v)))}" rx="3"/>'
                    for i, v in enumerate(series.values))
                parts.append(f'<g class="ls-series"{style}>{rects}</g>')
            else:
                points = ' '.join(f'{_n(x(i))},{_n(y(v))}' for i, v in enumerate(series.values))
                dots = ''.join(f'<circle class="ls-point" cx="{_n(x(i))}" cy="{_n(y(v))}" r="3.5"/>'
                               for i, v in enumerate(series.values)) if size <= 30 else ''
                parts.append(f'<g class="ls-series"{style}><polyline class="ls-line-path" points="{points}"/>{dots}</g>')
    if item.x_label:
        parts.append(f'<text class="ls-axis-label" x="{_n(left + plot_w / 2)}" y="{_n(height - 8)}" '
                     f'text-anchor="middle">{_e(item.x_label)}</text>')
    if item.y_label:
        parts.append(f'<text class="ls-axis-label" transform="translate(16 {_n(top + plot_h / 2)}) rotate(-90)" '
                     f'text-anchor="middle">{_e(item.y_label)}</text>')
    legend = ''
    if len(item.series) > 1 or item.series[0].name:
        entries = ''.join(f'<li style="--ls-c:var(--ls-viz-{i})"><i></i>{ctx.line(s.name)}</li>'
                          for i, s in enumerate(item.series, 1))
        legend = f'<ul class="ls-chart-legend">{entries}</ul>'
    svg = _svg(width, height, ''.join(parts), item.title or item.y_label or 'chart')
    return _visual('chart', item, ctx, f'<div class="ls-figure-svg">{svg}</div>{legend}', attrs=f' data-mode="{item.mode}"')


# -- neural networks --------------------------------------------------------------

def _shown(size: int) -> list[int | None]:
    """Neuron indexes drawn for a layer; ``None`` is the ellipsis."""
    return list(range(size)) if size <= 7 else [0, 1, 2, None, size - 3, size - 2, size - 1]


def render_network(item: Network, ctx: RenderContext) -> str:
    layers = [_shown(size) for size in item.layers]
    gap, radius = 58.0, 17.0
    tallest = max(len(layer) for layer in layers)
    width = max(560.0, 150.0 * len(layers))
    height = 30 + tallest * gap + 52
    column = (width - 120) / (len(layers) - 1)
    def center(layer: int, slot: int) -> tuple[float, float]:
        top = 30 + (tallest - len(layers[layer])) * gap / 2 + gap / 2
        return 60 + column * layer, top + slot * gap

    edges, nodes, labels = [], [], []
    for layer in range(len(layers) - 1):
        for i, a in enumerate(layers[layer]):
            for j, b in enumerate(layers[layer + 1]):
                if a is not None and b is not None:
                    (x1, y1), (x2, y2) = center(layer, i), center(layer + 1, j)
                    edges.append(f'<line x1="{_n(x1 + radius)}" y1="{_n(y1)}" x2="{_n(x2 - radius)}" y2="{_n(y2)}"/>')
    names = item.labels or [ctx.locale['network.input']] + [ctx.locale['network.hidden']] * (len(layers) - 2) + [
        ctx.locale['network.output']]
    for layer, neurons in enumerate(layers):
        role = 'input' if layer == 0 else 'output' if layer == len(layers) - 1 else 'hidden'
        for slot, neuron in enumerate(neurons):
            x, y = center(layer, slot)
            if neuron is None:
                nodes.append(f'<text class="ls-ellipsis" x="{_n(x)}" y="{_n(y + 6)}" text-anchor="middle">⋮</text>')
            else:
                nodes.append(f'<circle class="ls-neuron" data-role="{role}" cx="{_n(x)}" cy="{_n(y)}" r="{_n(radius)}"/>')
        x = 60 + column * layer
        labels.append(f'<text class="ls-layer-label" x="{_n(x)}" y="{_n(height - 30)}" text-anchor="middle">'
                      f'{_e(names[layer])}</text><text class="ls-tick" x="{_n(x)}" y="{_n(height - 11)}" '
                      f'text-anchor="middle">{item.layers[layer]}</text>')
    body = f'<g class="ls-synapses">{"".join(edges)}</g>{"".join(nodes)}{"".join(labels)}'
    svg = _svg(width, height, body, item.title or 'neural network')
    return _visual('network', item, ctx, f'<div class="ls-figure-svg">{svg}</div>')


# -- trees and graphs ----------------------------------------------------------------

def _node_box(x: float, y: float, value: str, *, selected: bool, note: str = '', shape: str = 'auto') -> str:
    label = _clip(value, 16)
    w = max(44.0, _text_width(label, 15, mono=True) + 22)
    state = ' is-selected' if selected else ''
    if shape == 'circle' or (shape == 'auto' and w <= 44):
        box = f'<circle class="ls-box{state}" cx="{_n(x)}" cy="{_n(y)}" r="22"/>'
    else:
        box = f'<rect class="ls-box{state}" x="{_n(x - w / 2)}" y="{_n(y - 20)}" width="{_n(w)}" height="40" rx="12"/>'
    extra = (f'<text class="ls-node-note" x="{_n(x)}" y="{_n(y + 38)}" text-anchor="middle">{_e(_clip(note, 22))}</text>'
             if note else '')
    return (f'{box}<text class="ls-label ls-mono{state}" x="{_n(x)}" y="{_n(y + 5)}" text-anchor="middle">'
            f'{_e(label)}</text>{extra}')


def render_tree(item: Tree, ctx: RenderContext) -> str:
    slot, level = 70.0, 86.0
    placed: list[tuple[float, float, TreeNode]] = []
    links: list[tuple[float, float, float, float]] = []
    counter = [0]
    deepest = [0]

    def place(node: TreeNode | None, depth: int) -> float:
        deepest[0] = max(deepest[0], depth)
        if node is None:
            counter[0] += 1
            return (counter[0] - 0.5) * slot
        if not node.children:
            counter[0] += 1
            x = (counter[0] - 0.5) * slot
        else:
            xs = [(place(child, depth + 1), child) for child in node.children]
            real = [cx for cx, child in xs if child is not None]
            x = sum(real) / len(real) if real else sum(cx for cx, _ in xs) / len(xs)
            for cx, child in xs:
                if child is not None:
                    links.append((x, depth, cx, depth + 1))
        placed.append((x, depth, node))
        return x
    place(item.root, 0)
    notes = any(node.note for _, _, node in placed)
    width = max(counter[0] * slot, 120.0) + 20
    height = (deepest[0] + 1) * level + (24 if notes else 0)

    def py(depth: float) -> float:
        return 36 + depth * level
    edges = ''.join(f'<line class="ls-edge" x1="{_n(a + 10)}" y1="{_n(py(b) + 22)}" x2="{_n(c + 10)}" y2="{_n(py(d) - 22)}"/>'
                    for a, b, c, d in links)
    nodes = ''.join(_node_box(x + 10, py(depth), node.value, selected=node.selected, note=node.note)
                    for x, depth, node in placed)
    svg = _svg(width, height, edges + nodes, item.title or 'tree')
    return _visual('tree', item, ctx, f'<div class="ls-figure-svg">{svg}</div>')


def render_graph(item: Graph, ctx: RenderContext) -> str:
    width, height, pad = 720.0, 420.0, 50.0
    if item.nodes[0].x is not None:
        pos = {n.id: (pad + (width - 2 * pad) * (n.x or 0) / 100, pad + (height - 2 * pad) * (n.y or 0) / 100)
               for n in item.nodes}
    else:
        count = len(item.nodes)
        radius = min(width, height) / 2 - pad
        pos = {n.id: (width / 2 + (radius * math.cos(-math.pi / 2 + 2 * math.pi * i / count) if count > 1 else 0),
                      height / 2 + (radius * math.sin(-math.pi / 2 + 2 * math.pi * i / count) if count > 1 else 0))
               for i, n in enumerate(item.nodes)}
    sizes = {n.id: max(24.0, (_text_width(_clip(n.label or n.id, 14), 15, mono=True) + 20) / 2) for n in item.nodes}
    pairs = {(e.source, e.target) for e in item.edges}
    edges, labels = [], []
    marker = f' marker-end="url(#{ctx.uid}-arrow)"' if item.directed else ''
    for edge in item.edges:
        (x1, y1), (x2, y2) = pos[edge.source], pos[edge.target]
        state = ' is-selected' if edge.selected else ''
        if edge.source == edge.target:
            r = sizes[edge.source]
            edges.append(f'<path class="ls-edge{state}" d="M{_n(x1 - 10)} {_n(y1 - r)} C{_n(x1 - 40)} {_n(y1 - r - 50)} '
                         f'{_n(x1 + 40)} {_n(y1 - r - 50)} {_n(x1 + 10)} {_n(y1 - r)}"{marker}/>')
            lx, ly = x1, y1 - r - 44
        else:
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy) or 1
            ux, uy = dx / length, dy / length
            bend = 26.0 if item.directed and (edge.target, edge.source) in pairs else 0.0
            sx, sy = x1 + ux * sizes[edge.source], y1 + uy * sizes[edge.source]
            reach = sizes[edge.target] + (3 if item.directed else 0)  # leave room for the arrowhead
            tx, ty = x2 - ux * reach, y2 - uy * reach
            mx, my = (sx + tx) / 2 - uy * bend, (sy + ty) / 2 + ux * bend
            if bend:
                edges.append(f'<path class="ls-edge{state}" d="M{_n(sx)} {_n(sy)} Q{_n(mx - uy * bend)} {_n(my + ux * bend)} '
                             f'{_n(tx)} {_n(ty)}"{marker}/>')
            else:
                edges.append(f'<line class="ls-edge{state}" x1="{_n(sx)}" y1="{_n(sy)}" x2="{_n(tx)}" y2="{_n(ty)}"{marker}/>')
            lx, ly = mx, my
        if edge.label:
            labels.append(f'<text class="ls-edge-label{state}" x="{_n(lx)}" y="{_n(ly + 4)}" text-anchor="middle">'
                          f'{_e(_clip(edge.label, 12))}</text>')
    nodes = ''.join(_node_box(*pos[n.id], n.label or n.id, selected=n.selected) for n in item.nodes)
    defs = _arrow_marker(ctx.uid) if item.directed else ''
    svg = _svg(width, height, ''.join(edges) + ''.join(labels) + nodes, item.title or 'graph', defs)
    return _visual('graph', item, ctx, f'<div class="ls-figure-svg">{svg}</div>')


# -- memory diagrams ---------------------------------------------------------------------

def _value_text(value) -> str:
    if isinstance(value, str):
        return value
    return repr(value) if isinstance(value, (list, tuple, dict, set)) else _cell(value)


def render_memory(item: Memory, ctx: RenderContext) -> str:
    box_w, row_h, head_h, gap = 300.0, 30.0, 34.0, 18.0
    has_frames, has_objects = bool(item.frames), bool(item.objects)
    frame_x = 20.0
    heap_x = frame_x + box_w + 140 if has_frames else 20.0
    width = (heap_x + box_w + 70) if has_objects else frame_x + box_w + 20
    parts, arrows = [], []
    anchors: dict[str, float] = {}
    y_obj = 40.0
    object_boxes = []
    for obj in item.objects:
        slots = obj.slots()
        height = head_h + row_h * len(slots)
        anchors[obj.id] = y_obj + head_h / 2
        object_boxes.append((obj, y_obj, slots))
        y_obj += height + gap
    y = 40.0
    titles = []
    if has_frames:
        titles.append(f'<text class="ls-column-title" x="{_n(frame_x)}" y="22">'
                      f'{_e(item.stack_label if item.stack_label is not None else ctx.locale["memory.stack"])}</text>')
    if has_objects:
        titles.append(f'<text class="ls-column-title" x="{_n(heap_x)}" y="22">'
                      f'{_e(item.heap_label if item.heap_label is not None else ctx.locale["memory.heap"])}</text>')

    def slot_rows(x: float, top: float, rows, source: str) -> str:
        out = []
        for r, (name, value) in enumerate(rows):
            ry = top + head_h + r * row_h
            out.append(f'<line class="ls-sep" x1="{_n(x)}" x2="{_n(x + box_w)}" y1="{_n(ry)}" y2="{_n(ry)}"/>')
            target = reference(value)
            if name:
                out.append(f'<text class="ls-slot-name ls-mono" x="{_n(x + 14)}" y="{_n(ry + 20)}">{_e(_clip(name, 14))}</text>')
            if target is not None:
                cx = x + box_w - 22
                out.append(f'<circle class="ls-ref-dot" cx="{_n(cx)}" cy="{_n(ry + row_h / 2)}" r="4.5"/>')
                ty = anchors[target]
                if source == 'frame':
                    x2 = heap_x
                    arrows.append(f'M{_n(cx)} {_n(ry + row_h / 2)} C{_n(cx + 90)} {_n(ry + row_h / 2)} '
                                  f'{_n(x2 - 70)} {_n(ty)} {_n(x2 - 2)} {_n(ty)}')
                else:
                    x2 = heap_x + box_w
                    arrows.append(f'M{_n(cx)} {_n(ry + row_h / 2)} C{_n(x2 + 60)} {_n(ry + row_h / 2)} '
                                  f'{_n(x2 + 60)} {_n(ty)} {_n(x2 + 2)} {_n(ty)}')
            else:
                anchor_x = x + box_w - 14 if name else x + 14
                anchor = 'end' if name else 'start'
                out.append(f'<text class="ls-slot-value ls-mono" x="{_n(anchor_x)}" y="{_n(ry + 20)}" text-anchor="{anchor}">'
                           f'{_e(_clip(_value_text(value), 24 if name else 34))}</text>')
        return ''.join(out)

    for index, frame in enumerate(item.frames):
        rows = list(frame.variables.items())
        height = head_h + row_h * max(len(rows), 0)
        active = ' is-active' if index == len(item.frames) - 1 else ''
        parts.append(f'<g class="ls-frame-box{active}"><rect class="ls-box" x="{_n(frame_x)}" y="{_n(y)}" width="{_n(box_w)}" '
                     f'height="{_n(height)}" rx="10"/><text class="ls-box-title" x="{_n(frame_x + 14)}" y="{_n(y + 22)}">'
                     f'{_e(_clip(frame.name, 30))}</text>{slot_rows(frame_x, y, rows, "frame")}</g>')
        y += height + gap
    for obj, top, slots in object_boxes:
        height = head_h + row_h * len(slots)
        title = obj.type or obj.id
        parts.append(f'<g class="ls-object-box"><rect class="ls-box" x="{_n(heap_x)}" y="{_n(top)}" width="{_n(box_w)}" '
                     f'height="{_n(height)}" rx="10"/><text class="ls-box-title" x="{_n(heap_x + 14)}" y="{_n(top + 22)}">'
                     f'{_e(_clip(title, 30))}</text>{slot_rows(heap_x, top, slots, "object")}</g>')
    height = max(y, y_obj) + 4
    paths = ''.join(f'<path class="ls-ref" d="{d}" marker-end="url(#{ctx.uid}-arrow)"/>' for d in arrows)
    svg = _svg(width, height, ''.join(titles) + ''.join(parts) + paths, item.title or 'memory',
               _arrow_marker(ctx.uid, 'ls-ref-head'))
    return _visual('memory', item, ctx, f'<div class="ls-figure-svg">{svg}</div>')


# -- database schemas ----------------------------------------------------------------------

def render_schema(item: Schema, ctx: RenderContext) -> str:
    box_w, row_h, head_h, gap_x, gap_y, margin = 240.0, 28.0, 36.0, 90.0, 56.0, 20.0
    per_row = min(item.per_row, len(item.tables))
    width = margin * 2 + per_row * box_w + (per_row - 1) * gap_x
    boxes: dict[str, tuple[float, float]] = {}
    row_heights: list[float] = []
    for index, table in enumerate(item.tables):
        row = index // per_row
        if row == len(row_heights):
            row_heights.append(0.0)
        row_heights[row] = max(row_heights[row], head_h + row_h * len(table.columns))
    for index, table in enumerate(item.tables):
        row, col = divmod(index, per_row)
        boxes[table.name] = (margin + col * (box_w + gap_x), margin + sum(row_heights[:row]) + row * gap_y)
    height = margin * 2 + sum(row_heights) + (len(row_heights) - 1) * gap_y
    parts, links = [], []
    for table in item.tables:
        x, y = boxes[table.name]
        rows = []
        for r, column in enumerate(table.columns):
            ry = y + head_h + r * row_h
            badges = ''.join(f'<tspan class="ls-key" data-key="{k}">{k.upper()} </tspan>' for k in column.key.split())
            rows.append(f'<line class="ls-sep" x1="{_n(x)}" x2="{_n(x + box_w)}" y1="{_n(ry)}" y2="{_n(ry)}"/>'
                        f'<text class="ls-slot-name ls-mono" x="{_n(x + 12)}" y="{_n(ry + 19)}">{badges}'
                        f'{_e(_clip(column.name, 18))}</text>'
                        + (f'<text class="ls-slot-type ls-mono" x="{_n(x + box_w - 12)}" y="{_n(ry + 19)}" text-anchor="end">'
                           f'{_e(_clip(column.type, 12))}</text>' if column.type else ''))
            if column.references:
                target, _, field_name = column.references.partition('.')
                tx, ty = boxes[target]
                target_row = [c.name for c in next(t for t in item.tables if t.name == target).columns].index(field_name)
                links.append((x, ry + row_h / 2, tx, ty + head_h + target_row * row_h + row_h / 2, target == table.name))
        head = (f'M{_n(x)} {_n(y + head_h)}V{_n(y + 10)}Q{_n(x)} {_n(y)} {_n(x + 10)} {_n(y)}H{_n(x + box_w - 10)}'
                f'Q{_n(x + box_w)} {_n(y)} {_n(x + box_w)} {_n(y + 10)}V{_n(y + head_h)}Z')
        parts.append(f'<g class="ls-table-box"><rect class="ls-box" x="{_n(x)}" y="{_n(y)}" width="{_n(box_w)}" '
                     f'height="{_n(head_h + row_h * len(table.columns))}" rx="10"/><path class="ls-box-head" d="{head}"/>'
                     f'<text class="ls-box-title" '
                     f'x="{_n(x + box_w / 2)}" y="{_n(y + 23)}" text-anchor="middle">{_e(_clip(table.name, 24))}</text>'
                     f'{"".join(rows)}</g>')
    paths = []
    for sx, sy, tx, ty, self_ref in links:
        if self_ref or abs(sx - tx) < 1:
            x1 = x2 = sx + box_w
            d = f'M{_n(x1)} {_n(sy)} C{_n(x1 + 60)} {_n(sy)} {_n(x2 + 60)} {_n(ty)} {_n(x2)} {_n(ty)}'
        elif tx > sx:
            x1, x2 = sx + box_w, tx
            d = f'M{_n(x1)} {_n(sy)} C{_n(x1 + 50)} {_n(sy)} {_n(x2 - 50)} {_n(ty)} {_n(x2)} {_n(ty)}'
        else:
            x1, x2 = sx, tx + box_w
            d = f'M{_n(x1)} {_n(sy)} C{_n(x1 - 50)} {_n(sy)} {_n(x2 + 50)} {_n(ty)} {_n(x2)} {_n(ty)}'
        paths.append(f'<path class="ls-relation" d="{d}" marker-start="url(#{ctx.uid}-many)" marker-end="url(#{ctx.uid}-one)"/>')
    size = 'markerWidth="14" markerHeight="14" markerUnits="userSpaceOnUse"'
    # "Many" (crow's foot) opens onto the foreign-key table; "one" is two bars at the key.
    defs = (f'<marker id="{ctx.uid}-many" viewBox="0 0 14 14" refX="1" refY="7" {size} orient="auto">'
            f'<path class="ls-marker" d="M13 7L1 1M13 7L1 7M13 7L1 13"/></marker>'
            f'<marker id="{ctx.uid}-one" viewBox="0 0 14 14" refX="12" refY="7" {size} orient="auto-start-reverse">'
            f'<path class="ls-marker" d="M6 1V13M10 1V13"/></marker>')
    svg = _svg(width, height, ''.join(paths) + ''.join(parts), item.title or 'schema', defs)
    return _visual('schema', item, ctx, f'<div class="ls-figure-svg">{svg}</div>')


register_component(Equation, render_equation)
register_component(Array, render_array)
register_component(Matrix, render_matrix)
register_component(Chart, render_chart)
register_component(Network, render_network)
register_component(Tree, render_tree)
register_component(Graph, render_graph)
register_component(Memory, render_memory)
register_component(Schema, render_schema)
