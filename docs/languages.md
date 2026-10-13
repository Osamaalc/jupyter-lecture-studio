# Languages

Lecture content is always yours. A *locale* supplies the small interface labels the library adds around it: "Reveal the answer", "Key idea:", "Step", "Output", the default footer and so on.

```python
from jupyter_lecture_studio import LectureDeck

LectureDeck(course="Data Science", locale="en")   # English labels, left-to-right
LectureDeck(course="علم البيانات")                  # Arabic labels, right-to-left (default)
LectureDeck(course="Data Science", direction="ltr")  # same as locale="en"
```

The locale and the direction follow each other unless you set both: `locale="en", direction="rtl"` is allowed.

## Change a few labels

```python
from jupyter_lecture_studio import LectureDeck, get_locale

labels = get_locale("en").with_labels(reveal="Check your prediction", footer="Read → Run → Reflect")
deck = LectureDeck(course="CS 101", locale=labels)
```

Use underscores for keys that contain dots (`callout__tip="Hint"`).

## Add a language

```python
from jupyter_lecture_studio import LectureDeck, register_locale

register_locale("fr", {
    "course": "Atelier", "reveal": "Voir la réponse", "activity": "Prédire avant d'exécuter",
    "reason": "Idée clé :", "quiz": "Vérifiez votre compréhension", "code.output": "Sortie",
}, direction="ltr", base="en")

deck = LectureDeck(course="Programmation", locale="fr")
```

Missing labels fall back to `base`. Arabic-script languages such as Urdu or Persian use `direction="rtl", base="ar"`. Contributions of complete locales are welcome; see `lecture_studio/i18n.py` for every key.

## Arabic typography

- Cairo is bundled for Arabic and Latin text; JetBrains Mono for code, with Cairo as a fallback so Arabic comments inside code stay joined.
- Letter spacing is never applied to Arabic text. Series names, hero labels and lesson labels written in Arabic are detected and rendered without spacing.
- Inline `` `code` `` and terms such as `C++` are isolated so mixed Arabic/English sentences keep their order.
