"""Fetch a web page and print its readable text.

Command-line tool registered with the llama.cpp server as ``web_fetch``. It
downloads a single URL, extracts the text found inside common text-bearing
HTML tags, collapses whitespace and writes the result to standard output so
that the server can return it to the language model.

Usage:
    python web_fetch.py <URL>

Behaviour:
    * Sends a GET request with a custom User-Agent and a 15 second timeout.
    * Prints a warning line to standard output if the response is not
      ``text/html``; the body is still decoded and processed.
    * Decodes the body as UTF-8 and prints the extracted text.
    * Exit status is 0 on success and 1 if no URL is given or if fetching or
      decoding fails (an error message is printed to standard output).

Only the standard library is used (``urllib`` and ``html.parser``).
"""

import sys
import urllib.request
from html.parser import HTMLParser
import re

class HTMLTextExtractor(HTMLParser):
    """Collect text that appears inside a fixed set of HTML text tags.

    Text is kept only while the parser is inside one of the following tags:
    ``p``, ``div``, ``span``, ``h1``-``h6``, ``li``, ``td`` and ``th``. Text
    inside other elements (for example ``script``, ``style``, ``a`` or
    ``title``) is ignored unless it is also nested in one of these tags.

    Attributes:
        result (list[str]): Text fragments collected so far, in document
            order.
        current_tag (str | None): The most recently opened text tag, or
            ``None`` when text should be ignored.

    Note:
        ``current_tag`` holds a single value and is cleared by any closing
        tag. Text that follows a nested closing tag, before the next text tag
        opens, is therefore dropped.
    """

    def __init__(self):
        """Initialise the parser with an empty result list and no active tag."""
        super().__init__()
        self.result = []
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        """Record the tag name if it is a text-bearing tag.

        Args:
            tag (str): Lower-case name of the opening tag.
            attrs (list[tuple[str, str | None]]): Tag attributes (unused).
        """
        # Only extract text from standard text tags
        if tag in ('p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th'):
            self.current_tag = tag

    def handle_endtag(self, tag):
        """Stop collecting text when any closing tag is reached.

        Args:
            tag (str): Lower-case name of the closing tag (unused).
        """
        self.current_tag = None

    def handle_data(self, data):
        """Store a text fragment if a text tag is currently active.

        Args:
            data (str): Text found between tags.
        """
        if self.current_tag:
            self.result.append(data)

def clean_text(html):
    """Convert an HTML string to whitespace-normalised plain text.

    Args:
        html (str): Raw HTML source.

    Returns:
        str: The extracted text, with every run of whitespace replaced by a
        single space and leading and trailing whitespace removed. An empty
        string is returned if ``html`` is empty or ``None``. If parsing
        fails, the function does not raise; it returns a string beginning
        with ``"Error parsing HTML:"`` followed by the exception message.
    """
    if not html:
        return ""
    try:
        parser = HTMLTextExtractor()
        parser.feed(html)
        text = ''.join(parser.result)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    except Exception as e:
        return f"Error parsing HTML: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python web_fetch.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (compatible; Llama.cpp/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            if 'text/html' not in response.headers.get('Content-Type', ''):
                 print(f"Warning: URL returned non-HTML content type: {response.headers.get('Content-Type')}")
            html = response.read().decode('utf-8')
            print(clean_text(html))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        sys.exit(1)
