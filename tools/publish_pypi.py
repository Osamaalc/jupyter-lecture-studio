"""Publish a checked release using a token held only in process memory."""
import argparse
import getpass
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='Directory containing exactly one wheel and one source archive')
    parser.add_argument('--token-file', type=Path, help='Read a restricted temporary token file outside the project; never pass a token as an argument')
    args = parser.parse_args()
    wheels = list(args.directory.glob('jupyter_lecture_studio-*.whl'))
    sources = list(args.directory.glob('jupyter_lecture_studio-*.tar.gz'))
    if len(wheels) != 1 or len(sources) != 1:
        parser.error('Expected exactly one matching wheel and one source archive')
    files = [str(p.resolve()) for p in wheels + sources]
    subprocess.run([sys.executable, '-m', 'twine', 'check', '--strict', *files], check=True)
    if args.token_file:
        token_path = args.token_file.resolve()
        project = Path(__file__).resolve().parent.parent
        if token_path.is_relative_to(project):
            parser.error('Keep credential files outside the project')
        if os.name == 'posix' and token_path.stat().st_mode & 0o077:
            parser.error('Token file must have mode 0600')
        token = token_path.read_text().strip()
    else:
        token = getpass.getpass('PyPI API token (input hidden): ').strip()
    if not token.startswith('pypi-'):
        parser.error('Expected a PyPI API token, not an account password')
    env = os.environ.copy()
    env.update(TWINE_USERNAME='__token__', TWINE_PASSWORD=token, TWINE_NON_INTERACTIVE='1')
    result = subprocess.run([sys.executable, '-m', 'twine', 'upload', '--repository-url', 'https://upload.pypi.org/legacy/', '--disable-progress-bar', *files], env=env)
    raise SystemExit(result.returncode)

if __name__ == '__main__':
    main()
