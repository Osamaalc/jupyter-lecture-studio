"""Command line: create a lecture starter, validate and export JSON courses.

Works without Jupyter. ``jupyter-lecture-studio --help`` lists the commands.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from .deck import LectureDeck

_TEXT: dict[str, dict[str, Any]] = {
    'ar': {
        'course': 'اسم المادة', 'title': 'عنوان المحاضرة',
        'lead': 'اكتب الفكرة الرئيسية هنا.\nما الذي سيستطيع الطالب تطبيقه؟',
        'tags': ['افهم', 'جرّب', 'فسّر'], 'sections': [('المفاهيم', 'المحور الأول'), ('التطبيق', 'المحور الثاني')],
        'goals': ['يشرح الفكرة الأساسية بكلماته', 'يكتب مثالاً صغيراً ويتوقع ناتجه'],
        'concept': 'المفهوم الأول', 'concept_text': 'شرح مختصر يربط الفكرة بخبرة الطالب.',
        'idea': 'الفكرة', 'idea_text': 'اكتب شرحك هنا. استخدم `code` للمصطلحات البرمجية.',
        'apply': 'تطبيق', 'apply_text': 'مثال صغير يساعد على الفهم.',
        'journey': 'رحلة الفكرة', 'nodes': [('مفهوم', 'نفهم'), ('تجربة', 'نطبق'), ('نتيجة', 'نفسر')],
        'caption': 'عدّل الرسم لأي مادة.', 'question': 'ماذا يطبع المثال؟', 'answer': 'يطبع Hello؛ اشرح لماذا قبل التنفيذ.',
        'quiz': 'أي سطر يطبع النص Hello؟', 'quiz_explanation': 'النص يجب أن يكون بين علامتي تنصيص.',
        'tip': 'كود البطاقات للعرض فقط؛ ضع التجارب القابلة للتنفيذ في خلايا Jupyter عادية.',
        'recap': ['الفكرة الأساسية في جملة', 'مثال واحد يمكن تذكره'],
        'notebook_title': '# محاضرتك الجديدة\nعدّل lecture.json ثم شغّل الخلية التالية.',
        'export_comment': '# نسخة للطلاب بدون إجابات، ونسخة عرض للمحاضرة',
        'readme': ('# محاضرة جديدة\n\n1. اختر kernel ثبتت فيه jupyter-lecture-studio.\n2. عدّل lecture.json.\n'
                   '3. افتح lecture.ipynb وشغّل الخلايا.\n4. للتصدير: `jupyter-lecture-studio export lecture.json lecture.html`.\n'
                   '5. نسخة الطلاب: أضف `--student`، ونسخة العرض: أضف `--present`.\n\n'
                   'يمكنك إضافة أمثلة قابلة للتنفيذ في خلايا مستقلة. كود البطاقات للعرض فقط.\n'),
    },
    'en': {
        'course': 'Course name', 'title': 'Lecture title',
        'lead': 'Write the main idea here.\nWhat will students be able to do?',
        'tags': ['Understand', 'Try', 'Explain'], 'sections': [('Concepts', 'First part'), ('Practice', 'Second part')],
        'goals': ['Explain the key idea in their own words', 'Write a small example and predict its output'],
        'concept': 'First concept', 'concept_text': 'A short explanation linked to what students already know.',
        'idea': 'The idea', 'idea_text': 'Write your explanation here. Use `code` for programming terms.',
        'apply': 'Apply it', 'apply_text': 'A small example that helps understanding.',
        'journey': 'From idea to result', 'nodes': [('Concept', 'understand'), ('Try', 'apply'), ('Result', 'explain')],
        'caption': 'Adapt the diagram to any subject.', 'question': 'What does the example print?',
        'answer': 'It prints Hello; explain why before running it.',
        'quiz': 'Which line prints the text Hello?', 'quiz_explanation': 'Text must be inside quotes.',
        'tip': 'Card code is for display; put runnable experiments in normal Jupyter cells.',
        'recap': ['The key idea in one sentence', 'One example worth remembering'],
        'notebook_title': '# Your new lecture\nEdit lecture.json, then run the next cell.',
        'export_comment': '# A student copy without answers, and a slideshow for class',
        'readme': ('# New lecture\n\n1. Choose a kernel where jupyter-lecture-studio is installed.\n2. Edit lecture.json.\n'
                   '3. Open lecture.ipynb and run the cells.\n'
                   '4. Export: `jupyter-lecture-studio export lecture.json lecture.html`.\n'
                   '5. Student copy: add `--student`; slideshow: add `--present`.\n\n'
                   'Add runnable examples in separate cells. Card code is for display only.\n'),
    },
}


def starter(course, locale='ar'):
    t = _TEXT[locale]
    return {
        'brand': {'course': course, 'series': 'LEARNING SERIES', 'lesson': '01', 'language': 'python'},
        'theme': {'preset': 'gold', 'motion': True},
        'locale': locale,
        'components': [
            {'type': 'cover', 'title': t['title'], 'description': t['lead'], 'tags': t['tags'],
             'sections': [{'title': a, 'description': b} for a, b in t['sections']]},
            {'type': 'agenda', 'items': t['goals']},
            {'type': 'slide', 'title': t['concept'], 'description': t['concept_text'],
             'cards': [{'title': t['idea'], 'explanation': t['idea_text']},
                       {'title': t['apply'], 'explanation': t['apply_text'], 'code': 'print("Hello")'}],
             'diagram': {'title': t['journey'], 'direction': 'rtl' if locale == 'ar' else 'ltr',
                         'nodes': [{'value': a, 'note': b} for a, b in t['nodes']], 'caption': t['caption']},
             'activity': {'question': t['question'], 'answer': t['answer']}},
            {'type': 'quiz', 'question': t['quiz'], 'options': ['print(Hello)', 'print("Hello")', 'echo Hello'],
             'answer': 1, 'explanation': t['quiz_explanation']},
            {'type': 'callout', 'style': 'tip', 'body': t['tip']},
            {'type': 'agenda', 'mode': 'recap', 'items': t['recap']},
        ],
    }


def create_starter(path, course, locale='ar'):
    if locale not in _TEXT:
        raise ValueError(f'Starter locale must be one of: {", ".join(_TEXT)}')
    t = _TEXT[locale]
    destination = Path(path)
    # Never replace an existing directory or overwrite user work.
    destination.mkdir(parents=True, exist_ok=False)
    data = starter(course, locale)
    (destination / 'lecture.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    cells = [
        {'id': 'welcome', 'cell_type': 'markdown', 'metadata': {}, 'source': t['notebook_title']},
        {'id': 'render', 'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [],
         'source': 'from jupyter_lecture_studio import LectureDeck\n\ndeck = LectureDeck.from_file("lecture.json")'},
        {'id': 'export', 'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [],
         'source': (t['export_comment'] + '\ndeck.export("lecture.html")\n'
                    'deck.export("lecture-student.html", include_answers=False)\n'
                    'deck.export("lecture-slides.html", present=True)')},
    ]
    notebook = {'nbformat': 4, 'nbformat_minor': 5, 'cells': cells,
                'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}}}
    (destination / 'lecture.ipynb').write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding='utf-8')
    (destination / 'README.md').write_text(t['readme'], encoding='utf-8')
    return destination.resolve()


def info():
    from . import __version__, available_locales, component_names, theme_names
    return '\n'.join([
        f'Lecture Studio {__version__}',
        'Components: ' + ', '.join(component_names()),
        'Themes:     ' + ', '.join(theme_names()),
        'Locales:    ' + ', '.join(available_locales()),
    ])


def main(argv=None):
    parser = argparse.ArgumentParser(prog='jupyter-lecture-studio',
                                     description='Bilingual teaching slides, quizzes and code walkthroughs')
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init', help='Create a new lecture folder (never overwrites)')
    init.add_argument('directory')
    init.add_argument('--course', default=None)
    init.add_argument('--locale', choices=sorted(_TEXT), default='ar', help='Starter language (default: ar)')
    export = sub.add_parser('export', help='Export a JSON course to standalone HTML')
    export.add_argument('source')
    export.add_argument('destination')
    export.add_argument('--student', action='store_true', help='Remove answers, quiz keys and solutions')
    export.add_argument('--present', action='store_true', help='Add slideshow mode (arrow keys, F, S)')
    export.add_argument('--fragments', action='store_true', help='With --present: reveal cards one at a time')
    validate = sub.add_parser('validate', help='Check a JSON course without writing files')
    validate.add_argument('source')
    pdf = sub.add_parser('pdf', help='Export saved JSON, HTML or notebook to PDF')
    pdf.add_argument('source')
    pdf.add_argument('destination')
    pdf.add_argument('--mode', choices=['faithful', 'vector'], default='faithful')
    pdf.add_argument('--width', type=int, default=1328)
    pdf.add_argument('--scale', type=int, default=2)
    answers = pdf.add_mutually_exclusive_group()
    answers.add_argument('--include-answers', dest='include_answers', action='store_true', help='Include answers (default)')
    answers.add_argument('--hide-answers', dest='include_answers', action='store_false', help='Hide activity answers only')
    pdf.set_defaults(include_answers=True)
    pdf.add_argument('--audit-dir')
    sub.add_parser('setup-pdf', help='Install Chromium for the optional PDF renderer')
    sub.add_parser('docs', help='Print the path to the bundled offline documentation')
    sub.add_parser('info', help='Show the version, components, themes and locales')
    args = parser.parse_args(argv)
    try:
        if args.command == 'pdf':
            from .pdf import export_pdf
            result = export_pdf(args.source, args.destination, mode=args.mode, width=args.width, scale=args.scale,
                                include_answers=args.include_answers, audit_dir=args.audit_dir)
        elif args.command == 'setup-pdf':
            from .pdf import _dependencies
            _dependencies()
            subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium', '--no-shell'], check=True)
            result = 'Chromium is ready for PDF export'
        elif args.command == 'docs':
            from jupyter_lecture_studio import documentation_path
            result = documentation_path()
        elif args.command == 'info':
            result = info()
        elif args.command == 'init':
            result = create_starter(args.directory, args.course or _TEXT[args.locale]['course'], args.locale)
        elif args.command == 'validate':
            deck = LectureDeck.from_file(args.source, show=False)
            result = f'OK: {len(deck)} components'
        else:
            deck = LectureDeck.from_file(args.source, show=False)
            result = deck.export(args.destination, include_answers=not args.student, present=args.present,
                                 fragments=args.fragments)
    except (OSError, ValueError, TypeError, RuntimeError, KeyError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    print(result)


if __name__ == '__main__':
    main()
