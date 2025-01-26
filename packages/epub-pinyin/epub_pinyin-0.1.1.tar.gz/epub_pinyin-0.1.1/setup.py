"""Setup configuration for epub-pinyin."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="epub-pinyin",
    version="0.1.1",
    author="Tony",
    author_email="tony.develop.2025@gmail.com",
    description="Add Pinyin annotations to Chinese text in EPUB files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tony-develop-2025/epub-pinyin",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Processing :: Markup :: XML",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "beautifulsoup4>=4.12.0",
        "pypinyin>=0.49.0",
        "lxml>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "epub-pinyin=epub_pinyin.main:main",
        ],
    },
) 