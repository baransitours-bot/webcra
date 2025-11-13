#!/usr/bin/env python3
"""
Scrapy-based Immigration Crawler
A more robust implementation using Scrapy framework
"""

import json
import yaml
from datetime import datetime
from urllib.parse import urlparse
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor


class ImmigrationSpider(scrapy.Spider):
    name = 'immigration_spider'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Load configuration
        with open('config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.start_urls = [seed['url'] for seed in self.config['seed_urls']]
        self.allowed_domains = self.config['allowed_domains']
        self.max_depth = self.config['max_depth']
        self.keywords = self.config['keywords']
        
        # Store seed URL metadata
        self.seed_metadata = {
            seed['url']: {'country': seed['country'], 'language': seed['language']}
            for seed in self.config['seed_urls']
        }
        
        self.results = []
        self.pages_crawled = 0
        self.max_pages = self.config['max_pages']
    
    def parse(self, response):
        """Parse each page"""
        
        # Check page limit
        if self.pages_crawled >= self.max_pages:
            return
        
        # Get current depth
        depth = response.meta.get('depth', 0)
        
        # Check if page contains relevant keywords
        page_text = ' '.join(response.css('*::text').getall()).lower()
        if not any(keyword in page_text for keyword in self.keywords):
            self.logger.info(f"Skipping (no keywords): {response.url}")
            return
        
        # Extract page data
        page_data = self.extract_page_data(response, depth)
        self.results.append(page_data)
        self.pages_crawled += 1
        
        self.logger.info(f"✅ Crawled ({depth}): {response.url}")
        self.logger.info(f"   Title: {page_data['title'][:60]}")
        
        # Follow links if within depth limit
        if depth < self.max_depth:
            link_extractor = LinkExtractor(
                allow_domains=self.allowed_domains,
                unique=True
            )
            
            for link in link_extractor.extract_links(response):
                yield scrapy.Request(
                    link.url,
                    callback=self.parse,
                    meta={'depth': depth + 1},
                    dont_filter=False
                )
    
    def extract_page_data(self, response, depth):
        """Extract structured data from response"""
        
        # Extract title
        title = response.css('title::text').get()
        if title:
            title = title.strip()
        else:
            title = 'No Title'
        
        # Extract breadcrumbs
        breadcrumbs = self.extract_breadcrumbs(response)
        
        # Extract main content
        # Remove unwanted elements
        content_text = ' '.join(response.css('main *::text, article *::text, .content *::text').getall())
        if not content_text.strip():
            content_text = ' '.join(response.css('body *::text').getall())
        
        content_text = ' '.join(content_text.split())  # Clean whitespace
        
        # Extract links
        links = []
        for link in response.css('a::attr(href)').getall():
            full_url = response.urljoin(link)
            if any(domain in full_url for domain in self.allowed_domains):
                links.append(full_url)
        
        # Extract attachments
        attachments = self.extract_attachments(response)
        
        # Determine country and language
        country, language = self.get_country_language(response.url)
        
        # Extract tags
        tags = [kw for kw in self.keywords if kw in content_text.lower()]
        
        return {
            'url': response.url,
            'source': f"{country} Immigration Portal",
            'country': country,
            'language': language,
            'title': title,
            'breadcrumbs': breadcrumbs,
            'content_text': content_text[:5000],  # Limit for demo
            'content_html': response.text[:3000],  # Limit for demo
            'depth': depth,
            'linked_urls': list(set(links))[:20],  # Unique links, limited
            'attachments': attachments[:10],
            'tags': tags,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def extract_breadcrumbs(self, response):
        """Extract breadcrumb navigation"""
        breadcrumbs = []
        
        # Try common breadcrumb selectors
        selectors = [
            'nav[aria-label*="breadcrumb"] a::text',
            '.breadcrumb a::text',
            '[class*="breadcrumb"] a::text',
            'ol.breadcrumb a::text'
        ]
        
        for selector in selectors:
            crumbs = response.css(selector).getall()
            if crumbs:
                breadcrumbs = [c.strip() for c in crumbs]
                break
        
        return breadcrumbs
    
    def extract_attachments(self, response):
        """Extract document links"""
        attachments = []
        
        for link in response.css('a::attr(href)').getall():
            if any(ext in link.lower() for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']):
                full_url = response.urljoin(link)
                
                # Get link text
                link_text = response.css(f'a[href="{link}"]::text').get()
                if not link_text:
                    link_text = 'Document'
                
                attachments.append({
                    'type': link.split('.')[-1].lower(),
                    'url': full_url,
                    'title': link_text.strip()
                })
        
        return attachments
    
    def get_country_language(self, url):
        """Determine country and language from URL"""
        for seed_url, metadata in self.seed_metadata.items():
            if urlparse(seed_url).netloc in url:
                return metadata['country'], metadata['language']
        
        return 'Unknown', 'en'
    
    def closed(self, reason):
        """Called when spider closes - save results"""
        import os
        
        os.makedirs(self.config['output_dir'], exist_ok=True)
        output_path = f"{self.config['output_dir']}/{self.config['output_file']}"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"\n💾 Results saved to: {output_path}")
        self.logger.info(f"📈 Total pages: {len(self.results)}")
        
        # Print statistics
        countries = {}
        for page in self.results:
            country = page['country']
            countries[country] = countries.get(country, 0) + 1
        
        self.logger.info(f"\n📊 Pages by country:")
        for country, count in countries.items():
            self.logger.info(f"   {country}: {count}")


def main():
    """Run the Scrapy crawler"""
    print("🌍 Universal Immigration Crawler - Scrapy Demo\n")
    print("=" * 60)
    
    # Configure Scrapy settings
    settings = {
        'USER_AGENT': 'Mozilla/5.0 (compatible; ImmigrationCrawler/1.0; Educational Purpose)',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1,
        'DEPTH_LIMIT': 3,
        'CLOSESPIDER_PAGECOUNT': 50,
        'LOG_LEVEL': 'INFO',
    }
    
    # Create and run crawler
    process = CrawlerProcess(settings=settings)
    process.crawl(ImmigrationSpider)
    process.start()
    
    print("\n" + "=" * 60)
    print("✨ Demo complete! Check the data/ directory for results.")


if __name__ == '__main__':
    main()
