# مرجع الواجهة — 1.0

## LectureDeck

```python
LectureDeck(
    course=None, *, series=None, lesson="", language="python",
    theme="gold", brand=None, locale=None, markup="markdown", **theme_options
)
```

`brand` يقبل `Brand` أو قاموسًا. `theme` يقبل اسم ثيم أو `Theme` أو قاموسًا. `locale` لغة الواجهة: `"ar"` (افتراضي) أو `"en"` أو لغة مسجّلة أو كائن `Locale`. `markup="text"` يوقف تنسيق `` `code` `` و`**bold**`. القيم `None` في الهوية تأخذ نصوص اللغة الافتراضية.

### مكونات العرض

كل الدوال التالية تقبل أيضًا `notes=""` (ملاحظات المحاضر) و`id=None` (استبدال بدل الإضافة) و`show=True`.

| الدالة | المعاملات الأساسية | الاستخدام |
|---|---|---|
| `cover` | `title, description='', *, kicker, tags, sections, hero_code, hero_result, hero_label, footer_label` | غلاف المحاضرة |
| `agenda` | `items, *, title=None, mode='goals'` | أهداف المحاضرة |
| `recap` | `items, *, title=None` | الخلاصة |
| `slide` | `title, description='', *, cards, subtitle, diagram, activity` | شريحة مرقّمة |
| `code` | `code, *, title, output, language, highlight, line_numbers, description, caption` | كود مع ناتجه |
| `trace` | `code, steps, *, title, language, description` | تتبّع التنفيذ |
| `compare` | `title, before, after, *, mode, before_label, after_label, before_note, after_note, description, language` | خطأ شائع وطريقة صحيحة |
| `quiz` | `question, options, answer, *, explanation, code, language, title` | اختيار من متعدد |
| `exercise` | `title, task, *, starter, hints, solution, explanation, language` | تمرين بتلميحات وحل |
| `callout` | `body, *, style='info', title=None` | تنبيه أو فكرة أساسية |
| `figure` | `src, *, caption, alt, title, width` | صورة مضمّنة |
| `divider` | `title, subtitle='', *, label=None` | فاصل بين أجزاء المحاضرة |
| `note` | `title, body=''` | فقرة على خلفية فاتحة |
| `table` | `title, headers, rows` | جدول |

### رسومات المواد

كلها تقبل أيضًا `title, description, caption`. التفاصيل في [صفحة الرسومات](visuals.md).

| الدالة | المعاملات الأساسية | الاستخدام |
|---|---|---|
| `math` | `latex, *, legend` | معادلة أو أكثر بلغة LaTeX |
| `array` | `values, *, name, highlight, pointers, slice, negative` | قائمة بفهارسها ومؤشراتها |
| `matrix` | `rows, *, name, row_labels, col_labels, row_title, col_title, heatmap, highlight, brackets, metrics` | مصفوفة أو خريطة حرارية |
| `confusion_matrix` | `counts, labels` | مصفوفة الالتباس مع الدقة |
| `chart` | `series, *, mode='line', labels, x_label, y_label, y_min, y_max` | رسم بياني |
| `network` | `layers, *, labels` | شبكة عصبية |
| `tree` | `root` | شجرة |
| `graph` | `nodes, edges=(), *, directed=False` | graph بأوزان |
| `memory` | `frames, objects=(), *, stack_label, heap_label` | الذاكرة والمراجع |
| `schema` | `tables, *, per_row=3` | مخطط قاعدة بيانات |

### إدارة المحاضرة

| الدالة | السلوك |
|---|---|
| `add(component, *, id=None, show=True)` | إضافة أي مكوّن مسجّل، ومنها مكونات الإضافات |
| `render(content, *, show=True)` | قاموس مكوّن أو قائمة؛ `type` افتراضيًا `slide` |
| `from_file(path)` / `from_dict(data)` | تحميل محاضرة JSON مع التحقق |
| `to_dict()` / `save(path)` | تحويل المحاضرة إلى JSON |
| `html(*, include_answers=True, notes=False)` | كل المحاضرة كقطعة HTML واحدة |
| `styles()` | عرض الخطوط والأنماط مرة واحدة في الدفتر |
| `export(path, *, title=None, include_answers=True, present=False, notes=None, fragments=False)` | ملف HTML مستقل |
| `export_pdf(path, ...)` | ملف PDF (الإضافة `pdf`) |
| `clear()` | تفريغ المحاضرة |
| `components` / `len(deck)` | النماذج الحالية بالترتيب وعددها |

الدوال تعرض داخل Jupyter وتعيد `None`. مع `show=False` تعيد HTML مستقلًا كسلسلة.

## النماذج

يمكن استخدام النماذج أو قواميس بنفس أسماء الحقول:

```python
Card(title, explanation='', code='', reason='', language=None)
Node(value, note='', selected=False)
Diagram(title, nodes, caption='', direction='ltr', arrows=True, kind='flow')
Activity(question, answer, code='', language=None, label=None, reveal=None)
CoverSection(title, description='')
TraceStep(line, variables={}, output='', note='')
RichText(html)

Brand(course=None, series=None, lesson='', footer=None, language='python')
Theme(preset='gold', accent=None, background=None, motion=True, direction=None,
      max_width=1280, notebook_style=False, external_fonts=False, tokens=None)
```

ولكل مكوّن نموذج: `Cover`, `Slide`, `Note`, `Table`, `Callout`, `Compare`, `CodeExample`, `Quiz`, `Trace`, `Exercise`, `Agenda`, `Figure`, `Divider`. كلها غير قابلة للتعديل وتتحقق من بياناتها عند الإنشاء، ولها `to_dict()`.

الألوان `#RRGGBB`. العرض بين 320 و2400. الثيمات: `gold`, `emerald`, `ocean`, `violet`, `ruby`, `paper` وما تسجله. الحقول غير المعروفة والبيانات غير الصحيحة ترفع `ValueError` أو `TypeError` بدل تجاهلها.

## نقاط التوسيع

| الدالة | الاستخدام |
|---|---|
| `register_component(Model, render)` | إضافة مكوّن جديد (انظر [دليل التوسيع](extending.md)) |
| `register_theme(name, *, accent, background, palette='custom', tokens=None)` | ثيم بهوية الجامعة أو القسم |
| `register_locale(code, labels, *, direction='ltr', base='en')` | لغة واجهة جديدة |
| `get_locale(code).with_labels(...)` | تعديل نصوص محددة |
| `register_highlighter(names, function, *, label=None)` | تلوين لغة برمجة إضافية أو استبدال تلوين مدمج |
| `to_mathml(latex, *, display=True)` | تحويل معادلة LaTeX إلى MathML |
| `component_names()`, `theme_names()`, `available_locales()` | القوائم المتاحة |

## رسومات جاهزة

`diagram_names()` يعيد أسماء رسومات بايثون، و`preset_diagram(name)` يعيد `Diagram` قابلًا للتعديل.

## واجهة التوافق

```python
from jupyter_lecture_studio.compat import LuxurySlideDeck

deck = LuxurySlideDeck()
deck.show({
    'title': 'المفهوم',
    'description': '<p>شرح قديم موثوق</p>',
    'steps_data': [{'title': 'مثال', 'explanation': 'شرح', 'code_snippet': 'print(1)'}],
    'visual': 'names',
    'checkpoint': {'question': 'ماذا يحدث؟', 'answer': 'التفسير'},
})
```

تحافظ على `show`, `steps_data`, `code_snippet`, `visual`, `checkpoint` للمحاضرات القديمة. الواجهة الجديدة هي الخيار المفضل للمحاضرات القادمة.
