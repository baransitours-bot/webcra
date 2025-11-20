"""
Crawler Engine - CORE LOGIC LAYER

Pure business logic for web crawling.
No direct database access - uses repository for data.

Think of this as the ENGINE that processes the FUEL (data).
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from datetime import datetime
import time
from typing import List, Dict, Set, Tuple

from shared.models import CrawledPage
from shared.logger import setup_logger
from services.crawler.repository import CrawlerRepository


class CrawlerEngine:
    """
    Core crawling logic.

    Responsibilities:
    - Fetch and parse web pages
    - Follow links
    - Extract content
    - Respect crawling rules (delays, depth)

    Does NOT:
    - Access database directly
    - Know about UI
    - Handle configuration loading
    """

    def __init__(self, config: dict, repository: CrawlerRepository):
        """
        Initialize engine.

        Args:
            config: Crawler configuration
            repository: Data access layer
        """
        self.config = config
        self.repo = repository
        self.logger = setup_logger('crawler_engine')

        # Crawl state
        self.visited: Set[str] = set()
        self.to_visit: deque = deque()

        # HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config['crawling']['user_agent']
        })

    def crawl_country(self, country_name: str, seed_urls: List[str]) -> Dict:
        """
        Crawl a country's immigration website.

        Args:
            country_name: Country to crawl
            seed_urls: Starting URLs

        Returns:
            Crawl statistics
        """
        self.logger.info(f"Starting crawl for {country_name}")

        # Initialize queue
        for url in seed_urls:
            self.to_visit.append((url, 0))  # (url, depth)

        # Crawl limits
        max_pages = self.config['crawling']['max_pages_per_country']
        max_depth = self.config['crawling']['max_depth']

        pages_crawled = 0
        pages_saved = 0

        while self.to_visit and pages_crawled < max_pages:
            url, depth = self.to_visit.popleft()

            # Skip if already visited or too deep
            if url in self.visited or depth > max_depth:
                continue

            # Skip if excluded
            if self._should_exclude(url):
                self.logger.info(f"Skipping (excluded): {url}")
                self.visited.add(url)
                continue

            # Crawl the page
            page = self._crawl_page(url, country_name, depth)

            if page:
                # Save via repository
                self.repo.save_page(page)
                pages_saved += 1

                # Add new links to queue
                for link in page.links:
                    if link not in self.visited:
                        self.to_visit.append((link, depth + 1))

                self.logger.info(f"✓ Saved: {page.title[:60]}")

            self.visited.add(url)
            pages_crawled += 1

            # Rate limiting
            time.sleep(self.config['crawling']['delay_between_requests'])

        self.logger.info(f"Crawl complete: {pages_saved}/{pages_crawled} pages saved")

        return {
            'country': country_name,
            'pages_crawled': pages_crawled,
            'pages_saved': pages_saved,
            'urls_queued': len(self.to_visit)
        }

    def _crawl_page(self, url: str, country: str, depth: int) -> Optional[CrawledPage]:
        """
        Fetch and parse a single page.

        Args:
            url: URL to crawl
            country: Country name
            depth: Current crawl depth

        Returns:
            CrawledPage or None if failed
        """
        try:
            self.logger.info(f"Crawling (depth {depth}): {url}")

            # Fetch page
            response = self.session.get(
                url,
                timeout=self.config['crawling']['timeout']
            )
            response.raise_for_status()

            # Check relevance
            if not self._is_relevant(response.text):
                self.logger.info("Skipping (no relevant keywords)")
                return None

            # Parse page
            return self._parse_page(url, country, response.text, depth)

        except Exception as e:
            self.logger.error(f"Failed to crawl {url}: {str(e)}")
            return None

    def _parse_page(self, url: str, country: str, html: str, depth: int) -> CrawledPage:
        """
        Parse HTML and extract structured data.

        Args:
            url: Page URL
            country: Country name
            html: HTML content
            depth: Crawl depth

        Returns:
            CrawledPage object
        """
        soup = BeautifulSoup(html, 'lxml')

        # Remove noise
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()

        # Extract data
        title = soup.title.string.strip() if soup.title else 'No Title'
        content_text = soup.get_text(separator='\n', strip=True)

        # Extract breadcrumbs
        breadcrumbs = self._extract_breadcrumbs(soup)

        # Extract links
        links = self._extract_links(soup, url)

        # Extract attachments
        attachments = self._extract_attachments(soup, url)

        # Build metadata
        metadata = {
            'breadcrumbs': breadcrumbs,
            'links': links[:50],  # Limit
            'attachments': attachments[:20],  # Limit
            'depth': depth
        }

        return CrawledPage(
            url=url,
            country=country,
            title=title,
            content=content_text[:10000],  # Limit size
            metadata=metadata
        )

    def _extract_breadcrumbs(self, soup: BeautifulSoup) -> List[str]:
        """Extract page breadcrumbs"""
        for selector in ['nav[aria-label*="breadcrumb"] a', '.breadcrumb a']:
            elements = soup.select(selector)
            if elements:
                return [e.get_text(strip=True) for e in elements]
        return []

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract same-domain links"""
        links = []
        base_domain = urlparse(base_url).netloc

        for link in soup.find_all('a', href=True):
            full_url = urljoin(base_url, link['href'])
            if urlparse(full_url).netloc == base_domain:
                links.append(full_url)

        return links

    def _extract_attachments(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract document attachments (PDFs, etc.)"""
        attachments = []
        extensions = self.config['download_extensions']

        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(ext in href.lower() for ext in extensions):
                attachments.append({
                    'type': href.split('.')[-1].lower(),
                    'url': urljoin(base_url, href),
                    'title': link.get_text(strip=True) or 'Document'
                })

        return attachments

    def _is_relevant(self, text: str) -> bool:
        """Check if page contains relevant keywords"""
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.config['keywords'])

    def _should_exclude(self, url: str) -> bool:
        """Check if URL should be excluded"""
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in self.config['exclude_patterns'])

    def reset(self):
        """Reset crawl state for new crawl"""
        self.visited.clear()
        self.to_visit.clear()
