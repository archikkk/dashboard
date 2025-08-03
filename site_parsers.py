"""Site-specific parsers for online cinema websites.

WARNING: Many of these websites are protected by Cloudflare.  We use the
`cloudscraper` package, which automates the necessary JavaScript + cookie
challenge solving.  If the challenge becomes too complex, manual solving
(via browser automation) may be required.

Each *XXXParser* implements one public method:
    search(query: str, limit: int = 10) -> list[dict]
which returns a list of dicts with at least `title` and `url` keys.

If the markup changes on the source website, adjust the CSS selectors inside
`_extract_results` helpers accordingly.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List
from urllib.parse import quote_plus, urljoin

import cloudscraper
from bs4 import BeautifulSoup


def _create_scraper() -> cloudscraper.CloudScraper:
    """Return a Cloudflare-aware requests.Session compatible object."""
    return cloudscraper.create_scraper(browser={
        "custom": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/117.0 Safari/537.36"
    })


@dataclass(frozen=True)
class Movie:
    """Simple container for search results."""

    title: str
    url: str
    thumb: str | None = None
    year: str | None = None


class BaseSiteParser:
    """Common scaffolding for site scrapers."""

    base_url: str
    search_path: str  # path template expecting {query}

    def __init__(self, timeout: int = 15):
        self.session = _create_scraper()
        self.timeout = timeout

    # ----------------------- Public API ----------------------------------
    def search(self, query: str, limit: int = 10) -> List[Movie]:
        """Search the site and return up to `limit` results."""
        url = urljoin(self.base_url, self.search_path.format(query=quote_plus(query)))
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        return self._extract_results(soup, limit)

    # ----------------------- Implementation hooks ------------------------
    def _extract_results(self, soup: BeautifulSoup, limit: int) -> List[Movie]:
        """Site-specific extraction logic. Must be overridden."""
        raise NotImplementedError


class LordfilmParser(BaseSiteParser):
    base_url = "https://lordfilm.lu/"
    # Lordfilm's search uses traditional DLE query params
    search_path = "index.php?do=search&subaction=search&story={query}"

    def _extract_results(self, soup: BeautifulSoup, limit: int) -> List[Movie]:
        items: List[Movie] = []
        for story in soup.select("div.shortstory")[:limit]:
            a = story.select_one("div.title > a") or story.select_one("a")
            title = a.get_text(strip=True) if a else "<No title>"
            url = urljoin(self.base_url, a["href"]) if a and a.has_attr("href") else ""
            thumb_tag = story.select_one("img")
            thumb = urljoin(self.base_url, thumb_tag["src"]) if thumb_tag and thumb_tag.has_attr("src") else None
            items.append(Movie(title=title, url=url, thumb=thumb))
            if len(items) >= limit:
                break
        return items


class KinogoParser(BaseSiteParser):
    base_url = "https://kinogo.biz/"  # kinogo domain frequently changes
    search_path = "index.php?do=search&subaction=search&story={query}"

    def _extract_results(self, soup: BeautifulSoup, limit: int) -> List[Movie]:
        items: List[Movie] = []
        for li in soup.select(".shortstory")[:limit]:
            a = li.select_one("a[href][title]")
            title = a["title"].strip() if a and a.has_attr("title") else a.get_text(" ", strip=True)
            url = a["href"] if a else ""
            thumb_tag = li.select_one("img[src]")
            thumb = urljoin(self.base_url, thumb_tag["src"]) if thumb_tag and thumb_tag.has_attr("src") else None
            items.append(Movie(title=title, url=url, thumb=thumb))
            if len(items) >= limit:
                break
        return items


class FilmixParser(BaseSiteParser):
    base_url = "https://filmix.ac/"
    search_path = "search/{query}.html"

    def _extract_results(self, soup: BeautifulSoup, limit: int) -> List[Movie]:
        items: List[Movie] = []
        # Filmix uses <div class="shortstory"> structure as well but wrapped differently
        for card in soup.select("div.shortstory")[:limit]:
            a = card.select_one("a[href][title]")
            title = a["title"].strip() if a and a.has_attr("title") else a.get_text(strip=True)
            url = a["href"] if a else ""
            thumb_tag = card.select_one("img[src]")
            thumb = urljoin(self.base_url, thumb_tag["src"]) if thumb_tag and thumb_tag.has_attr("src") else None
            year_span = card.select_one("span.year")
            year = year_span.get_text(strip=True) if year_span else None
            items.append(Movie(title=title, url=url, thumb=thumb, year=year))
            if len(items) >= limit:
                break
        return items


# Helper to map CLI name -> Parser class
SITE_PARSERS = {
    "lordfilm": LordfilmParser,
    "kinogo": KinogoParser,
    "filmix": FilmixParser,
}