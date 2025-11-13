#!/usr/bin/env python3
"""
Simple Immigration Crawler
A lightweight demonstration using requests + BeautifulSoup
"""

import json
import time
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from collections import deque
import yaml
import requests
from bs4 import BeautifulSoup


class SimpleImmigrationCrawler:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.visited = set()
        self.to_visit = deque()
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config['user_agent']
        })
    
    def is_allowed_domain(self, url):
        """Check if URL is from allowed domains"""
        domain = urlparse(url).netloc
        return any(allowed in domain for allowed in self.config['allowed_domains'])
    
    def contains_keywords(self, text):
        """Check if text contains relevant keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.config['keywords'])
    
    def extract_breadcrumbs(self, soup):
        """Extract breadcrumb navigation"""
        breadcrumbs = []
        
        # Common breadcrumb selectors
        for selector in [
            'nav[aria-label*="breadcrumb"] a',
            '.breadcrumb a',
            '[class*="breadcrumb"] a',
            'ol.breadcrumb a'
        ]:
            elements = soup.select(selector)
            if elements:
                breadcrumbs = [e.get_text(strip=True) for e in elements]
                break
        
        return breadcrumbs
    
    def extract_attachments(self, soup, base_url):
        """Extract PDF and document links"""
        attachments = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']):
                attachments.append({
                    'type': href.split('.')[-1].lower(),
                    'url': full_url,
                    'title': link.get_text(strip=True) or 'Document'
                })
        
        return attachments
    
    def extract_page_data(self, url, html, depth):
        """Extract structured data from a page"""
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract title
        title = soup.title.string.strip() if soup.title else 'No Title'
        
        # Extract main content
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        content_text = soup.get_text(separator='\n', strip=True)
        
        # Extract breadcrumbs
        breadcrumbs = self.extract_breadcrumbs(soup)
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])
            if self.is_allowed_domain(full_url) and full_url not in self.visited:
                links.append(full_url)
        
        # Extract attachments
        attachments = self.extract_attachments(soup, url)
        
        # Determine country and language from seed URLs
        country = "Unknown"
        language = "en"
        for seed in self.config['seed_urls']:
            if seed['url'] in url or urlparse(seed['url']).netloc in url:
                country = seed['country']
                language = seed['language']
                break
        
        # Extract tags based on keywords found
        tags = [kw for kw in self.config['keywords'] if kw in content_text.lower()]
        
        return {
            'url': url,
            'source': f"{country} Immigration Portal",
            'country': country,
            'language': language,
            'title': title,
            'breadcrumbs': breadcrumbs,
            'content_text': content_text[:5000],  # Limit for demo
            'content_html': str(soup)[:3000],  # Limit for demo
            'depth': depth,
            'linked_urls': links[:20],  # Limit for demo
            'attachments': attachments[:10],  # Limit for demo
            'tags': tags,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def crawl(self):
        """Main crawling loop"""
        # Initialize queue with seed URLs
        for seed in self.config['seed_urls']:
            self.to_visit.append((seed['url'], 0))
        
        pages_crawled = 0
        max_pages = self.config['max_pages']
        max_depth = self.config['max_depth']
        
        print(f"🚀 Starting crawl with {len(self.to_visit)} seed URLs...")
        print(f"📊 Max pages: {max_pages}, Max depth: {max_depth}\n")
        
        while self.to_visit and pages_crawled < max_pages:
            url, depth = self.to_visit.popleft()
            
            if url in self.visited or depth > max_depth:
                continue
            
            if not self.is_allowed_domain(url):
                continue
            
            try:
                print(f"🔍 Crawling (depth {depth}): {url}")
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                # Check if page contains relevant keywords
                if not self.contains_keywords(response.text):
                    print(f"⏭️  Skipping (no relevant keywords)")
                    self.visited.add(url)
                    continue
                
                # Extract data
                page_data = self.extract_page_data(url, response.text, depth)
                self.results.append(page_data)
                
                print(f"✅ Extracted: {page_data['title'][:60]}")
                print(f"   Tags: {', '.join(page_data['tags'][:5])}")
                print(f"   Links found: {len(page_data['linked_urls'])}\n")
                
                # Add new links to queue
                for link in page_data['linked_urls']:
                    if link not in self.visited:
                        self.to_visit.append((link, depth + 1))
                
                self.visited.add(url)
                pages_crawled += 1
                
                # Rate limiting
                time.sleep(self.config['delay_between_requests'])
                
            except Exception as e:
                print(f"❌ Error crawling {url}: {str(e)}\n")
                self.visited.add(url)
                continue
        
        print(f"\n🎉 Crawl complete! Pages crawled: {pages_crawled}")
        return self.results
    
    def save_results(self):
        """Save results to JSON file"""
        import os
        os.makedirs(self.config['output_dir'], exist_ok=True)
        
        output_path = f"{self.config['output_dir']}/{self.config['output_file']}"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_path}")
        print(f"📈 Total pages: {len(self.results)}")
        
        # Print summary statistics
        countries = {}
        for page in self.results:
            country = page['country']
            countries[country] = countries.get(country, 0) + 1
        
        print(f"\n📊 Pages by country:")
        for country, count in countries.items():
            print(f"   {country}: {count}")


def main():
    print("🌍 Universal Immigration Crawler - Simple Demo\n")
    print("=" * 60)
    
    crawler = SimpleImmigrationCrawler()
    crawler.crawl()
    crawler.save_results()
    
    print("\n" + "=" * 60)
    print("✨ Demo complete! Check the data/ directory for results.")


if __name__ == '__main__':
    main()
