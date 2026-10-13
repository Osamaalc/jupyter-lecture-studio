"""Lecture Studio: bilingual, theme-able teaching components for Jupyter and HTML."""
from ._version import __version__
from .components import ComponentSpec, RenderContext, component_names, get_component, register_component
from .deck import LectureDeck
from .i18n import Locale, available_locales, get_locale, register_locale
from .lexers import highlighter_names, register_highlighter
from .mathml import to_mathml
from .models import (
    Activity,
    Agenda,
    Brand,
    Callout,
    Card,
    CodeExample,
    Compare,
    Component,
    Cover,
    CoverSection,
    Diagram,
    Divider,
    Exercise,
    Figure,
    Node,
    Note,
    Quiz,
    RichText,
    Slide,
    Table,
    Theme,
    Trace,
    TraceStep,
)
from .pdf import export_pdf
from .presets import diagram_names, preset_diagram
from .themes import ThemePreset, get_theme, register_theme, theme_names
from .visuals import (
    Array,
    Chart,
    Column,
    Equation,
    Frame,
    Graph,
    GraphEdge,
    GraphNode,
    HeapObject,
    Matrix,
    Memory,
    Network,
    Schema,
    SchemaTable,
    Series,
    Tree,
    TreeNode,
)

__all__ = [
    'LectureDeck', 'Theme', 'Brand', 'RichText',
    # content models
    'Card', 'Node', 'Diagram', 'Activity', 'CoverSection', 'TraceStep',
    'Series', 'TreeNode', 'GraphNode', 'GraphEdge', 'Frame', 'HeapObject', 'Column', 'SchemaTable',
    # components
    'Component', 'Cover', 'Slide', 'Note', 'Table', 'Callout', 'Compare', 'CodeExample', 'Quiz', 'Trace',
    'Exercise', 'Agenda', 'Figure', 'Divider',
    # subject visuals
    'Equation', 'Array', 'Matrix', 'Chart', 'Network', 'Tree', 'Graph', 'Memory', 'Schema', 'to_mathml',
    # extension points
    'register_component', 'get_component', 'component_names', 'ComponentSpec', 'RenderContext',
    'register_theme', 'get_theme', 'theme_names', 'ThemePreset',
    'register_locale', 'get_locale', 'available_locales', 'Locale',
    'register_highlighter', 'highlighter_names',
    # helpers
    'diagram_names', 'preset_diagram', 'export_pdf', '__version__',
]
