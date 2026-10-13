"""Cover, slide, note and table: the original Lecture Studio components."""
from __future__ import annotations

import re

from ..markup import escape
from ..models import Activity, Cover, Diagram, Note, Slide, Table
from . import register_component
from .base import RenderContext, script


def render_cover(cover: Cover, ctx: RenderContext) -> str:
    tags = ''.join(f'<span class="ls-tag">{escape(t)}</span>' for t in cover.tags)
    blocks = ''.join(f'<div class="ls-section"><b>{escape(s.title)}</b><p>{escape(s.description)}</p></div>'
                     for s in cover.sections)
    hero = ''
    if cover.hero_code or cover.hero_result:
        code = re.sub(r'(^|\n)(&gt;&gt;&gt;)', r'\1<em>\2</em>', escape(cover.hero_code)).replace('\n', '<br>')
        label = cover.hero_label or ctx.series
        hero = (f'<div class="ls-hero"><div class="ls-hero-head"><i></i><i></i><i></i>'
                f'<span{script(label, attribute=True)}>{escape(label)}</span></div>'
                f'<div class="ls-hero-code">{code}</div><div class="ls-hero-result">{escape(cover.hero_result)}</div>'
                '<span class="ls-hero-orbit" aria-hidden="true"></span></div>')
    modifiers = ('' if hero else ' ls-no-hero') + (' ls-flex-sections' if len(cover.sections) != 2 else '')
    return (f'<section class="ls-frame ls-cover{modifiers}">{ctx.topline()}<div class="ls-cover-grid"><div>'
            f'<div class="ls-kicker">{escape(cover.kicker or ctx.brand.lesson)}</div>'
            f'<h1 class="ls-cover-title">{ctx.line(cover.title)}</h1><p class="ls-lead">{ctx.text(cover.description)}</p>'
            f'<div class="ls-tags">{tags}</div></div>{hero}</div><div class="ls-sections">{blocks}</div>'
            f'{ctx.footer(cover.footer_label or "")}{ctx.notes(cover)}</section>')


def render_diagram(diagram: Diagram | None, ctx: RenderContext) -> str:
    if diagram is None:
        return ''
    nodes = []
    arrow = '←' if diagram.direction == 'rtl' else '→'
    for i, node in enumerate(diagram.nodes):
        selected = ' ls-selected' if node.selected else ''
        nodes.append(f'<div class="ls-node{selected}" style="--order:{i}"><b>{escape(node.value)}</b>'
                     f'<span>{escape(node.note)}</span></div>')
        if diagram.arrows and i < len(diagram.nodes) - 1:
            nodes.append(f'<span class="ls-arrow" aria-hidden="true">{arrow}</span>')
    return (f'<details class="ls-stage" open><summary><span>{ctx.label("stage")}</span>'
            f'<span class="ls-stage-toggle">{ctx.label("stage_toggle")}</span></summary>'
            f'<figure class="ls-diagram" data-kind="{diagram.kind}"><figcaption>'
            f'<span class="ls-diagram-eyebrow">{ctx.label("diagram_eyebrow")}</span><strong>{escape(diagram.title)}</strong>'
            f'</figcaption><div class="ls-track" dir="{diagram.direction}">{"".join(nodes)}</div>'
            f'<p class="ls-caption">{escape(diagram.caption)}</p></figure></details>')


def render_activity(activity: Activity | None, ctx: RenderContext) -> str:
    if activity is None:
        return ''
    label = activity.label if activity.label is not None else ctx.locale['activity']
    reveal = activity.reveal if activity.reveal is not None else ctx.locale['reveal']
    answer = ''
    if ctx.include_answers:
        answer = (f'<details data-answer><summary>{escape(reveal)}</summary>'
                  f'<div class="ls-answer">{ctx.text(activity.answer)}</div></details>')
    return (f'<aside class="ls-activity"><div class="ls-activity-label">{escape(label)}</div>'
            f'<p>{ctx.line(activity.question)}</p>{ctx.code(activity.code, activity.language, toolbar=False)}{answer}</aside>')


def render_slide(slide: Slide, ctx: RenderContext) -> str:
    number = f'{ctx.ordinal:02d}'
    cards = []
    for i, card in enumerate(slide.cards, 1):
        reason = (f'<div class="ls-reason"><strong>{ctx.label("reason")}</strong> {ctx.text(card.reason)}</div>'
                  if card.reason else '')
        cards.append(f'<li class="ls-card" style="--order:{i - 1}"><div class="ls-card-head">'
                     f'<span class="ls-card-number">{i:02d}</span><h4 class="ls-card-title">{ctx.line(card.title)}</h4></div>'
                     f'<p class="ls-card-text">{ctx.text(card.explanation)}</p>{ctx.code(card.code, card.language)}{reason}</li>')
    subtitle = f'<div class="ls-subtitle">{ctx.line(slide.subtitle)}</div>' if slide.subtitle else ''
    single = ' ls-single' if len(cards) == 1 else ''
    lesson = ctx.brand.lesson + ' / ' if ctx.brand.lesson else ''
    return (f'<section class="ls-frame ls-slide" data-scene="{number}">{ctx.topline()}<header class="ls-header">'
            f'<div class="ls-watermark" aria-hidden="true">{number}</div>'
            f'<span class="ls-eyebrow">{ctx.label("eyebrow")} / {number}</span>'
            f'<h2 class="ls-title">{ctx.line(slide.title)}</h2>{subtitle}</header>'
            f'<div class="ls-description">{ctx.text(slide.description)}</div>{render_diagram(slide.diagram, ctx)}'
            f'<ol class="ls-cards{single}">{"".join(cards)}</ol>{render_activity(slide.activity, ctx)}'
            f'{ctx.footer(lesson + number)}{ctx.notes(slide)}</section>')


def render_note(note: Note, ctx: RenderContext) -> str:
    return f'<section class="ls-note"><h2>{ctx.line(note.title)}</h2><div>{ctx.text(note.body)}</div>{ctx.notes(note)}</section>'


def render_table(table: Table, ctx: RenderContext) -> str:
    head = ''.join(f'<th scope="col">{escape(h)}</th>' for h in table.headers)
    body = ''.join('<tr>' + ''.join(f'<td>{escape(c)}</td>' for c in row) + '</tr>' for row in table.rows)
    return (f'<section class="ls-note"><h2>{ctx.line(table.title)}</h2><div class="ls-table"><table>'
            f'<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>{ctx.notes(table)}</section>')


register_component(Cover, render_cover)
register_component(Slide, render_slide)
register_component(Note, render_note)
register_component(Table, render_table)
