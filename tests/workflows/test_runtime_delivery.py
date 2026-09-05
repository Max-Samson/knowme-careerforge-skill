"""Portable installation and low-noise runtime entry regressions."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / 'scripts/rendering/browser-engine.js'


class RuntimeDeliveryTests(unittest.TestCase):
    def test_help_and_missing_dependencies_without_candidate_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            engine = directory / ENGINE.name
            shutil.copyfile(ENGINE, engine)
            help_result = subprocess.run(['node', str(engine), '--help'], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(help_result.returncode, 0, help_result.stderr)
            self.assertIn('--check-runtime', help_result.stdout)
            result = subprocess.run(['node', str(engine), '--check-runtime'], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report['status'], 'UNVERIFIED')
            self.assertEqual(len(report['errors']), 3)
            self.assertEqual(set(report['checks'].values()), {'MISSING'})
            self.assertEqual(list(directory.iterdir()), [engine])

    def test_summary_keeps_full_manifest_for_draft_and_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            profile = directory / 'profile.json'
            profile.write_text(json.dumps({'basics': {'name': 'Synthetic Candidate'}}))
            args = ['python3', str(ROOT / 'scripts/pipeline/forge.py'), '--profile-json', str(profile),
                    '--workspace', str(directory / 'runs'), '--template', 'minimal', '--summary']
            for mode, expected in [(['--draft'], 'DRAFT'), ([], 'FAIL')]:
                result = subprocess.run(args + mode, cwd=tmp, capture_output=True, text=True)
                compact = json.loads(result.stdout)
                self.assertEqual(compact['status'], expected)
                full = json.loads(Path(compact['manifest']).read_text())
                self.assertIn('checks', full)
                self.assertNotIn('checks', compact)
                if expected == 'DRAFT':
                    self.assertEqual(compact['outputs'], {'html': full['outputs']['htmlCanvas']})
                self.assertEqual(compact['errors'], full['errors'])
                if expected == 'FAIL':
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(compact['outputs'], {})

    def test_install_bundle_outside_repository_and_unknown_platform_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            init = ROOT / 'dist/cli/src/commands/init.js'
            script = 'require(process.argv[1]).runInit({platform:process.argv[2],projectDir:process.argv[3]})'
            result = subprocess.run(['node', '-e', script, str(init), 'opencode', tmp], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            bundle = Path(tmp) / '.opencode/skills/knowme-careerforge'
            self.assertTrue((bundle / 'package.json').is_file())
            self.assertTrue((bundle / 'package-lock.json').is_file())
            self.assertFalse((bundle / 'AGENT.md').exists())
            profile = Path(tmp) / 'profile.json'
            profile.write_text('{"basics":{"name":"Synthetic Candidate"}}')
            draft = subprocess.run(['python3', str(bundle / 'scripts/pipeline/forge.py'), '--profile-json',
                                    str(profile), '--draft', '--template', 'minimal', '--workspace',
                                    str(Path(tmp) / 'runs'), '--summary'], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(draft.returncode, 0, draft.stderr + draft.stdout)
            self.assertEqual(json.loads(draft.stdout)['status'], 'DRAFT')
            bad = subprocess.run(['node', '-e', script, str(init), 'unsupported', tmp], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)

    def test_summary_pass_identifies_only_current_delivery_copies(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp).resolve()
            profile = directory / 'profile.json'
            profile.write_text(json.dumps({'language': 'en-US', 'basics': {'name': 'Synthetic Candidate'},
                                           'skills': [{'category': 'Languages', 'items': ['Python']}]}))
            html, pdf = directory / 'delivery.html', directory / 'delivery.pdf'
            result = subprocess.run(['python3', str(ROOT / 'scripts/pipeline/forge.py'),
                '--profile-json', str(profile), '--workspace', str(directory / 'runs'), '--template', 'minimal',
                '--html-output', str(html), '--output', str(pdf), '--summary'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(report['outputs'], {'html': str(html), 'pdf': str(pdf)})
            self.assertTrue(pdf.read_bytes().startswith(b'%PDF-'))
            full = json.loads(Path(report['manifest']).read_text())
            self.assertIn('master', full['outputs'])
            self.assertIn('qa', full['checks'])

    def test_all_adapters_have_runtime_entry_and_windsurf_updates_its_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            home, project = base / 'home', base / 'project'
            project.mkdir()
            rules = project / '.windsurfrules'
            rules.write_text('User-owned instruction\n')
            script = ("require('os').homedir = () => process.argv[2]; "
                      "require(process.argv[1]).runInit({all:true,projectDir:process.argv[3]})")
            args = ['node', '-e', script, str(ROOT / 'dist/cli/src/commands/init.js'), str(home), str(project)]
            for _ in range(2):
                result = subprocess.run(args, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(rules.read_text().startswith('User-owned instruction'))
            self.assertEqual(rules.read_text().count('<!-- knowme-careerforge:start -->'), 1)
            local = project / '.knowme/skills/knowme-careerforge'
            self.assertIn(str(local / 'SKILL.md'), rules.read_text())
            self.assertIn(str(local / 'SKILL.md'), (project / '.cursor/rules/knowme-careerforge.mdc').read_text())
            config = json.loads((home / '.gemini/skills/knowme-careerforge.json').read_text())
            self.assertTrue(Path(config['entrypoint']).is_file())
            for bundle in [local, home / '.claude/skills/knowme-careerforge',
                           home / '.codex/skills/knowme-careerforge', Path(config['entrypoint']).parent,
                           project / '.opencode/skills/knowme-careerforge']:
                self.assertTrue((bundle / 'package.json').is_file())
                self.assertTrue((bundle / 'scripts/pipeline/forge.py').is_file())

    def test_template_summary_preserves_ranking_without_duplicate_metadata(self):
        script = ROOT / 'scripts/template/search-template.py'
        full = subprocess.run(['python3', str(script), 'Java backend engineer', '--json'],
                              capture_output=True, text=True, check=True)
        summary = subprocess.run(['python3', str(script), 'Java backend engineer', '--summary'],
                                 capture_output=True, text=True, check=True)
        ranked, compact = json.loads(full.stdout), json.loads(summary.stdout)
        self.assertEqual(compact['totalMatches'], len(ranked))
        self.assertEqual([item['id'] for item in compact['candidates']], [item['id'] for item in ranked[:3]])
        for original, brief in zip(ranked, compact['candidates']):
            self.assertEqual(brief['score'], original['matchScore'])
            self.assertEqual(brief['layout'], original['layout'])
            self.assertNotIn('template', brief)
        self.assertLess(len(summary.stdout), len(full.stdout) / 4)
