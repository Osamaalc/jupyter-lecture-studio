# Themes and design tokens

## Built-in themes

| Theme | Palette | Character |
|---|---|---|
| `gold` | original | The reference design: deep navy, warm gold, teal highlights |
| `emerald` | custom | Dark design with a mint accent |
| `ocean` | custom | Dark design with a sky-blue accent |
| `violet` | custom | Dark design with a lavender accent |
| `ruby` | custom | Dark design with a rose accent |
| `paper` | paper | Light design for bright classrooms, projectors and printing |

```python
from jupyter_lecture_studio import LectureDeck

deck = LectureDeck(course="Databases", theme="paper")
deck = LectureDeck(course="AI", theme="gold", accent="#8fd3ff")   # any dark accent
```

Passing `accent` or `background` to `gold` switches it to the custom palette, where every interface accent follows your color. Code blocks stay dark in every theme so syntax colors keep their contrast.

## Theme options

| Option | Default | Meaning |
|---|---|---|
| `preset` / `theme` | `gold` | A registered theme name |
| `accent` | `None` | `#RRGGBB` accent |
| `background` | `None` | `#RRGGBB` background for custom palettes |
| `direction` | from locale | `rtl` or `ltr` |
| `motion` | `True` | Animations and transitions (system reduced-motion is always respected) |
| `max_width` | `1280` | Maximum component width, 320–2400 pixels |
| `notebook_style` | `False` | Also style the surrounding JupyterLab notebook; it follows the light or dark JupyterLab theme |
| `external_fonts` | `False` | Load Cairo and JetBrains Mono from Google Fonts instead of the bundled copies |
| `tokens` | `None` | Override individual design tokens |

## Design tokens

Every color, gradient and font in the stylesheet is a CSS custom property named `--ls-<token>`. Override any of them per deck:

```python
from jupyter_lecture_studio import LectureDeck

deck = LectureDeck(course="Physics", theme="paper", tokens={
    "title": "#0b3954",
    "card-bg": "#ffffff",
    "font": "'IBM Plex Sans Arabic', 'Cairo', sans-serif",
})
```

Frequently used tokens: `text`, `muted`, `title`, `frame-bg`, `frame-border`, `card-bg`, `card-border`, `card-title`, `card-text`, `number-bg`, `eyebrow`, `topline`, `code-bg`, `code-text`, `tok-keyword`, `tok-string`, `tok-number`, `tok-comment`, `tok-builtin`, `good`, `bad`, `note-bg`. The full list is at the top of `lecture_studio/assets/studio.css`. Token names are validated and values cannot close the style attribute.

## A theme for your institution

Register a theme once (for example in a shared course module) and use it by name everywhere:

```python
from jupyter_lecture_studio import LectureDeck, register_theme

register_theme("campus", accent="#2a9df4", background="#0d1726",
               tokens={"frame-border": "#2c4766", "number-text": "#04121f"})

deck = LectureDeck(course="Operating Systems", theme="campus")
```

`palette="paper"` starts from the light design instead of the dark one.

## Direction

Layouts use CSS logical properties, so right-to-left and left-to-right lectures mirror automatically: description rules, card accents, cover cards and diagram notes follow the reading direction. Code, terminal output and variable tables always stay left-to-right.

## Several decks on one page

Themes are variables on each deck's wrapper, not separate stylesheets, so an Arabic gold deck and an English paper deck can share a notebook or a web page without interfering.
