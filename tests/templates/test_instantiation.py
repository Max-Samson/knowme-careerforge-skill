#!/usr/bin/env python3
"""Independent binding regressions; no forge, schema, browser or rendering runner."""
import contextlib
import importlib.util
import io
import json
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts/template/instantiate-resume.py'
spec = importlib.util.spec_from_file_location('instantiate_resume', SCRIPT)
binder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binder)
TEMPLATES = sorted(p.parent.name for p in (ROOT / 'src/templates').glob('*/metadata.json'))


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.tags = []
        self.hidden = 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag in ('style', 'title'):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ('style', 'title'):
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.text.append(data)

    @property
    def visible(self):
        return ''.join(self.text).strip()


class InstantiationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.profile = self.directory / 'profile.json'
        self.output = self.directory / 'resume.html'

    def instantiate(self, template, profile, **kwargs):
        self.profile.write_text(json.dumps(profile), encoding='utf-8')
        binder.instantiate_workspace(template, str(self.profile), output_path=str(self.output), quiet=True, **kwargs)
        return self.output.read_text(encoding='utf-8')

    def test_font_preset_preserves_text_and_rejects_unknown_choices(self):
        value = {'basics': {'name': '测试候选人'}, 'education': [{'institution': '测试学校'}]}
        default = self.instantiate('minimal', value)
        explicit = self.instantiate('minimal', value, font_preset='arial-unicode')
        self.assertEqual(Document(default).visible, Document(explicit).visible)
        before = self.output.read_bytes()
        with self.assertRaises(ValueError):
            binder.instantiate_workspace('minimal', str(self.profile), output_path=str(self.output), font_preset='unknown')
        self.assertEqual(self.output.read_bytes(), before)

    def test_ten_independent_blank_canvases(self):
        self.assertEqual(len(TEMPLATES), 10)
        for template in TEMPLATES:
            with self.subTest(template=template):
                canvas = (ROOT / 'src/templates' / template / 'canvas.html').read_text()
                binder.validate_canvas(canvas)
                self.assertEqual(Document(canvas).visible, '')
                result = self.instantiate(template, {})
                self.assertEqual(Document(result).visible, '')
                self.assertNotIn('<!-- resume:', result)
                self.assertNotIn('<link', result)
                self.assertIn('--primitive-page-width: 210mm', result)

    def test_all_facts_and_all_education_in_every_template(self):
        profile = {
            'basics': {'name': '唯一候选人', 'title': '唯一岗位', 'phone': '电话标记',
                       'email': 'owned@candidate.test', 'location': '唯一地点', 'github': 'github.com/owned', 'summary': '唯一简介'},
            'skills': [{'category': f'分类{i}', 'items': [f'技能{i}']} for i in range(12)],
            'experience': [{'company': '唯一公司', 'role': '唯一职责', 'bullets': [{'text': '唯一工作事实'}]}],
            'projects': [{'name': '唯一项目', 'techStack': ['唯一技术'], 'bullets': [{'text': '唯一项目事实'}]}],
            'education': [{'institution': f'学校{i}', 'degree': f'学位{i}', 'startDate': f'入学{i}', 'endDate': f'毕业{i}', 'summary': f'教育描述{i}'} for i in range(3)]
        }
        expected = ['唯一候选人', '唯一岗位', '电话标记', 'owned@candidate.test', '唯一地点', 'github.com/owned', '唯一简介', '唯一公司', '唯一职责', '唯一工作事实', '唯一项目', '唯一技术', '唯一项目事实']
        expected += [f'{label}{i}' for i in range(3) for label in ('学校', '学位', '入学', '毕业', '教育描述')]
        expected += [f'技能{i}' for i in range(12)]
        for template in TEMPLATES:
            with self.subTest(template=template):
                text = Document(self.instantiate(template, profile)).visible
                for fact in expected:
                    self.assertIn(fact, text)
                self.assertNotIn('优秀毕业生', text)
                self.assertNotIn('统招全日制', text)
                self.assertNotIn('至今', text)

    def test_projects_only_and_sparse_education(self):
        for template in TEMPLATES:
            with self.subTest(template=template):
                html = self.instantiate(template, {'projects': [{'name': 'Only project'}], 'education': [{'institution': 'School A'}, {'institution': 'School B'}]})
                doc = Document(html)
                self.assertIn('Only project', doc.visible)
                self.assertIn('School A', doc.visible)
                self.assertIn('School B', doc.visible)
                self.assertNotIn('experience', [a.get('id') for _, a in doc.tags])
                for invented in ('GPA:', '至今', '优秀毕业生', '统招', ' - ', ' – '):
                    self.assertNotIn(invented, doc.visible)

    def test_escape_every_display_surface_and_keyword_safety(self):
        payload = '<script>alert("x")</script> & \\1 \\g<1> <!-- resume:skills -->'
        profile = {
            'basics': dict.fromkeys(('name', 'title', 'phone', 'email', 'location', 'github', 'summary'), payload),
            'skills': [{'category': payload, 'items': [payload]}],
            'experience': [{'company': payload, 'role': payload, 'summary': payload, 'bullets': [{'text': payload}]}],
            'projects': [{'name': payload, 'role': payload, 'techStack': [payload], 'bullets': [{'text': payload}]}],
            'education': [{'institution': payload, 'degree': payload, 'summary': payload, 'startDate': payload, 'endDate': payload}]
        }
        for template in TEMPLATES:
            with self.subTest(template=template):
                html = self.instantiate(template, profile, keywords='<script>,script,skills,&')
                doc = Document(html)
                self.assertNotIn('script', [t for t, _ in doc.tags])
                self.assertEqual(doc.visible.count(payload), 22)
                self.assertNotIn('<strong><strong>', html)
                self.assertIn('<strong>&lt;script&gt;</strong>', html)

    def test_cli_failures_preserve_output(self):
        cases = ['{', '[]', '{"basics": 2}', '{"education": "bad"}', '{"skills": [{"items": [2]}]}', '{"experience": [{"bullets": [2]}]}']
        for raw in cases + [None]:
            with self.subTest(raw=raw):
                self.output.write_bytes(b'OLD OUTPUT\x00')
                if raw is None:
                    self.profile.unlink(missing_ok=True)
                else:
                    self.profile.write_text(raw)
                result = subprocess.run([sys.executable, str(SCRIPT), '-t', 'minimal', '-p', str(self.profile), '-o', str(self.output)], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stderr, '')
                report = json.loads(result.stdout)
                self.assertEqual(report['status'], 'FAIL')
                self.assertTrue(report['errors'])
                self.assertEqual(report['warnings'], [])
                self.assertFalse(report['checks']['canvasWritten'])
                self.assertEqual(self.output.read_bytes(), b'OLD OUTPUT\x00')

    def test_slot_errors_fail_closed(self):
        canvas = (ROOT / 'src/templates/minimal/canvas.html').read_text()
        for broken in (canvas.replace('<!-- resume:education -->', ''),
                       canvas.replace('<!-- resume:education -->', '<!-- resume:skills -->'),
                       canvas.replace('<!-- resume:education -->', '<!-- resume:unknown -->'),
                       canvas.replace('<!-- resume:education -->', '<div title="<!-- resume:education -->"></div>')):
            with self.subTest(canvas=broken):
                with self.assertRaises(ValueError):
                    binder.render_profile_into_html(broken, {})

    def test_no_preview_fallback_and_atomic_failure(self):
        fake = self.directory / 'repository'
        shutil.copytree(ROOT / 'src/templates', fake / 'src/templates')
        # Contract is shared, so copy it unchanged into the isolated fixture.
        shutil.copytree(ROOT / 'scripts/contracts', fake / 'scripts/contracts')
        shutil.copytree(ROOT / 'src/knowledge', fake / 'src/knowledge')
        for preview in (fake / 'src/templates').glob('*/sample-profile.json'):
            preview.write_text('PREVIEW POISON')
        with patch.object(binder, 'get_project_root', return_value=fake):
            self.assertNotIn('PREVIEW POISON', self.instantiate('minimal', {'basics': {'name': 'Actual'}}))
            self.output.write_text('OLD')
            with patch.object(binder.os, 'replace', side_effect=OSError('simulated publication failure')):
                with self.assertRaises(OSError):
                    self.instantiate('minimal', {})
            self.assertEqual(self.output.read_text(), 'OLD')
            self.assertEqual(list(self.directory.glob('.resume.html.*.tmp')), [])
            (fake / 'src/templates/minimal/canvas.html').unlink()
            with self.assertRaises(FileNotFoundError):
                self.instantiate('minimal', {})
            self.assertEqual(self.output.read_text(), 'OLD')

    def test_nulls_and_shared_contract_fields(self):
        profile = {'basics': {'name': '  ', 'summary': None}, 'skills': None,
                   'experience': None, 'projects': [{'name': 'Demo', 'demoUrl': 'https://demo.test'}],
                   'education': [{'institution': 'A', 'degree': None, 'field': '物理',
                                  'startDate': None, 'endDate': None, 'gpa': None, 'honors': ['奖项A']},
                                 {'institution': 'B', 'honors': None}],
                   'certifications': ['证书A', None]}
        for template in TEMPLATES:
            with self.subTest(template=template):
                text = Document(self.instantiate(template, profile)).visible
                for fact in ('https://demo.test', '物理', '奖项A', '证书A', 'A', 'B'):
                    self.assertIn(fact, text)
                self.assertNotIn('None', text)
                self.assertNotIn('GPA:', text)
                self.assertNotIn('至今', text)

    def test_wrapped_documents_and_bad_hash(self):
        contract = binder.profile_contract()
        for kind in ('draft', 'master', 'variant'):
            wrapped = contract.document(kind, {'basics': {'name': 'Wrapped'}},
                                        {'masterSha256': 'master-reference'})
            for template in TEMPLATES:
                with self.subTest(kind=kind, template=template):
                    self.assertIn('Wrapped', Document(self.instantiate(template, wrapped)).visible)
            self.profile.write_text(json.dumps(wrapped))
            result = subprocess.run([sys.executable, str(SCRIPT), '-t', 'minimal', '-p', str(self.profile), '-o', str(self.output), '--quiet'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'], 'PASS')
        wrapped['profileSha256'] = 'wrong'
        self.output.write_text('OLD')
        with self.assertRaises(ValueError):
            self.instantiate('minimal', wrapped)
        self.assertEqual(self.output.read_text(), 'OLD')

    def test_binding_and_write_errors_preserve_existing_bytes(self):
        self.output.write_bytes(b'previous canvas')
        for failure in ('binding', 'write'):
            with self.subTest(failure=failure):
                target = ('render_profile_into_html' if failure == 'binding' else 'tempfile.NamedTemporaryFile')
                with patch.object(binder, target, side_effect=ValueError('binding failed')) if failure == 'binding' else patch.object(binder.tempfile, 'NamedTemporaryFile', side_effect=OSError('write failed')):
                    with self.assertRaises((ValueError, OSError)):
                        self.instantiate('minimal', {})
                self.assertEqual(self.output.read_bytes(), b'previous canvas')

    def test_highlighting_overlaps_and_html_entities(self):
        html = binder.highlight_keywords('C++ Python Python &lt; <b>', ['Python', 'python', 'Py', 'C++', 'lt', '<b>'])
        self.assertEqual(Document(html).visible, 'C++ Python Python &lt; <b>')
        self.assertEqual(html.count('<strong>Python</strong>'), 2)
        self.assertIn('<strong>C++</strong>', html)
        self.assertNotIn('<b>', html)

    def test_language_drives_all_templates(self):
        for language in ('en', 'en-US', 'EN-gb', 'zh-CN', None):
            for template in TEMPLATES:
                with self.subTest(language=language, template=template):
                    html = self.instantiate(template, {
                        'language': language, 'basics': {'name': 'Actual', 'summary': 'Summary fact'},
                        'skills': [{'items': ['Python']}], 'experience': [{'company': 'Company'}],
                        'projects': [{'name': 'Project'}], 'education': [{'institution': 'School'}],
                        'certifications': ['Certificate']})
                    doc = Document(html)
                    self.assertEqual(dict(next(a.items() for t, a in doc.tags if t == 'html'))['lang'], language or 'zh-CN')
                    labels = binder.LABELS['en' if (language or '').lower().startswith('en') else 'zh']
                    self.assertIn('<title>Actual - ' + labels['document-title'] + '</title>', html)
                    for key, label in labels.items():
                        if key != 'document-title':
                            self.assertIn('>' + label + '</h2>', html)

    def test_cli_json_success_and_failure_with_quiet(self):
        for quiet in ([], ['--quiet']):
            command = [sys.executable, str(SCRIPT), '-t', 'minimal', '-o', str(self.output)] + quiet
            result = subprocess.run(command, capture_output=True, text=True)
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, '')
            self.assertEqual(report['status'], 'PASS')
            self.assertEqual(report['errors'], [])
            self.assertEqual(report['warnings'], [])
            self.assertTrue(report['checks']['canvasWritten'])
            self.assertEqual(Path(report['output']), self.output.resolve())
            old = self.output.read_bytes()
            for extra in (['--unknown'], ['--profile', str(self.directory / 'missing.json')]):
                result = subprocess.run(command + extra, capture_output=True, text=True)
                report = json.loads(result.stdout)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(report['status'], 'FAIL')
                self.assertTrue(report['errors'])
                self.assertFalse(report['checks']['canvasWritten'])
                self.assertEqual(self.output.read_bytes(), old)

    def test_invalid_language_or_language_slot_fails_closed(self):
        self.output.write_text('OLD')
        for language in ('fr', 'en" onclick="alert(1)'):
            with self.assertRaises(ValueError):
                self.instantiate('minimal', {'language': language})
            self.assertEqual(self.output.read_text(), 'OLD')
        canvas = (ROOT / 'src/templates/minimal/canvas.html').read_text()
        with self.assertRaises(ValueError):
            binder.validate_canvas(canvas.replace('{{ resume:language }}', 'zh-CN'))

    def test_quiet_and_omitted_profile(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            binder.instantiate_workspace('minimal', output_path=str(self.output), quiet=True)
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(Document(self.output.read_text()).visible, '')


if __name__ == '__main__':
    unittest.main()
