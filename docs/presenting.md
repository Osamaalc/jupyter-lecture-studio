# Teaching, sharing and presenting

## In Jupyter

Each component displays under its cell. Re-running a cell **replaces** what that cell added: slide numbers stay correct and exports never contain duplicates. To replace a component from anywhere, give it an `id`:

```python
deck.slide("Introduction", id="intro")   # running this again replaces the same slide
```

The embedded fonts (about 200 KB) are sent with the first lecture output only, and again when that cell is re-run; later outputs are about 50 KB. If you clear that first output, call `deck.styles()` once to restore the fonts. Hosts that do not report cell ids (for example `nbconvert --execute`) receive the fonts with every output, which is always safe.

## One lecture, three files

```python
deck.export("lecture.html")                              # teacher copy with answers
deck.export("lecture-student.html", include_answers=False)  # no answers, quiz keys or solutions
deck.export("lecture-slides.html", present=True)            # slideshow with speaker notes
```

All exports are single offline HTML files with embedded fonts and styles. Only presentation exports contain a small script.

## Presentation mode

Open the `present=True` export in a browser:

| Key | Action |
|---|---|
| → / ← (mirrored in Arabic), Space, Page Down | Next / previous |
| Home / End | First / last component |
| F | Fullscreen |
| S | Speaker notes for the current slide |

Each component is scaled to fit the screen; very tall slides fit the width and scroll. The address bar keeps the slide number (`#7`), so a refresh returns to the same place. `fragments=True` reveals cards, agenda items and quiz options one at a time.

Speaker notes come from the `notes=` argument of any component. They are omitted from normal exports unless you pass `notes=True`.

## PDF

See [PDF export](pdf.md): `deck.export_pdf("lecture.pdf")`, or `include_answers=False` for a student handout.

## JSON courses

Keep content in JSON and render it anywhere:

```python
from jupyter_lecture_studio import LectureDeck

deck.save("lecture.json")                     # any deck → JSON
deck = LectureDeck.from_file("lecture.json")  # JSON → deck (validated)
```

```bash
jupyter-lecture-studio validate lecture.json
jupyter-lecture-studio export lecture.json lecture.html --student
```
