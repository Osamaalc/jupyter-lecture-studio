"""Rebuild portable comparison pages; canonical JSON snapshots stay unchanged.

PYTHONPATH=src python tools/build_design_audit.py --notebook /path/lecture.ipynb
Without --notebook, render the saved snapshots only.
"""
import argparse
import json
from pathlib import Path
import re

from lecture_studio.deck import bundled_fonts

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / 'design-audit'

def build(notebook=None):
    if notebook:
        data = json.loads(Path(notebook).read_text(encoding='utf-8'))
        components = []
        for cell in data['cells']:
            for output in cell.get('outputs', []):
                content = output.get('data', {}).get('text/html', '')
                if isinstance(content, list):
                    content = ''.join(content)
                if any(name in content for name in ('ls-frame', 'luxury-slide-container', 'luxury-cover')):
                    components.append(content)
        if not components:
            raise ValueError('Execute the lecture first; no design outputs were found')
        (AUDIT / 'after-fixed.json').write_text(json.dumps(components, ensure_ascii=False), encoding='utf-8')
    for name in ('before', 'after-extraction', 'after-fixed'):
        components = json.loads((AUDIT / (name + '.json')).read_text(encoding='utf-8'))
        # Resolve the reference typefaces locally for fair, offline comparisons.
        body = re.sub(r'@import\s+url\([^)]*\);', '', ''.join(components))
        page = '<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + name + '</title><style>body{margin:0;background:#e9e9e5}' + bundled_fonts() + '</style></head><body>' + body + '<style>*,*::before,*::after{animation:none!important;transition:none!important;opacity:1!important;transform:none!important}</style></body></html>'
        (AUDIT / (name + '.html')).write_text(page, encoding='utf-8')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--notebook', type=Path)
    build(parser.parse_args().notebook)
