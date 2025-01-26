"""Main entry point for the EPUB Pinyin Adder application."""

import argparse
import os
import sys
import tempfile
from typing import Optional

from . import epub_parser
from . import text_processor


def process_epub(input_path: str, output_path: Optional[str] = None) -> None:
    """Process an EPUB file to add pinyin annotations.
    
    Args:
        input_path: Path to the input EPUB file
        output_path: Path where the annotated EPUB will be saved (optional)
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist")
        sys.exit(1)

    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_annotated{ext}"

    # Create a temporary directory for extraction
    with tempfile.TemporaryDirectory() as extract_dir:
        try:
            # Initialize EPUB parser
            epub = epub_parser.EpubParser(extract_dir)

            print(f"Extracting {input_path}...")
            try:
                epub.extract_epub(input_path)
            except ValueError as e:
                print(f"Error: {str(e)}")
                sys.exit(1)

            print("Finding HTML files...")
            html_files = epub.get_html_files()

            if not html_files:
                print("Warning: No HTML files found in EPUB")
            else:
                print(f"Processing {len(html_files)} HTML files...")
                for html_file in html_files:
                    print(f"  Annotating {os.path.basename(html_file)}...")
                    text_processor.annotate_file_with_pinyin(html_file)

            print(f"Creating annotated EPUB: {output_path}")
            epub.package_epub(output_path)
            
            print("Done!")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)


def main() -> None:
    """Main entry point for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Add pinyin annotations to Chinese text in EPUB files"
    )
    parser.add_argument(
        "input_epub",
        help="Path to the input EPUB file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output EPUB file name (default: input_annotated.epub)",
        default=None
    )

    args = parser.parse_args()
    process_epub(args.input_epub, args.output)


if __name__ == "__main__":
    # process_epub("/Users/tony/Documents/GitHub/app_ideas/epub_pinyin_adder/test.epub", "/Users/tony/Documents/GitHub/app_ideas/epub_pinyin_adder/test_pinyin.epub")
    main()
