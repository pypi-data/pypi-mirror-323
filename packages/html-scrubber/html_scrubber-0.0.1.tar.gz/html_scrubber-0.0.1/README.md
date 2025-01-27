# html-cleaner

`html-cleaner` is a simple Python library built with BeautifulSoup that allows you to clean HTML content by removing unwanted tags such as styles, scripts, iframes, and more. It's ideal for web scraping, data extraction, or sanitizing HTML content before further processing.

## Features

- Clean HTML content by removing unnecessary elements
- Supports removal of `<style>`, `<script>`, `<iframe>`, `<svg>`, `<meta>`, and `<noscript>` tags
- Easily extendable with custom tags to remove
- Option to return the cleaned HTML as a BeautifulSoup object or a plain string

## Installation

To install `html-cleaner`, you can use pip:

```bash
pip install html-cleaner
```

## Usage

Here is an example of how to use the `html-cleaner` library to clean HTML content:

```python
from html_cleaner import clean_html

raw_html = """
<html>
    <head><style>body {color: red;}</style></head>
    <body>
        <script>alert("test");</script>
        <div>Test content</div>
        <iframe src="https://example.com"></iframe>
    </body>
</html>
"""

# Clean the HTML content by removing style, script, and iframe tags
cleaned_html = clean_html(
    html_content=raw_html,
    remove_styles=True,
    remove_scripts=True,
    remove_iframes=True,
    return_as_string=True,
)