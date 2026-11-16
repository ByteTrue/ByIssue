"""Offline regression checks for evidence collection and the frozen CLI oracle."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import run
import run_repository
from freeze_repository import freeze, inventory
from prepare_rebuild import prepare, remove_functions


class EvidenceTests(unittest.TestCase):
    def collect(self, events):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "raw.jsonl"
            raw.write_text("\n".join(json.dumps(e) for e in events))
            result = run.trace(raw, root / "trace.jsonl", root)
            return result, (root / "trace.jsonl").read_text()

    def events(self, stop="stop"):
        return [
            {"type": "session", "id": "new-session"},
            {"type": "message_update", "delta": "private thought", "usage": {"input": 999}},
            {"type": "tool_execution_start", "toolName": "read", "args": {"path": "SKILL.md"}},
            {"type": "tool_execution_end", "toolName": "read", "result": {"text": "ok"}},
            {"type": "message_end", "message": {"role": "assistant", "provider": "p", "model": "m",
             "stopReason": stop, "usage": {"input": 5, "output": 3, "cacheRead": 2, "cost": {"total": 99}},
             "content": [{"type": "thinking", "thinking": "private thought"}, {"type": "text", "text": "done"}]}},
            {"type": "agent_end", "willRetry": False},
        ]

    def test_usage_counted_once_and_thinking_excluded(self):
        result, transcript = self.collect(self.events())
        self.assertEqual(result["usage"], {"input": 5, "output": 3, "cacheRead": 2})
        self.assertEqual(result["tool_calls"], {"read": 1})
        self.assertEqual(result["errors"], [])
        self.assertNotIn("private thought", transcript)
        self.assertIn("done", transcript)

    def test_truncated_or_error_session_cannot_pass(self):
        for events in (self.events()[:-1], self.events("error"), [], self.events("toolUse")):
            with self.subTest(events=events):
                self.assertTrue(self.collect(events)[0]["errors"])

    def test_invalid_json_cannot_look_like_an_empty_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw").write_text('{"type":')
            with self.assertRaises(json.JSONDecodeError):
                run.trace(root / "raw", root / "trace", root)

    def test_compaction_events_are_kept_without_counting_summary_usage_twice(self):
        events = self.events()
        events[2:2] = [{"type": "compaction_start", "reason": "threshold"},
                       {"type": "compaction_end", "reason": "threshold", "result": {"summary": "checkpoint"}, "aborted": False}]
        result, transcript = self.collect(events)
        self.assertIn('"compaction_start"', transcript)
        self.assertIn('"summary": "checkpoint"', transcript)
        self.assertEqual(result['usage']['input'], 5)

    def test_compaction_requires_matching_persisted_native_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sessions = root / 'sessions'
            sessions.mkdir()
            entry = {'type': 'compaction', 'id': 'c', 'summary': 'checkpoint', 'firstKeptEntryId': 'a', 'tokensBefore': 400100,
                     'usage': {'input': 100, 'output': 10}}
            (sessions / 'one.jsonl').write_text(json.dumps({'type': 'message', 'id': 'a'}) + '\n' + json.dumps(entry))
            events = [{'type': 'compaction_start', 'reason': 'threshold'},
                      {'type': 'compaction_end', 'reason': 'threshold', 'result': {'summary': 'checkpoint'}, 'aborted': False}]
            raw = root / 'raw'
            raw.write_text('\n'.join(map(json.dumps, events)))
            result = run_repository.compaction_evidence(raw, sessions)
            self.assertEqual(result['count'], 1)
            self.assertEqual(result['summary_usage'], {'input': 100, 'output': 10})
            self.assertEqual(result['errors'], [])
            (sessions / 'one.jsonl').write_text(json.dumps({'type': 'message', 'id': 'a'}))
            self.assertIn('compaction events do not match persisted summaries', run_repository.compaction_evidence(raw, sessions)['errors'])
            raw.write_text(json.dumps(events[0]))
            self.assertIn('unfinished compaction attempt', run_repository.compaction_evidence(raw, sessions)['errors'])

    def test_repository_environment_cannot_inherit_live_daemon_or_github_credentials(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'BYSPACE_HOME': '/live', 'BYSPACE_AGENT_ID': 'live', 'E2E_FORK_BYSPACE_HOME_FROM': '/live', 'GH_TOKEN': 'secret', 'GOROOT': '/stale'}):
            env = run.repository_env(Path(tmp))
            self.assertEqual(env['BYSPACE_HOME'], str(Path(tmp) / 'home'))
            self.assertEqual(env['BYSPACE_HOST'], '127.0.0.1:1')
            for key in ('BYSPACE_AGENT_ID', 'E2E_FORK_BYSPACE_HOME_FROM', 'GH_TOKEN', 'GOROOT'):
                self.assertNotIn(key, env)

    def test_failed_command_preserves_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "log"
            result = run.command([sys.executable, "-c", "print('evidence'); raise SystemExit(7)"],
                                 tmp, os.environ, log, 5)
            self.assertEqual(result["returncode"], 7)
            self.assertIn("evidence", log.read_text())

    def test_timeout_leaves_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "log"
            with self.assertRaises(subprocess.TimeoutExpired):
                run.command([sys.executable, "-c", "import time; print('started', flush=True); time.sleep(30)"],
                            tmp, os.environ, log, 0.5)
            self.assertEqual(log.read_text().strip(), "started")

    def test_existing_run_directory_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "keep"
            marker.write_text("evidence")
            result = subprocess.run([sys.executable, str(run.HERE / "run.py"), "--output", tmp, "--model", "p/m"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("output already exists", result.stderr)
            self.assertEqual(marker.read_text(), "evidence")

    def test_oracle_accepts_known_result_and_rejects_noop_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            oracle = run.HERE / "cases/ledger/acceptance.py"
            known = run.ROOT / "byissue/work/v2-readiness/evaluation/ledger-result.py"
            shutil.copy2(known, project / "ledger.py")
            command = [sys.executable, str(oracle), str(project), "2"]
            good = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(good.returncode, 0, good.stderr)
            (project / "ledger.py").write_text("print('done')\n")
            bad = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)

    def test_oracle_rejects_real_cross_session_format_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            bad = run.ROOT / "byissue/work/eval-standardization/evaluation/revision-2-ledger/phase-2/project/ledger.py"
            shutil.copy2(bad, project / "ledger.py")
            oracle = run.HERE / "cases/ledger/acceptance.py"
            result = subprocess.run([sys.executable, str(oracle), str(project), "2"],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PASS: recursive coverage", result.stdout)
            self.assertIn("JSONDecodeError", result.stderr)

    def test_inbox_oracle_rejects_success_without_real_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / 'inbox.py').write_text("print('done')\n")
            oracle = run.HERE / 'cases/webhook-inbox/acceptance.py'
            result = subprocess.run([sys.executable, str(oracle), str(project), '1'],
                                    capture_output=True, text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('service started without a secret', result.stderr)


class RebuildTests(unittest.TestCase):
    def test_function_removal_keeps_neighbors_and_rejects_unknown_names(self):
        source = 'package example\n\nfunc keep() {}\n\nfunc (s *Server) gone[T any](x T) {\n\tif true {\n\t\tuse(x)\n\t}\n}\n\nfunc last() {}\n'
        text, count = remove_functions(source, ['gone'])
        self.assertNotIn('use(x)', text)
        self.assertIn('func keep() {}', text)
        self.assertIn('func last() {}', text)
        self.assertGreater(count, 0)
        with self.assertRaises(ValueError):
            remove_functions(source, ['missing'])

    def test_frozen_rebuild_has_no_history_or_v1_and_keeps_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, case = root / 'repo', root / 'case'
            repo.mkdir(); case.mkdir()
            (repo / 'byissue/issues').mkdir(parents=True)
            (repo / 'byissue/issues/old.md').write_text('v1')
            (repo / 'feature.py').write_text('answer')
            (repo / 'feature_test.py').write_text('assert behavior')
            for args in (['init'], ['add', '.'], ['-c', 'user.name=Test', '-c', 'user.email=test@localhost', '-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'original']):
                subprocess.run(['git', *args], cwd=repo, check=True, capture_output=True)
            corpus = root / 'corpus'
            manifest = freeze(repo, 'HEAD', corpus)
            recipe = {'commit': manifest['commit'], 'branch': 'eval/test', 'remove_files': ['feature.py'], 'remove_implementation_dirs': [], 'remove_functions': {}}
            run.save(case / 'rebuild.json', recipe)
            output = root / 'run'
            result = prepare(corpus, output, case)
            project = output / 'project'
            self.assertFalse((project / 'byissue').exists())
            self.assertFalse((project / 'feature.py').exists())
            self.assertTrue((project / 'feature_test.py').exists())
            self.assertEqual(result['removed_v1_files'], 1)
            self.assertEqual(subprocess.check_output(['git', 'rev-list', '--count', 'HEAD'], cwd=project).strip(), b'1')
            self.assertEqual(inventory(corpus / 'source'), manifest['files_sha256'])
            with self.assertRaises(FileExistsError):
                prepare(corpus, output, case)
            (corpus / 'source/feature.py').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'differs'):
                prepare(corpus, root / 'other', case)


if __name__ == "__main__":
    unittest.main()
