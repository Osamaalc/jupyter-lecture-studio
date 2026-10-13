"""Build and bundle the public offline documentation using Sphinx."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
DESTINATION = ROOT / 'src/jupyter_lecture_studio/docs'
BUILD = ROOT / 'build/public-docs'


def build():
    subprocess.run([sys.executable, '-m', 'sphinx', '-E', '-a', '-b', 'html', '-W', '--keep-going', str(ROOT / 'docs'), str(BUILD)], check=True)
    if DESTINATION.exists():
        shutil.rmtree(DESTINATION)
    DESTINATION.mkdir(parents=True, exist_ok=True)
    # Only replace files in the generated documentation directory.
    for item in BUILD.iterdir():
        if item.name in ('.doctrees', '.buildinfo', '.buildinfo.bak'):
            continue
        target = DESTINATION / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
    print(DESTINATION / 'index.html')

if __name__ == '__main__':
    build()
