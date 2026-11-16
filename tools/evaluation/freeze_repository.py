#!/usr/bin/env python3
"""Export a committed repository into a standalone, fingerprinted evaluation corpus."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile


def inventory(root):
    files = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'corpus must contain ordinary files: {path}')
        if path.is_file():
            files[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def freeze(repository, revision, output):
    repository, output = repository.resolve(), output.resolve()
    if output.is_relative_to(repository) or repository.is_relative_to(output):
        raise ValueError('corpus must be separate from the source repository')
    commit = subprocess.check_output(
        ['git', 'rev-parse', '--verify', f'{revision}^{{commit}}'], cwd=repository, text=True,
    ).strip()
    output.mkdir(parents=True, exist_ok=False)
    archive = output / 'source.tar'
    subprocess.run(['git', 'archive', '--format=tar', '-o', str(archive), commit],
                   cwd=repository, check=True)
    source = output / 'source'
    source.mkdir()
    with tarfile.open(archive) as bundle:
        for member in bundle:
            target = (source / member.name).resolve()
            if not target.is_relative_to(source) or not (member.isfile() or member.isdir()):
                raise ValueError(f'unsupported archive member: {member.name}')
        bundle.extractall(source, filter='data')
    files = inventory(source)
    code = [source / p for p in files if Path(p).suffix in {'.ts', '.tsx', '.go', '.mjs', '.js'}]
    manifest = {
        'repository': repository.name, 'commit': commit,
        'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'files_sha256': files, 'file_count': len(files), 'source_file_count': len(code),
        'source_lines': sum(len(p.read_bytes().splitlines()) for p in code),
        'bytes': sum((source / p).stat().st_size for p in files),
    }
    (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--revision', default='HEAD')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    manifest = freeze(args.repo, args.revision, args.output)
    print(json.dumps({k: v for k, v in manifest.items() if k != 'files_sha256'}, indent=2))
