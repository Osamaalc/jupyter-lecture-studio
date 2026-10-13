"""Jupyter Lecture Studio: bilingual teaching components, slides and offline HTML.

This is the recommended import name. It exposes exactly the same objects as
``lecture_studio``, which stays available for existing notebooks.
"""
from importlib.resources import files
from pathlib import Path

import lecture_studio as _core
from lecture_studio import *  # noqa: F401,F403  (re-export the complete public API)
from lecture_studio import __version__  # noqa: F401

__all__ = [*_core.__all__, 'documentation_path']


def documentation_path():
    """Return the bundled offline documentation index as an absolute Path.

    A source checkout needs ``python tools/build_docs.py`` first. Published
    wheels and source archives already contain the generated documentation.
    """
    path = Path(str(files(__package__).joinpath('docs').joinpath('index.html'))).resolve()
    if not path.is_file():
        raise RuntimeError('Documentation has not been built; run python tools/build_docs.py')
    return path
