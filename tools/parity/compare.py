"""Compare computed styles of two lecture builds element by element.

Both builds must contain the same component structure (tools/parity/sample_decks.py).
Elements are matched in document order, so renamed CSS classes are allowed.

    python tools/parity/compare.py out/before out/after [--width 1328 760 420]

Chrome for Testing from the Playwright cache is used automatically; set CHROME
to another Chromium executable if needed. Exit status 1 means differences.
"""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

PROPS = [
    'display', 'position', 'top', 'right', 'bottom', 'left', 'z-index', 'box-sizing',
    'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
    'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
    'border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width',
    'border-top-style', 'border-right-style', 'border-bottom-style', 'border-left-style',
    'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color',
    'border-top-left-radius', 'border-top-right-radius', 'border-bottom-left-radius', 'border-bottom-right-radius',
    'color', 'background-color', 'background-image', 'box-shadow', 'text-shadow', 'opacity', 'transform',
    'font-family', 'font-size', 'font-weight', 'font-style', 'line-height', 'letter-spacing',
    'text-align', 'direction', 'unicode-bidi', 'white-space', 'overflow-x', 'overflow-y', 'overflow-wrap',
    'flex-grow', 'flex-shrink', 'flex-basis', 'flex-direction', 'flex-wrap', 'justify-content', 'align-items',
    'grid-template-columns', 'grid-column-start', 'grid-column-end', 'row-gap', 'column-gap',
    'list-style-type', 'cursor', 'pointer-events', 'isolation', 'content', 'width', 'height', 'max-width', 'min-height',
    'animation-name', 'animation-duration', 'animation-delay', 'transition-duration', 'outline-style',
]

MEASURE = r"""<script>(async () => {
  await document.fonts.ready;
  // Headless Chrome on macOS may never deliver animation frames; use a timer.
  await new Promise(r => setTimeout(r, 200));
  for (const a of document.getAnimations()) {
    const t = a.effect.getComputedTiming();
    if (t.iterations === Infinity) { a.pause(); a.currentTime = 0; }
    else { try { a.finish(); } catch (_) { a.pause(); } }
  }
  const props = __PROPS__;
  const read = (cs) => props.map(p => cs.getPropertyValue(p));
  const out = [];
  for (const el of document.querySelectorAll('.lecture-studio, .lecture-studio *')) {
    if (el.tagName === 'BR') continue;
    const r = el.getBoundingClientRect();
    const own = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim().slice(0, 24);
    const rec = {tag: el.tagName.toLowerCase(), cls: String(el.getAttribute('class') || ''), text: own,
                 rect: [r.x, r.width, r.height].map(Math.round), s: read(getComputedStyle(el))};
    for (const pseudo of ['::before', '::after']) {
      const ps = getComputedStyle(el, pseudo);
      if (ps.content && ps.content !== 'none' && ps.content !== 'normal') rec[pseudo] = read(ps);
    }
    out.push(rec);
  }
  const pre = document.createElement('pre');
  pre.id = 'parity' + '-result';  // split so the marker never matches this source
  pre.textContent = JSON.stringify(out);
  document.documentElement.replaceChildren(pre);
})();</script>""".replace("__PROPS__", json.dumps(PROPS))


def chrome():
    if os.environ.get('CHROME'):
        return os.environ['CHROME']
    cache = Path.home() / 'Library/Caches/ms-playwright'
    found = sorted(cache.glob('chromium-*/chrome-mac*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'))
    found += sorted((Path.home() / '.cache/ms-playwright').glob('chromium-*/chrome-linux*/chrome'))
    if not found:
        raise SystemExit('Set CHROME to a Chromium executable')
    return str(found[-1])


def measure(page, width):
    html = page.read_text(encoding='utf-8')
    html = html.replace('</body>', MEASURE + '</body>')
    with tempfile.TemporaryDirectory() as temp:
        probe = Path(temp) / page.name
        probe.write_text(html, encoding='utf-8')
        result = subprocess.run([chrome(), '--headless', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                                 f'--window-size={width},1200', '--virtual-time-budget=8000', '--dump-dom', probe.as_uri()],
                                capture_output=True, text=True, timeout=120)
    match = re.search(r'<pre id="parity-result">(.*?)</pre>', result.stdout, re.S)
    if not match:
        raise RuntimeError(f'No measurement for {page}: {result.stderr[-400:]}')
    import html as html_lib
    return json.loads(html_lib.unescape(match[1]))


TOKEN_CLASSES = {'keyword', 'string', 'number', 'comment', 'built_in', 'k', 'kc', 'kd', 'kn', 'kp', 'kr', 'kt', 'ow',
                 's', 's1', 's2', 'sa', 'sb', 'sc', 'sd', 'se', 'sh', 'si', 'sx', 'm', 'mf', 'mi', 'mh', 'c', 'c1', 'cm',
                 'ch', 'cp', 'nb', 'bp', 'nf', 'nc', 'nd', 'n', 'o', 'p', 'w', 'na', 'nn', 'nt', 'nv', 'err'}

# Keyframes renamed in 1.0; the animation itself is unchanged.
ANIMATION_ALIASES = {'ls-premium-reveal': 'ls-reveal', 'ls-premium-answer': 'ls-answer-in',
                     'ls-premium-terminal': 'ls-hero-float', 'ls-premium-orbit': 'ls-orbit',
                     'ls-premium-light': 'ls-sheen'}


def normalize(values):
    """Hide differences that cannot be seen (colors of zero-width borders)."""
    style = dict(zip(PROPS, values, strict=True))
    for side in ('top', 'right', 'bottom', 'left'):
        if style[f'border-{side}-width'] == '0px':
            style[f'border-{side}-color'] = style[f'border-{side}-style'] = '-'
    if style['outline-style'] == 'none':
        style['outline-style'] = '-'
    # 'start'/'end' are the logical spelling of left/right for this direction.
    rtl = style['direction'] == 'rtl'
    style['text-align'] = {'start': 'right' if rtl else 'left', 'end': 'left' if rtl else 'right'}.get(
        style['text-align'], style['text-align'])
    style['animation-name'] = ANIMATION_ALIASES.get(style['animation-name'], style['animation-name'])
    return [style[p] for p in PROPS]


def compare(before, after, label, limit):
    problems = Counter()
    examples = {}
    if len(before) != len(after):
        print(f'  {label}: element count {len(before)} -> {len(after)}')
        problems['structure'] += 1
    for i, (a, b) in enumerate(zip(before, after, strict=False)):  # lengths may differ
        if a['tag'] != b['tag']:
            print(f'  {label}: structure diverges at #{i}: <{a["tag"]} {a["cls"]}> {a["text"]!r} vs <{b["tag"]} {b["cls"]}> {b["text"]!r}')
            problems['structure'] += 1
            break
        for part in ('s', '::before', '::after'):
            sa, sb = a.get(part), b.get(part)
            if sa is None and sb is None:
                continue
            if (sa is None) != (sb is None):
                key = (a['cls'], part, 'present')
                problems[key] += 1
                examples.setdefault(key, (b['cls'], sa is not None, sb is not None))
                continue
            for prop, va, vb in zip(PROPS, normalize(sa), normalize(sb), strict=True):
                if va != vb:
                    key = (a['cls'] or a['tag'], part, prop)
                    problems[key] += 1
                    examples.setdefault(key, (b['cls'] or b['tag'], va, vb))
        if a['rect'] != b['rect']:
            key = (a['cls'] or a['tag'], 'rect', '')
            problems[key] += 1
            examples.setdefault(key, (b['cls'] or b['tag'], a['rect'], b['rect']))
    for key, count in problems.most_common(limit):
        if key == 'structure':
            continue
        new_cls, va, vb = examples[key]
        print(f'  {label}: [{count}x] {key[0]!r} -> {new_cls!r} {key[1]} {key[2]}: {va!r} -> {vb!r}')
    return sum(problems.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    parser.add_argument('--width', type=int, nargs='+', default=[1328, 760, 420])
    parser.add_argument('--only', nargs='*', help='scenario names, e.g. gold-rtl')
    parser.add_argument('--limit', type=int, default=40)
    parser.add_argument('--skip-tokens', action='store_true',
                        help='ignore syntax-highlighting spans (when highlighting itself changed)')
    args = parser.parse_args()
    total = 0
    for page in sorted(args.before.glob('*.html')):
        if args.only and page.stem not in args.only:
            continue
        for width in args.width:
            label = f'{page.stem}@{width}'
            before, after = measure(page, width), measure(args.after / page.name, width)
            if args.skip_tokens:
                before, after = ([e for e in items if not (e['tag'] == 'span' and e['cls'] in TOKEN_CLASSES)]
                                 for items in (before, after))
            diff = compare(before, after, label, args.limit)
            print(f'{label}: {"OK" if not diff else str(diff) + " differences"}')
            total += diff
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
