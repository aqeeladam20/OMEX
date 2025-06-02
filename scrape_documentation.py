#!/usr/bin/env python3
"""
Documentation Scraper for ERPNext/Frappe
This script scrapes documentation from official sites and saves it locally
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
from urllib.parse import urljoin, urlparse
import re

class DocumentationScraper:
    def __init__(self):
        self.base_urls = [
            "https://erpnext.com/docs/",
            "https://frappeframework.com/docs/",
            "https://docs.erpnext.com/"
        ]
        self.scraped_data = {}
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_all_documentation(self):
        """Scrape documentation from all base URLs"""
        print("Starting documentation scraping...")
        
        for base_url in self.base_urls:
            print(f"\nScraping from: {base_url}")
            self.scrape_site(base_url)
            time.sleep(2)  # Be respectful to the servers
        
        # Save the scraped data
        self.save_documentation()
        print(f"\nScraping completed! Found {len(self.scraped_data)} pages.")
    
    def scrape_site(self, base_url):
        """Scrape a specific documentation site"""
        try:
            # Get the main page
            response = self.session.get(base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all documentation links
            links = self.find_documentation_links(soup, base_url)
            
            # Scrape each page
            for link in links[:50]:  # Limit to first 50 pages to avoid overwhelming
                if link not in self.visited_urls:
                    self.scrape_page(link)
                    time.sleep(1)  # Rate limiting
                    
        except Exception as e:
            print(f"Error scraping {base_url}: {str(e)}")
    
    def find_documentation_links(self, soup, base_url):
        """Find all documentation links on a page"""
        links = set()
        
        # Look for common documentation link patterns
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            
            # Filter for documentation pages
            if self.is_documentation_url(full_url):
                links.add(full_url)
        
        return list(links)
    
    def is_documentation_url(self, url):
        """Check if URL is a documentation page"""
        doc_patterns = [
            '/docs/',
            '/manual/',
            '/user/',
            '/guide/',
            '/tutorial/'
        ]
        
        # Exclude certain file types and external links
        exclude_patterns = [
            '.pdf', '.zip', '.tar', '.gz',
            'github.com', 'youtube.com', 'twitter.com'
        ]
        
        url_lower = url.lower()
        
        # Check if it's a documentation URL
        has_doc_pattern = any(pattern in url_lower for pattern in doc_patterns)
        has_exclude_pattern = any(pattern in url_lower for pattern in exclude_patterns)
        
        return has_doc_pattern and not has_exclude_pattern
    
    def scrape_page(self, url):
        """Scrape content from a single page"""
        try:
            print(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract page content
            content = self.extract_content(soup)
            
            if content['title'] and content['text']:
                # Create a clean key for the page
                page_key = self.create_page_key(url, content['title'])
                self.scraped_data[page_key] = content
                
            self.visited_urls.add(url)
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
    
    def extract_content(self, soup):
        """Extract meaningful content from a page"""
        content = {
            'title': '',
            'text': '',
            'headings': [],
            'url': ''
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            content['title'] = title_tag.get_text().strip()
        
        # Try to find main content area
        main_content = None
        
        # Common content selectors
        content_selectors = [
            'main', '.content', '.main-content', '.documentation',
            '.docs-content', '.article', '.post-content'
        ]
        
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Remove unwanted elements
            for unwanted in main_content.find_all(['script', 'style', 'nav', 'footer', 'header']):
                unwanted.decompose()
            
            # Extract headings
            for heading in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                content['headings'].append(heading.get_text().strip())
            
            # Extract text content
            text = main_content.get_text()
            # Clean up the text
            text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace with single space
            text = text.strip()
            content['text'] = text
        
        return content
    
    def create_page_key(self, url, title):
        """Create a clean key for storing page data"""
        # Extract meaningful part from URL
        parsed = urlparse(url)
        path_parts = [part for part in parsed.path.split('/') if part]
        
        # Use the last meaningful part of the path or title
        if path_parts:
            key = path_parts[-1].replace('-', ' ').replace('_', ' ').title()
        else:
            key = title
        
        # Clean up the key
        key = re.sub(r'[^\w\s]', '', key)
        key = re.sub(r'\s+', ' ', key).strip()
        
        return key or 'Unknown Page'
    
    def save_documentation(self):
        """Save scraped documentation to JSON file"""
        output_file = 'scraped_documentation.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        
        print(f"Documentation saved to {output_file}")
        
        # Also create a summary file
        self.create_summary()
    
    def create_summary(self):
        """Create a summary of scraped content"""
        summary = {
            'total_pages': len(self.scraped_data),
            'pages': []
        }
        
        for key, content in self.scraped_data.items():
            summary['pages'].append({
                'key': key,
                'title': content['title'],
                'headings_count': len(content['headings']),
                'text_length': len(content['text'])
            })
        
        with open('documentation_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print("Summary saved to documentation_summary.json")

def main():
    """Main function to run the scraper"""
    scraper = DocumentationScraper()
    scraper.scrape_all_documentation()
    
    print("\n" + "="*50)
    print("SCRAPING COMPLETED!")
    print("="*50)
    print("\nNext steps:")
    print("1. Review 'scraped_documentation.json' for the scraped content")
    print("2. Review 'documentation_summary.json' for an overview")
    print("3. Use the scraped data to enhance the AI help system")
    print("\nTo integrate with the AI system:")
    print("- Copy the JSON data to the Frappe server")
    print("- Update frappe/utils/ai_help.py to load this data")
    print("- Restart the Frappe server")

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("Required packages not found. Please install them:")
        print("pip install requests beautifulsoup4")
        exit(1)
    
    main() 