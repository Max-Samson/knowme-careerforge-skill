"""JD semantics and release-mode regressions; never execute release subprocesses."""
import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def load(relative):
    spec = importlib.util.spec_from_file_location(Path(relative).stem, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReviewRegressions(unittest.TestCase):
    def test_chinese_adjacent_skills_and_identifier_boundaries(self):
        analyzer = load('scripts/evidence/analyze-jd.py')
        result = analyzer.analyze_jd_text('熟练掌握Java和MySQL，熟悉Redis。使用C++、Node.js和CI/CD。')
        self.assertEqual(set(result['detectedSkills']), {'Java', 'MySQL', 'Redis', 'C++', 'Node.js', 'CI/CD'})
        result = analyzer.analyze_jd_text('JavaScript Golang Django Reactivity MySQLBackup')
        self.assertEqual(set(result['detectedSkills']), {'JavaScript', 'Golang'})

    def test_requirement_meaning_overrides_dictionary_order(self):
        analyzer = load('scripts/evidence/analyze-jd.py')
        result = analyzer.analyze_jd_text(
            'Required: Kubernetes. Nice to have: Python, TypeScript, JavaScript, Java, Go, Rust.')
        self.assertEqual(result['mustHaveSkills'], ['Kubernetes'])
        self.assertEqual(set(result['niceToHaveSkills']), {'Python', 'TypeScript', 'JavaScript', 'Java', 'Go', 'Rust'})

    def test_headings_scope_and_unknown_requirements(self):
        analyzer = load('scripts/evidence/analyze-jd.py')
        result = analyzer.analyze_jd_text(
            '## 必备技能：\n- Java\n- MySQL\n## 加分项：\n- Redis\n职责：\n使用Docker\n## Required\n- Rust\n## About us\nWe use Go')
        self.assertEqual(result['mustHaveSkills'], ['Java', 'Rust', 'MySQL'])
        self.assertEqual(result['niceToHaveSkills'], ['Redis'])
        self.assertIn('Docker', result['detectedSkills'])
        result = analyzer.analyze_jd_text('Python TypeScript JavaScript Java Go Rust Kubernetes')
        self.assertEqual(result['mustHaveSkills'], [])
        self.assertEqual(result['niceToHaveSkills'], [])

    def test_inline_negation_and_conflicting_requirements(self):
        analyzer = load('scripts/evidence/analyze-jd.py')
        result = analyzer.analyze_jd_text('必须Java，Python优先。Rust is not required. Required: Go. Optional: Go.')
        self.assertEqual(result['mustHaveSkills'], ['Java'])
        self.assertEqual(set(result['niceToHaveSkills']), {'Python', 'Rust'})

    def test_release_modes_conflict_before_any_command(self):
        release = load('scripts/build/release.py')
        for flags in (['--dry-run', '--publish'], ['--publish', '--dry-run']):
            with self.subTest(flags=flags), patch.object(sys, 'argv', ['release.py'] + flags), \
                    patch.object(release, 'run_command') as command, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    release.main()
                self.assertEqual(error.exception.code, 2)
                command.assert_not_called()

    def test_only_explicit_publish_reaches_publish_command(self):
        release = load('scripts/build/release.py')
        for flags in ([], ['--dry-run'], ['--publish']):
            with self.subTest(flags=flags), patch.object(sys, 'argv', ['release.py'] + flags), \
                    patch.object(release, 'run_command', return_value='[]') as command, \
                    contextlib.redirect_stdout(io.StringIO()):
                release.main()
                commands = [call.args[0] for call in command.call_args_list]
                self.assertEqual('npm publish --access public' in commands, flags == ['--publish'])


if __name__ == '__main__':
    unittest.main()
