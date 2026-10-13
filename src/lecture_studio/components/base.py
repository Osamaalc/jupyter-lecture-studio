"""Rendering context shared by every component renderer."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from ..highlight import highlight, split_lines
from ..i18n import Locale
from ..lexers import language_label
from ..markup import escape, inline, rich
from ..models import Brand, Theme

__all__ = ['RenderContext', 'script']

_JOINING_SCRIPT = re.compile(r'[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]')


def script(value: str, *, attribute: bool = False) -> str:
    """Mark Arabic-script text placed in letter-spaced Latin slots.

    Letter spacing breaks Arabic letter joining, so such labels opt out of it.
    """
    if not _JOINING_SCRIPT.search(value or ''):
        return ''
    return ' class="ls-arabic"' if attribute else ' ls-arabic'


@dataclass
class RenderContext:
    """Everything a renderer needs besides the component itself.

    ``ordinal`` counts components of the same kind (slide 1, 2, 3...).
    ``uid`` is stable for the same content and position, for form controls.
    """
    brand: Brand
    theme: Theme
    locale: Locale
    direction: str
    markup: str = 'markdown'
    ordinal: int = 1
    uid: str = 'ls'
    include_answers: bool = True
    include_notes: bool = False
    base_dir: Path = field(default_factory=Path.cwd)

    # -- text -------------------------------------------------------------
    def esc(self, value) -> str:
        return escape(value)

    def line(self, value: str) -> str:
        """One line of author text: escaped, with inline code and bold."""
        return inline(value, markup=self.markup, direction=self.direction)

    def text(self, value) -> str:
        """Multi-line author content (plain text or trusted RichText)."""
        return rich(value, markup=self.markup, direction=self.direction)

    def label(self, key: str) -> str:
        return escape(self.locale[key])

    @property
    def course(self) -> str:
        return self.brand.course if self.brand.course is not None else self.locale['course']

    @property
    def series(self) -> str:
        return self.brand.series if self.brand.series is not None else self.locale['series']

    # -- shared fragments ---------------------------------------------------
    def topline(self) -> str:
        return (f'<div class="ls-topline"><span class="ls-course">{escape(self.course)}</span>'
                f'<span class="ls-series{script(self.series)}">{escape(self.series)}</span></div>')

    def footer(self, label: str = '') -> str:
        footer = self.brand.footer if self.brand.footer is not None else self.locale['footer']
        label = label or self.brand.lesson
        return (f'<footer class="ls-footer"><span>{self.line(footer)}</span>'
                f'<span{script(label, attribute=True)}>{escape(label)}</span></footer>')

    def code(self, code: str, language: str | None = None, *, toolbar: bool = True,
             marked=(), numbers: bool = False, label: str | None = None) -> str:
        if not code:
            return ''
        lang = language or self.brand.language
        content = highlight(code, lang)
        if marked or numbers:
            content = split_lines(content, marked=marked, numbers=numbers)
        bar = ''
        if toolbar:
            caption = escape(label) if label is not None else escape(language_label(lang))
            bar = f'<div class="ls-code-bar"><i></i><i></i><i></i><span>{caption}</span></div>'
        return f'<div class="ls-code">{bar}<pre><code>{content}</code></pre></div>'

    def notes(self, component) -> str:
        notes = getattr(component, 'notes', '')
        if not (self.include_notes and notes):
            return ''
        return f'<aside class="ls-notes" hidden>{self.text(notes)}</aside>'
