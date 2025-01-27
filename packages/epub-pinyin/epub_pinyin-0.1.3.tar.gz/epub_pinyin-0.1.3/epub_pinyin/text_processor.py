"""Module for processing text and adding pinyin annotations."""

from bs4 import BeautifulSoup
from pypinyin import pinyin, Style
from typing import List, Tuple


def is_chinese_char(char: str) -> bool:
    """Check if a character is a Chinese character.
    
    Args:
        char: Single character to check
        
    Returns:
        True if the character is in the CJK Unified Ideographs range
    """
    return '\u4e00' <= char <= '\u9fff'


def get_pinyin_for_char(char: str) -> str:
    """Get the pinyin with tone marks for a Chinese character.
    
    Args:
        char: Chinese character to convert
        
    Returns:
        Pinyin string with tone marks
    """
    py_list = pinyin(char, style=Style.TONE, heteronym=False)
    return py_list[0][0] if py_list else char


def create_xhtml_content(title: str, content: str) -> str:
    """Create a properly formatted XHTML content with pinyin annotations.
    
    Args:
        title: Title of the XHTML document
        content: Content to be processed
        
    Returns:
        Complete XHTML document as string
    """
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">
<head>
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
{content}
</body>
</html>"""


def annotate_text_with_pinyin(text: str) -> str:
    """Add pinyin annotations to Chinese characters in text.
    
    Args:
        text: Text containing Chinese characters
        
    Returns:
        Text with pinyin annotations in ruby tags
    """
    result = []
    for char in text:
        if is_chinese_char(char):
            pinyin_text = get_pinyin_for_char(char)
            result.append(f"<ruby>{char}<rt>{pinyin_text}</rt></ruby>")
        else:
            result.append(char)
    return "".join(result)


def process_html_content(content: str) -> Tuple[str, str]:
    """Process HTML content and extract title and body.
    
    Args:
        content: Original HTML content
        
    Returns:
        Tuple of (title, processed_body)
    """
    soup = BeautifulSoup(content, "lxml")
    
    # Get title
    title_tag = soup.find('title')
    title = title_tag.string if title_tag else "Untitled"
    
    # Process body content
    body = soup.find('body')
    if not body:
        return title, "<p>No content</p>"
        
    processed_content = []
    for element in body.children:
        if element.name:  # If it's a tag
            if element.name in ['script', 'style', 'rt', 'h1']:
                continue
            # Process text within the tag
            for text in element.find_all(text=True, recursive=True):
                if text.parent.name != 'rt':  # Skip if already in rt tag
                    annotated = annotate_text_with_pinyin(text)
                    text.replace_with(BeautifulSoup(annotated, 'lxml'))
        elif element.string and element.string.strip():  # If it's a text node
            annotated = annotate_text_with_pinyin(element.string)
            element.replace_with(BeautifulSoup(annotated, 'lxml'))
            
    return title, str(body)


def annotate_file_with_pinyin(html_filepath: str) -> None:
    """Process an HTML file and add pinyin annotations to Chinese characters.
    
    Args:
        html_filepath: Path to the HTML file to process
    """
    with open(html_filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title, processed_body = process_html_content(content)
    new_content = create_xhtml_content(title, processed_body)
    
    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(new_content) 