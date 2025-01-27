"""Tests for epub_parser module."""

import os
import tempfile
from pathlib import Path
import pytest
from epub_pinyin_adder.epub_parser import EpubParser, MediaType, ManifestItem, EpubMetadata, EpubStructure


@pytest.fixture
def sample_epub_content():
    """Create a minimal valid EPUB structure."""
    return {
        "mimetype": "application/epub+zip",
        "META-INF/container.xml": """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""",
        "OEBPS/content.opf": """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uuid_id" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Test Book</dc:title>
    <dc:language>zh</dc:language>
    <dc:creator>Test Author</dc:creator>
    <dc:publisher>Test Publisher</dc:publisher>
    <dc:identifier>test-id-123</dc:identifier>
  </metadata>
  <manifest>
    <item href="chapter1.xhtml" id="chapter1" media-type="application/xhtml+xml"/>
    <item href="style.css" id="css" media-type="text/css"/>
    <item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine toc="ncx">
    <itemref idref="chapter1"/>
  </spine>
</package>""",
        "OEBPS/chapter1.xhtml": """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body><p>你好，世界！</p></body>
</html>""",
        "OEBPS/style.css": "body { font-family: serif; }",
        "OEBPS/toc.ncx": """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content="test-id-123"/></head>
  <docTitle><text>Test Book</text></docTitle>
  <navMap>
    <navPoint id="chapter1" playOrder="1">
      <navLabel><text>Chapter 1</text></navLabel>
      <content src="chapter1.xhtml"/>
    </navPoint>
  </navMap>
</ncx>"""
    }


@pytest.fixture
def sample_epub(tmp_path, sample_epub_content):
    """Create a sample EPUB file for testing."""
    import zipfile
    
    epub_path = tmp_path / "test.epub"
    
    with zipfile.ZipFile(epub_path, "w") as zf:
        # Write mimetype first, uncompressed
        mimetype_info = zipfile.ZipInfo("mimetype")
        mimetype_info.compress_type = zipfile.ZIP_STORED
        zf.writestr(mimetype_info, sample_epub_content["mimetype"])
        
        # Write other files
        for name, content in sample_epub_content.items():
            if name != "mimetype":
                zf.writestr(name, content)
    
    return epub_path


def test_epub_parser_initialization():
    """Test EpubParser initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        parser = EpubParser(tmpdir)
        assert parser.extract_dir == os.path.abspath(tmpdir)
        assert parser.structure is None


def test_epub_extraction(sample_epub):
    """Test EPUB extraction and structure parsing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        parser = EpubParser(tmpdir)
        parser.extract_epub(sample_epub)
        
        assert parser.structure is not None
        assert parser.structure.metadata.title == "Test Book"
        assert parser.structure.metadata.language == "zh"
        assert len(parser.structure.html_items) == 1
        assert len(parser.structure.css_items) == 1
        assert parser.structure.ncx_item is not None


def test_get_html_files(sample_epub):
    """Test getting HTML files in spine order."""
    with tempfile.TemporaryDirectory() as tmpdir:
        parser = EpubParser(tmpdir)
        parser.extract_epub(sample_epub)
        
        html_files = parser.get_html_files()
        assert len(html_files) == 1
        assert html_files[0].endswith("chapter1.xhtml")


def test_get_css_files(sample_epub):
    """Test getting CSS files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        parser = EpubParser(tmpdir)
        parser.extract_epub(sample_epub)
        
        css_files = parser.get_css_files()
        assert len(css_files) == 1
        assert css_files[0].endswith("style.css")


def test_get_ncx_file(sample_epub):
    """Test getting NCX file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        parser = EpubParser(tmpdir)
        parser.extract_epub(sample_epub)
        
        ncx_file = parser.get_ncx_file()
        assert ncx_file is not None
        assert ncx_file.endswith("toc.ncx")


def test_invalid_epub():
    """Test handling of invalid EPUB without content.opf."""
    with tempfile.TemporaryDirectory() as tmpdir:
        epub_path = Path(tmpdir) / "invalid.epub"
        with open(epub_path, "wb") as f:
            f.write(b"invalid content")
        
        parser = EpubParser(tmpdir)
        with pytest.raises(ValueError, match="No content.opf found"):
            parser.extract_epub(epub_path) 