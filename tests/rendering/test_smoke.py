"""User-input lifecycle regressions. Every artifact stays in a temporary workspace."""
import concurrent.futures
import contextlib
import io
from unittest.mock import patch
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('test_profile_contract', ROOT/'scripts/contracts/profile.py')
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


def facts():
    return {'basics': {'name': '陈测试', 'title': '工程师', 'email': 'test@example.org'},
            'skills': [{'category': '技术', 'items': ['Python']}],
            'experience': [{'company': '用户真实公司', 'role': '研发', 'bullets': [{'text': '负责业务接口开发与维护。'}]}],
            'education': [{'institution': '学校甲', 'degree': '本科'}, {'institution': '学校乙', 'degree': '硕士'}]}


class TestInputLifecycle(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='knowme-lifecycle-')
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.source = self.work/'input.json'
        self.source.write_text(json.dumps(facts(), ensure_ascii=False))

    def forge(self, *args, env=None):
        proc = subprocess.run([sys.executable, str(ROOT/'scripts/pipeline/forge.py'),
                               '--profile-json', str(self.source), '--template', 'minimal',
                               '--workspace', str(self.work/'runs'), '--quiet', *args],
                              capture_output=True, text=True, cwd=self.work, env=env)
        try:
            data = json.loads(proc.stdout)
        except ValueError:
            self.fail(proc.stdout + proc.stderr)
        return proc, data

    def test_missing_values_share_one_normalization(self):
        value = contract.normalize_profile({'basics': None, 'education': None, 'skills': [], 'certifications': [None, ' ', '证书']})
        self.assertEqual(value['basics'], {})
        self.assertEqual(value['education'], [])
        self.assertEqual(value['certifications'], ['证书'])
        self.assertEqual(contract.digest(contract.normalize_profile({})),
                         contract.digest(contract.normalize_profile({'basics': {'name': None, 'phone': ' '}, 'education': []})))
        for invalid in [{'basics': {'name': 3}}, {'education': '学校'}, {'education': [{'degree': False}]}, {'unexpected': 'fact'}]:
            with self.subTest(invalid=invalid), self.assertRaises(contract.ContractError):
                contract.normalize_profile(invalid)

    def test_pipeline_preserves_input_provenance_and_font_choice(self):
        self.source.write_text(json.dumps({'schemaVersion': '1.0', 'kind': 'master', 'profile': facts(),
            'source': {'type': 'synthetic-simulation', 'note': 'Test fixture only'}}))
        proc, data = self.forge('--draft', '--font-preset', 'arial-unicode')
        self.assertEqual(proc.returncode, 0, data)
        run = Path(data['runDirectory'])
        master = json.loads((run/'draft.json').read_text())
        variant = json.loads((run/'draft-canvas-profile.json').read_text())
        self.assertEqual(master['source']['suppliedSource']['type'], 'synthetic-simulation')
        self.assertEqual(variant['source']['fontPreset'], 'arial-unicode')
        self.assertEqual(data['fontPreset'], 'arial-unicode')

    def test_document_hash_and_variant_lineage_are_checked(self):
        master = contract.document('master', facts())
        self.assertEqual(contract.load_document(master), master)
        master['profile']['basics']['name'] = 'changed'
        with self.assertRaises(contract.ContractError):
            contract.load_document(master)
        with self.assertRaises(contract.ContractError):
            contract.load_document(contract.document('variant', facts()))

    def test_draft_is_not_a_verified_delivery(self):
        self.source.write_text(json.dumps({'schemaVersion': '1.0', 'kind': 'draft', 'profile': {'basics': None}}))
        proc, data = self.forge('--draft')
        self.assertEqual(proc.returncode, 0, data)
        self.assertEqual(data['status'], 'DRAFT')
        self.assertNotIn('pdfDelivery', data['outputs'])
        self.assertFalse((Path(data['runDirectory'])/'resume.pdf').exists())
        proc, data = self.forge()
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(data['status'], 'FAIL')
        self.assertEqual(data['outputs'], {})

    def test_invalid_input_preserves_existing_outputs(self):
        self.source.write_text('{broken json')
        pdf, html = self.work/'old.pdf', self.work/'old.html'
        pdf.write_bytes(b'old PDF'); html.write_text('old HTML')
        proc, data = self.forge('--output', str(pdf), '--html-output', str(html))
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(data['outputs'], {})
        self.assertEqual(pdf.read_bytes(), b'old PDF')
        self.assertEqual(html.read_text(), 'old HTML')
        self.assertEqual(json.loads((Path(data['runDirectory'])/'manifest.json').read_text())['status'], 'FAIL')

    def test_source_output_collision_rejected(self):
        original = self.source.read_bytes()
        proc, data = self.forge('--output', str(self.source))
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(self.source.read_bytes(), original)
        self.assertEqual(data['stage'], 'input')

    def test_unavailable_browser_runtime_never_uses_old_pdf(self):
        pdf = self.work/'old.pdf'; pdf.write_bytes(b'old PDF')
        env = dict(os.environ); env['PATH'] = str(self.work/'no-tools')
        proc, data = self.forge('--output', str(pdf), env=env)
        self.assertEqual(proc.returncode, 2, data)
        self.assertEqual(data['status'], 'UNVERIFIED')
        self.assertEqual(data['outputs'], {})
        self.assertEqual(pdf.read_bytes(), b'old PDF')

    def test_variant_input_cannot_silently_become_master(self):
        variant = contract.document('variant', facts(), {'masterSha256': 'a'*64})
        self.source.write_text(json.dumps(variant))
        proc, data = self.forge()
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(data['outputs'], {})

    def test_two_runs_are_isolated_and_master_is_preserved(self):
        original = self.source.read_bytes()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(self.forge, '--role', role) for role in ('后端工程师', '全栈工程师')]
            results = [f.result() for f in futures]
        directories = set()
        for (proc, data), role in zip(results, ('后端工程师', '全栈工程师')):
            self.assertEqual(proc.returncode, 0, data)
            self.assertEqual(data['status'], 'PASS')
            run = Path(data['runDirectory']); directories.add(run)
            master = json.loads((run/'master.json').read_text())
            variant = json.loads((run/'variant.json').read_text())
            self.assertEqual(master['profile']['basics']['title'], '工程师')
            self.assertEqual(variant['profile']['basics']['title'], role)
            self.assertEqual(variant['source']['masterSha256'], master['profileSha256'])
            self.assertEqual(variant['profile']['education'], master['profile']['education'])
            self.assertEqual((run/'input.json').read_bytes(), original)
            self.assertTrue((run/'resume.pdf').read_bytes().startswith(b'%PDF-'))
            self.assertEqual(data['sha256']['pdf'], __import__('hashlib').sha256((run/'resume.pdf').read_bytes()).hexdigest())
            self.assertEqual(json.loads((run/'qa.json').read_text())['status'], 'PASS')
        self.assertEqual(len(directories), 2)
        self.assertEqual(self.source.read_bytes(), original)

    def test_auto_template_selection_with_jd(self):
        proc = subprocess.run([sys.executable, str(ROOT/'scripts/pipeline/forge.py'), '--profile-json', str(self.source),
                               '--workspace', str(self.work/'runs'), '--jd', '需要 Python 经验', '--quiet'],
                              capture_output=True, text=True, cwd=self.work)
        data = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 0, data)
        self.assertTrue(data['templateUsed'])
        self.assertTrue((Path(data['runDirectory'])/'jd-analysis.json').exists())

    def test_failed_copy_does_not_replace_existing_pdf(self):
        pdf, html = self.work/'old.pdf', self.work/'directory.html'
        pdf.write_bytes(b'old PDF'); html.mkdir()
        proc, data = self.forge('--output', str(pdf), '--html-output', str(html))
        self.assertEqual(proc.returncode, 1, data)
        self.assertEqual(data['outputs'], {})
        self.assertEqual(pdf.read_bytes(), b'old PDF')
        self.assertEqual(data['stage'], 'publish')

    def test_cli_propagates_failed_json_validation(self):
        proc = subprocess.run(['node', str(ROOT/'bin/knowme.js'), 'validate', str(self.work/'missing.html'), '--json'], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertNotEqual(json.loads(proc.stdout)['status'], 'PASS')

    def test_incomplete_or_contradictory_qa_never_delivers(self):
        spec = importlib.util.spec_from_file_location('forge_protocol_test', ROOT/'scripts/pipeline/forge.py')
        forge = importlib.util.module_from_spec(spec); spec.loader.exec_module(forge)
        payloads = [([], 0), ({'status': 'PASS', 'errors': [], 'warnings': [], 'checks': {}}, 0),
                    ({'status': 'PASS', 'errors': [], 'warnings': [], 'checks': {}}, 1),
                    ({'status': 'PASS', 'errors': [], 'warnings': [], 'checks': {'output': []}}, 0)]
        for payload, code in payloads:
            with self.subTest(payload=payload, code=code):
                output = io.StringIO()
                argv = ['forge', '--profile-json', str(self.source), '--template', 'minimal', '--workspace', str(self.work/'runs'), '--quiet']
                with patch.object(sys, 'argv', argv), patch.object(forge.subprocess, 'run', return_value=subprocess.CompletedProcess([], code, json.dumps(payload), '')), contextlib.redirect_stdout(output):
                    result = forge.main()
                report = json.loads(output.getvalue())
                self.assertEqual(result, 2, report)
                self.assertEqual(report['status'], 'UNVERIFIED')
                self.assertEqual(report['outputs'], {})

    def test_python_bridge_rejects_incomplete_pass(self):
        spec = importlib.util.spec_from_file_location('bridge_protocol_test', ROOT/'scripts/rendering/browser_engine.py')
        bridge = importlib.util.module_from_spec(spec); spec.loader.exec_module(bridge)
        for payload in [[], {'status': 'PASS', 'errors': [], 'warnings': [], 'checks': {}}]:
            with patch.object(bridge.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, json.dumps(payload), '')):
                self.assertEqual(bridge.run('unused.html')['status'], 'UNVERIFIED')
