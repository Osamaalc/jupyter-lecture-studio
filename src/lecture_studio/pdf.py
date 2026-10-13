"""Offline Chromium rendering for faithful snapshots and searchable PDF output.

Optional dependencies are imported only inside the worker. Notebook exports use
saved outputs, never execute notebook code, and respect hidden inputs/outputs.
"""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from io import BytesIO
import json
import os
from pathlib import Path
import tempfile
from typing import Any


@dataclass(frozen=True)
class PDFOptions:
    width: int = 1328
    scale: int = 2
    mode: str = 'faithful'
    include_answers: bool = True
    timeout: int = 60

    def __post_init__(self):
        if isinstance(self.width, bool) or not isinstance(self.width, int) or not 320 <= self.width <= 2448:
            raise ValueError('PDF width must be an integer between 320 and 2448 CSS pixels')
        if isinstance(self.scale, bool) or not isinstance(self.scale, int) or not 1 <= self.scale <= 4:
            raise ValueError('PDF scale must be an integer between 1 and 4')
        if self.mode not in ('faithful', 'vector'):
            raise ValueError('PDF mode must be faithful or vector')
        if not isinstance(self.include_answers, bool):
            raise TypeError('include_answers must be a bool')
        if isinstance(self.timeout, bool) or not isinstance(self.timeout, int) or not 1 <= self.timeout <= 600:
            raise ValueError('PDF timeout must be an integer between 1 and 600 seconds')


def _dependencies():
    try:
        from playwright.sync_api import sync_playwright
        from pypdf import PdfReader, PdfWriter
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfgen.canvas import Canvas
    except ImportError as exc:
        raise RuntimeError('Install jupyter-lecture-studio[pdf], then run python -m playwright install chromium') from exc
    return sync_playwright, Canvas, ImageReader, PdfReader, PdfWriter


def _notebook_html(source, title):
    try:
        from nbconvert import HTMLExporter
        import nbformat
        from traitlets.config import Config
    except ImportError as exc:
        raise RuntimeError('Install jupyter-lecture-studio[pdf] to export notebooks') from exc
    notebook = nbformat.read(source, as_version=4)
    # Work on the parsed copy, preserving the original notebook on disk.
    for cell in notebook.cells:
        tags = list(cell.metadata.get('tags', []))
        state = cell.metadata.get('jupyter', {})
        if state.get('source_hidden') or cell.metadata.get('hide_input'):
            tags.append('studio-pdf-hide-input')
        if state.get('outputs_hidden'):
            tags.append('studio-pdf-hide-output')
        cell.metadata['tags'] = tags
        if cell.cell_type == 'code' and 'lecture-display' in tags and not cell.get('outputs'):
            raise ValueError('Lecture display outputs are missing. Run and save the notebook before exporting PDF.')
    config = Config()
    config.TagRemovePreprocessor.enabled = True
    config.TagRemovePreprocessor.remove_input_tags = {'studio-pdf-hide-input', 'hide-input', 'remove-input'}
    config.TagRemovePreprocessor.remove_all_outputs_tags = {'studio-pdf-hide-output', 'hide-output', 'remove-output'}
    config.TagRemovePreprocessor.remove_cell_tags = {'remove-cell', 'studio-pdf-exclude'}
    config.HTMLExporter.exclude_input_prompt = True
    config.HTMLExporter.exclude_output_prompt = True
    exporter = HTMLExporter(config=config, template_name='lab')
    document, _ = exporter.from_notebook_node(notebook, resources={'metadata': {'name': title}})
    return document


def _prepare_document(source, work, title):
    suffix = source.suffix.lower()
    if suffix == '.ipynb':
        content = _notebook_html(source, title)
    elif suffix == '.json':
        from .deck import LectureDeck
        deck = LectureDeck.from_file(source, show=False)
        content = deck.export(work / 'source.html', title=title).read_text(encoding='utf-8')
    elif suffix in ('.html', '.htm'):
        content = source.read_text(encoding='utf-8')
    else:
        raise ValueError('PDF source must be a lecture .html, .json or saved .ipynb file')
    import html

    from .deck import bundled_fonts
    # Local fonts take precedence even when the HTML opted into remote fonts.
    extra = ('<base href="' + html.escape(source.parent.as_uri() + '/', quote=True) + '">'
             '<style>' + bundled_fonts() + '</style>')
    if '</head>' not in content.lower():
        raise ValueError('PDF export needs a standalone HTML document with a head element')
    import re
    # Keep browser scheduling enabled for our font/animation preparation while
    # blocking author scripts and event handlers before the document is parsed.
    csp = '<meta http-equiv="Content-Security-Policy" content="script-src \'none\'; object-src \'none\'; connect-src \'none\'">'
    content = re.sub(r'(<head\b[^>]*>)', lambda m: m[0] + csp, content, count=1, flags=re.I)
    content = re.sub(r'</head\s*>', lambda _: extra + '</head>', content, count=1, flags=re.I)
    output = work / 'render.html'
    output.write_text(content, encoding='utf-8')
    return output


# This script runs only in the temporary document rendered by our own worker.
_PREPARE = """async (answers) => {
    // PDF has no disclosure interaction: expose every content section first.
    document.querySelectorAll('details').forEach(e => e.open = true);
    document.querySelectorAll('.lesson-check details, details[data-answer]').forEach(e => e.open = answers);
    // Steppers cannot be clicked on paper: lay out every trace step instead.
    document.querySelectorAll('.lecture-studio').forEach(e => e.dataset.static = 'true');
    document.querySelectorAll('.ls-step-input').forEach(e => e.checked = false);
    await document.fonts.load('800 20px "Cairo"', 'أساسيات Python');
    await document.fonts.load('400 16px "JetBrains Mono"', 'print(123)');
    await document.fonts.ready;
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
    for (const animation of document.getAnimations()) {
        const timing = animation.effect.getComputedTiming();
        if (timing.iterations === Infinity) {
            animation.pause();
            animation.currentTime = 0;
        } else {
            try { animation.finish(); } catch (_) { animation.pause(); }
        }
    }
    await new Promise(r => requestAnimationFrame(r));
    const failed = [...document.images].filter(e => !e.complete || !e.naturalWidth);
    if (failed.length) throw new Error('An image is unavailable offline. Embed images or provide local files.');
    const overflow = [...document.querySelectorAll('.luxury-code pre,.studio-table,.ls-code pre,.ls-table,.jp-InputArea-editor pre,.jp-OutputArea-output pre')]
        .filter(e => e.clientWidth > 0 && e.scrollWidth > e.clientWidth + 2);
    if (overflow.length) throw new Error('Content has horizontal overflow. Increase PDF width or split long code/table rows before export.');
    if (document.querySelector('.math')) throw new Error('Offline PDF needs math formulas prerendered as SVG or images.');
    const fontState = [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family);
    if (!fontState.some(f => f.includes('Cairo')) || !fontState.some(f => f.includes('JetBrains Mono')))
        throw new Error('The bundled lecture fonts did not load.');
    const disclosures = [...document.querySelectorAll('details')];
    return {fonts: [...new Set(fontState)], animations: document.getAnimations().length,
        disclosures: {total:disclosures.length, open:disclosures.filter(e => e.open).length,
            closed:disclosures.filter(e => !e.open).map(e => e.querySelector('summary')?.innerText || '')}};
}"""

_REGIONS = """() => {
    const notebook = document.querySelector('.jp-Notebook');
    const candidates = notebook ? [...notebook.querySelectorAll('.jp-Cell')]
        : [...document.querySelectorAll('.lecture-studio > section')];
    const visible = candidates.filter(e => e.getBoundingClientRect().height > 0 &&
        (e.innerText.trim() || e.querySelector('img,svg,canvas')));
    // Short remarks (callouts) share the page of the content before them.
    const attach = e => e.classList.contains('ls-callout');
    const expanded = visible.flatMap(e => {
        if (!notebook) return [{element:e,major:true,attach:attach(e)}];
        const sections=[...e.querySelectorAll('.lecture-studio > section')];
        return sections.length ? sections.map((section,i) => ({element:section,major:true,attach:attach(section),
            first:i===0?e:null,last:i===sections.length-1?e:null})) : [{element:e,major:false}];
    });
    const items = expanded.map(({element:e,major,attach,first,last}) => {
        const b = e.getBoundingClientRect();
        return {top:(first?first.getBoundingClientRect().top:b.top)+scrollY,
            bottom:(last?last.getBoundingClientRect().bottom:b.bottom)+scrollY,major,attach,
            cover:e.classList.contains('ls-cover'),
            // A short notebook heading belongs to the page of what follows it.
            keep:!major && e.classList.contains('jp-MarkdownCell') && !!e.querySelector('h1,h2,h3') && b.height < 170,
            title:(e.querySelector('h1,h2,h3,.ls-question')?.innerText || '').trim()};
    });
    for (let i = items.length - 2; i >= 0; i--) {
        if (items[i].keep) {
            items[i + 1].top = items[i].top;
            items[i + 1].title = items[i].title || items[i + 1].title;
            items.splice(i, 1);
        }
    }
    const total = Math.ceil(document.documentElement.scrollHeight);
    const groups=[];
    let group=null;
    for (const item of items) {
        if (item.attach && group && item.bottom-group.top <= 2000) {group.bottom=item.bottom; continue;}
        // Practice cells join the page before them when it has room (never a cover).
        const room = group && !group.cover && item.bottom-group.top <= (group.major ? 1300 : 1050);
        if (item.major || !room) {
            group={...item}; groups.push(group);
        } else {group.bottom=item.bottom; if(!group.title) group.title=item.title;}
    }
    if (!groups.length) throw new Error('No visible lecture content was found.');
    let start=0, section='';
    return groups.map((g,i) => {
        const end=i+1===groups.length ? total : Math.floor((g.bottom+groups[i+1].top)/2);
        // Untitled pages (practice code) are bookmarked under the section before them.
        section = g.title || section;
        const region={y:start,height:end-start,title:g.title || section || `Page ${i+1}`};
        start=end;return region;
    });
}"""


def _render(source, destination, options, title, audit_dir, browser_path):
    sync_playwright, Canvas, ImageReader, PdfReader, PdfWriter = _dependencies()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='lecture-studio-pdf-') as temp:
        work = Path(temp)
        document = _prepare_document(source, work, title)
        if audit_dir is not None:
            audit_dir.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as playwright:
            launch = {'headless': True, 'timeout': options.timeout * 1000}
            if browser_path is not None:
                launch['executable_path'] = str(browser_path)
            else:
                # Use Chromium's modern headless renderer; the separate legacy
                # headless-shell download is unnecessary for this exporter.
                launch['channel'] = 'chromium'
            try:
                browser = playwright.chromium.launch(**launch)
            except Exception as exc:
                raise RuntimeError('Chromium could not start. Run python -m playwright install chromium. ' + str(exc).splitlines()[0]) from exc
            try:
                context = browser.new_context(viewport={'width': options.width, 'height': 900},
                    device_scale_factor=options.scale, offline=True, java_script_enabled=True)
                page = context.new_page()
                page.set_default_timeout(options.timeout * 1000)
                page.goto(document.as_uri(), wait_until='load')
                page.emulate_media(media='screen', color_scheme='light')
                state = page.evaluate('''async (settings) => {
                    let timer;
                    try {
                        return await Promise.race([
                            (''' + _PREPARE + ''')(settings.answers),
                            new Promise((_,reject) => {timer=setTimeout(() => reject(new Error('PDF preparation timed out')),settings.timeout);})
                        ]);
                    } finally {clearTimeout(timer);}
                }''', {'answers':options.include_answers, 'timeout':options.timeout * 1000})
                regions = page.evaluate(_REGIONS)
                if options.mode == 'vector':
                    # PDF viewers flatten blurred shadows inconsistently (grey
                    # boxes in macOS Preview); shadows never move layout.
                    page.add_style_tag(content='.lecture-studio,.lecture-studio *,.lecture-studio *::before,'
                                               '.lecture-studio *::after{box-shadow:none!important;text-shadow:none!important}')
                if any(r['height'] <= 0 or r['height'] * options.scale > 30000 for r in regions):
                    raise ValueError('A PDF page is empty or too tall. Split the content into smaller slides/cells.')
                result = work / 'result.pdf'
                canvas = Canvas(str(result), pageCompression=1) if options.mode == 'faithful' else None
                writer: Any = PdfWriter() if options.mode == 'vector' else None
                if canvas:
                    canvas.setTitle(title)
                    canvas.setSubject('Lecture Studio — faithful screen snapshots')
                for i, region in enumerate(regions, 1):
                    image = page.screenshot(type='png', clip={'x': 0, 'y': region['y'], 'width': options.width, 'height': region['height']},
                        full_page=True, animations='allow', caret='hide', timeout=options.timeout * 1000)
                    if audit_dir is not None:
                        (audit_dir / f'page-{i:03d}.png').write_bytes(image)
                    width_pt, height_pt = options.width * .75, region['height'] * .75
                    if canvas:
                        canvas.setPageSize((width_pt, height_pt))
                        canvas.drawImage(ImageReader(BytesIO(image)), 0, 0, width_pt, height_pt)
                        canvas.bookmarkPage(f'page-{i}')
                        canvas.addOutlineEntry(region['title'][:120], f'page-{i}')
                        canvas.showPage()
                    else:
                        # Keep screen CSS and static transforms; do not use the
                        # existing print stylesheet, which changes the design.
                        # A fixed body is never split into print pages, so
                        # content near a page boundary keeps its screen position.
                        page.evaluate('(y) => {Object.assign(document.body.style,{position:"fixed",left:"0",right:"0",top:`-${y}px`,height:"auto",minHeight:"0",overflow:"visible"});}', region['y'])
                        try:
                            buffer = page.pdf(width=f'{options.width}px', height=f"{region['height']}px", page_ranges='1',
                                margin={'top':'0','bottom':'0','left':'0','right':'0'}, print_background=True,
                                display_header_footer=False, tagged=True)
                        finally:
                            page.evaluate('() => {Object.assign(document.body.style,{position:"",left:"",right:"",top:"",height:"",minHeight:"",overflow:""});}')
                        rendered = PdfReader(BytesIO(buffer))
                        writer.add_page(rendered.pages[0])
                        writer.add_outline_item(region['title'][:120], i-1)
                if canvas:
                    canvas.save()
                else:
                    writer.add_metadata({'/Title': title, '/Subject': 'Lecture Studio — searchable screen PDF'})
                    with result.open('wb') as handle:
                        writer.write(handle)
                if audit_dir is not None:
                    manifest = {'mode': options.mode, 'width': options.width, 'scale': options.scale,
                        'include_answers': options.include_answers, 'browser': browser.version, 'fonts': state['fonts'],
                        'disclosures':state['disclosures'], 'pages': regions}
                    (audit_dir / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
                # A failure must not replace an existing lecture PDF.
                with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.pdf', delete=False) as output:
                    pending = Path(output.name)
                    try:
                        output.write(result.read_bytes())
                    except BaseException:
                        pending.unlink(missing_ok=True)
                        raise
                try:
                    os.replace(pending, destination)
                finally:
                    pending.unlink(missing_ok=True)
            finally:
                browser.close()
    return destination.resolve()


def export_pdf(source, destination, *, width=1328, scale=2, mode='faithful', include_answers=True,
               title=None, timeout=60, audit_dir=None, browser_path=None):
    """Export saved HTML/JSON/notebook content without executing notebook code.

    ``faithful`` embeds lossless high-resolution screen images; text is not
    selectable. ``vector`` preserves selectable text and embedded fonts, with
    possible differences in effects rendered by Chromium's PDF engine;
    lecture shadows are omitted because PDF viewers flatten them unevenly.
    Each slide gets its own fitted page. Notebook practice cells are grouped.
    Collapsible sections and answers are expanded by default. Set
    ``include_answers=False`` to hide activity answers only.
    Fonts are local; external network access is disabled. Browser installation
    is explicit. ``audit_dir`` optionally saves PNG references and dimensions.
    """
    options = PDFOptions(width, scale, mode, include_answers, timeout)
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if destination.suffix.lower() != '.pdf':
        raise ValueError('PDF destination must end in .pdf')
    # Playwright's sync API cannot run in the notebook's asyncio loop. An
    # isolated worker thread supports both Jupyter and ordinary Python scripts.
    with ThreadPoolExecutor(max_workers=1) as worker:
        try:
            return worker.submit(_render, source, destination, options, title or source.stem,
                Path(audit_dir).resolve() if audit_dir is not None else None, browser_path).result()
        except (ValueError, TypeError, OSError, RuntimeError):
            raise
        except Exception as exc:
            raise RuntimeError(str(exc).splitlines()[0]) from exc


def export_deck_pdf(deck, destination, **options):
    """Render the deck collection without changing its theme or component state."""
    if not len(deck):
        raise ValueError('Add lecture components before exporting PDF')
    options.setdefault('width', deck.theme.max_width + 48)
    options.setdefault('title', deck.brand.course)
    with tempfile.TemporaryDirectory(prefix='lecture-studio-deck-') as temp:
        source = deck.export(Path(temp) / 'lecture.html', title=options['title'])
        return export_pdf(source, destination, **options)
