#!/usr/bin/env python3
"""Build a verified resume in isolation; retain only delivery files unless archiving is requested."""
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

    Source bytes have already passed QA. Lock files reject concurrent publishers
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
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--profile-json', help='User/Agent facts file, or - to read JSON from stdin without saving an input file')
    inputs.add_argument('--html-input', help='Existing edited canvas file, or - for HTML on stdin; validates and publishes the pair without reconstructing a profile')
    parser.add_argument('--workspace', help='Explicit archive parent; implies --keep-workspace (legacy behavior)')
    parser.add_argument('--keep-workspace', action='store_true', help='Retain full diagnostic runs under --workspace or workspace/runs; default uses temporary staging')
    parser.add_argument('--draft', action='store_true', help='Create an incomplete draft canvas without claiming PDF delivery')
    parser.add_argument('--role')
    parser.add_argument('--jd', help='Optional JD path or inline text; used only as highlighting/search hints')
    parser.add_argument('--template', '-t')
    parser.add_argument('--font-preset', choices=('system', 'arial-unicode'), default='system', help='Explicit local font choice; missing fonts fail verification')
    for key in ('name', 'email', 'phone'):
        parser.add_argument('--' + key)
    parser.add_argument('--output', '-o', help='Verified PDF destination; default resume/resume.pdf in clean mode')
    parser.add_argument('--html-output', help='HTML destination; default beside the PDF, or resume/draft.html for Draft')
    parser.add_argument('--expected-pages', type=int, choices=(1, 2), default=1)
    parser.add_argument('--auto-heal', action='store_true')
    parser.add_argument('--quiet', '-q', action='store_true')
    parser.add_argument('--summary', action='store_true', help='Compact report (default in clean mode); manifest exists only for archived runs')
    args = parser.parse_args()
    if args.draft and args.output:
        parser.error('--output is a PDF destination and cannot be used with --draft')
    if args.html_input is not None and (any(getattr(args, key) is not None for key in ('role', 'jd', 'template', 'name', 'email', 'phone')) or args.font_preset != 'system'):
        parser.error('Existing HTML keeps its own content, template and fonts; edit the canvas instead of passing profile overrides')
    retained = args.keep_workspace or args.workspace is not None
    try:
        if not retained:
            if args.draft:
                args.html_output = args.html_output or 'resume/draft.html'
            else:
                args.output = args.output or str(Path(args.html_output).with_suffix('.pdf') if args.html_output else Path('resume/resume.pdf'))
                args.html_output = args.html_output or str(Path(args.output).with_suffix('.html'))
    except ValueError as error:
        parser.error(str(error))
    report = {'schemaVersion': '1.0', 'runId': uuid.uuid4().hex, 'status': 'RUNNING',
              'stage': 'input', 'errors': [], 'warnings': [], 'checks': {}, 'outputs': {}}
    run = None
    temporary = None
    exit_code = 1
    try:
        if retained:
            parent = Path(args.workspace or 'workspace/runs').resolve()
            parent.mkdir(parents=True, exist_ok=True)
            run = parent / report['runId']
            run.mkdir(mode=0o700)
        else:
            temporary = tempfile.TemporaryDirectory(prefix='knowme-run-')
            run = Path(temporary.name).resolve()
        report['retention'] = 'archived' if retained else 'temporary'
        report['runDirectory'] = str(run) if retained else None
        report['startedAt'] = datetime.now(timezone.utc).isoformat()
        write_json(run / 'manifest.json', report)
        input_arg = args.profile_json if args.profile_json is not None else args.html_input
        source = None if input_arg == '-' else Path(input_arg).resolve()
        aliases = [Path(p).resolve() for p in (args.html_output, args.output) if p]
        paths = ([source] if source is not None else []) + aliases
        if len(set(paths)) != len(paths):
            raise ValueError('Input, HTML and PDF output paths must be distinct')
        for target in aliases:
            if target == run or run in target.parents:
                raise ValueError('Explicit output cannot replace an internal run artifact')
        raw_bytes = sys.stdin.read().encode('utf-8') if source is None else source.read_bytes()
        canvas, pdf = run / 'resume.html', run / 'resume.pdf'
        if args.html_input is not None:
            report.update(stage='binding', templateUsed='existing-canvas', fontPreset='existing', inputMode='html')
            atomic_write(run / 'input.html', raw_bytes)
            atomic_write(canvas, raw_bytes)
        else:
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
            master = contract.document(kind, facts, {'type': 'user-input', 'path': str(source) if source else None, 'inputMode': 'file' if source else 'stdin',
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
            with contextlib.redirect_stdout(io.StringIO()):
                inst.instantiate_workspace(template, str(variant_path), ','.join(keywords), str(canvas), font_preset=args.font_preset)
        if args.draft:
            if args.html_output:
                report['stage'] = 'publish'
                publish_aliases([(canvas, Path(args.html_output).resolve())])
            draft_outputs = {'htmlCanvas': str(canvas)}
            if args.profile_json is not None:
                draft_outputs['draft'] = str(run / 'draft.json')
            report.update(status='DRAFT', stage='draft', outputs=draft_outputs)
            if not retained:
                report['outputs'] = {'htmlCanvas': str(Path(args.html_output).resolve())}
            report['sha256'] = {'html': file_hash(canvas)}
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
            outputs = {'htmlCanvas': str(canvas), 'pdfDelivery': str(pdf), 'qa': str(run / 'qa.json'),
                       'copies': [str(target) for _, target in pairs]}
            hashes = {'html': file_hash(canvas), 'pdf': file_hash(pdf)}
            if args.profile_json is not None:
                outputs.update(master=str(run / 'master.json'), variant=str(variant_path))
                hashes['master'] = master['profileSha256']
            report.update(status='PASS', stage='complete', outputs=outputs, sha256=hashes)
            if not retained:
                report['outputs'] = {'htmlCanvas': str(Path(args.html_output).resolve()),
                                     'pdfDelivery': str(Path(args.output).resolve())}
            exit_code = 0
    except Exception as error:
        if report['status'] == 'RUNNING':
            report['status'] = 'UNVERIFIED' if (report['stage'] == 'qa' and isinstance(error, (subprocess.TimeoutExpired, FileNotFoundError))) or not isinstance(error, (OSError, ValueError, TypeError, RuntimeError)) else 'FAIL'
        report['errors'].append(str(error))
        report['outputs'] = {}
        exit_code = 2 if report['status'] == 'UNVERIFIED' else 1
    finally:
        report['finishedAt'] = datetime.now(timezone.utc).isoformat()
        if run and retained:
            try:
                write_json(run / 'manifest.json', report)
            except OSError as error:
                report.update(status='FAIL', outputs={})
                report['errors'].append('Could not persist manifest: ' + str(error))
                exit_code = 1
        if temporary:
            try:
                temporary.cleanup()
            except OSError as error:
                report['warnings'].append('Temporary staging cleanup failed: ' + str(error))
        emitted = report
        if args.summary or not retained:
            emitted = {key: report[key] for key in ('runId', 'status', 'stage', 'retention', 'templateUsed', 'fontPreset', 'errors', 'warnings', 'outputs', 'sha256') if key in report}
            emitted['outputs'] = {}
            if report['status'] in ('PASS', 'DRAFT'):
                emitted['outputs']['html'] = str(Path(args.html_output).resolve()) if args.html_output else report['outputs']['htmlCanvas']
            if report['status'] == 'PASS':
                emitted['outputs']['pdf'] = str(Path(args.output).resolve()) if args.output else report['outputs']['pdfDelivery']
            emitted['manifest'] = str(run / 'manifest.json') if run and retained else None
            if report['status'] in ('FAIL', 'UNVERIFIED'):
                failed_checks = report['checks'].get('qa', {}).get('checks', {})
                details = {}
                for key, check in failed_checks.items():
                    if check.get('status') != 'PASS':
                        details[key] = {'status': check.get('status')}
                        if key == 'dom':
                            if 'totalPagesFound' in check:
                                details[key]['totalPagesFound'] = check['totalPagesFound']
                            for field in ('issues', 'unsupported'):
                                if isinstance(check.get(field), list):
                                    details[key][field + 'Count'] = len(check[field])
                                    details[key][field] = check[field][:20]
                        if key == 'pdf':
                            for field in ('pageCount', 'pages'):
                                if field in check:
                                    details[key][field] = check[field]
                        if key == 'text' and isinstance(check.get('pages'), list):
                            details[key]['pages'] = [
                                {field: page[field] for field in ('pageIndex', 'missingCodepoints', 'missingFragments', 'extractedRadicals') if field in page}
                                for page in check['pages'] if isinstance(page, dict)]
                if details:
                    emitted['diagnostics'] = details
        print(json.dumps(emitted, ensure_ascii=False, indent=None if args.quiet else 2))
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
