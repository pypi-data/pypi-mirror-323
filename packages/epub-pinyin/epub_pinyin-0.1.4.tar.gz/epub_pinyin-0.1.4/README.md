# EPUB Pinyin

A Python tool to add Pinyin annotations above Chinese characters in EPUB files. This tool helps Chinese language learners by automatically adding pronunciation guides to Chinese text while maintaining the EPUB format and structure.

## Features

- Automatically detects Chinese characters in EPUB content
- Adds Pinyin annotations using `<ruby>` tags
- Preserves original EPUB structure and formatting
- Supports tone marks in Pinyin
- Handles complex EPUB structures
- Maintains original file organization
- Processes files in correct spine order

## Installation

You can install the package directly from PyPI:

```bash
pip install epub-pinyin
```

Or install from source:

```bash
git clone https://github.com/tony-develop-2025/epub-pinyin.git
cd epub-pinyin
pip install -e .
```

## Usage

### Command Line

After installation, you can use the tool from the command line:

```bash
epub-pinyin input.epub -o output.epub
```

Or use the module directly:

```bash
python -m epub_pinyin.main input.epub -o output.epub
```

Where:
- `input.epub` is your source EPUB file containing Chinese text
- `-o output.epub` (optional) specifies the output file name (defaults to "input_annotated.epub")

### Python API

You can also use the tool programmatically in your Python code:

```python
from epub_pinyin import process_epub

# Process an EPUB file
process_epub("input.epub", "output.epub")
```

## Example

When rendered in an EPUB reader, the Pinyin appears above each character:
```
 nǐ  hǎo    shì  jiè
你好，世界！
```
![alt text](image.png)

## Requirements

- Python 3.7 or higher
- beautifulsoup4
- pypinyin
- lxml

## Development

To set up the development environment:

1. Clone the repository:
```bash
git clone https://github.com/tony-develop-2025/epub-pinyin.git
cd epub-pinyin
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Run tests:
```bash
pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


