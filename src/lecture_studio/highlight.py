"""Syntax highlighting with Pygments-compatible token classes.

Python uses the standard library tokenizer and about twenty other teaching
languages (C, C++, Java, C#, JavaScript, SQL, ...) use the built-in grammars
in ``lexers``, so the core package has no dependencies and output is the same
everywhere. Other languages use Pygments when it is installed and fall back
to escaped plain text. Every path emits the same short classes (``k``, ``s``,
``m``, ``c``, ``nb`` ...), so one set of theme colors covers all languages.
Code is always escaped; nothing is executed.
"""
from __future__ import annotations

import html
import io
import keyword
import re
import tokenize

from .lexers import get_highlighter, register_highlighter

__all__ = ['highlight', 'highlight_python', 'split_lines']

PYTHON = {'python', 'py', 'python3', 'ipython', 'ipython3'}
_BUILTINS = {
    'print', 'int', 'float', 'str', 'len', 'range', 'type', 'input', 'list', 'dict', 'set',
    'sum', 'sorted', 'enumerate', 'open', 'bool', 'tuple',
}
# Python 3.12+ splits f-strings into several tokens; color every literal part.
_STRING_PARTS = {getattr(tokenize, name) for name in (
    'FSTRING_START', 'FSTRING_MIDDLE', 'FSTRING_END', 'TSTRING_START', 'TSTRING_MIDDLE', 'TSTRING_END',
) if hasattr(tokenize, name)}


def highlight_python(code: str) -> str:
    """Color Python tokens without modifying HTML markup or losing operators."""
    if not code:
        return ''
    lines = code.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))

    def position(row_col):
        row, col = row_col
        return offsets[min(row - 1, len(offsets) - 1)] + col
    parts = []
    cursor = 0
    try:
        for token in tokenize.generate_tokens(io.StringIO(code).readline):
            style = None
            if token.type == tokenize.COMMENT:
                style = 'c'
            elif token.type == tokenize.STRING or token.type in _STRING_PARTS:
                style = 's'
            elif token.type == tokenize.NUMBER:
                style = 'm'
            elif token.type == tokenize.NAME:
                if keyword.iskeyword(token.string):
                    style = 'k'
                elif token.string in _BUILTINS:
                    style = 'nb'
            if style:
                start, end = position(token.start), position(token.end)
                if start < cursor or end <= start:
                    continue
                parts.append(html.escape(code[cursor:start]))
                parts.append(f'<span class="{style}">{html.escape(code[start:end])}</span>')
                cursor = end
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return html.escape(code)
    parts.append(html.escape(code[cursor:]))
    return ''.join(parts)


register_highlighter(sorted(PYTHON), highlight_python)


def highlight(code: str, language: str) -> str:
    """Highlighted, escaped HTML for ``code`` (plain escaped text if unknown)."""
    builtin = get_highlighter(language)
    if builtin is not None:
        return builtin(code)
    try:
        from pygments import highlight as render
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import get_lexer_by_name
        from pygments.util import ClassNotFound
    except ImportError:
        return html.escape(code)
    try:
        lexer = get_lexer_by_name(language)
    except ClassNotFound:
        return html.escape(code)
    return render(code, lexer, HtmlFormatter(nowrap=True))


_PIECE = re.compile(r'(<span[^>]*>|</span>|\n)')


def split_lines(markup: str, *, marked=(), numbers: bool = False) -> str:
    """Wrap each source line in its own element, keeping token spans balanced.

    Lines listed in ``marked`` (from 1) are emphasised; ``numbers`` adds a
    gutter. Line elements carry ``data-line`` for steppers and traces.
    """
    marked = set(marked)
    lines: list[str] = []
    current: list[str] = []
    stack: list[str] = []
    for piece in _PIECE.split(markup):
        if piece == '\n':
            current.extend('</span>' for _ in stack)
            lines.append(''.join(current))
            current = list(stack)
        elif piece.startswith('<span'):
            stack.append(piece)
            current.append(piece)
        elif piece == '</span>':
            if stack:
                stack.pop()
            current.append(piece)
        elif piece:
            current.append(piece)
    if current and ''.join(current) != ''.join(stack):
        lines.append(''.join(current))
    cls = 'ls-lines ls-numbered' if numbers else 'ls-lines'
    rows = []
    for number, line in enumerate(lines, 1):
        state = ' ls-marked' if number in marked else ''
        rows.append(f'<span class="ls-line{state}" data-line="{number}">{line}</span>')
    return f'<span class="{cls}">{"".join(rows)}</span>'
