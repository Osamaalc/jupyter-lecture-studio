Python API reference
====================

``jupyter_lecture_studio`` and ``lecture_studio`` expose the same objects. Component methods display in Jupyter by default; pass ``show=False`` to receive HTML in scripts.

LectureDeck
-----------

.. autoclass:: lecture_studio.LectureDeck
   :members: cover, agenda, recap, slide, code, trace, compare, quiz, exercise, callout, figure, divider, note, table,
             math, array, matrix, confusion_matrix, chart, network, tree, graph, memory, schema,
             add, render, from_file, from_dict, to_dict, save, html, styles, export, export_pdf, clear,
             components, direction
   :special-members: __init__

Settings
--------

.. autoclass:: lecture_studio.Theme

.. autoclass:: lecture_studio.Brand

.. autoclass:: lecture_studio.RichText

Content models
--------------

.. autoclass:: lecture_studio.Card

.. autoclass:: lecture_studio.CoverSection

.. autoclass:: lecture_studio.Node

.. autoclass:: lecture_studio.Diagram

.. autoclass:: lecture_studio.Activity

.. autoclass:: lecture_studio.TraceStep

Components
----------

.. autoclass:: lecture_studio.Component
   :members: to_dict

.. autoclass:: lecture_studio.Cover
.. autoclass:: lecture_studio.Slide
.. autoclass:: lecture_studio.Note
.. autoclass:: lecture_studio.Table
.. autoclass:: lecture_studio.Callout
.. autoclass:: lecture_studio.Compare
.. autoclass:: lecture_studio.CodeExample
.. autoclass:: lecture_studio.Quiz
.. autoclass:: lecture_studio.Trace
.. autoclass:: lecture_studio.Exercise
.. autoclass:: lecture_studio.Agenda
.. autoclass:: lecture_studio.Figure
.. autoclass:: lecture_studio.Divider

Subject visuals
---------------

.. autoclass:: lecture_studio.Equation
.. autoclass:: lecture_studio.Array
.. autoclass:: lecture_studio.Matrix
.. autoclass:: lecture_studio.Chart
.. autoclass:: lecture_studio.Series
.. autoclass:: lecture_studio.Network
.. autoclass:: lecture_studio.Tree
.. autoclass:: lecture_studio.TreeNode
.. autoclass:: lecture_studio.Graph
.. autoclass:: lecture_studio.GraphNode
.. autoclass:: lecture_studio.GraphEdge
.. autoclass:: lecture_studio.Memory
.. autoclass:: lecture_studio.Frame
.. autoclass:: lecture_studio.HeapObject
.. autoclass:: lecture_studio.Schema
.. autoclass:: lecture_studio.SchemaTable
.. autoclass:: lecture_studio.Column
.. autofunction:: lecture_studio.to_mathml

Extension points
----------------

.. autofunction:: lecture_studio.register_component
.. autofunction:: lecture_studio.get_component
.. autofunction:: lecture_studio.component_names
.. autoclass:: lecture_studio.RenderContext
   :members: line, text, esc, label, code, topline, footer, notes
.. autofunction:: lecture_studio.register_theme
.. autofunction:: lecture_studio.get_theme
.. autofunction:: lecture_studio.theme_names
.. autofunction:: lecture_studio.register_locale
.. autofunction:: lecture_studio.get_locale
.. autofunction:: lecture_studio.available_locales
.. autoclass:: lecture_studio.Locale
   :members: with_labels
.. autofunction:: lecture_studio.register_highlighter
.. autofunction:: lecture_studio.highlighter_names

Helpers
-------

.. autofunction:: lecture_studio.preset_diagram
.. autofunction:: lecture_studio.diagram_names
.. autofunction:: lecture_studio.export_pdf
.. autofunction:: jupyter_lecture_studio.documentation_path
