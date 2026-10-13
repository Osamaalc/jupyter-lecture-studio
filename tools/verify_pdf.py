"""Verify a faithful PDF against its actual browser PNG reference pages.

Needs pypdf and Pillow. This measures embedded pixels, independent of viewers.
"""
import argparse
from io import BytesIO
import json
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


def verify(pdf_path, audit_dir, viewer_raster=False):
    manifest=json.loads((audit_dir/'manifest.json').read_text())
    if manifest['mode'] != 'faithful':
        raise ValueError('Exact embedded-pixel verification applies to faithful mode')
    reader=PdfReader(pdf_path)
    viewer=None
    if viewer_raster:
        import pymupdf
        viewer=pymupdf.open(pdf_path)
    assert len(reader.pages)==len(manifest['pages']), 'Page count mismatch'
    results=[]
    for i,(page,region) in enumerate(zip(reader.pages,manifest['pages'],strict=False),1):
        reference=Image.open(audit_dir/f'page-{i:03d}.png').convert('RGB')
        images=list(page.images)
        assert len(images)==1, f'Page {i}: expected one lossless page image'
        embedded=Image.open(BytesIO(images[0].data)).convert('RGB')
        assert reference.size==embedded.size, f'Page {i}: image dimensions changed'
        identical=reference.tobytes()==embedded.tobytes()
        assert identical, f'Page {i}: screen pixels changed inside PDF'
        assert abs(float(page.mediabox.width)-manifest['width']*.75)<.01
        assert abs(float(page.mediabox.height)-region['height']*.75)<.01
        entry={'page':i,'title':region['title'],'pixels':list(reference.size),'embedded_pixels_identical':identical}
        if viewer is not None:
            factor=manifest['scale']*96/72
            pix=viewer[i-1].get_pixmap(matrix=pymupdf.Matrix(factor,factor),alpha=False)
            rendered=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
            entry['pymupdf_pixels_identical']=rendered.size==reference.size and rendered.tobytes()==reference.tobytes()
            assert entry['pymupdf_pixels_identical'], f'Page {i}: viewer raster differs'
        results.append(entry)
    report={'pdf':pdf_path.name,'pages':len(results),'fonts':manifest['fonts'],
        'browser':manifest['browser'],'width':manifest['width'],'scale':manifest['scale'],
        'comparison':'Decoded RGB pixels in the PDF image versus browser reference PNG, all pages',
        'identical_pages':len(results),'results':results,
        'limits':'Measures the static captured screen at this width and scale; does not certify every PDF viewer, arbitrary content or printing device.'}
    if viewer is not None:
        report['viewer']={'name':'PyMuPDF','version':pymupdf.VersionBind,'identical_pages':len(results),'scale':manifest['scale']*96/72}
        viewer.close()
    (audit_dir/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(f'{pdf_path.name}: {len(results)}/{len(results)} pages have 100% identical embedded RGB pixels.')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf',type=Path);parser.add_argument('audit_dir',type=Path)
    parser.add_argument('--viewer-raster',action='store_true',help='Also compare PyMuPDF rasterization at the native image resolution (requires PyMuPDF)')
    args=parser.parse_args();verify(args.pdf,args.audit_dir,args.viewer_raster)
