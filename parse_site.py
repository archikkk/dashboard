#!/usr/bin/env python3
"""Simple website parser.

Usage:
    python parse_site.py https://example.com

Outputs:
    - Page title
    - All headings (h1-h6) with hierarchy preserved
    - All hyperlinks found (deduplicated and sorted)

Dependencies (add to requirements.txt):
    requests
    beautifulsoup4

Author: AI Assistant
"""
from __future__ import annotations

import argparse
import sys
from typing import List, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag


class WebsiteParser:
    """Parses a webpage and extracts useful information."""

    def __init__(self, url: str, timeout: int = 10) -> None:
        self.url = url
        self.timeout = timeout
        self.response: requests.Response | None = None
        self.soup: BeautifulSoup | None = None

    def fetch(self) -> None:
        """Fetches the URL and stores the response."""
        try:
            self.response = requests.get(self.url, timeout=self.timeout, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
            self.response.raise_for_status()
        except requests.RequestException as exc:
            print(f"Error fetching {self.url}: {exc}", file=sys.stderr)
            sys.exit(1)

    def parse(self) -> None:
        """Parses the HTML content using BeautifulSoup."""
        if self.response is None:
            raise RuntimeError("Response not fetched. Call fetch() first.")
        self.soup = BeautifulSoup(self.response.text, "lxml")

    # ---------------------------------------------------------
    # Extraction helpers
    # ---------------------------------------------------------
    def get_title(self) -> str | None:
        if self.soup is None:
            raise RuntimeError("Soup not parsed. Call parse() first.")
        if self.soup.title and self.soup.title.string:
            return self.soup.title.string.strip()
        return None

    def get_headings(self) -> List[str]:
        if self.soup is None:
            raise RuntimeError("Soup not parsed. Call parse() first.")
        headings: List[str] = []
        for level in range(1, 7):
            for tag in self.soup.find_all(f"h{level}"):
                text = self._get_text(tag)
                headings.append(f"h{level}: {text}")
        return headings

    def get_links(self) -> Set[str]:
        if self.soup is None:
            raise RuntimeError("Soup not parsed. Call parse() first.")
        links: Set[str] = set()
        base_url = self.response.url if self.response else self.url
        for tag in self.soup.find_all("a", href=True):
            href = tag["href"].strip()
            # Ignore JavaScript and mailto links
            if href.startswith("javascript:") or href.startswith("mailto:"):
                continue
            absolute = urljoin(base_url, href)
            links.add(absolute)
        return links

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------
    @staticmethod
    def _get_text(tag: Tag) -> str:
        """Extracts and cleans text content from a BeautifulSoup Tag."""
        return " ".join(chunk.strip() for chunk in tag.stripped_strings)


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Parse a website and extract basic information.")
    parser.add_argument("url", help="URL of the website to parse")
    args = parser.parse_args(argv)

    parsed = urlparse(args.url)
    if not parsed.scheme or not parsed.netloc:
        parser.error("Please provide a valid absolute URL, e.g., https://example.com")

    wp = WebsiteParser(args.url)
    wp.fetch()
    wp.parse()

    # Output results
    print("\n=== Page Title ===")
    print(wp.get_title() or "<No title found>")

    print("\n=== Headings ===")
    for heading in wp.get_headings():
        print(heading)

    print("\n=== Links ===")
    for link in sorted(wp.get_links()):
        print(link)


if __name__ == "__main__":
    main()