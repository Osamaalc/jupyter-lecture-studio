# إصدار المكتبة على PyPI

اسم المشروع العام: **jupyter-lecture-studio**. اسم الاستيراد الجديد: `jupyter_lecture_studio`. يجب أن تبقى واجهة `lecture_studio` متاحة للمحاضرات الموجودة.

1. حدّث الإصدار في `pyproject.toml` و`src/lecture_studio/__init__.py` وسجل التغييرات.
2. ثبت أدوات البناء والتوثيق في بيئة مستقلة: `python -m pip install build twine "sphinx>=8,<10" "myst-parser>=4,<6" "furo>=2024"`.
3. ابنِ التوثيق: `python tools/build_docs.py`، ثم نفّذ `PYTHONPATH=src python -m unittest discover -s tests` في بيئة تحتوي IPython وPygments.
4. ابنِ إصدارًا جديدًا في مجلد مستقل: `python -m build --outdir dist/pypi-0.2.0`.
5. افحص ملفات النشر: `python tools/verify_release.py dist/pypi-0.2.0` و`python -m twine check --strict dist/pypi-0.2.0/*`.
6. نفّذ النشر بعد التأكد من رقم الإصدار وملفات الحزمة: `python tools/publish_pypi.py dist/pypi-0.2.0`. أدخل رمز API عندما يطلبه البرنامج؛ الإدخال مخفي. كلمة مرور الحساب ليست رمز نشر.
7. تحقق من صفحة PyPI، ثم جرّب `pip install` في بيئة جديدة من الفهرس العام.

لا تضع رموز API في المشروع أو ملفات JSON أو الدفاتر أو أوامر shell. يتيح البرنامج قراءة ملف مؤقت خارج المشروع عبر `--token-file` بشرط أن تكون صلاحياته `0600`. احذف الملف المؤقت بعد الاستخدام. محتويات `design-audit` و`revision_backup` وتقارير المحاضرة الخاصة مستبعدة من النشر.

لأن اسم المشروع جديد، قد يحتاج النشر الأول إلى رمز على مستوى الحساب. بعد إنشاء المشروع يمكن استخدام رمز خاص بالمشروع للإصدارات اللاحقة. إعداد وسائل المصادقة الثنائية يتم بواسطة صاحب الحساب.
