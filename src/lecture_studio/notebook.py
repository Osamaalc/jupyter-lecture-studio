"""Jupyter integration: displaying output, cell identity and shared fonts.

Re-running a notebook cell must replace what that cell added to a deck
instead of appending a copy. JupyterLab, Notebook 7 and VS Code send the
cell id with each execution; it is read here. Without a cell id (plain
scripts, some hosts) components are appended in call order.

The embedded fonts are ~200 KB. In a notebook they are sent with the first
lecture output only (the "font host" cell) and again whenever that cell is
re-run, instead of with every slide.
"""
from __future__ import annotations

__all__ = ['current_cell', 'display_html', 'claim_fonts', 'reset_fonts']

_font_host: str | None = None


def current_cell() -> tuple[str, int] | None:
    """Return (cell id, execution count) for the running notebook cell."""
    try:
        from IPython import get_ipython
    except ImportError:
        return None
    shell = get_ipython()
    if shell is None:
        return None
    parent = None
    kernel = getattr(shell, 'kernel', None)
    if kernel is not None and hasattr(kernel, 'get_parent'):
        try:
            parent = kernel.get_parent()
        except TypeError:
            parent = kernel.get_parent('shell')
        except Exception:
            parent = None
    if not parent:
        parent = getattr(shell, 'parent_header', None)
    if not isinstance(parent, dict):
        return None
    cell_id = (parent.get('metadata') or {}).get('cellId')
    if not isinstance(cell_id, str) or not cell_id:
        return None
    return cell_id, int(getattr(shell, 'execution_count', 0) or 0)


def display_html(markup: str) -> None:
    try:
        from IPython.display import HTML, display
    except ImportError as exc:
        raise RuntimeError('Install jupyter-lecture-studio[notebook] or use show=False in scripts') from exc
    display(HTML(markup))


def claim_fonts(cell_id: str | None) -> bool:
    """Should this output carry the embedded fonts?"""
    global _font_host
    if cell_id is None:
        return True
    if _font_host is None or _font_host == cell_id:
        _font_host = cell_id
        return True
    return False


def reset_fonts(cell_id: str | None = None) -> None:
    """Make ``cell_id`` (or the next output) the font host again."""
    global _font_host
    _font_host = cell_id
