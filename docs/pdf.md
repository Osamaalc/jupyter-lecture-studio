# Save your lecture as PDF

PDF export is available in the local **0.3.0.dev0** preview. The public PyPI release remains 0.2.0 until the preview is reviewed.

## Setup once

For this unreleased preview, install from the project folder in the same environment as your notebook kernel, then install Chromium:

```bash
python -m pip install ".[pdf]"
python -m playwright install chromium --no-shell
```

After the stable update is published, the registry command will be `python -m pip install --upgrade "jupyter-lecture-studio[pdf]"`. The command `jupyter-lecture-studio setup-pdf` is also available after installing the extra. Export never downloads a browser automatically.

## Save the deck

```python
deck.export_pdf("lecture.pdf")
```

This exports the components collected by that deck. Each component gets a page fitted to its rendered height. The default canvas matches a 1280px lecture plus the original 24px outer margin on either side. Colors, backgrounds, rotations, shadows and typography use the existing screen stylesheet.

## Save the entire notebook

```python
from jupyter_lecture_studio import export_pdf

export_pdf("lecture.ipynb", "complete-lecture.pdf")
```

Run your notebook and **save it first**. The exporter reads saved outputs; it never executes notebook code. It includes Markdown explanations, visible practice code and saved results. Inputs hidden through Jupyter metadata are hidden in PDF. `hide-input`, `remove-input`, `hide-output`, `remove-output` and `remove-cell` tags are respected; `studio-pdf-exclude` excludes a cell. Ordinary practice cells between slides are grouped into pages without cutting a cell in half.

## Fidelity and searchable text

| Mode | Content | Use |
|---|---|---|
| `faithful` (default) | Lossless PNG snapshots placed in PDF pages | Preserve the exact rendered appearance, including effects that PDF print engines may approximate |
| `vector` | Chromium PDF text and graphics | Select/copy/search text and embed the rendered fonts; some compositing effects may differ |

```python
deck.export_pdf("lecture-searchable.pdf", mode="vector")
```

In faithful mode, the font appearance is captured from the bundled **Cairo** and **JetBrains Mono** files; the PDF pages are images, so the text itself is not selectable. The default capture is 2× CSS resolution (192 pixels per inch). `scale=3` or `scale=4` increases raster resolution and file size. A raster PDF does not retain infinitely scalable font outlines.

In vector mode, Chromium embeds the font resources it actually renders. Variable fonts may be embedded as Type 3 glyph outlines with Unicode mappings; other fonts may use embedded font files. Text selection and Arabic extraction depend partly on the PDF reader.

The PDF is static. Entry animations finish; repeating animations are paused at their first frame. The source notebook and its animation settings are unchanged. All collapsible sections are expanded before page measurement and capture, including learning objectives, notebook instructions, concept diagrams and activity answers. Nested sections are expanded too. This affects only the temporary PDF rendering; the notebook and HTML keep their original interactive state. To make a student version without activity solutions:

```python
deck.export_pdf("lecture-student.pdf", include_answers=False)
```

## Options

```python
deck.export_pdf(
    "lecture.pdf",
    width=1328,          # browser canvas width in CSS pixels, including margins
    scale=2,             # faithful raster resolution: 1–4
    mode="faithful",
    include_answers=True,  # default: include activity answers
    title="Python foundations",
    audit_dir="pdf-check",  # optional PNG references and a JSON page manifest
)
```

Each page keeps the canvas width and adapts its height. This is a screen-preserving page format, rather than a fixed A4 layout. PDF viewers can fit pages to the screen; printing to A4 scales the pages. Large content blocks should be split into smaller slides or cells. Horizontal code/table overflow raises an error to prevent silently clipping content.

Network access is disabled during rendering. Fonts are embedded locally even when the original deck selected external fonts. Embed images or provide local files; unavailable images cause a clear error. Math formulas must be prerendered as SVG/images for this offline exporter. Animated GIF/video/JavaScript widgets require a static representation.

An existing destination PDF is replaced only after successful rendering. Export failures preserve the previous file.

## CLI

```bash
jupyter-lecture-studio pdf lecture.ipynb complete-lecture.pdf
jupyter-lecture-studio pdf lecture.json lecture-student.pdf --hide-answers
jupyter-lecture-studio pdf lecture.html lecture.pdf --mode vector
jupyter-lecture-studio pdf lecture.json lecture.pdf --audit-dir pdf-check
```

For CI or an explicitly managed browser runtime, the Python API accepts `browser_path` for a Chromium executable. Normal installations use the browser installed by Playwright.

## العربية — حفظ المحاضرة

ثبت الإضافة مرة واحدة في بيئة Jupyter، ثم نفّذ `python -m playwright install chromium --no-shell`. في نسخة المصدر الحالية استخدم `pip install ".[pdf]"`؛ الإصدار التجريبي لم يُنشر بعد.

- لحفظ الشرائح والبطاقات الموجودة في الكائن: `deck.export_pdf("lecture.pdf")`.
- لحفظ الدفتر كاملًا مع الشرح والتطبيق والنتائج: احفظ الدفتر ثم استدعِ `export_pdf("lecture.ipynb", "lecture.pdf")`.
- جميع الأقسام القابلة للطي والحلول تظهر مفتوحة افتراضيًا، بما فيها أهداف التعلم وطريقة تشغيل الدفتر.
- لإخفاء حلول الأنشطة فقط: `include_answers=False`، أو `--hide-answers` في CLI. الأقسام التعليمية الأخرى تبقى ظاهرة.
- للنص القابل للنسخ والبحث: `mode="vector"`.

الوضع الافتراضي يحفظ لقطات مرئية دون ضغط فقدان، بخطوط Cairo وJetBrains Mono الأصلية. كل شريحة في صفحة تناسب ارتفاع محتواها؛ الأسئلة والتطبيقات الأخرى تُجمع في صفحات متتابعة. لا يُعاد تشغيل الدفتر أثناء التصدير، ولا تظهر أكواد الخلايا المخفية.

الانميشن يصبح حالة ثابتة في PDF. في وضع المطابقة البصرية تكون الصفحات صورًا عالية الدقة، ويظل شكل النص محفوظًا لكن النص غير قابل للتحديد. لا يمكن تعميم تطابق بنسبة 100٪ على كل قارئ PDF أو إعداد طباعة أو ملف عشوائي؛ تقرير الاختبار يحدّد المحتوى والبيئة والقياس الذي تحقق فعليًا.
