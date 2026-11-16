#!/usr/bin/env python3
"""Run public-boundary probes, frozen regressions and the schedule browser paths."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

CASE = Path(__file__).resolve().parent
sys.path.insert(0, str(CASE.parents[1]))
from run import command, repository_env, save


def accept(project, output, browser=False):
    output.mkdir(parents=True, exist_ok=False)
    env = repository_env(output)
    if Path('/Applications/Google Chrome.app').exists():
        env['E2E_CHANNEL'] = 'chrome'
    results = []

    def check(name, args, cwd=project, timeout=600):
        result = {'name': name, 'command': args}
        results.append(result)
        try:
            result.update(command(args, cwd, env, output / f'{name}.log', timeout))
        except (OSError, subprocess.SubprocessError) as exc:
            result['error'] = str(exc)
        save(output / 'results.json', results)
        print(f"{name}: {result.get('returncode', result.get('error'))}", flush=True)
        return result.get('returncode') == 0

    # The overlay adds a separate package, avoiding private implementation dependencies in old tests.
    probe = project / 'internal/byevaluation'
    probe.mkdir(exist_ok=False)
    try:
        overlay = output / 'overlay.json'
        save(overlay, {'Replace': {str(probe / name): str(CASE / name) for name in ('probe_test.go', 'compat_test.go')}})
        check('independent', ['go', 'test', '-count=1', '-timeout=90s', '-overlay', str(overlay), '-v', './internal/byevaluation'])
    finally:
        probe.rmdir()
    check('schedule-regression', ['go', 'test', '-race', '-count=1', '-timeout=120s', './internal/cadence', './internal/schedule'])
    check('rpc-cli-regression', ['go', 'test', '-count=1', '-timeout=120s', './internal/server', './internal/cli', '-run', 'Schedule|Heartbeat|Scheduled|TestCLIVersionHelpLsRunAndLogs'])
    check('go-build', ['make', 'build'])
    check('go-vet', ['go', 'vet', './internal/cadence', './internal/schedule', './internal/server', './internal/cli'])
    deps = check('app-deps', ['npm', 'run', 'build:app-deps'])
    if deps:
        check('web-unit', ['npm', 'test', '--', 'src/core/schedules', 'src/core/screens/schedules-screen-state', 'src/core/utils/schedule-format', '--bail=1'], project / 'web')
        check('web-types', ['npm', 'run', 'typecheck'], project / 'web')
        built = check('web-build', ['npm', 'run', 'build', '--workspace=@bytetrue/web'])
        relay = check('relay-build', ['npm', 'run', 'build:relay']) if browser else False
        if browser and built and relay:
            check('web-browser', ['npm', 'run', 'test:e2e', '--', 'e2e/browser/schedules-project-target.spec.ts', 'e2e/browser/schedules-edit-model-hydration.spec.ts', '--output', str(output / 'browser-results')], project / 'web', 1200)
            injected = project / 'web/e2e/browser/evaluation-compat.spec.ts'
            with injected.open('x') as out:
                out.write((CASE / 'compat-browser.spec.ts').read_text())
            try:
                check('web-compat', ['npm', 'run', 'test:e2e', '--', 'e2e/browser/evaluation-compat.spec.ts', '--output', str(output / 'compat-browser-results')], project / 'web', 1200)
            finally:
                injected.unlink()
    return all(r.get('returncode') == 0 for r in results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--browser', action='store_true')
    args = parser.parse_args()
    sys.exit(0 if accept(args.project.resolve(), args.output.resolve(), args.browser) else 1)
