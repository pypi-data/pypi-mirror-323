"""Tests for text_processor module."""

import os
import tempfile
import pytest
from epub_pinyin_adder.text_processor import annotate_file_with_pinyin


@pytest.fixture
def sample_html_content():
    """Create sample HTML content for testing."""
    return """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">
<head>
  <title>测试</title>
  <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
  <h1>你好，世界！</h1>
  <p>这是一个测试。</p>
  <div>
    <p>更多的<span>中文</span>文本。</p>
  </div>
</body>
</html>"""


def test_annotate_file_with_pinyin(sample_html_content):
    """Test adding pinyin annotations to HTML file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = os.path.join(tmpdir, "test.xhtml")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(sample_html_content)
        
        # Process the file
        annotate_file_with_pinyin(test_file)
        
        # Read and verify the result
        with open(test_file, "r", encoding="utf-8") as f:
            result = f.read()
        
        # Check that all Chinese characters have pinyin annotations
        assert '<ruby>你<rt>nǐ</rt></ruby>' in result
        assert '<ruby>好<rt>hǎo</rt></ruby>' in result
        assert '<ruby>世<rt>shì</rt></ruby>' in result
        assert '<ruby>界<rt>jiè</rt></ruby>' in result
        assert '<ruby>测<rt>cè</rt></ruby>' in result
        assert '<ruby>试<rt>shì</rt></ruby>' in result
        assert '<ruby>中<rt>zhōng</rt></ruby>' in result
        assert '<ruby>文<rt>wén</rt></ruby>' in result
        
        # Check that non-Chinese text is unchanged
        assert '，' in result  # Punctuation should be preserved
        assert '！' in result  # Punctuation should be preserved
        assert '。' in result  # Punctuation should be preserved
        
        # Check that HTML structure is preserved
        assert '<h1>' in result
        assert '</h1>' in result
        assert '<p>' in result
        assert '</p>' in result
        assert '<div>' in result
        assert '</div>' in result
        assert '<span>' in result
        assert '</span>' in result


def test_annotate_file_with_pinyin_empty_file():
    """Test handling of empty file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "empty.xhtml")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("")
        
        with pytest.raises(ValueError):
            annotate_file_with_pinyin(test_file)


def test_annotate_file_with_pinyin_no_chinese():
    """Test handling of file without Chinese characters."""
    content = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html><body><p>Hello, World!</p></body></html>"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "no_chinese.xhtml")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        annotate_file_with_pinyin(test_file)
        
        with open(test_file, "r", encoding="utf-8") as f:
            result = f.read()
        
        # Content should be unchanged
        assert result == content


def test_annotate_file_with_pinyin_mixed_content():
    """Test handling of mixed Chinese and non-Chinese content."""
    content = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html><body><p>Hello 你好 World 世界！</p></body></html>"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "mixed.xhtml")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        annotate_file_with_pinyin(test_file)
        
        with open(test_file, "r", encoding="utf-8") as f:
            result = f.read()
        
        # Check that only Chinese characters are annotated
        assert "Hello" in result
        assert "World" in result
        assert '<ruby>你<rt>nǐ</rt></ruby>' in result
        assert '<ruby>好<rt>hǎo</rt></ruby>' in result
        assert '<ruby>世<rt>shì</rt></ruby>' in result
        assert '<ruby>界<rt>jiè</rt></ruby>' in result 