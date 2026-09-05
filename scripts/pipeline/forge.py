#!/usr/bin/env python3
"""Run an isolated user-input resume build with explicit artifact and QA states."""
import argparse
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


contract = load_module('profile_contract', 'contracts/profile.py')


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data if isinstance(data, bytes) else data.encode('utf-8'))
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def write_json(path, value):
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def publish_aliases(pairs):
    """Stage every requested copy before publishing; rollback ordinary write failures.

    The run directory remains canonical. Lock files reject concurrent publishers
    to the same requested destination instead of interleaving their outputs.
    """
    staged, locks, replaced = [], [], []
    try:
        for source, target in pairs:
            target.parent.mkdir(parents=True, exist_ok=True)
            lock = target.with_name('.' + target.name + '.knowme-lock')
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
            locks.append(lock)
            if target.exists() and not target.is_file():
                raise ValueError('Output is not a regular file: ' + str(target))
            backup = target.read_bytes() if target.exists() else None
            fd, temp = tempfile.mkstemp(prefix='.knowme-export-', dir=target.parent)
            os.close(fd)
            staged.append((Path(temp), target, backup))
            shutil.copyfile(source, temp)
        for temp, target, backup in staged:
            os.replace(temp, target)
            replaced.append((target, backup))
    except Exception:
        for target, backup in reversed(replaced):
            if backup is None:
                target.unlink(missing_ok=True)
            else:
                atomic_write(target, backup)
        raise
    finally:
        for temp, _, _ in staged:
            temp.unlink(missing_ok=True)
        for lock in locks:
            lock.unlink(missing_ok=True)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        print(json.dumps({'status': 'FAIL', 'stage': 'arguments', 'errors': [message],
                          'warnings': [], 'checks': {}, 'outputs': {}}, ensure_ascii=False))
        self.exit(1)


def main():
    parser = Parser(description=__doc__)
    parser.add_argument('--profile-json', required=True, help='User/Agent supplied facts or Draft/Master document; never a repository')
    parser.add_argument('--workspace', default='workspace/runs', help='Parent directory for unique run directories')
    parser.add_argument('--draft', action='store_true', help='Create an incomplete draft canvas without claiming PDF delivery')
    parser.add_argument('--role')
    parser.add_argument('--jd', help='Optional JD path or inline text; used only as highlighting/search hints')
    parser.add_argument('--template', '-t')
    parser.add_argument('--font-preset', choices=('system', 'arial-unicode'), default='system', help='Explicit local font choice; missing fonts fail verification')
    for key in ('name', 'email', 'phone'):
        parser.add_argument('--' + key)
    parser.add_argument('--output', '-o', help='Optional verified PDF copy; default is the isolated run PDF')
    parser.add_argument('--html-output', help='Optional verified HTML copy; default is the isolated run canvas')
    parser.add_argument('--expected-pages', type=int, choices=(1, 2), default=1)
    parser.add_argument('--auto-heal', action='store_true')
    parser.add_argument('--quiet', '-q', action='store_true')
    parser.add_argument('--summary', action='store_true', help='Compact report with manifest path; full diagnostics stay on disk')
    args = parser.parse_args()
    report = {'schemaVersion': '1.0', 'runId': uuid.uuid4().hex, 'status': 'RUNNING',
              'stage': 'input', 'errors': [], 'warnings': [], 'checks': {}, 'outputs': {}}
    run = None
    exit_code = 1
    try:
        parent = Path(args.workspace).resolve()
        parent.mkdir(parents=True, exist_ok=True)
        run = parent / report['runId']
        run.mkdir(mode=0o700)
        report['runDirectory'] = str(run)
        report['startedAt'] = datetime.now(timezone.utc).isoformat()
        write_json(run / 'manifest.json', report)
        source = Path(args.profile_json).resolve()
        aliases = [Path(p).resolve() for p in (args.html_output, args.output) if p]
        if len(set([source] + aliases)) != len([source] + aliases):
            raise ValueError('Input, HTML and PDF output paths must be distinct')
        for target in aliases:
            if target == run or run in target.parents:
                raise ValueError('Explicit output cannot replace an internal run artifact')
        raw_bytes = source.read_bytes()
        atomic_write(run / 'input.json', raw_bytes)
        supplied = contract.load_document(json.loads(raw_bytes))
        if supplied['kind'] == 'variant':
            raise ValueError('A Variant is not a Master; use its original Master to derive another resume')
        if supplied['kind'] == 'draft' and not args.draft:
            raise ValueError('Draft input cannot be delivered; review facts and provide a Master, or use --draft')
        facts = copy.deepcopy(supplied['profile'])
        for key in ('name', 'email', 'phone'):
            if getattr(args, key) is not None:
                facts['basics'][key] = getattr(args, key)
        kind = 'draft' if args.draft else 'master'
        master = contract.document(kind, facts, {'type': 'user-input', 'path': str(source),
                     'inputSha256': hashlib.sha256(raw_bytes).hexdigest(),
                     'suppliedKind': supplied['kind'], 'suppliedSource': supplied['source']})
        write_json(run / (kind + '.json'), master)
        report['checks']['missingFields'] = master['missingFields']
        report['warnings'].extend('Missing optional contact/position field: ' + v for v in master['missingFields'] if v != 'basics.name')
        if not args.draft:
            errors = contract.delivery_errors(master['profile'])
            if errors:
                raise ValueError('; '.join(errors))
        profile = copy.deepcopy(master['profile'])
        if args.role is not None:
            profile['basics']['title'] = args.role
        keywords = []
        if args.jd:
            report['stage'] = 'jd'
            try:
                jd_file = Path(args.jd)
                jd = jd_file.read_text(encoding='utf-8') if jd_file.is_file() else args.jd
            except OSError:
                jd = args.jd
            atomic_write(run / 'jd.txt', jd)
            analyzer = load_module('jd_analyzer', 'evidence/analyze-jd.py')
            with contextlib.redirect_stdout(io.StringIO()):
                result = analyzer.analyze_jd_text(jd)
            write_json(run / 'jd-analysis.json', result)
            keywords = result.get('detectedSkills', [])
        report['stage'] = 'template'
        template = args.template
        if not template:
            search = load_module('template_search', 'template/search-template.py')
            with contextlib.redirect_stdout(io.StringIO()):
                results = search.search_templates(role=args.role or profile['basics'].get('title') or '',
                                                  keywords=','.join(keywords), target_pages=args.expected_pages, engine='hybrid')
            if not results:
                raise ValueError('No matching template available')
            template = results[0].get('id') or results[0]['template']['id']
        variant = contract.document('draft' if args.draft else 'variant', profile,
                     {'masterSha256': master['profileSha256'], 'masterPath': str(run / (kind + '.json')),
                      'template': template, 'targetRole': args.role, 'fontPreset': args.font_preset})
        variant_path = run / ('draft-canvas-profile.json' if args.draft else 'variant.json')
        write_json(variant_path, variant)
        report['templateUsed'] = template
        report['fontPreset'] = args.font_preset
        report['stage'] = 'binding'
        inst = load_module('instantiate_resume', 'template/instantiate-resume.py')
        canvas, pdf = run / 'resume.html', run / 'resume.pdf'
        with contextlib.redirect_stdout(io.StringIO()):
            inst.instantiate_workspace(template, str(variant_path), ','.join(keywords), str(canvas), font_preset=args.font_preset)
        if args.draft:
            report.update(status='DRAFT', stage='draft', outputs={'draft': str(run / 'draft.json'), 'htmlCanvas': str(canvas)})
            exit_code = 0
        else:
            report['stage'] = 'qa'
            cmd = ['node', str(ROOT / 'scripts/rendering/browser-engine.js'), str(canvas),
                   '--expected-pages', str(args.expected_pages), '--output', str(pdf)]
            if args.auto_heal:
                cmd.append('--auto-heal')
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            try:
                qa = json.loads(process.stdout)
                if not isinstance(qa, dict):
                    raise ValueError('QA result must be an object')
                expected_exit = {'PASS': 0, 'FAIL': 1, 'UNVERIFIED': 2}.get(qa.get('status'))
                if expected_exit is None or process.returncode != expected_exit:
                    raise ValueError('QA status and exit code disagree')
                if (not isinstance(qa.get('checks'), dict)
                        or any(not isinstance(v, dict) for v in qa['checks'].values())
                        or any(not isinstance(qa.get(key), list) or any(not isinstance(v, str) for v in qa[key])
                               for key in ('errors', 'warnings'))):
                    raise ValueError('Malformed QA diagnostics')
            except (ValueError, TypeError) as error:
                report['status'] = 'UNVERIFIED'
                raise ValueError('Browser returned no valid QA result: ' + str(error) + '; ' + process.stderr[:400])
            write_json(run / 'qa.json', qa)
            report['checks']['qa'] = qa
            report['warnings'].extend(qa.get('warnings', []))
            if process.returncode != 0 or qa.get('status') != 'PASS':
                report['status'] = 'UNVERIFIED' if qa.get('status') == 'UNVERIFIED' else 'FAIL'
                raise ValueError('; '.join(qa.get('errors', [])) or 'PDF validation did not pass')
            checks = qa.get('checks', {})
            required_checks = ('input', 'fonts', 'dom', 'pdf', 'text', 'output')
            if qa.get('errors') or any(checks.get(key, {}).get('status') != 'PASS' for key in required_checks):
                report['status'] = 'UNVERIFIED'
                raise ValueError('Incomplete or contradictory QA result; refusing delivery')
            accepted = checks['output']
            if not accepted.get('committed') or accepted.get('path') != str(pdf):
                report['status'] = 'UNVERIFIED'
                raise ValueError('QA did not commit this run PDF')
            if not pdf.is_file() or not pdf.read_bytes().startswith(b'%PDF-'):
                raise ValueError('Verified PDF was not produced by this run')
            if accepted.get('pdfSha256') != file_hash(pdf) or accepted.get('htmlSha256') != file_hash(canvas):
                raise ValueError('Output changed after QA or acceptance hashes are missing')
            report['stage'] = 'publish'
            pairs = []
            if args.html_output:
                pairs.append((canvas, Path(args.html_output).resolve()))
            if args.output:
                pairs.append((pdf, Path(args.output).resolve()))
            publish_aliases(pairs)
            report.update(status='PASS', stage='complete', outputs={
                'master': str(run / 'master.json'), 'variant': str(variant_path),
                'htmlCanvas': str(canvas), 'pdfDelivery': str(pdf), 'qa': str(run / 'qa.json'),
                'copies': [str(target) for _, target in pairs]},
                sha256={'html': file_hash(canvas), 'pdf': file_hash(pdf), 'master': master['profileSha256']})
            exit_code = 0
    except Exception as error:
        if report['status'] == 'RUNNING':
            report['status'] = 'UNVERIFIED' if (report['stage'] == 'qa' and isinstance(error, (subprocess.TimeoutExpired, FileNotFoundError))) or not isinstance(error, (OSError, ValueError, TypeError, RuntimeError)) else 'FAIL'
        report['errors'].append(str(error))
        report['outputs'] = {}
        exit_code = 2 if report['status'] == 'UNVERIFIED' else 1
    finally:
        report['finishedAt'] = datetime.now(timezone.utc).isoformat()
        if run:
            try:
                write_json(run / 'manifest.json', report)
            except OSError as error:
                report.update(status='FAIL', outputs={})
                report['errors'].append('Could not persist manifest: ' + str(error))
                exit_code = 1
        emitted = report
        if args.summary:
            emitted = {key: report[key] for key in ('runId', 'status', 'stage', 'templateUsed', 'fontPreset', 'errors', 'warnings', 'outputs') if key in report}
            emitted['outputs'] = {}
            if report['status'] in ('PASS', 'DRAFT'):
                emitted['outputs']['html'] = str(Path(args.html_output).resolve()) if report['status'] == 'PASS' and args.html_output else report['outputs']['htmlCanvas']
            if report['status'] == 'PASS':
                emitted['outputs']['pdf'] = str(Path(args.output).resolve()) if args.output else report['outputs']['pdfDelivery']
            emitted['manifest'] = str(run / 'manifest.json') if run else None
        print(json.dumps(emitted, ensure_ascii=False, indent=None if args.quiet else 2))
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
