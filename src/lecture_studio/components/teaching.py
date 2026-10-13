"""Teaching components added in 1.0: callouts, comparisons, runnable-looking
examples, quizzes, execution traces, exercises, agendas, figures and dividers.

Interactive parts (quiz choices, trace steps, reveals) use native form
controls and ``details`` elements, so they work offline, in notebooks and in
exported HTML without any JavaScript.
"""
from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
import re

from ..markup import escape
from ..models import Agenda, Callout, CodeExample, Compare, Divider, Exercise, Figure, Quiz, Trace
from . import register_component
from .base import RenderContext

_SVG = ('<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{}</svg>')
ICONS = {
    'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
    'tip': '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    'warning': '<path d="M12 3 2.5 20h19L12 3z"/><path d="M12 10v4M12 17v.5"/>',
    'mistake': '<circle cx="12" cy="12" r="9"/><path d="m9 9 6 6M15 9l-6 6"/>',
    'success': '<circle cx="12" cy="12" r="9"/><path d="m8 12.5 2.5 2.5L16 9.5"/>',
    'key': '<path d="m12 3 2.7 5.6 6.1.8-4.5 4.2 1.1 6.1L12 16.8l-5.4 2.9 1.1-6.1-4.5-4.2 6.1-.8z"/>',
}


def icon(name: str) -> str:
    return _SVG.format(ICONS[name])


def panel(name: str, ctx: RenderContext, body: str, *, label: str = '', title: str = '', attrs: str = '', component=None) -> str:
    """The shared dark frame for teaching components."""
    head = ''
    if label or title:
        head = ('<header class="ls-panel-head">'
                + (f'<span class="ls-panel-label">{label}</span>' if label else '')
                + (f'<h3 class="ls-panel-title">{ctx.line(title)}</h3>' if title else '') + '</header>')
    notes = ctx.notes(component) if component is not None else ''
    return f'<section class="ls-frame ls-panel ls-{name}"{attrs}>{head}{body}{notes}</section>'


def description(value, ctx: RenderContext) -> str:
    return f'<div class="ls-panel-text">{ctx.text(value)}</div>' if value else ''


def render_callout(callout: Callout, ctx: RenderContext) -> str:
    title = callout.title if callout.title is not None else ctx.locale['callout.' + callout.style]
    return (f'<section class="ls-callout" data-style="{callout.style}"><span class="ls-callout-icon">{icon(callout.style)}</span>'
            f'<div class="ls-callout-content"><strong class="ls-callout-title">{ctx.line(title)}</strong>'
            f'<div class="ls-callout-body">{ctx.text(callout.body)}</div></div>{ctx.notes(callout)}</section>')


def render_compare(compare: Compare, ctx: RenderContext) -> str:
    wrong_right = compare.mode == 'wrong-right'
    sides = []
    for side, code, label, note, default, mark in (
        ('before', compare.before, compare.before_label, compare.before_note,
         'compare.wrong' if wrong_right else 'compare.before', '✕' if wrong_right else '−'),
        ('after', compare.after, compare.after_label, compare.after_note,
         'compare.right' if wrong_right else 'compare.after', '✓' if wrong_right else '+'),
    ):
        text = escape(label) if label is not None else ctx.label(default)
        note_html = f'<div class="ls-compare-note">{ctx.text(note)}</div>' if note else ''
        sides.append(f'<div class="ls-compare-side" data-side="{side}"><div class="ls-compare-label">'
                     f'<span class="ls-compare-mark" aria-hidden="true">{mark}</span>{text}</div>'
                     f'{ctx.code(code, compare.language)}{note_html}</div>')
    body = description(compare.description, ctx) + f'<div class="ls-compare-grid">{"".join(sides)}</div>'
    return panel('compare', ctx, body, title=compare.title, attrs=f' data-mode="{compare.mode}"', component=compare)


def output_block(output: str, ctx: RenderContext) -> str:
    if not output:
        return ''
    return (f'<div class="ls-output"><div class="ls-output-bar"><span>{ctx.label("code.output")}</span></div>'
            f'<pre>{escape(output)}</pre></div>')


def render_code(example: CodeExample, ctx: RenderContext) -> str:
    body = (description(example.description, ctx)
            + ctx.code(example.code, example.language, marked=example.highlight, numbers=example.line_numbers)
            + output_block(example.output, ctx)
            + (f'<p class="ls-panel-caption">{ctx.line(example.caption)}</p>' if example.caption else ''))
    return panel('example', ctx, body, title=example.title, component=example)


def _keys(ctx: RenderContext, count: int) -> list[str]:
    keys = ctx.locale['quiz.keys']
    return list(keys[:count]) if len(keys) >= count else [str(i) for i in range(1, count + 1)]


def render_quiz(quiz: Quiz, ctx: RenderContext) -> str:
    answer = quiz.answer if isinstance(quiz.answer, int) else quiz.options.index(quiz.answer)
    keys = _keys(ctx, len(quiz.options))
    yes, no = ctx.label('quiz.correct'), ctx.label('quiz.incorrect')
    options = []
    for i, option in enumerate(quiz.options):
        correct = ' data-correct' if ctx.include_answers and i == answer else ''
        options.append(f'<li class="ls-option"{correct}><input type="radio" name="{ctx.uid}" id="{ctx.uid}-{i}">'
                       f'<label for="{ctx.uid}-{i}"><span class="ls-option-key">{escape(keys[i])}</span>'
                       f'<span class="ls-option-text">{ctx.line(option)}</span>'
                       f'<span class="ls-option-state" data-yes="{yes}" data-no="{no}"></span></label></li>')
    reveal = ''
    if ctx.include_answers:
        explanation = f' {ctx.text(quiz.explanation)}' if quiz.explanation else ''
        reveal = (f'<details class="ls-reveal" data-answer><summary>{ctx.label("quiz.reveal")}</summary>'
                  f'<div class="ls-answer"><strong>{escape(keys[answer])} · {ctx.line(quiz.options[answer])}</strong>'
                  f'{explanation}</div></details>')
    body = (f'<p class="ls-question">{ctx.line(quiz.question)}</p>{ctx.code(quiz.code, quiz.language)}'
            f'<ol class="ls-options">{"".join(options)}</ol>{reveal}')
    graded = ' data-graded' if ctx.include_answers else ''
    return panel('quiz', ctx, body, label=ctx.label('quiz'), title=quiz.title or '', attrs=graded, component=quiz)


def render_trace(trace: Trace, ctx: RenderContext) -> str:
    uid = ctx.uid
    rules, inputs, buttons, states = [], [], [], []
    for n, step in enumerate(trace.steps, 1):
        sid = f'{uid}-s{n}'
        checked = ' checked' if n == 1 else ''
        inputs.append(f'<input class="ls-step-input" type="radio" name="{uid}" id="{sid}"{checked}>')
        buttons.append(f'<label for="{sid}">{n}</label>')
        scope = f'#{uid} #{sid}:checked~'
        rules.append(f'{scope}.ls-trace-body .ls-line[data-line="{step.line}"]{{background:var(--ls-trace-line-bg);'
                     f'box-shadow:inset 3px 0 0 var(--ls-trace-line-rule)}}'
                     f'{scope}.ls-trace-body .ls-state[data-step="{n}"]{{display:block}}'
                     f'{scope}.ls-trace-controls label[for="{sid}"]{{background:var(--ls-trace-active-bg);'
                     f'color:var(--ls-trace-active-text);border-color:transparent}}')
        rows = ''.join(f'<tr><th scope="row">{escape(name)}</th><td>{escape(value)}</td></tr>'
                       for name, value in step.variables.items())
        variables = (f'<div class="ls-state-title">{ctx.label("trace.variables")}</div>'
                     f'<table class="ls-vars"><tbody>{rows}</tbody></table>') if rows else ''
        output = (f'<div class="ls-state-title">{ctx.label("trace.output")}</div><pre class="ls-state-output">'
                  f'{escape(step.output)}</pre>') if step.output else ''
        note = f'<p class="ls-state-note">{ctx.line(step.note)}</p>' if step.note else ''
        nav = ''
        if n < len(trace.steps):
            nav = f'<label class="ls-step-next" for="{uid}-s{n + 1}">{ctx.label("present.next")}</label>'
        states.append(f'<div class="ls-state" data-step="{n}"><div class="ls-state-head">{ctx.label("trace.step")} {n} · '
                      f'{ctx.label("trace.line")} {step.line}</div>{variables}{output}{note}{nav}</div>')
    code = ctx.code(trace.code, trace.language, numbers=True, marked=())
    body = (f'<style>{"".join(rules)}</style>{description(trace.description, ctx)}{"".join(inputs)}'
            f'<div class="ls-trace-controls"><span>{ctx.label("trace.step")}</span>{"".join(buttons)}</div>'
            f'<div class="ls-trace-body"><div class="ls-trace-code">{code}</div>'
            f'<div class="ls-trace-states">{"".join(states)}</div></div>')
    return panel('trace', ctx, body, label=ctx.label('trace'), title=trace.title, attrs=f' id="{uid}"', component=trace)


def render_exercise(exercise: Exercise, ctx: RenderContext) -> str:
    hints = ''.join(f'<details class="ls-hint"><summary>{ctx.label("exercise.hint")} {i}</summary>'
                    f'<div>{ctx.text(hint)}</div></details>' for i, hint in enumerate(exercise.hints, 1))
    solution = ''
    if ctx.include_answers and (exercise.solution or exercise.explanation):
        explanation = f'<div class="ls-panel-text">{ctx.text(exercise.explanation)}</div>' if exercise.explanation else ''
        solution = (f'<details class="ls-reveal ls-solution" data-answer><summary>{ctx.label("exercise.solution")}</summary>'
                    f'<div class="ls-answer">{ctx.code(exercise.solution, exercise.language)}{explanation}</div></details>')
    body = (f'<div class="ls-panel-text ls-task">{ctx.text(exercise.task)}</div>{ctx.code(exercise.starter, exercise.language)}'
            + (f'<div class="ls-hints">{hints}</div>' if hints else '') + solution)
    return panel('exercise', ctx, body, label=ctx.label('exercise'), title=exercise.title, component=exercise)


def render_agenda(agenda: Agenda, ctx: RenderContext) -> str:
    items = ''.join(f'<li><span class="ls-agenda-mark">{"✓" if agenda.mode == "recap" else f"{i:02d}"}</span>'
                    f'<span>{ctx.line(item)}</span></li>' for i, item in enumerate(agenda.items, 1))
    title = agenda.title if agenda.title is not None else ctx.locale['agenda.' + agenda.mode]
    return panel('agenda', ctx, f'<ol class="ls-agenda-list">{items}</ol>', title=title,
                 attrs=f' data-mode="{agenda.mode}"', component=agenda)


IMAGE_TYPES = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
               '.webp': 'image/webp', '.svg': 'image/svg+xml', '.avif': 'image/avif'}
MAX_IMAGE_BYTES = 15 * 1024 * 1024


def image_source(src: str, base: Path) -> str:
    """Embed local images so lectures stay self-contained; allow web URLs."""
    if re.match(r'https?://', src, re.I):
        return src
    if src.startswith('data:image/'):
        return src
    if re.match(r'[a-z][a-z0-9+.-]*:', src, re.I) and not re.match(r'[a-z]:[\\/]', src, re.I):
        raise ValueError('Figure src must be a local file, an http(s) URL or a data:image URI')
    path = Path(src).expanduser()
    if not path.is_absolute():
        path = base / path
    mime = IMAGE_TYPES.get(path.suffix.lower()) or mimetypes.guess_type(path.name)[0]
    if not mime or not mime.startswith('image/'):
        raise ValueError(f'Unsupported image type: {path.suffix or src}')
    if not path.is_file():
        raise FileNotFoundError(f'Figure image not found: {path}')
    if path.stat().st_size > MAX_IMAGE_BYTES:
        raise ValueError('Figure images must be smaller than 15 MB')
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def render_figure(figure: Figure, ctx: RenderContext) -> str:
    source = escape(image_source(figure.src, ctx.base_dir))
    width = f' style="max-width:{figure.width}px"' if figure.width else ''
    caption = ''
    if figure.caption:
        caption = (f'<figcaption><span>{ctx.label("figure")} {ctx.ordinal}</span> {ctx.line(figure.caption)}</figcaption>')
    alt = escape(figure.alt or figure.caption)
    body = (f'<figure class="ls-figure"><div class="ls-figure-mat"><img src="{source}" alt="{alt}"{width}></div>'
            f'{caption}</figure>')
    return panel('figure-panel', ctx, body, title=figure.title, component=figure)


def render_divider(divider: Divider, ctx: RenderContext) -> str:
    label = divider.label if divider.label is not None else f'{ctx.locale["divider"]} {ctx.ordinal:02d}'
    subtitle = f'<p class="ls-divider-subtitle">{ctx.line(divider.subtitle)}</p>' if divider.subtitle else ''
    return (f'<section class="ls-frame ls-divider">{ctx.topline()}<div class="ls-divider-body">'
            f'<span class="ls-divider-label">{escape(label)}</span><h2 class="ls-divider-title">{ctx.line(divider.title)}</h2>'
            f'{subtitle}</div>{ctx.footer()}{ctx.notes(divider)}</section>')


register_component(Callout, render_callout)
register_component(Compare, render_compare)
register_component(CodeExample, render_code)
register_component(Quiz, render_quiz)
register_component(Trace, render_trace)
register_component(Exercise, render_exercise)
register_component(Agenda, render_agenda)
register_component(Figure, render_figure)
register_component(Divider, render_divider)
