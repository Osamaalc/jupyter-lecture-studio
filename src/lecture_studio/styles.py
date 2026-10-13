"""Stylesheet and font assembly.

One versioned stylesheet serves every deck; themes are CSS custom properties
on each deck's wrapper, so decks with different themes coexist on one page.
Fonts (the bulk of the weight) are embedded once per page where possible.
"""
from __future__ import annotations

import base64
from functools import lru_cache
from importlib.resources import files
import re

__all__ = ['asset', 'bundled_fonts', 'stylesheet', 'font_styles']

GOOGLE_FONTS = ("@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900"
                "&family=JetBrains+Mono:wght@400;500&display=swap');")


@lru_cache(maxsize=16)
def asset(name: str) -> str:
    return files('lecture_studio').joinpath('assets').joinpath(name).read_text(encoding='utf-8')


@lru_cache(maxsize=1)
def bundled_fonts() -> str:
    """Embed the original typefaces so notebook and exported HTML need no network."""
    css = asset('fonts.css')

    def embed(match):
        data = files('lecture_studio').joinpath('assets').joinpath('fonts').joinpath(match[1]).read_bytes()
        return 'url(data:font/woff2;base64,' + base64.b64encode(data).decode('ascii') + ')'
    return re.sub(r'url\(([^)]+\.woff2)\)', embed, css)


def minify(css: str) -> str:
    """Drop comments and layout whitespace; values and strings are untouched."""
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    css = re.sub(r'\s*\n\s*', '\n', css)
    css = re.sub(r'\s*([{};])\s*', r'\1', css)
    return css.replace('\n', ' ').strip()


@lru_cache(maxsize=4)
def stylesheet(notebook_style: bool = False, present: bool = False) -> str:
    css = minify(asset('studio.css'))
    if notebook_style:
        css += minify(asset('notebook.css'))
    if present:
        css += minify(asset('present.css'))
    return css


def font_styles(external: bool) -> str:
    return GOOGLE_FONTS if external else bundled_fonts()
