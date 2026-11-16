#!/usr/bin/env python3
"""Run one continuous pi task on a prepared rebuild branch; observe native compaction."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from run import HERE, ROOT, TEMP, command, hashes, repository_env, save, trace


def compaction_evidence(raw, sessions):
    events, entries, usage, errors = [], [], Counter(), []
    peak = 0
    for number, line in enumerate(raw.read_text().splitlines(), 1):
        event = json.loads(line)
        if event.get('type') in {'compaction_start', 'compaction_end'}:
            events.append({'line': number, **event})
    files = list(sessions.glob('*.jsonl'))
    if len(files) != 1:
        errors.append('expected exactly one persisted session')
    for path in files:
        ids = set()
        for line in path.read_text().splitlines():
            entry = json.loads(line)
            ids.add(entry.get('id'))
            if entry.get('type') == 'compaction':
                entries.append(entry)
                if not entry.get('summary') or entry.get('tokensBefore', 0) <= 0 or entry.get('firstKeptEntryId') not in ids or entry.get('fromHook'):
                    errors.append('invalid or non-native persisted compaction')
                usage.update({k: v for k, v in entry.get('usage', {}).items() if isinstance(v, (int, float))})
            message = entry.get('message', {})
            if message.get('role') == 'assistant':
                u = message.get('usage', {})
                peak = max(peak, u.get('totalTokens', 0) or sum(u.get(k, 0) for k in ('input', 'output', 'cacheRead', 'cacheWrite')))
    starts = [e for e in events if e['type'] == 'compaction_start']
    ends = [e for e in events if e['type'] == 'compaction_end']
    successful = [e for e in ends if e.get('result') and not e.get('aborted') and not e.get('errorMessage')]
    if len(starts) != len(ends):
        errors.append('unfinished compaction attempt')
    if [e['result'].get('summary') for e in successful] != [e.get('summary') for e in entries]:
        errors.append('compaction events do not match persisted summaries')
    if any(e.get('reason') == 'manual' for e in events):
        errors.append('manual compaction in natural task')
    return {'events': events, 'entries': entries, 'count': len(entries), 'attempts': len(starts),
            'summary_usage': dict(usage), 'peak_reported_context_tokens': peak, 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, type=Path, help='Prepared run containing project/ and seed.json')
    parser.add_argument('--source', type=Path, default=ROOT)
    parser.add_argument('--case', type=Path, default=HERE / 'cases/byspace-schedules')
    parser.add_argument('--config', type=Path, default=Path.home() / '.pi/agent')
    parser.add_argument('--model', required=True)
    parser.add_argument('--thinking', default='medium')
    parser.add_argument('--no-skill', action='store_true',
                        help='Control arm: do not install any skill; the model works from the task text alone')
    parser.add_argument('--compact-at', type=int, default=400000, help='Native context threshold; no compaction count is prescribed')
    parser.add_argument('--timeout', type=int, default=14400, help='Whole-task limit in seconds')
    args = parser.parse_args()
    root, source, case, config = (p.expanduser().resolve() for p in (args.run, args.source, args.case, args.config))
    project, skill = root / 'project', source / 'skills/bi'
    if args.no_skill and source != ROOT:
        parser.error('--no-skill installs nothing; --source is meaningless with it')
    if any(root.is_relative_to(p) or p.is_relative_to(root) for p in (ROOT, source, case)):
        parser.error('run must be separate from source and case')
    if not (root / 'seed.json').is_file() or (root / 'report.json').exists() or (root / 'agent').exists():
        parser.error('need an unused prepared run; previous evidence is never overwritten')
    seed = json.loads((root / 'seed.json').read_text())
    if subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=project, text=True).strip() != seed['seed_commit']:
        parser.error('project is not at the prepared seed commit')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=project):
        parser.error('seed project has changes')
    if (project / '.pi/settings.json').exists():
        parser.error('project settings could override the recorded evaluation settings')
    provider, _, model_id = args.model.partition('/')
    models = json.loads((config / 'models.json').read_text())['providers'].get(provider, {}).get('models', [])
    model = next((m for m in models if m['id'] == model_id), None)
    if not model or not 20000 < args.compact_at < model['contextWindow'] or args.timeout <= 0:
        parser.error('need an exact configured model, valid context threshold and positive timeout')
    settings = {'compaction': {'enabled': True, 'reserveTokens': model['contextWindow'] - args.compact_at, 'keepRecentTokens': 20000}}
    report = {'execution': 'in_progress', 'model': args.model, 'thinking': args.thinking,
              'model_limits': {k: model.get(k) for k in ('contextWindow', 'maxTokens')},
              'settings': settings, 'compact_at': args.compact_at, 'seed_commit': seed['seed_commit'],
              'arm': 'no-skill-control' if args.no_skill else 'bi-skill',
              'skill_sha256': {} if args.no_skill else hashes(skill),
              'case_sha256': hashes(case), 'business': '无法判定'}
    save(root / 'report.json', report)
    env = repository_env(root)
    env['PI_CODING_AGENT_DIR'] = str(root / 'agent')
    raw = root / 'raw.jsonl'
    try:
        (root / 'agent').mkdir()
        for name in ('auth.json', 'models.json'):
            (root / 'agent' / name).symlink_to(config / name)
        save(root / 'agent/settings.json', settings)
        report['pi_version'] = subprocess.check_output(['pi', '--version'], env=env, text=True, timeout=30).strip()
        skill_args = []
        if args.no_skill:
            installed = None
            report['install'] = {'skipped': 'no-skill control arm installs nothing'}
        else:
            install = ['npx', '--yes', 'skills', 'add', str(source), '--skill', 'bi', '-a', 'pi', '--copy', '-y']
            report['install'] = command(install, project, env, root / 'install.log', 180)
            installed = project / '.agents/skills/bi'
            if report['install']['returncode'] or hashes(installed) != report['skill_sha256']:
                raise RuntimeError('skill installation failed or differs from source')
            skill_args = ['--skill', str(installed)]
        shutil.copy2(case / 'task.txt', root / 'prompt.txt')
        shutil.copy2(case / 'workflow-rubric.md', root / 'review.md')
        cmd = ['pi', '--model', args.model, '--thinking', args.thinking, '--mode', 'json', '--print', '--approve',
               '--no-extensions', '--no-mcp', '--no-context-files', '--no-prompt-templates', '--no-skills',
               *skill_args, '--session-dir', str(root / 'sessions'), '--append-system-prompt', TEMP,
               (root / 'prompt.txt').read_text()]
        report['command'] = cmd
        save(root / 'report.json', report)
        report['pi'] = command(cmd, project, env, raw, args.timeout)
        collected = trace(raw, root / 'trace.jsonl', root)
        report['pi'].update(collected)
        if report['pi']['returncode'] or 'incomplete pi session' in collected['errors'] or collected['models'] != [args.model]:
            raise RuntimeError('pi failed, ended incompletely or changed models')
        original = seed['source_files_sha256']
        protected = [p for p in original if p.endswith('_test.go') or '.test.' in p or '.spec.' in p]
        report['changed_original_tests'] = [p for p in protected if not (project / p).is_file() or hashlib.sha256((project / p).read_bytes()).hexdigest() != original[p]]
        if args.no_skill:
            stray = project / '.agents/skills/bi'
            if stray.exists():
                raise RuntimeError('no-skill control arm found an installed bi skill; the control is contaminated')
        elif hashes(installed) != report['skill_sha256']:
            raise RuntimeError('skill changed during execution')
        if hashes(case) != report['case_sha256']:
            raise RuntimeError('independent acceptance changed during execution')
        result = command([sys.executable, str(case / 'acceptance.py'), '--project', str(project), '--output', str(root / 'acceptance'), '--browser'], project, env, root / 'acceptance.log', 3600)
        report['acceptance'] = result
        report['business'] = '通过' if result['returncode'] == 0 and not report['changed_original_tests'] else '未通过'
        report['execution'] = 'complete'
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, KeyboardInterrupt) as exc:
        report['execution'] = 'failed'
        report['error'] = f'{type(exc).__name__}: {exc}'
    finally:
        if raw.exists():
            try:
                report['pi_trace'] = trace(raw, root / 'trace.jsonl', root)
                evidence = compaction_evidence(raw, root / 'sessions')
                save(root / 'compactions.json', evidence)
                report['compaction'] = {k: v for k, v in evidence.items() if k not in ('events', 'entries')}
                if evidence['errors']:
                    report['execution'] = 'failed'
            except (OSError, ValueError) as exc:
                report['evidence_error'] = str(exc)
                report['execution'] = 'failed'
        with (root / 'changes.diff').open('w') as out:
            subprocess.run(['git', 'diff', 'HEAD'], cwd=project, stdout=out, check=False)
        report['git_status'] = subprocess.check_output(['git', 'status', '--short'], cwd=project, text=True)
        save(root / 'report.json', report)
    print(json.dumps({k: report.get(k) for k in ('execution', 'business', 'error', 'compaction')}, ensure_ascii=False, indent=2))
    return 0 if report['execution'] == 'complete' and report['business'] == '通过' else 1


if __name__ == '__main__':
    sys.exit(main())
