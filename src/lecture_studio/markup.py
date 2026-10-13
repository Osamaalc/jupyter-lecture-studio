"""Turn author text into safe HTML.

Plain strings are always escaped. Lightweight markup is applied on top, and
it can never introduce tags of its own:

* ```code``` becomes inline code (isolated left-to-right inside Arabic text);
* ``**bold**`` becomes strong text;
* ``$x^2$`` becomes an inline formula (MathML, see ``mathml``). As in Pandoc,
  the opening ``$`` must touch the formula and the closing one must not be
  followed by a digit, so prices such as "$5 to $10" stay text; ``\\$`` is a
  literal dollar sign;
* in right-to-left text, terms such as ``C++`` or ``C#`` are isolated so their
  symbols stay attached to the correct side.

``RichText`` bypasses all of this and is inserted verbatim (trusted HTML).
"""
from __future__ import annotations

import html
import re

from .mathml import to_mathml
from .models import RichText, text

__all__ = ['escape', 'inline', 'rich']

_SPECIAL = re.compile(r'`(?P<code>[^`\n]+)`|(?<![\\$])\$(?=[^\s$])(?P<math>[^$\n]*?[^\s\\$])\$(?!\d)')
# ``**`` opens bold at a word start, or right after a one-letter Arabic proclitic
# (و ف ب ل ك), as in ``و**الكائن**``; ``a**2`` and ``**kwargs`` stay literal.
_BOLD = re.compile(r'(?:(?<![\w*])|(?<=(?<![\w*])[وفبلك]))\*\*(?=\S)(.+?)(?<=\S)\*\*(?![\w*])')
_SYMBOL_TERM = re.compile(r'(?<![\w#+])([A-Za-z][A-Za-z0-9]*(?:\+\+|#))(?![\w#+])')
_TAG = re.compile(r'(<[^>]+>)')


def escape(value) -> str:
    return html.escape(str(value))


def _isolate(markup: str) -> str:
    """Wrap symbol-suffixed Latin terms outside tags, code and math in <bdi>."""
    parts = _TAG.split(markup)
    depth = 0
    for i, part in enumerate(parts):
        if i % 2:
            if part.startswith(('<code', '<math')):
                depth += 1
            elif part in ('</code>', '</math>'):
                depth = max(0, depth - 1)
        elif not depth and part:
            parts[i] = _SYMBOL_TERM.sub(r'<bdi dir="ltr">\1</bdi>', part)
    return ''.join(parts)


def _plain(value: str) -> str:
    return _BOLD.sub(r'<strong>\1</strong>', html.escape(value).replace('\\$', '$'))


def inline(value: str, *, markup: str = 'markdown', direction: str = 'rtl') -> str:
    """Escape a single line of author text and apply inline markup."""
    text(value, 'text')
    if markup != 'markdown':
        result = html.escape(value)
    else:
        pieces, last = [], 0
        for match in _SPECIAL.finditer(value):
            pieces.append(_plain(value[last:match.start()]))
            if match['code'] is not None:
                pieces.append(f'<code>{html.escape(match["code"])}</code>')
            else:
                pieces.append(to_mathml(match['math'], display=False))
            last = match.end()
        pieces.append(_plain(value[last:]))
        result = ''.join(pieces)
    if direction == 'rtl':
        result = _isolate(result)
    return result


def rich(value, *, markup: str = 'markdown', direction: str = 'rtl') -> str:
    """Multi-line content: plain text with line breaks, or trusted RichText."""
    if isinstance(value, RichText):
        return value.html
    text(value, 'content')
    return inline(value, markup=markup, direction=direction).replace('\n', '<br>')
