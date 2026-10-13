"""Component registry: maps each JSON ``type`` to a model and an HTML renderer.

Third-party packages add components without changing this library::

    # pyproject.toml of the plugin
    [project.entry-points."lecture_studio.components"]
    timeline = "my_package:register"

    # my_package/__init__.py
    def register():
        register_component(Timeline, render_timeline)

Registered components work in ``LectureDeck.add``, ``render`` and JSON files.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from importlib.metadata import entry_points
from typing import Any
import warnings

from ..models import Component
from .base import RenderContext

__all__ = ['ComponentSpec', 'RenderContext', 'register_component', 'get_component', 'component_names']

Renderer = Callable[[Any, RenderContext], str]


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    model: type[Component]
    render: Renderer


_REGISTRY: dict[str, ComponentSpec] = {}
_plugins_loaded = False


def register_component(model: type[Component], render: Renderer, *, replace: bool = False) -> ComponentSpec:
    """Register a component model (a ``Component`` dataclass) and its renderer."""
    if not (isinstance(model, type) and issubclass(model, Component)) or not model.kind:
        raise TypeError('model must be a Component subclass with a kind')
    if model.kind in _REGISTRY and not replace:
        raise ValueError(f'Component type {model.kind!r} is already registered')
    spec = ComponentSpec(model.kind, model, render)
    _REGISTRY[model.kind] = spec
    return spec


def _load_plugins():
    global _plugins_loaded
    if _plugins_loaded:
        return
    _plugins_loaded = True
    for entry in entry_points(group='lecture_studio.components'):
        try:
            entry.load()()
        except Exception as exc:  # A broken plugin must not break lectures.
            warnings.warn(f'Lecture Studio plugin {entry.name!r} failed to load: {exc}', RuntimeWarning, stacklevel=2)


def get_component(name: str) -> ComponentSpec:
    if name not in _REGISTRY:
        _load_plugins()
    try:
        return _REGISTRY[name]
    except KeyError:
        raise ValueError(f'Unknown component type: {name!r}. Available: {", ".join(_REGISTRY)}') from None


def component_names() -> tuple[str, ...]:
    _load_plugins()
    return tuple(_REGISTRY)


from . import core, teaching, visuals  # noqa: E402,F401  (register built-in components)
