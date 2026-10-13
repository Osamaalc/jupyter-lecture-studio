"""Migration bridge for existing LuxurySlideDeck notebooks."""
import html
import re

from .deck import LectureDeck
from .models import Brand, Card, RichText


def legacy_rich(value):
    for token in ("start:stop:step", ":.2f"):
        value = value.replace(token, "<code>" + html.escape(token) + "</code>")
    value = re.sub(r'\\text{(.*?)}', lambda m: '<span>' + html.escape(m[1].replace(r'\_', '_')) + '</span>', value)
    return RichText(value)


class LuxurySlideDeck(LectureDeck):
    """Keeps show(), steps_data and code_snippet working for old lectures."""
    def __init__(self, max_width_px=1280, width_vw=100, **kwargs):
        # width_vw was unused in the original renderer; retain the argument only.
        kwargs.setdefault('brand', Brand('أساسيات بايثون · مختبر المفاهيم', 'PYTHON / FOUNDATIONS', 'LESSON 01—02'))
        kwargs.setdefault('notebook_style', True)
        super().__init__(max_width=max_width_px, **kwargs)
        self.width_vw = width_vw

    def show(self, content):
        values = [content] if 'title' in content else content.values()
        for raw in values:
            data = dict(raw)
            data['cards'] = [
                Card(re.sub(r'^\d+\.\s*', '', item.get('title', '')), legacy_rich(item.get('explanation', '')),
                     item.get('code_snippet', ''), legacy_rich(item.get('reason', '')))
                for item in data.pop('steps_data', [])
            ]
            data['title'] = re.sub(r'[✨🐍🔄🧮🎨🚦📜🛠️]', '', data['title']).strip()
            data['description'] = RichText(data.get('description', '').replace('C++', '<bdi dir="ltr">C++</bdi>'))
            data['diagram'] = data.pop('visual', None)
            data['activity'] = data.pop('checkpoint', None)
            self.slide(**data)
        return None
