"""Retired/invalid entries must fail without creating candidate artifacts."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


class EntryBoundaryTests(unittest.TestCase):
    def test_all_extract_entries_reject_without_reading_or_overwriting(self):
        commands = [[sys.executable, str(ROOT / 'scripts/evidence/extract-evidence.py')],
                    ['node', str(ROOT / 'bin/knowme.js'), 'extract'],
                    ['npm', '--silent', '--prefix', str(ROOT), 'run', 'extract', '--']]
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            target = work / 'existing.json'
            target.write_text('USER ORIGINAL')
            repo = work / 'repo'
            repo.mkdir()
            (repo / 'package.json').write_text('{"dependencies":{"react":"1"}}')
            for command in commands:
                for args in [[], ['--repo', str(repo), '--output', str(target), '--quiet'],
                             ['--repo', str(work / 'absent'), '--output', str(work / 'unexpected.json'), '--json']]:
                    with self.subTest(command=command, args=args):
                        proc = subprocess.run(command + args, cwd=work, capture_output=True, text=True, timeout=20)
                        self.assertEqual(proc.returncode, 1, proc.stderr)
                        report = json.loads(proc.stdout)
                        self.assertEqual(report['status'], 'FAIL')
                        self.assertEqual(report['stage'], 'unsupported')
                        self.assertEqual(report['outputs'], {})
                        self.assertIn('forge --profile-json', report['errors'][0])
                        self.assertEqual(target.read_text(), 'USER ORIGINAL')
                        self.assertEqual({str(p.relative_to(work)) for p in work.rglob('*') if p.is_file()},
                                         {'existing.json', 'repo/package.json'})
        # Importing the retired module cannot expose the old scanning implementation either.
        spec = importlib.util.spec_from_file_location('retired_extract', ROOT / 'scripts/evidence/extract-evidence.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertFalse(hasattr(module, 'scan_repo'))
        self.assertFalse(hasattr(module, 'build_master_profile'))

    def test_unknown_commands_fail_but_help_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            for command, code in [('froge', 1), ('wizard', 1), ('preview', 1), ('help', 0)]:
                proc = subprocess.run(['node', str(ROOT / 'bin/knowme.js'), command], cwd=tmp,
                                      capture_output=True, text=True, timeout=20)
                self.assertEqual(proc.returncode, code, proc.stderr)
                if code:
                    self.assertIn('Unknown command', proc.stderr)
                    self.assertEqual(proc.stdout, '')
                self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_interactive_stdin_fails_before_creating_archive(self):
        spec = importlib.util.spec_from_file_location('entry_forge', ROOT / 'scripts/pipeline/forge.py')
        forge = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(forge)
        with tempfile.TemporaryDirectory() as tmp:
            for flag in ('--profile-json', '--html-input'):
                output = io.StringIO()
                stream = io.StringIO()
                args = ['forge', flag, '-', '--workspace', str(Path(tmp) / 'archive')]
                with patch.object(sys, 'argv', args), patch.object(sys, 'stdin', stream), \
                     patch.object(stream, 'isatty', return_value=True), \
                     patch.object(stream, 'read', side_effect=AssertionError('must not wait for input')), \
                     contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as stopped:
                    forge.main()
                self.assertEqual(stopped.exception.code, 1)
                report = json.loads(output.getvalue())
                self.assertEqual(report['status'], 'FAIL')
                self.assertEqual(report['outputs'], {})
                self.assertIn('Stdin input is required', report['errors'][0])
                self.assertEqual(list(Path(tmp).iterdir()), [])
