"""
Immigration Spider
Crawls immigration websites and extracts data
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from datetime import datetime
import time
import yaml

from shared.database import DataStore, Database
from shared.logger import setup_logger

class ImmigrationCrawler:
    def __init__(self, countries, config):
        self.countries = countries
        self.config = config
        self.visited = set()
        self.to_visit = deque()
        self.data_store = DataStore()  # Keep for backward compatibility
        self.db = Database()  # New SQLite database with versioning
        self.logger = setup_logger('crawler', 'crawler.log')

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config['crawling']['user_agent']
        })

    def is_relevant(self, text):
        """Check if page contains relevant keywords"""
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.config['keywords'])

    def should_exclude(self, url):
        """Check if URL should be excluded based on patterns"""
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in self.config['exclude_patterns'])

    def extract_page_data(self, url, html, country, depth):
        """Extract structured data from page"""
        soup = BeautifulSoup(html, 'lxml')

        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()

        # Extract data
        title = soup.title.string.strip() if soup.title else 'No Title'
        content_text = soup.get_text(separator='\n', strip=True)

        # Extract breadcrumbs
        breadcrumbs = []
        for selector in ['nav[aria-label*="breadcrumb"] a', '.breadcrumb a']:
            elements = soup.select(selector)
            if elements:
                breadcrumbs = [e.get_text(strip=True) for e in elements]
                break

        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])
            if urlparse(full_url).netloc == urlparse(url).netloc:
                links.append(full_url)

        # Extract attachments
        attachments = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(ext in href.lower() for ext in self.config['download_extensions']):
                attachments.append({
                    'type': href.split('.')[-1].lower(),
                    'url': urljoin(url, href),
                    'title': link.get_text(strip=True) or 'Document'
                })

        return {
            'url': url,
            'country': country,
            'title': title,
            'content_text': content_text[:10000],  # Limit size
            'content_html': str(soup)[:5000],
            'breadcrumbs': breadcrumbs,
            'links': links[:50],
            'attachments': attachments[:20],
            'crawled_date': datetime.utcnow().isoformat() + 'Z',
            'depth': depth
        }

    def crawl_country(self, country_name, seed_urls):
        """Crawl a specific country"""
        self.logger.info(f"🕷️  Starting crawl for {country_name}")

        # Initialize queue
        for url in seed_urls:
            self.to_visit.append((url, 0))

        pages_crawled = 0
        max_pages = self.config['crawling']['max_pages_per_country']
        max_depth = self.config['crawling']['max_depth']

        while self.to_visit and pages_crawled < max_pages:
            url, depth = self.to_visit.popleft()

            if url in self.visited or depth > max_depth:
                continue

            # Check if URL should be excluded
            if self.should_exclude(url):
                self.logger.info(f"⏭️  Skipping (excluded pattern): {url}")
                self.visited.add(url)
                continue

            try:
                self.logger.info(f"Crawling (depth {depth}): {url}")

                response = self.session.get(url, timeout=self.config['crawling']['timeout'])
                response.raise_for_status()

                # Check relevance
                if not self.is_relevant(response.text):
                    self.logger.info("⏭️  Skipping (no relevant keywords)")
                    self.visited.add(url)
                    continue

                # Extract data
                page_data = self.extract_page_data(url, response.text, country_name, depth)

                # Save to files (backward compatibility)
                self.data_store.save_raw_page(country_name, page_data)

                # Save to database with versioning
                self.db.save_crawled_page(
                    url=page_data['url'],
                    country=country_name,
                    title=page_data['title'],
                    content=page_data['content_text'],
                    metadata={
                        'breadcrumbs': page_data['breadcrumbs'],
                        'links': page_data['links'],
                        'attachments': page_data['attachments'],
                        'depth': page_data['depth']
                    }
                )

                self.logger.info(f"✅ Saved: {page_data['title'][:60]}")

                # Add new links to queue
                for link in page_data['links']:
                    if link not in self.visited:
                        self.to_visit.append((link, depth + 1))

                self.visited.add(url)
                pages_crawled += 1

                # Rate limiting
                time.sleep(self.config['crawling']['delay_between_requests'])

            except Exception as e:
                self.logger.error(f"❌ Error crawling {url}: {str(e)}")
                self.visited.add(url)
                continue

        self.logger.info(f"✅ {country_name} crawl complete: {pages_crawled} pages")

    def crawl_all(self):
        """Crawl all configured countries"""
        for country in self.countries:
            self.crawl_country(country['name'], country['seed_urls'])
            self.visited.clear()
            self.to_visit.clear()
