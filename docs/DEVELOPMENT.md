# تطوير المكتبة

الوصف الكامل للبنية وطبقاتها وضماناتها في [architecture.md](architecture.md)، وخطوات المساهمة في `CONTRIBUTING.md`. هذه الصفحة ملخص عربي لها.

## الهيكل

```text
src/lecture_studio/
├── models.py            نماذج المحتوى والتحقق (غير قابلة للتعديل)
├── i18n.py              لغات الواجهة واتجاه الكتابة
├── themes.py            سجل الثيمات ومتغيرات التصميم
├── markup.py            تهريب النص و`code` و**bold** وعزل الاتجاه
├── highlight.py         تلوين الكود (بايثون مدمج + Pygments)
├── components/          سجل المكونات ومُصيّرات HTML لكل مكوّن
├── deck.py              المحاضرة: الترتيب، العرض في Jupyter، JSON، التصدير
├── notebook.py          معرّف الخلية والخطوط المشتركة في الدفتر
├── styles.py            تجميع CSS والخطوط
├── pdf.py / cli.py / compat.py
└── assets/              studio.css، notebook.css، present.css/js، الخطوط
```

## قواعد التصميم

- كل لون في `studio.css` متغير `--ls-*`. الثيم الذهبي هو القيم الافتراضية، و`data-palette="custom"` يشتق الألوان من `--ls-accent`، و`data-palette="paper"` الثيم الفاتح.
- كل محدد يبدأ بـ `.lecture-studio`؛ لا قواعد عامة للصفحة. تنسيق الدفتر المحيط في `notebook.css` فقط وباختيار صريح.
- استخدم الخصائص المنطقية (`inline-start`/`inline-end`) ليعمل التخطيط في الاتجاهين، ولا تضع تباعد أحرف على نص عربي.
- لا JavaScript في مخرجات الدفتر. التفاعل بـ `details` وعناصر النماذج وCSS.

## الاختبار

```bash
python -m pip install -e ".[dev,notebook,highlight]"
pytest && ruff check src tests tools && mypy
```

عند تعديل CSS أو بنية HTML لمكوّن موجود شغّل فحص المطابقة البصرية (`tools/parity`) كما في architecture.md: يقارن الأنماط المحسوبة لكل عنصر بين إصدارين في ثلاثة عروض شاشة. لا تقبل فرقًا غير مقصود في التصميم الذهبي.

## الإصدار

ارفع الرقم في `src/lecture_studio/_version.py`، حدّث `CHANGELOG.md`، ابنِ التوثيق `python tools/build_docs.py` ثم الحزمة `python -m build`، وتحقق بـ `python tools/verify_release.py dist`. النشر من GitHub عبر وسم `vX.Y.Z` و«trusted publishing» دون رموز محفوظة.
