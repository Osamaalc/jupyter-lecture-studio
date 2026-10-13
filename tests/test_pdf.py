import asyncio
from contextlib import redirect_stdout
import importlib.util
from io import BytesIO, StringIO
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lecture_studio import LectureDeck, export_pdf
from lecture_studio.pdf import PDFOptions, _notebook_html


class PDFValidationTests(unittest.TestCase):
    def test_invalid_settings_fail_before_rendering(self):
        for settings in [{'width': True}, {'width': 100}, {'scale': 0}, {'mode': 'print'},
                         {'scale': 1.5}, {'include_answers': 1}, {'timeout': 0}]:
            with self.subTest(settings=settings), self.assertRaises((TypeError, ValueError)):
                PDFOptions(**settings)

    def test_empty_deck_does_not_create_pdf(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / 'lesson.pdf'
            with self.assertRaises(ValueError):
                LectureDeck().export_pdf(destination)
            self.assertFalse(destination.exists())

    def test_missing_extra_is_actionable(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'lecture.html'
            source.write_text('<html><head></head><body></body></html>')
            with patch('lecture_studio.pdf._dependencies', side_effect=RuntimeError('Install jupyter-lecture-studio[pdf]')):
                with self.assertRaisesRegex(RuntimeError, r'\[pdf\]'):
                    export_pdf(source, Path(temp) / 'lecture.pdf')

    def test_destination_extension_is_validated(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'lecture.html';source.write_text('content')
            with self.assertRaisesRegex(ValueError, 'end in .pdf'):
                export_pdf(source, Path(temp) / 'lecture.html')
            self.assertEqual(source.read_text(), 'content')

    def test_cli_expands_answers_by_default_and_supports_hiding(self):
        from lecture_studio.cli import main
        for flags,expected in [([],True),(['--include-answers'],True),(['--hide-answers'],False)]:
            with self.subTest(flags=flags), patch('lecture_studio.pdf.export_pdf',return_value=Path('lecture.pdf')) as render:
                with redirect_stdout(StringIO()):
                    main(['pdf','lecture.html','lecture.pdf',*flags])
                self.assertEqual(render.call_args.kwargs['include_answers'],expected)


PDF_AVAILABLE = all(importlib.util.find_spec(name) for name in ['playwright','reportlab','pypdf','nbconvert'])

@unittest.skipUnless(PDF_AVAILABLE, 'PDF integration needs the optional pdf extra and Chromium')
class PDFIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.browser = os.environ.get('LECTURE_STUDIO_TEST_BROWSER')

    def tearDown(self):
        self.temp.cleanup()

    def deck(self):
        deck = LectureDeck(course='أساسيات بايثون', notebook_style=True)
        deck.cover('الاسم والقيمة', 'شرح عربي\nمع سطر ثانٍ.', hero_code='>>> value = 10', hero_result='10', show=False)
        deck.slide('التطبيق', cards=[{'title':'Predict','code':'print(123)'}], diagram='names',
            activity={'question':'توقّع النتيجة','answer':'SECRET ANSWER 123'}, show=False)
        deck.table('مقارنة', ['A','B'], [['Python','C++']], show=False)
        return deck

    def test_faithful_pixels_dimensions_and_deck_state(self):
        from PIL import Image
        from pypdf import PdfReader
        deck=self.deck();before=list(deck._components);theme=deck.theme
        result=deck.export_pdf(self.root/'lecture.pdf',audit_dir=self.root/'audit',browser_path=self.browser)
        reader=PdfReader(result)
        manifest=json.loads((self.root/'audit/manifest.json').read_text())
        self.assertEqual(len(reader.pages),3)
        self.assertIs(deck.theme,theme);self.assertEqual(deck._components,before)
        self.assertTrue(manifest['include_answers'])
        self.assertFalse(manifest['disclosures']['closed'])
        for i,page in enumerate(reader.pages,1):
            image=Image.open(BytesIO(list(page.images)[0].data)).convert('RGB')
            reference=Image.open(self.root/f'audit/page-{i:03d}.png').convert('RGB')
            self.assertEqual(image.size,reference.size)
            self.assertEqual(image.tobytes(),reference.tobytes())
            self.assertAlmostEqual(float(page.mediabox.width),1328*.75,places=2)
        self.assertTrue(any('Cairo' in f for f in manifest['fonts']))
        self.assertTrue(any('JetBrains Mono' in f for f in manifest['fonts']))

    def test_vector_text_fonts_and_answers(self):
        from pypdf import PdfReader
        result=self.deck().export_pdf(self.root/'vector.pdf',mode='vector',browser_path=self.browser)
        pages=PdfReader(result).pages
        self.assertEqual(len(pages),3)
        self.assertIn('SECRET ANSWER 123',''.join(page.extract_text() for page in pages))
        fonts=[]
        for page in pages:
            for font in page['/Resources'].get('/Font',{}).get_object().values():
                font=font.get_object()
                descriptor=font['/FontDescriptor'].get_object() if '/FontDescriptor' in font else {}
                fonts.append(str(font.get('/BaseFont') or descriptor.get('/FontName')))
                if font['/Subtype']=='/Type3':
                    self.assertTrue(font['/CharProcs'].get_object())
                    self.assertIn('/ToUnicode',font)
                else:
                    descendants=font.get('/DescendantFonts',[font])
                    for descendant in descendants:
                        embedded=descendant.get_object()['/FontDescriptor'].get_object()
                        self.assertTrue(any(key in embedded for key in ['/FontFile','/FontFile2','/FontFile3']))
        self.assertTrue(any('Cairo' in f for f in fonts),fonts)
        self.assertTrue(any('JetBrainsMono' in f for f in fonts),fonts)

    def test_notebook_saved_outputs_hidden_input_and_no_execution(self):
        import nbformat
        from pypdf import PdfReader
        deck=self.deck()
        cell=nbformat.v4.new_code_cell('raise RuntimeError("MUST NEVER EXECUTE")',metadata={'jupyter':{'source_hidden':True},'tags':['lecture-display']},
            outputs=[nbformat.v4.new_output('display_data',data={'text/html':deck.html()})])
        notebook=nbformat.v4.new_notebook(cells=[cell,nbformat.v4.new_markdown_cell('### Practice\nKeep this explanation.'),
            nbformat.v4.new_code_cell('print(123)',outputs=[nbformat.v4.new_output('stream',name='stdout',text='123\n')])])
        source=self.root/'lecture.ipynb';nbformat.write(notebook,source);before=source.read_bytes()
        html=_notebook_html(source,'Saved lecture')
        self.assertNotIn('MUST NEVER EXECUTE',html)
        self.assertIn('Keep this explanation',html)
        result=export_pdf(source,self.root/'notebook.pdf',browser_path=self.browser)
        self.assertEqual(len(PdfReader(result).pages),3)  # the short practice heading and cell share the table page
        self.assertEqual(source.read_bytes(),before)

    def test_missing_notebook_outputs_preserves_existing_destination(self):
        import nbformat
        source=self.root/'missing.ipynb'
        nbformat.write(nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell('print(1)',metadata={'tags':['lecture-display']})]),source)
        destination=self.root/'lecture.pdf';destination.write_bytes(b'KEEP EXISTING PDF')
        with self.assertRaisesRegex(ValueError,'outputs are missing'):
            export_pdf(source,destination,browser_path=self.browser)
        self.assertEqual(destination.read_bytes(),b'KEEP EXISTING PDF')

    def test_notebook_asyncio_loop_and_repeatable_snapshot(self):
        from pypdf import PdfReader
        async def render():
            return self.deck().export_pdf(self.root/'async.pdf',browser_path=self.browser)
        result=asyncio.run(render())
        self.assertEqual(len(PdfReader(result).pages),3)

    def test_overflow_fails_without_replacing_existing_pdf(self):
        deck=LectureDeck();deck.slide('Overflow',cards=[{'title':'Long line','code':'x'*1000}],show=False)
        target=self.root/'existing.pdf';target.write_bytes(b'KEEP')
        with self.assertRaisesRegex(RuntimeError,'horizontal overflow'):
            deck.export_pdf(target,browser_path=self.browser)
        self.assertEqual(target.read_bytes(),b'KEEP')

    def test_student_answers_are_hidden_in_searchable_pdf(self):
        from pypdf import PdfReader
        result=self.deck().export_pdf(self.root/'student.pdf',mode='vector',include_answers=False,browser_path=self.browser)
        self.assertNotIn('SECRET ANSWER', ''.join(p.extract_text() for p in PdfReader(result).pages))

    def test_notebook_markdown_disclosures_and_nested_sections_are_expanded(self):
        import nbformat
        from pypdf import PdfReader
        cell=nbformat.v4.new_markdown_cell('''### Practice
<details><summary>أهداف التعلم وطريقة تشغيل الدفتر</summary>
<p>LEARNING OUTCOMES CONTENT</p>
<details><summary>تشغيل الدفتر</summary><p>NESTED NOTEBOOK INSTRUCTIONS</p></details>
</details>''')
        source=self.root/'folded.ipynb'
        nbformat.write(nbformat.v4.new_notebook(cells=[cell]),source)
        result=export_pdf(source,self.root/'expanded.pdf',mode='vector',audit_dir=self.root/'expanded-audit',browser_path=self.browser)
        content=''.join(p.extract_text() for p in PdfReader(result).pages)
        self.assertIn('LEARNING OUTCOMES CONTENT',content)
        self.assertIn('NESTED NOTEBOOK INSTRUCTIONS',content)
        manifest=json.loads((self.root/'expanded-audit/manifest.json').read_text())
        self.assertEqual(manifest['disclosures'],{'total':2,'open':2,'closed':[]})

    def test_html_scripts_are_not_executed(self):
        from pypdf import PdfReader
        source=self.deck().export(self.root/'source.html')
        html=source.read_text().replace('</head>', '<script>document.addEventListener("DOMContentLoaded",()=>document.querySelectorAll("section").forEach(e=>e.remove()))</script></head>')
        source.write_text(html)
        result=export_pdf(source,self.root/'script.pdf',browser_path=self.browser)
        self.assertEqual(len(PdfReader(result).pages),3)

    def test_teaching_components_are_static_on_paper(self):
        from pypdf import PdfReader
        deck=LectureDeck(course='CS 101',locale='en',theme='paper')
        deck.trace('total = 0\nfor x in [4, 5]:\n    total += x',[{'line':1,'variables':{'total':0}},
            {'line':3,'variables':{'total':'STEP-A'}},{'line':3,'variables':{'total':'STEP-B'}}],title='Trace',show=False)
        deck.callout('Short remark that shares the page.',style='tip',show=False)
        deck.quiz('Pick one',['a','b'],1,explanation='QUIZ-KEY',show=False)
        deck.exercise('Task','Do it.',hints=['HINT-TEXT'],solution='print("SOLUTION-CODE")',show=False)
        audit=self.root/'teaching-audit'
        result=deck.export_pdf(self.root/'teaching.pdf',mode='vector',audit_dir=audit,browser_path=self.browser)
        pages=PdfReader(result).pages
        self.assertEqual(len(pages),3)  # the callout joins the trace page
        content=''.join(page.extract_text() for page in pages)
        for expected in ['STEP-A','STEP-B','HINT-TEXT','QUIZ-KEY','SOLUTION-CODE','Short remark']:
            self.assertIn(expected,content)
        self.assertEqual(json.loads((audit/'manifest.json').read_text())['pages'][1]['title'],'Pick one')
        student=deck.export_pdf(self.root/'student.pdf',mode='vector',include_answers=False,browser_path=self.browser)
        content=''.join(page.extract_text() for page in PdfReader(student).pages)
        self.assertIn('HINT-TEXT',content)
        for secret in ['QUIZ-KEY','SOLUTION-CODE']:
            self.assertNotIn(secret,content)

    def test_formulas_and_svg_visuals_export_as_text(self):
        from pypdf import PdfReader
        deck=LectureDeck(course='ML',locale='en',theme='paper')
        deck.math(r'\hat{y} = \operatorname{softmax}(Wx + b)',title='Softmax',show=False)
        deck.chart({'loss':[0.9,0.5,0.3]},x_label='EPOCH-AXIS',show=False)
        deck.schema({'students':['id PK'],'grades':['student_id FK -> students.id']},show=False)
        result=deck.export_pdf(self.root/'visuals.pdf',mode='vector',browser_path=self.browser)
        pages=PdfReader(result).pages
        self.assertEqual(len(pages),3)
        content=''.join(page.extract_text() for page in pages)
        for expected in ['softmax','EPOCH-AXIS','students','grades']:
            self.assertIn(expected,content)

    def test_unavailable_image_preserves_existing_pdf(self):
        source=self.deck().export(self.root/'source.html')
        source.write_text(source.read_text().replace('</body>','<img src="missing-image.png"></body>'))
        target=self.root/'existing.pdf';target.write_bytes(b'KEEP')
        with self.assertRaisesRegex(RuntimeError,'image is unavailable offline'):
            export_pdf(source,target,browser_path=self.browser)
        self.assertEqual(target.read_bytes(),b'KEEP')

if __name__ == '__main__':
    unittest.main()
