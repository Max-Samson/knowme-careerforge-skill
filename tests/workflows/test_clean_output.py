"""Delivery purity is a filesystem contract, not a short-response convention."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
FORGE = ROOT / 'scripts/pipeline/forge.py'
spec = importlib.util.spec_from_file_location('clean_output_forge', FORGE)
forge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(forge)


def profile():
    return {'language': 'en-US', 'basics': {'name': 'Synthetic Candidate', 'title': 'Backend Engineer'},
            'skills': [{'category': 'Languages', 'items': ['Go']}],
            'experience': [{'company': 'Synthetic Company', 'role': 'Engineer',
                            'bullets': [{'text': 'Participated in API development.'}]}],
            'education': [{'degree': 'Bachelor', 'field': 'Computer Science'}]}


class CleanOutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='knowme-clean-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.work = self.base / 'candidate'
        self.work.mkdir()
        self.scratch = self.base / 'scratch'
        self.scratch.mkdir()
        self.env = dict(os.environ, TMPDIR=str(self.scratch))

    def execute(self, *args, value=None, env=None, cli=False):
        command = ['node', str(ROOT / 'bin/knowme.js'), 'forge'] if cli else [sys.executable, str(FORGE)]
        proc = subprocess.run(command + ['--profile-json', '-', '--template', 'minimal', *args],
                              input=json.dumps(profile() if value is None else value), cwd=self.work,
                              env=env or self.env, capture_output=True, text=True)
        self.assertTrue(proc.stdout.strip(), proc.stderr)
        return proc, json.loads(proc.stdout)

    def files(self):
        return {str(p.relative_to(self.work)) for p in self.work.rglob('*') if p.is_file()}

    def staging_is_clean(self):
        self.assertEqual(list(self.scratch.glob('knowme-run-*')), [])

    def test_success_and_update_leave_only_two_current_files(self):
        for value in [profile(), dict(profile(), basics={'name': 'Synthetic Updated Candidate'})]:
            proc, report = self.execute(value=value)
            self.assertEqual(proc.returncode, 0, report)
            self.assertEqual(report['status'], 'PASS')
            self.assertEqual(report['retention'], 'temporary')
            self.assertIsNone(report['manifest'])
            self.assertEqual(self.files(), {'resume/resume.html', 'resume/resume.pdf'})
            for key in ['html', 'pdf']:
                file = Path(report['outputs'][key])
                self.assertTrue(file.is_file())
                self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(), report['sha256'][key])
            self.assertIn(value['basics']['name'], Path(report['outputs']['html']).read_text())
            self.staging_is_clean()

    def test_unavailable_runtime_and_bad_input_preserve_old_pair(self):
        delivery = self.work / 'resume'
        delivery.mkdir()
        (delivery / 'resume.html').write_text('OLD HTML')
        (delivery / 'resume.pdf').write_bytes(b'OLD PDF')
        missing = dict(self.env, PATH=str(self.base / 'no-node'))
        for value, env, expected in [(profile(), missing, 'UNVERIFIED'), ({'unknown': 'fact'}, self.env, 'FAIL')]:
            proc, report = self.execute(value=value, env=env)
            self.assertNotEqual(proc.returncode, 0)
            self.assertEqual(report['status'], expected)
            self.assertEqual(report['outputs'], {})
            self.assertIsNone(report['manifest'])
            self.assertEqual((delivery / 'resume.html').read_text(), 'OLD HTML')
            self.assertEqual((delivery / 'resume.pdf').read_bytes(), b'OLD PDF')
            self.assertEqual(self.files(), {'resume/resume.html', 'resume/resume.pdf'})
            self.staging_is_clean()

    def test_draft_through_cli_leaves_one_file_without_touching_existing_pdf(self):
        proc, report = self.execute('--draft', value={}, cli=True)
        self.assertEqual(proc.returncode, 0, report)
        self.assertEqual(report['status'], 'DRAFT')
        self.assertEqual(set(report['outputs']), {'html'})
        self.assertEqual(self.files(), {'resume/draft.html'})
        self.staging_is_clean()
        pdf = self.work / 'resume/resume.pdf'
        pdf.write_bytes(b'OLD PDF')
        proc, report = self.execute('--draft', '--html-output', 'drafts/current.html', value={})
        self.assertEqual(proc.returncode, 0, report)
        self.assertEqual(Path(report['outputs']['html']), self.work / 'drafts/current.html')
        self.assertEqual(pdf.read_bytes(), b'OLD PDF')
        proc, report = self.execute('--draft', '--output', str(pdf), value={})
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(report['outputs'], {})
        self.assertEqual(pdf.read_bytes(), b'OLD PDF')

    def test_explicit_archive_retains_debug_data_and_stdin_provenance(self):
        for flags in [('--keep-workspace',), ('--workspace', 'debug-runs')]:
            proc, report = self.execute(*flags, '--draft', '--summary')
            self.assertEqual(proc.returncode, 0, report)
            self.assertEqual(report['retention'], 'archived')
            manifest = Path(report['manifest'])
            self.assertTrue(manifest.is_file())
            saved = json.loads((manifest.parent / 'draft.json').read_text())
            self.assertEqual(saved['source']['inputMode'], 'stdin')
            self.assertIsNone(saved['source']['path'])
            self.assertEqual(json.loads((manifest.parent / 'input.json').read_text()), profile())
            self.assertTrue((manifest.parent / 'draft-canvas-profile.json').is_file())

    def test_existing_source_is_never_deleted_or_replaced(self):
        source = self.work / 'user-profile.json'
        original = json.dumps(profile())
        source.write_text(original)
        for destination in ['different.html', str(source)]:
            proc = subprocess.run([sys.executable, str(FORGE), '--profile-json', str(source), '--draft',
                                   '--template', 'minimal', '--html-output', destination],
                                  cwd=self.work, env=self.env, capture_output=True, text=True)
            report = json.loads(proc.stdout)
            self.assertEqual(proc.returncode, 0 if destination == 'different.html' else 1, report)
            self.assertEqual(source.read_text(), original)
            self.staging_is_clean()

    def test_clean_mode_does_not_accept_fabricated_qa_pass(self):
        output = io.StringIO()
        args = ['forge', '--profile-json', '-', '--template', 'minimal', '--output', str(self.work / 'resume.pdf')]
        bogus = subprocess.CompletedProcess([], 0, json.dumps({'status': 'PASS', 'checks': {}, 'errors': [], 'warnings': []}), '')
        with patch.object(sys, 'argv', args), patch.object(sys, 'stdin', io.StringIO(json.dumps(profile()))), \
             patch.object(forge.subprocess, 'run', return_value=bogus), contextlib.redirect_stdout(output):
            code = forge.main()
        report = json.loads(output.getvalue())
        self.assertEqual(code, 2, report)
        self.assertEqual(report['status'], 'UNVERIFIED')
        self.assertEqual(report['outputs'], {})
        self.assertEqual(self.files(), set())

    def test_publication_failure_rolls_back_both_deliveries_and_removes_own_locks(self):
        sources = [self.base / 'new.html', self.base / 'new.pdf']
        targets = [self.work / 'resume.html', self.work / 'resume.pdf']
        for source, target in zip(sources, targets):
            source.write_bytes(b'NEW')
            target.write_bytes(b'OLD')
        replace = os.replace
        failed = False

        def fail_second(source, target):
            nonlocal failed
            if Path(target) == targets[1] and not failed:
                failed = True
                raise OSError('Synthetic second-file failure')
            return replace(source, target)

        with patch.object(forge.os, 'replace', side_effect=fail_second), self.assertRaises(OSError):
            forge.publish_aliases(list(zip(sources, targets)))
        self.assertEqual([p.read_bytes() for p in targets], [b'OLD', b'OLD'])
        self.assertEqual(self.files(), {'resume.html', 'resume.pdf'})

    def test_edit_html_through_same_pipeline_keeps_pair_and_rolls_back_invalid_edit(self):
        proc, report = self.execute()
        self.assertEqual(proc.returncode, 0, report)
        html = Path(report['outputs']['html'])
        pdf = Path(report['outputs']['pdf'])
        edited = html.read_text().replace('Synthetic Candidate', 'Updated Contact Candidate')
        args = [sys.executable, str(FORGE), '--html-input', '-']
        result = subprocess.run(args, input=edited, cwd=self.work, env=self.env, capture_output=True, text=True)
        current = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, current)
        self.assertEqual(current['templateUsed'], 'existing-canvas')
        self.assertEqual(html.read_text(), edited)
        accepted = (html.read_bytes(), pdf.read_bytes())
        result = subprocess.run(args, input='<html><body>Broken edit</body></html>', cwd=self.work,
                                env=self.env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['outputs'], {})
        self.assertEqual((html.read_bytes(), pdf.read_bytes()), accepted)
        self.assertEqual(self.files(), {'resume/resume.html', 'resume/resume.pdf'})
        self.staging_is_clean()

    def test_overflow_reports_actionable_location_without_retaining_files(self):
        html = '''<!doctype html><html><head><style>
        @page { size: A4; margin: 0; }
        body { margin: 0; } .resume-page { width: 210mm; height: 297mm; }
        #overflow { position: absolute; left: 220mm; top: 40mm; }
        </style></head><body><main class="resume-page">
        <h1 class="candidate-name">Synthetic Candidate</h1>
        <p id="overflow">Participated in synthetic API development.</p>
        </main></body></html>'''
        result = subprocess.run([sys.executable, str(FORGE), '--html-input', '-'],
                                input=html, cwd=self.work, env=self.env, capture_output=True, text=True)
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1, report)
        self.assertEqual(report['outputs'], {})
        dom = report['diagnostics']['dom']
        self.assertTrue(any(issue.get('selector') == '#overflow' and issue.get('pageIndex') == 1
                            and issue.get('bounds') for issue in dom['issues']), dom)
        self.assertNotIn('pages', dom)  # Do not emit full DOM text in the compact report.
        self.assertEqual(self.files(), set())
        self.staging_is_clean()

    def test_output_path_errors_and_html_overrides_return_structured_failures(self):
        for args in [['--profile-json', '-', '--output', '/'],
                     ['--html-input', '-', '--role', 'Invented role']]:
            result = subprocess.run([sys.executable, str(FORGE), *args], input='{}', cwd=self.work,
                                    env=self.env, capture_output=True, text=True)
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1, report)
            self.assertEqual(report['status'], 'FAIL')
            self.assertEqual(report['outputs'], {})
            self.assertEqual(self.files(), set())
