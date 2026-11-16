#!/usr/bin/env python3
"""Create a standalone feature-rebuild branch with no answer in its Git history."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess

from freeze_repository import inventory
from run import HERE, ROOT, save


def remove_functions(text, names):
    removed = 0
    for name in names:
        pattern = rf"^func (?:\([^\n]*\) )?{re.escape(name)}(?:\[[^\n]*\])?\([^\n]*"
        matches = list(re.finditer(pattern, text, re.MULTILINE))
        if len(matches) != 1:
            raise ValueError(f"expected one function {name}, found {len(matches)}")
        start = matches[0].start()
        end = re.search(r"^}\s*$", text[matches[0].end():], re.MULTILINE)
        if not end:
            raise ValueError(f"missing closing brace: {name}")
        stop = matches[0].end() + end.end()
        removed += len(text[start:stop].splitlines())
        text = text[:start] + text[stop:]
    return text, removed


def copy_dependencies(donor, project):
    # macOS clonefile gives independent copy-on-write files; workspace symlinks remain relative.
    locations = [Path("node_modules"), Path("web/node_modules")]
    locations += [p.relative_to(donor) for p in (donor / "packages").glob("*/node_modules")]
    for relative in locations:
        if (donor / relative).is_dir():
            (project / relative).parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["cp", "-cR", str(donor / relative), str(project / relative)], check=True)


def prepare(corpus, output, case):
    corpus, output = corpus.resolve(), output.resolve()
    if any(output.is_relative_to(p) or p.is_relative_to(output) for p in (corpus, ROOT)):
        raise ValueError("output must be separate from the corpus and ByIssue")
    manifest = json.loads((corpus / "manifest.json").read_text())
    recipe = json.loads((case / "rebuild.json").read_text())
    if manifest["commit"] != recipe["commit"] or inventory(corpus / "source") != manifest["files_sha256"]:
        raise ValueError("corpus commit or content differs from the frozen case")
    output.mkdir(parents=True, exist_ok=False)
    project = output / "project"
    shutil.copytree(corpus / "source", project)
    removed_history = inventory(project / "byissue")
    shutil.rmtree(project / "byissue")
    paths = [Path(p) for p in recipe["remove_files"]]
    for folder in recipe["remove_implementation_dirs"]:
        paths += [p.relative_to(project) for p in (project / folder).iterdir()
                  if p.suffix in {".ts", ".tsx"} and ".test." not in p.name]
    removed_lines = 0
    for relative in paths:
        path = project / relative
        removed_lines += len(path.read_text().splitlines())
        path.unlink()
    for relative, names in recipe["remove_functions"].items():
        path = project / relative
        text, count = remove_functions(path.read_text(), names)
        path.write_text(text)
        removed_lines += count
        subprocess.run(["gofmt", "-w", str(path)], check=True)
    for args in (["init", "-b", recipe["branch"]], ["add", "."],
                 ["-c", "user.name=ByIssue Evaluation", "-c", "user.email=evaluation@localhost",
                  "-c", "core.hooksPath=/dev/null", "commit", "-m", "test: seed schedule rebuild benchmark"]):
        subprocess.run(["git", *args], cwd=project, check=True, capture_output=True)
    seed = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=project, text=True).strip()
    result = {"corpus_commit": manifest["commit"], "branch": recipe["branch"], "seed_commit": seed,
              "removed_files": sorted(str(p) for p in paths), "removed_functions": recipe["remove_functions"],
              "removed_implementation_lines": removed_lines, "removed_v1_files": len(removed_history),
              "source_files_sha256": manifest["files_sha256"]}
    save(output / "seed.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dependencies-from", type=Path)
    parser.add_argument("--case", type=Path, default=HERE / "cases/byspace-schedules")
    args = parser.parse_args()
    result = prepare(args.corpus, args.output, args.case)
    if args.dependencies_from:
        donor = args.dependencies_from.resolve()
        project = args.output.resolve() / "project"
        if (donor / "package-lock.json").read_bytes() != (project / "package-lock.json").read_bytes():
            raise ValueError("dependency donor lockfile does not match corpus")
        copy_dependencies(donor, project)
    print(json.dumps({k: v for k, v in result.items() if k != "source_files_sha256"}, ensure_ascii=False, indent=2))
