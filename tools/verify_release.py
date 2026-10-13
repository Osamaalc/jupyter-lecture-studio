"""Inspect the actual wheel/sdist contents before publishing."""
import argparse
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path
import re
import tarfile
import zipfile


def verify(directory):
    wheels = list(directory.glob('jupyter_lecture_studio-*.whl'))
    sources = list(directory.glob('jupyter_lecture_studio-*.tar.gz'))
    assert len(wheels) == len(sources) == 1, 'Expected one wheel and one source archive'
    with zipfile.ZipFile(wheels[0]) as archive:
        data = {name: archive.read(name) for name in archive.namelist() if not name.endswith('/')}
    metadata = BytesParser().parsebytes(next(value for name, value in data.items() if name.endswith('.dist-info/METADATA')))
    assert metadata['Name'] == 'jupyter-lecture-studio'
    assert re.fullmatch(r'\d+\.\d+\.\d+((a|b|rc)\d+|\.dev\d+)?', metadata['Version']), metadata['Version']
    assert metadata['Requires-Python'] == '>=3.10'
    assert metadata['Description-Content-Type'] == 'text/markdown'
    assert metadata['License-Expression'] == 'MIT AND OFL-1.1 AND BSD-2-Clause'
    assert len(metadata.get_all('License-File')) >= 7
    assert all('extra ==' in item for item in metadata.get_all('Requires-Dist', [])), 'Unexpected mandatory dependency'
    if metadata['Version'] != '0.2.0':
        assert 'pdf' in metadata.get_all('Provides-Extra', [])
        assert 'lecture_studio/pdf.py' in data
        assert 'jupyter_lecture_studio/docs/pdf.html' in data
    if not metadata['Version'].startswith('0.'):
        for name in ['lecture_studio/assets/studio.css', 'lecture_studio/assets/present.css', 'lecture_studio/assets/present.js',
                     'lecture_studio/i18n.py', 'lecture_studio/themes.py', 'lecture_studio/components/teaching.py',
                     'lecture_studio/py.typed', 'jupyter_lecture_studio/docs/components.html',
                     'jupyter_lecture_studio/docs/themes.html', 'jupyter_lecture_studio/docs/languages.html']:
            assert name in data, name
    for name in ['lecture_studio/__init__.py','jupyter_lecture_studio/__init__.py',
                 'jupyter_lecture_studio/docs/index.html','jupyter_lecture_studio/docs/USAGE_AR.html',
                 'jupyter_lecture_studio/docs/reference.html','jupyter_lecture_studio/docs/searchindex.js',
                 'jupyter_lecture_studio/docs/_static/licenses/Sphinx-LICENSE.txt']:
        assert name in data, name
    reference = data['jupyter_lecture_studio/docs/reference.html']
    assert b'.. py:class::' not in reference and b'id="lecture_studio.LectureDeck.cover"' in reference, 'API reference did not render'
    assert b'direction:rtl' in data['jupyter_lecture_studio/docs/USAGE_AR.html'], 'Arabic RTL missing'
    manifest = json.loads(data['lecture_studio/assets/fonts/manifest.json'])
    for item in manifest['files']:
        assert hashlib.sha256(data['lecture_studio/assets/fonts/' + item['file']]).hexdigest() == item['sha256']
    with tarfile.open(sources[0]) as archive:
        source_data = {member.name: archive.extractfile(member).read() for member in archive.getmembers() if member.isfile()}
    for collection in [data, source_data]:
        for name, value in collection.items():
            assert not any(part in name for part in ['revision_backup/', 'design-audit/', 'pdf-audit/', '.pypirc', '.doctrees/', '.buildinfo', 'DESIGN_PARITY.md', 'VERIFICATION.md']), name
            assert str(Path.home()).encode() not in value, 'Private machine path: ' + name
            assert not re.search(rb'pypi-[A-Za-z0-9_-]{50,}', value), 'Credential-like content: ' + name
    for path in wheels + sources:
        print(f'{path.name}: {path.stat().st_size:,} bytes; SHA256 {hashlib.sha256(path.read_bytes()).hexdigest()}')
    print(f'Checked {len(data)} wheel files and {len(source_data)} source files; fonts, documentation, licenses and metadata passed.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    verify(parser.parse_args().directory)
