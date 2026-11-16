#!/usr/bin/env python3
"""Run a frozen case through fresh pi sessions; keep semantic grading separate."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
# shortcut: TMPDIR is advisory; serialize comparisons until filesystem sandboxing is available.
TEMP = "在当前项目内工作。实验临时文件用 TMPDIR 下的独立临时目录；不读取项目外的评测材料。"


def hashes(directory):
    return {
        p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(directory.rglob("*")) if p.is_file() and "__pycache__" not in p.parts
    }


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def repository_env(root):
    """Keep repository tests away from the developer's daemon and GitHub fixtures."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("BYSPACE_", "E2E_"))}
    for key in ("GOROOT", "GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN"):
        env.pop(key, None)
    for folder in ("tmp", "home", "gh-config"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    env.update(TMPDIR=str(root / "tmp"), BYSPACE_HOME=str(root / "home"),
               BYSPACE_HOST="127.0.0.1:1", BYSPACE_LISTEN="127.0.0.1:1",
               GH_CONFIG_DIR=str(root / "gh-config"), PI_TELEMETRY="0", DISABLE_TELEMETRY="1",
               PYTHONDONTWRITEBYTECODE="1", E2E_VIDEO="off", E2E_WORKERS="1")
    return env


def command(args, cwd, env, output, timeout):
    """Retain output even on failure; stop the whole command group on timeout."""
    start = time.monotonic()
    with output.open("w") as out, Path(str(output) + ".stderr").open("w") as err:
        proc = subprocess.Popen(args, cwd=cwd, env=env, stdout=out, stderr=err, start_new_session=True)
        try:
            code = proc.wait(timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            raise
    return {"returncode": code, "seconds": round(time.monotonic() - start, 2)}


def trace(raw, destination, run_root):
    usage, calls = Counter(), Counter()
    sessions, models, errors = [], set(), []
    messages, ended, last_stop = 0, False, None
    with raw.open(encoding="utf-8") as source, destination.open("w", encoding="utf-8") as out:
        for number, line in enumerate(source, 1):
            if not line.strip():
                continue
            event = json.loads(line)
            kind = event.get("type")
            kept = None
            if kind == "session":
                sessions.append(event["id"])
            elif kind in {"compaction_start", "compaction_end", "agent_settled"}:
                kept = event
            elif kind == "tool_execution_start":
                calls[event["toolName"]] += 1
                kept = event
            elif kind == "tool_execution_end":
                kept = event
            elif kind == "message_end" and event.get("message", {}).get("role") == "assistant":
                msg = event["message"]
                messages += 1
                models.add(f"{msg.get('provider')}/{msg.get('model')}")
                last_stop = msg.get("stopReason")
                if last_stop in {"error", "aborted"}:
                    errors.append(f"line {number}: {last_stop}")
                for key, value in msg.get("usage", {}).items():
                    if isinstance(value, (int, float)):
                        usage[key] += value
                text = [item["text"] for item in msg.get("content", []) if item.get("type") == "text"]
                if text:
                    kept = {"type": "assistant_text", "text": "\n".join(text)}
            elif kind == "agent_end" and not event.get("willRetry"):
                ended = True
            if kept is not None:
                # Raw streams and session files stay local; the review trace excludes thinking/deltas.
                text = json.dumps(kept, ensure_ascii=False).replace(str(run_root), "<run-root>")
                out.write(text + "\n")
    if not ended or not messages or last_stop != "stop" or len(sessions) != 1:
        errors.append("incomplete pi session")
    return {"assistant_messages": messages, "tool_calls": dict(calls), "usage": dict(usage),
            "sessions": sessions, "models": sorted(models), "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT, help="Local repository or frozen source containing skills/bi")
    parser.add_argument("--case", type=Path, default=HERE / "cases/ledger")
    parser.add_argument("--output", type=Path, required=True, help="New run directory outside the repository")
    parser.add_argument("--model", required=True, help="Exact provider/model, not a fuzzy model pattern")
    parser.add_argument("--thinking", default="medium")
    parser.add_argument("--config", type=Path, default=Path.home() / ".pi/agent", help="Use only auth.json and models.json")
    parser.add_argument("--timeout", type=int, default=1200, help="Timeout per pi phase in seconds")
    args = parser.parse_args()
    source, case, output = args.source.resolve(), args.case.resolve(), args.output.resolve()
    skill = source / "skills/bi"
    try:
        prompts = sorted(case.glob("phase-*.txt"), key=lambda p: int(p.stem.split("-")[-1]))
    except ValueError:
        parser.error("phase prompt names must use integer numbers")
    if not (skill / "SKILL.md").is_file() or not all((case / p).exists() for p in ("acceptance.py", "workflow-rubric.md", "project")):
        parser.error("source needs skills/bi; case needs acceptance.py, workflow-rubric.md and project/")
    if not prompts or [p.name for p in prompts] != [f"phase-{i}.txt" for i in range(1, len(prompts) + 1)]:
        parser.error("case needs consecutive phase-1.txt, phase-2.txt, ...")
    if args.timeout <= 0 or "/" not in args.model:
        parser.error("timeout must be positive; model must be provider/model")
    if output.is_relative_to(ROOT) or output.is_relative_to(source) or source.is_relative_to(output):
        parser.error("output must be separate from the repository and source")
    if output.is_relative_to(case) or case.is_relative_to(output):
        parser.error("output must be separate from the case")
    if output.exists():
        parser.error("output already exists; each run needs a fresh directory")
    output.mkdir(parents=True)
    report = {"source": str(source), "case": str(case), "model": args.model, "thinking": args.thinking,
              "skill_sha256": hashes(skill), "case_sha256": hashes(case), "phases": [],
              "execution": "in_progress", "workflow_review": "review.md"}
    env = dict(os.environ, PI_CODING_AGENT_DIR=str(output / "agent"), PI_TELEMETRY="0",
               DISABLE_TELEMETRY="1", PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(output / "tmp"))
    try:
        for folder in ("agent", "tmp", "project"):
            (output / folder).mkdir()
        for name in ("auth.json", "models.json"):
            config = args.config.expanduser().resolve() / name
            if config.is_file():
                (output / "agent" / name).symlink_to(config)
        report["pi_version"] = subprocess.check_output(["pi", "--version"], env=env, text=True, timeout=30).strip()
        project = output / "project"
        install = ["npx", "--yes", "skills", "add", str(source), "--skill", "bi", "-a", "pi", "--copy", "-y"]
        report["install"] = command(install, project, env, output / "install.log", 180)
        installed = project / ".agents/skills/bi"
        if report["install"]["returncode"] or hashes(installed) != report["skill_sha256"]:
            raise RuntimeError("skill installation failed or differs from source")
        shutil.copytree(case / "project", project, dirs_exist_ok=True)
        initial = hashes(case / "project")
        seen_sessions = set()
        shutil.copy2(case / "workflow-rubric.md", output / "review.md")
        save(output / "report.json", report)
        for number, prompt in enumerate(prompts, 1):
            phase = output / f"phase-{number}"
            phase.mkdir()
            text = prompt.read_text(encoding="utf-8")
            (phase / "prompt.txt").write_text(text, encoding="utf-8")
            cmd = ["pi", "--model", args.model, "--thinking", args.thinking, "--mode", "json", "--print",
                   "--approve", "--no-extensions", "--no-mcp", "--no-context-files", "--no-prompt-templates",
                   "--no-skills", "--skill", str(installed), "--session-dir", str(phase / "sessions"),
                   "--append-system-prompt", TEMP, text]
            result = {"phase": number, "command": cmd, "business": "无法判定"}
            report["phases"].append(result)
            save(output / "report.json", report)
            result.update(command(cmd, project, env, phase / "raw.jsonl", args.timeout))
            result.update(trace(phase / "raw.jsonl", phase / "trace.jsonl", output))
            shutil.copytree(project, phase / "project", symlinks=True,
                            ignore=shutil.ignore_patterns(".agents", ".git", "__pycache__", "*.pyc"))
            if result["returncode"] or result["errors"]:
                raise RuntimeError(f"phase {number}: pi failed or stream incomplete")
            if result["models"] != [args.model] or seen_sessions.intersection(result["sessions"]):
                raise RuntimeError("model changed or a session was reused")
            seen_sessions.update(result["sessions"])
            if hashes(installed) != report["skill_sha256"] or hashes(case) != report["case_sha256"]:
                raise RuntimeError("installed skill or independent case was modified during the run")
            result["sources_preserved"] = all(
                (project / p).is_file() and hashlib.sha256((project / p).read_bytes()).hexdigest() == digest
                for p, digest in initial.items()
            )
            acceptance = [sys.executable, str(case / "acceptance.py"), str(project), str(number)]
            result["acceptance"] = command(acceptance, project, env, phase / "acceptance.log", 120)
            passed = result["sources_preserved"] and result["acceptance"]["returncode"] == 0
            result["business"] = "通过" if passed else "未通过"
            save(output / "report.json", report)
            if not passed:
                raise RuntimeError(f"phase {number}: independent acceptance or source preservation failed")
        report["execution"] = "complete"
        print(f"业务验收通过；工作流待审查：{output / 'review.md'}")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, KeyboardInterrupt) as exc:
        report["execution"] = "failed"
        report["error"] = f"{type(exc).__name__}: {exc}"
        print(report["error"], file=sys.stderr)
        return 1
    finally:
        save(output / "report.json", report)


if __name__ == "__main__":
    sys.exit(main())
