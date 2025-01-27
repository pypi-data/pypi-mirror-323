import unittest

from html_scrubber import clean_html


class TestHTMLCleaner(unittest.TestCase):
    def test_clean_html(self):
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
        cleaned_html = clean_html(
            html_content=raw_html,
            remove_styles=True,
            remove_scripts=True,
            remove_iframes=True,
            return_as_string=True,
        )

        assert "<style>" not in cleaned_html
        assert "<script>" not in cleaned_html
        assert "<iframe>" not in cleaned_html
        assert "<div>" in cleaned_html

    def test_clean_html_remove_svg(self):
        html = """
    <html>
      <body>
        <svg width="100" height="100">
          <circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" />
        </svg>
        <div>Test content</div>
      </body>
    </html>
    """
        cleaned = clean_html(html, remove_svgs=True, return_as_string=True)
        assert "<svg" not in cleaned
        assert "<div>" in cleaned

    def test_clean_html_remove_noscript(self):
        html = """
    <html>
      <body>
        <noscript>JavaScript is required</noscript>
        <div>Test content</div>
      </body>
    </html>
    """
        cleaned = clean_html(html, remove_noscripts=True, return_as_string=True)
        assert "<noscript>" not in cleaned
        assert "<div>" in cleaned

    def test_clean_html_remove_meta(self):
        html = """
        <html>
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width">
          </head>
          <body>
            <div>Test content</div>
          </body>
        </html>
        """
        cleaned = clean_html(html, remove_metas=True, return_as_string=True)
        assert "<meta" not in cleaned
        assert "<div>" in cleaned

    def test_clean_html_additional_tags(self):
        html = """
    <html>
      <body>
        <custom>Custom tag</custom>
        <div>Test content</div>
        <span>Keep this</span>
      </body>
    </html>
    """
        cleaned = clean_html(
            html, tags=["custom", "div"], return_as_string=True
        )
        assert "<custom>" not in cleaned
        assert "<div>" not in cleaned
        assert "<span>" in cleaned

    def test_clean_html_return_soup(self):
        html = "<div>Test content</div>"
        cleaned = clean_html(html, return_as_string=False)
        assert str(cleaned) == "<div>Test content</div>"
        assert "BeautifulSoup" in str(type(cleaned))

    def test_clean_html_empty_content(self):
        with self.assertRaises(ValueError):
            clean_html("")

    def test_clean_html_invalid_content(self):
        with self.assertRaises(ValueError):
            clean_html(123)

    def test_clean_html_invalid_bool_params(self):
        with self.assertRaises(ValueError):
            clean_html("test", remove_styles="test")

    def test_clean_html_invalid_additional_tags(self):
        with self.assertRaises(ValueError):
            clean_html("test", tags="test")

    def test_clean_html_invalid_additional_tags_elements(self):
        with self.assertRaises(ValueError):
            clean_html("test", tags=[123])


if __name__ == "__main__":
    unittest.main()
