import unittest
from crawl import (
    normalize_url,
    get_heading_from_html,
    get_first_paragraph_from_html,
    get_urls_from_html,
    get_images_from_html,
    extract_page_data,
)


class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)
    def test_normalize_url_with_slash(self):
        input_url = "https://www.boot.dev/blog/path/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)
    def test_http_with_slash(self):
        input_url = "http://www.boot.dev/blog/path/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)
    def test_http_without_slash(self):
        input_url = "http://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)
    def test_url_capital(self):
        input_url = "HTTPS://WWW.BOOT.DEV/BLOG/PATH"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)
    def test_normalize_url_root(self):
        input_url = "https://boot.dev/"
        actual = normalize_url(input_url)
        expected = "boot.dev"
        self.assertEqual(actual, expected)
    def test_get_heading_from_html_h1_exists(self):
        # Situation 1: <h1> exists -> should return its text
        input_body = "<html><body><h1>Main Heading</h1><p>Some content</p></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Main Heading"
        self.assertEqual(actual, expected)
    def test_get_heading_from_html_fallback_h2(self):
        # Situation 2: No <h1>, but <h2> exists -> should return <h2> text as fallback
        input_body = "<html><body><h2>Fallback Subtitle</h2><p>Some content</p></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Fallback Subtitle"
        self.assertEqual(actual, expected)
    def test_get_heading_from_html_neither_exists(self):
        # Situation 3: Neither <h1> nor <h2> exists -> should return an empty string
        input_body = "<html><body><p>Just a paragraph with no heading tags.</p></body></html>"
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)
    def test_get_first_paragraph_from_html_main_with_p(self):
        # Situation 1: <main> exists with a <p> inside -> returns that text
        input_body = "<html><body><main><p>First paragraph in main.</p></main></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = "First paragraph in main."
        self.assertEqual(actual, expected)
    def test_get_first_paragraph_from_html_main_empty(self):
        # Situation 2: <main> exists but is empty of <p> -> returns ""
        input_body = "<html><body><main><div>Just a div, no paragraph here.</div></main></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)
    def test_get_first_paragraph_from_html_no_main_but_p(self):
        # Situation 3: No <main>, but a <p> exists somewhere -> returns that text (fallback)
        input_body = "<html><body><div><p>Paragraph outside main.</p></div></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = "Paragraph outside main."
        self.assertEqual(actual, expected)
    def test_get_first_paragraph_from_html_neither(self):
        # Situation 4: Neither <main> nor <p> exists -> returns ""
        input_body = "<html><body><div><span>Just some generic text, no tags.</span></div></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)
    def test_get_urls_from_html_relative(self):
        # Scenario 1: Converts a relative URL into an absolute URL using the base_url
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/about"><span>About</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/about"]
        self.assertEqual(actual, expected)
    def test_get_urls_from_html_multiple(self):
        # Scenario 2: Finds all <a> tags in the body (mixed absolute and relative)
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com/page1">Page 1</a><a href="/page2">Page 2</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/page1", "https://crawler-test.com/page2"]
        self.assertEqual(actual, expected)
    def test_get_urls_from_html_nested(self):
        # Scenario 3: Finds <a> tags nested deep within other elements (like divs and paragraphs)
        input_url = "https://crawler-test.com"
        input_body = '<html><body><div><p><a href="/contact">Contact Us</a></p></div></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/contact"]
        self.assertEqual(actual, expected)
    def test_get_images_from_html_absolute(self):
        # Scenario 1: Extracts standard absolute image URLs
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="https://crawler-test.com/images/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/images/logo.png"]
        self.assertEqual(actual, expected)
    def test_get_images_from_html_relative(self):
        # Scenario 2: Converts relative image URLs into absolute URLs using base_url
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/assets/banner.jpg" alt="Banner"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/assets/banner.jpg"]
        self.assertEqual(actual, expected)
    def test_get_images_from_html_missing_src(self):
        # Scenario 3: Handles edge cases where <img> tags are missing the 'src' attribute safely
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img alt="Broken Image Tag"><span>No source here</span></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)
    def test_extract_page_data_fallbacks(self):
        # Edge Case 1: Relies on heading fallback (<h2>) and general paragraph fallback, with no images
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h2>Fallback Subtitle</h2>
            <p>Paragraph outside main content.</p>
            <a href="/contact">Contact</a>
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Fallback Subtitle",
            "first_paragraph": "Paragraph outside main content.",
            "outgoing_links": ["https://crawler-test.com/contact"],
            "image_urls": [],
        }
        self.assertEqual(actual, expected)
    def test_extract_page_data_missing_text_tags(self):
        # Edge Case 2: Missing heading and paragraph tags entirely, but contains links and images
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <a href="/page-two">Next Page</a>
            <img src="/banner.png" alt="Banner">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "",
            "first_paragraph": "",
            "outgoing_links": ["https://crawler-test.com/page-two"],
            "image_urls": ["https://crawler-test.com/banner.png"],
        }
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()