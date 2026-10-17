"""Verify review readiness, not product behavior; never run relocated tests."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def main():
    package = json.loads((HERE / 'REVIEW_PACKAGE.json').read_text(encoding='utf-8'))
    assert (ROOT / '.git').is_dir(), 'Wrong repository root'
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    assert head == package['base_commit'], 'HEAD changed: refresh package before review'
    for entry in package['files']:
        path = (ROOT / entry['path']).resolve()
        assert path.is_relative_to(ROOT), 'Path escapes repository'
        assert path.is_file(), f'Missing canonical file: {entry["path"]}'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], f'Changed file: {entry["path"]}'
    assert all('snapshot/' not in command for command in package['allowed_test_commands'])
    result = {'status': 'READY', 'base_commit': head,
              'verified_files': len(package['files']),
              'root_marker_checks': ['.git', 'electre3', 'app', 'tests'],
              'production_tests_executed': False,
              'reviewer_retries_executed': False,
              'limitation': 'Local paths and hashes only; agent access and browser behavior not verified.'}
    for name in result['root_marker_checks']:
        assert (ROOT / name).is_dir(), f'Missing root marker: {name}'
    (HERE / 'PACKAGE_READINESS.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
