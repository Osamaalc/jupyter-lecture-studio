"""Theme presets. A preset is a palette family plus design-token overrides.

Every color in the stylesheet is a ``--ls-*`` custom property. Palettes:

``original``  the reference gold design, unchanged since 0.1.
``custom``    the dark design with interface accents derived from ``accent``.
``paper``     a light design for bright classrooms and printing.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
import re
from types import MappingProxyType

__all__ = ['ThemePreset', 'register_theme', 'get_theme', 'theme_names']

PALETTES = ('original', 'custom', 'paper')
_HEX = re.compile(r'#[0-9a-fA-F]{6}')
_TOKEN = re.compile(r'[a-z][a-z0-9-]*')
_UNSAFE = re.compile(r'[;{}<>\\]|/\*|\*/')


def validate_tokens(tokens: Mapping[str, str] | None) -> dict[str, str]:
    """Token names are bare (``card-bg``); values cannot escape the declaration."""
    result = {}
    for name, value in (tokens or {}).items():
        if not isinstance(name, str) or not _TOKEN.fullmatch(name.removeprefix('--ls-')):
            raise ValueError(f'Invalid design token name {name!r}')
        if not isinstance(value, str) or not value.strip() or _UNSAFE.search(value):
            raise ValueError(f'Invalid value for design token {name!r}')
        result[name.removeprefix('--ls-')] = value.strip()
    return result


@dataclass(frozen=True)
class ThemePreset:
    name: str
    accent: str
    background: str
    palette: str = 'custom'
    tokens: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not _TOKEN.fullmatch(self.name):
            raise ValueError('Theme names are lowercase identifiers')
        for value in (self.accent, self.background):
            if not _HEX.fullmatch(value):
                raise ValueError('Theme colors must be six-digit hex colors')
        if self.palette not in PALETTES:
            raise ValueError('Theme palette must be one of: ' + ', '.join(PALETTES))
        object.__setattr__(self, 'tokens', MappingProxyType(validate_tokens(self.tokens)))


_THEMES: dict[str, ThemePreset] = {}


def register_theme(name: str, *, accent: str, background: str, palette: str = 'custom',
                   tokens: Mapping[str, str] | None = None) -> ThemePreset:
    """Register a reusable theme, e.g. a university or department identity."""
    preset = ThemePreset(name, accent, background, palette, tokens or {})
    _THEMES[name] = preset
    return preset


def get_theme(name: str) -> ThemePreset:
    try:
        return _THEMES[name]
    except (KeyError, TypeError):
        raise ValueError(f'preset must be one of: {", ".join(_THEMES)}') from None


def theme_names() -> tuple[str, ...]:
    return tuple(_THEMES)


register_theme('gold', accent='#ecd29a', background='#0c141f', palette='original')
register_theme('emerald', accent='#a6e5c4', background='#0d1c1c')
register_theme('ocean', accent='#9fceff', background='#0b1728')
register_theme('violet', accent='#cdb9ff', background='#120f22')
register_theme('ruby', accent='#f4b3c0', background='#1a0f15')
register_theme('paper', accent='#b8913f', background='#fbf9f4', palette='paper')
