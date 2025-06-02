#!/usr/bin/env python3
"""
Enhanced Documentation Scraper for ERPNext/Frappe
This script scrapes specific documentation URLs provided by the user
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
from urllib.parse import urljoin, urlparse
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

class EnhancedDocumentationScraper:
    def __init__(self):
        # Comprehensive list of ERPNext documentation URLs provided by user
        self.target_urls = [
            # Buying Module
            "https://docs.frappe.io/erpnext/user/manual/en/buying",
            "https://docs.frappe.io/erpnext/user/manual/en/supplier-essentials",
            "https://docs.frappe.io/erpnext/user/manual/en/purchase-transactions",
            "https://docs.frappe.io/erpnext/user/manual/en/supplier-scorecard",
            "https://docs.frappe.io/erpnext/user/manual/en/buying_reports",
            "https://docs.frappe.io/erpnext/user/manual/en/buying-settings",
            "https://docs.frappe.io/erpnext/v13/user/videos/learn/discounts",
            "https://docs.frappe.io/erpnext/v13/user/videos/learn/taxes",
            "https://docs.frappe.io/erpnext/user/manual/en/material-request",
            "https://docs.frappe.io/erpnext/user/manual/en/purchase-order",
            "https://docs.frappe.io/erpnext/user/manual/en/purchase-invoice",
            "https://docs.frappe.io/erpnext/user/manual/en/debit-note",
            "https://docs.frappe.io/erpnext/user/manual/en/request-for-quotation",
            "https://docs.frappe.io/erpnext/user/manual/en/supplier-quotation",
            "https://docs.frappe.io/erpnext/user/manual/en/how-to-create-a-supplier-quotation-through-the-supplier-portal",
            "https://docs.frappe.io/erpnext/user/manual/en/purchase-return",
            "https://docs.frappe.io/erpnext/user/manual/en/supplier-group",
            "https://docs.frappe.io/erpnext/user/manual/en/supplier",
            
            # Selling Module
            "https://docs.frappe.io/erpnext/user/manual/en/customer",
            "https://docs.frappe.io/erpnext/user/manual/en/customer-group",
            "https://docs.frappe.io/erpnext/user/manual/en/sales-person",
            "https://docs.frappe.io/erpnext/user/manual/en/sales-partner",
            "https://docs.frappe.io/erpnext/user/manual/en/territory",
            "https://docs.frappe.io/erpnext/user/manual/en/sales-order",
            "https://docs.frappe.io/erpnext/user/manual/en/sales-invoice",
            "https://docs.frappe.io/erpnext/user/manual/en/quotation",
            "https://docs.frappe.io/erpnext/user/manual/en/credit-note",
            "https://docs.frappe.io/erpnext/user/manual/en/blanket-order",
            "https://docs.frappe.io/erpnext/user/manual/en/drop-shipping-in-erpnext",
            "https://docs.frappe.io/erpnext/user/manual/en/sales-return",
            "https://docs.frappe.io/erpnext/user/manual/en/delivery-note",
            "https://docs.frappe.io/erpnext/user/manual/en/pos-profile",
            "https://docs.frappe.io/erpnext/user/manual/en/point-of-sales",
            "https://docs.frappe.io/erpnext/user/manual/en/pos_invoice_consolidation",
            "https://docs.frappe.io/erpnext/user/manual/en/loyalty-program",
            "https://docs.frappe.io/erpnext/user/manual/en/loyalty-points-redemption-in-pos",
            "https://docs.frappe.io/erpnext/user/manual/en/selling-settings",
            "https://docs.frappe.io/erpnext/user/manual/en/sales-analytics",
            
            # Stock/Inventory Module
            "https://docs.frappe.io/erpnext/v13/user/videos/learn/stock-entries",
            "https://docs.frappe.io/erpnext/v13/user/videos/learn/opening-stock",
            "https://docs.frappe.io/erpnext/v13/user/videos/learn/item",
            "https://docs.frappe.io/erpnext/v13/user/videos/learn/batch-inventory",
            "https://docs.frappe.io/erpnext/v13/user/videos/learn/item-variant",
            "https://docs.frappe.io/erpnext/v13/user/videos/learn/serialized-inventory",
            "https://docs.frappe.io/erpnext/user/manual/en/item",
            "https://docs.frappe.io/erpnext/user/manual/en/item-group",
            "https://docs.frappe.io/erpnext/user/manual/en/brand",
            "https://docs.frappe.io/erpnext/user/manual/en/item-alternative",
            "https://docs.frappe.io/erpnext/user/manual/en/product-bundle",
            "https://docs.frappe.io/erpnext/user/manual/en/manufacturer",
            "https://docs.frappe.io/erpnext/user/manual/en/item-variants",
            "https://docs.frappe.io/erpnext/user/manual/en/item-attribute",
            "https://docs.frappe.io/erpnext/user/manual/en/uom",
            "https://docs.frappe.io/erpnext/user/manual/en/managing-fractions-in-uom",
            "https://docs.frappe.io/erpnext/user/manual/en/inventory_dimension",
            "https://docs.frappe.io/erpnext/user/manual/en/warehouse",
            "https://docs.frappe.io/erpnext/user/manual/en/pricing",
            "https://docs.frappe.io/erpnext/user/manual/en/price-lists",
            "https://docs.frappe.io/erpnext/user/manual/en/item-price",
            "https://docs.frappe.io/erpnext/user/manual/en/setup-shipping-rule",
            "https://docs.frappe.io/erpnext/user/manual/en/pricing-rule",
            "https://docs.frappe.io/erpnext/user/manual/en/auto-creation-of-material-request",
            "https://docs.frappe.io/erpnext/user/manual/en/opening-stock",
            "https://docs.frappe.io/erpnext/user/manual/en/stock-entry",
            "https://docs.frappe.io/erpnext/user/manual/en/accounting-of-inventory-stock",
            "https://docs.frappe.io/erpnext/user/manual/en/shipment",
            "https://docs.frappe.io/erpnext/user/manual/en/pick-list",
            "https://docs.frappe.io/erpnext/user/manual/en/delivery-trip",
            "https://docs.frappe.io/erpnext/user/manual/en/purchase-receipt",
            "https://docs.frappe.io/erpnext/user/manual/en/packing-slip",
            "https://docs.frappe.io/erpnext/user/manual/en/putaway-rule",
            "https://docs.frappe.io/erpnext/user/manual/en/stock-reconciliation",
            "https://docs.frappe.io/erpnext/user/manual/en/stock-reservation",
            "https://docs.frappe.io/erpnext/user/manual/en/perpetual-inventory",
            "https://docs.frappe.io/erpnext/user/manual/en/stock-transactions-landed-cost-voucher",
            "https://docs.frappe.io/erpnext/user/manual/en/quality-inspection",
            "https://docs.frappe.io/erpnext/user/manual/en/stock-inspection",
            "https://docs.frappe.io/erpnext/user/manual/en/serial-no",
            "https://docs.frappe.io/erpnext/user/manual/en/serial-no-naming",
            "https://docs.frappe.io/erpnext/user/manual/en/batch",
            "https://docs.frappe.io/erpnext/user/manual/en/serial-and-batch-bundle",
            "https://docs.frappe.io/erpnext/user/manual/en/managing-batch-wise-inventory",
            "https://docs.frappe.io/erpnext/user/manual/en/disassembly-order",
            "https://docs.frappe.io/erpnext/user/manual/en/stock-settings",
            "https://docs.frappe.io/erpnext/user/manual/en/stock-reposting-settings",
            "https://docs.frappe.io/erpnext/user/manual/en/stock-ledger",
            "https://docs.frappe.io/erpnext/user/manual/en/stock-level-report",
            "https://docs.frappe.io/erpnext/user/manual/en/bom_explorer",
            "https://docs.frappe.io/erpnext/user/manual/en/closing-stock-balance",
            "https://docs.frappe.io/erpnext/user/manual/en/stock-value-account-value-comparison",
            "https://docs.frappe.io/erpnext/stock-closing-entry",
            "https://docs.frappe.io/erpnext/stock-reposting",
            "https://docs.frappe.io/erpnext/user/manual/en/stock-adjustment-cogs-with-negative-stock",
            "https://docs.frappe.io/erpnext/change-valuation-method",
            "https://docs.frappe.io/erpnext/v13/user/manual/en/stock/warehouse",
            
            # Manufacturing Module
            "https://docs.frappe.io/erpnext/v13/user/manual/en/manufacturing/workstation",
            "https://docs.frappe.io/erpnext/v13/user/manual/en/manufacturing/operation",
            "https://docs.frappe.io/erpnext/v13/user/manual/en/manufacturing/routing",
            "https://docs.frappe.io/erpnext/v13/user/manual/en/manufacturing/bill-of-materials",
            "https://docs.frappe.io/erpnext/v13/user/manual/en/manufacturing/work-order",
            "https://docs.frappe.io/erpnext/v13/user/manual/en/manufacturing/job-card",
            "https://docs.frappe.io/erpnext/v13/user/manual/en/manufacturing/production-plan",
            "https://docs.frappe.io/erpnext/user/manual/en/manufacturing",
            "https://docs.frappe.io/erpnext/user/manual/en/manufacturing-settings",
            "https://docs.frappe.io/erpnext/user/manual/en/manufacturing-dashboard",
            "https://docs.frappe.io/erpnext/user/manual/en/manufacturing-reports",
            "https://docs.frappe.io/erpnext/user/manual/en/production-and-material-planning",
            "https://docs.frappe.io/erpnext/user/manual/en/workstation",
            "https://docs.frappe.io/erpnext/user/manual/en/workstation_type",
            "https://docs.frappe.io/erpnext/user/manual/en/bill-of-materials",
            "https://docs.frappe.io/erpnext/user/manual/en/managing-multi-level-bom",
            "https://docs.frappe.io/erpnext/user/manual/en/bom-creator",
            "http://docs.frappe.io/erpnext/user/manual/en/bom-update-tool",
            "https://docs.frappe.io/erpnext/user/manual/en/bom-comparison-tool",
            "https://docs.frappe.io/erpnext/user/manual/en/bom-search",
            "https://docs.frappe.io/erpnext/user/manual/en/bom-costing-in-different-currency",
            "https://docs.frappe.io/erpnext/user/manual/en/bom-stock-report",
            "https://docs.frappe.io/erpnext/user/manual/en/operation",
            "https://docs.frappe.io/erpnext/user/manual/en/bom-operation-time",
            "https://docs.frappe.io/erpnext/user/manual/en/routing",
            "https://docs.frappe.io/erpnext/user/manual/en/track-semi-finished-goods",
            "https://docs.frappe.io/erpnext/stock-reservation-for-work-order",
            "https://docs.frappe.io/erpnext/stock-reservation-for-production-plan",
            "https://docs.frappe.io/erpnext/user/manual/en/subcontracting-in-erpnext",
            
            # Core Settings and Configuration
            "https://docs.frappe.io/erpnext/user/manual/en/core-settings",
            "https://docs.frappe.io/erpnext/user/manual/en/module-settings", 
            "https://docs.frappe.io/erpnext/user/manual/en/email",
            "https://docs.frappe.io/erpnext/user/manual/en/document-naming",
            "https://docs.frappe.io/erpnext/user/manual/en/workflow",
            "https://docs.frappe.io/erpnext/user/manual/en/printing",
            "https://docs.frappe.io/erpnext/user/manual/en/automation",
            
            # Users and Permissions
            "https://docs.frappe.io/erpnext/user/manual/en/users",
            "https://docs.frappe.io/erpnext/user/manual/en/permissions",
            "https://docs.frappe.io/erpnext/v13/user/manual/en/setting-up/users-and-permissions",
            "https://docs.frappe.io/erpnext/v13/user/manual/en/setting-up/users-and-permissions/role-and-role-profile",
            
            # Accounting
            "https://docs.frappe.io/erpnext/user/manual/en/accounting-masters",
            "https://docs.frappe.io/erpnext/user/manual/en/opening-and-closing",
            "https://docs.frappe.io/erpnext/user/manual/en/general-ledger",
            "https://docs.frappe.io/erpnext/user/manual/en/taxes",
            "https://docs.frappe.io/erpnext/user/manual/en/accounting-reports",
            "https://docs.frappe.io/erpnext/user/manual/en/accounts-receivable-and-payable",
            "https://docs.frappe.io/erpnext/user/manual/en/cost-center-and-budgeting",
            "https://docs.frappe.io/erpnext/user/manual/en/multi-currency-setup",
            "https://docs.frappe.io/erpnext/user/manual/en/deferred-accounting",
            "https://docs.frappe.io/erpnext/user/manual/en/banking-in-erpnext",
            "https://docs.frappe.io/erpnext/user/manual/en/subscription-management",
            "https://docs.frappe.io/erpnext/user/manual/en/shareholder-management",
            
            # CRM
            "https://docs.frappe.io/erpnext/user/manual/en/introduction-to-crm",
            "https://docs.frappe.io/erpnext/user/manual/en/crm-masters",
            "https://docs.frappe.io/erpnext/user/manual/en/managing-campaigns",
            "https://docs.frappe.io/erpnext/user/manual/en/sales-pipeline",
            "https://docs.frappe.io/erpnext/user/manual/en/crm-reports",
            "https://docs.frappe.io/erpnext/user/manual/en/crm-settings",
            
            # Selling
            "https://docs.frappe.io/erpnext/user/manual/en/introduction-to-selling-module",
            "https://docs.frappe.io/erpnext/user/manual/en/selling-essentials",
            "https://docs.frappe.io/erpnext/user/manual/en/selling-transactions",
            "https://docs.frappe.io/erpnext/user/manual/en/point-of-sale",
            "https://docs.frappe.io/erpnext/user/manual/en/selling-settings",
            "https://docs.frappe.io/erpnext/user/manual/en/sales-reports",
            
            # Buying
            "https://docs.frappe.io/erpnext/user/manual/en/introduction-to-buying-module",
            "https://docs.frappe.io/erpnext/user/manual/en/buying-settings",
            "https://docs.frappe.io/erpnext/user/manual/en/buying-reports",
            
            # Stock/Inventory
            "https://docs.frappe.io/erpnext/user/manual/en/introduction-stock-module",
            "https://docs.frappe.io/erpnext/user/manual/en/stock-masters",
            "https://docs.frappe.io/erpnext/user/manual/en/stock-transactions",
            "https://docs.frappe.io/erpnext/user/manual/en/stock-reports",
            
            # Data Management
            "https://docs.frappe.io/erpnext/user/manual/en/data-import",
            "https://docs.frappe.io/erpnext/user/manual/en/data-export",
            "https://docs.frappe.io/erpnext/user/manual/en/downloading-backups",
            "https://docs.frappe.io/erpnext/user/manual/en/bulk-renaming-of-records",
            "https://docs.frappe.io/erpnext/user/manual/en/bulk-update",
            
            # Additional important pages
            "https://docs.frappe.io/erpnext/user/manual/en/introduction",
            "https://docs.frappe.io/erpnext/user/manual/en/getting-started-with-erpnext",
            "https://docs.frappe.io/erpnext/user/manual/en/concepts-and-terms",
        ]
        
        self.scraped_data = {}
        self.failed_urls = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_all_documentation(self):
        """Scrape all target documentation URLs"""
        print(f"Starting enhanced documentation scraping for {len(self.target_urls)} URLs...")
        
        # Use ThreadPoolExecutor for faster scraping
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(self.scrape_page, url): url for url in self.target_urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Error scraping {url}: {str(e)}")
                    self.failed_urls.append(url)
                
                # Small delay to be respectful
                time.sleep(0.5)
        
        # Try to scrape related pages
        self.scrape_related_pages()
        
        # Save the scraped data
        self.save_documentation()
        print(f"\nScraping completed! Successfully scraped {len(self.scraped_data)} pages.")
        
        if self.failed_urls:
            print(f"Failed to scrape {len(self.failed_urls)} URLs:")
            for url in self.failed_urls:
                print(f"  - {url}")
    
    def scrape_page(self, url):
        """Scrape content from a single page"""
        try:
            print(f"Scraping: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract page content
            content = self.extract_content(soup, url)
            
            if content['title'] and content['text']:
                # Create a clean key for the page
                page_key = self.create_page_key(url, content['title'])
                content['url'] = url  # Store the original URL
                self.scraped_data[page_key] = content
                print(f"  ✓ Successfully scraped: {page_key}")
            else:
                print(f"  ⚠ No content found for: {url}")
                
        except Exception as e:
            print(f"  ✗ Error scraping {url}: {str(e)}")
            raise
    
    def extract_content(self, soup, url):
        """Extract meaningful content from a page"""
        content = {
            'title': '',
            'text': '',
            'headings': [],
            'sections': {},
            'url': url
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            content['title'] = title_tag.get_text().strip()
        
        # Also try h1 for title if title tag is generic
        h1_tag = soup.find('h1')
        if h1_tag and ('ERPNext' in content['title'] or 'Frappe' in content['title']):
            content['title'] = h1_tag.get_text().strip()
        
        # Try to find main content area
        main_content = None
        
        # Common content selectors for docs.frappe.io
        content_selectors = [
            '.content',
            'main',
            '.main-content', 
            '.documentation',
            '.docs-content',
            '.article',
            '.post-content',
            '#content',
            '.wiki-content'
        ]
        
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Remove unwanted elements
            for unwanted in main_content.find_all(['script', 'style', 'nav', 'footer', 'header', '.navbar', '.sidebar']):
                unwanted.decompose()
            
            # Extract structured content
            current_section = None
            section_content = []
            
            for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'div']):
                if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    # Save previous section
                    if current_section and section_content:
                        content['sections'][current_section] = ' '.join(section_content)
                    
                    # Start new section
                    current_section = element.get_text().strip()
                    content['headings'].append(current_section)
                    section_content = []
                    
                elif element.name in ['p', 'ul', 'ol', 'div']:
                    text = element.get_text().strip()
                    if text and len(text) > 10:  # Only meaningful content
                        section_content.append(text)
            
            # Save last section
            if current_section and section_content:
                content['sections'][current_section] = ' '.join(section_content)
            
            # Extract all text content
            text = main_content.get_text()
            # Clean up the text
            text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace with single space
            text = text.strip()
            content['text'] = text
        
        return content
    
    def scrape_related_pages(self):
        """Scrape related pages found in the main pages"""
        print("\nLooking for related pages...")
        
        related_urls = set()
        base_domain = "https://docs.frappe.io"
        
        # Look for links in already scraped content
        for page_data in self.scraped_data.values():
            if 'url' in page_data:
                try:
                    response = self.session.get(page_data['url'], timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find links to other documentation pages
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('/erpnext/user/manual/'):
                            full_url = base_domain + href
                            if full_url not in [data.get('url', '') for data in self.scraped_data.values()]:
                                related_urls.add(full_url)
                                
                except Exception as e:
                    continue
        
        # Scrape related pages (limit to avoid overwhelming)
        related_urls = list(related_urls)[:20]  # Limit to 20 additional pages
        
        if related_urls:
            print(f"Found {len(related_urls)} related pages to scrape...")
            for url in related_urls:
                try:
                    self.scrape_page(url)
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    print(f"Failed to scrape related page {url}: {str(e)}")
    
    def create_page_key(self, url, title):
        """Create a clean key for storing page data"""
        # Extract meaningful part from URL
        parsed = urlparse(url)
        path_parts = [part for part in parsed.path.split('/') if part and part != 'en']
        
        # Use the last meaningful part of the path
        if path_parts:
            key = path_parts[-1].replace('-', ' ').replace('_', ' ').title()
        else:
            key = title
        
        # Clean up the key
        key = re.sub(r'[^\w\s]', '', key)
        key = re.sub(r'\s+', ' ', key).strip()
        
        # Make it more descriptive
        if 'manual' in url:
            key = f"ERPNext {key}"
        
        return key or 'Unknown Page'
    
    def save_documentation(self):
        """Save scraped documentation to JSON file"""
        output_file = 'erpnext_documentation.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        
        print(f"Documentation saved to {output_file}")
        
        # Create summary and integration files
        self.create_summary()
        self.create_ai_integration_file()
    
    def create_summary(self):
        """Create a summary of scraped content"""
        summary = {
            'total_pages': len(self.scraped_data),
            'failed_urls': len(self.failed_urls),
            'pages': [],
            'modules_covered': set(),
            'topics_covered': []
        }
        
        for key, content in self.scraped_data.items():
            page_info = {
                'key': key,
                'title': content['title'],
                'headings_count': len(content['headings']),
                'sections_count': len(content.get('sections', {})),
                'text_length': len(content['text']),
                'url': content.get('url', '')
            }
            summary['pages'].append(page_info)
            
            # Extract module information
            url = content.get('url', '')
            if '/selling/' in url:
                summary['modules_covered'].add('Selling')
            elif '/buying/' in url:
                summary['modules_covered'].add('Buying')
            elif '/stock/' in url or '/inventory/' in url:
                summary['modules_covered'].add('Stock')
            elif '/accounting/' in url or '/accounts/' in url:
                summary['modules_covered'].add('Accounts')
            elif '/manufacturing/' in url:
                summary['modules_covered'].add('Manufacturing')
            elif '/crm/' in url:
                summary['modules_covered'].add('CRM')
            elif '/users/' in url or '/permissions/' in url:
                summary['modules_covered'].add('Users & Permissions')
            elif '/settings/' in url or '/setup/' in url:
                summary['modules_covered'].add('Setup')
        
        summary['modules_covered'] = list(summary['modules_covered'])
        
        with open('erpnext_documentation_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print("Summary saved to erpnext_documentation_summary.json")
        print(f"Modules covered: {', '.join(summary['modules_covered'])}")
    
    def create_ai_integration_file(self):
        """Create a file ready for AI integration"""
        ai_data = {}
        
        for key, content in self.scraped_data.items():
            # Create structured data for AI system
            ai_entry = {
                'description': content['title'],
                'topics': {}
            }
            
            # Use sections as topics
            if content.get('sections'):
                for section_title, section_content in content['sections'].items():
                    if len(section_content) > 50:  # Only meaningful content
                        ai_entry['topics'][section_title] = section_content[:500] + "..." if len(section_content) > 500 else section_content
            
            # If no sections, use the full text as a single topic
            if not ai_entry['topics'] and content['text']:
                ai_entry['topics']['Overview'] = content['text'][:1000] + "..." if len(content['text']) > 1000 else content['text']
            
            if ai_entry['topics']:  # Only add if we have content
                ai_data[key] = ai_entry
        
        with open('ai_documentation_data.json', 'w', encoding='utf-8') as f:
            json.dump(ai_data, f, indent=2, ensure_ascii=False)
        
        print("AI integration data saved to ai_documentation_data.json")

def main():
    """Main function to run the enhanced scraper"""
    scraper = EnhancedDocumentationScraper()
    scraper.scrape_all_documentation()
    
    print("\n" + "="*60)
    print("ENHANCED SCRAPING COMPLETED!")
    print("="*60)
    print("\nFiles created:")
    print("1. erpnext_documentation.json - Full scraped content")
    print("2. erpnext_documentation_summary.json - Overview and statistics")
    print("3. ai_documentation_data.json - Ready for AI integration")
    print("\nNext steps:")
    print("1. Review the scraped content")
    print("2. Copy ai_documentation_data.json to your Frappe server")
    print("3. Update frappe/utils/ai_help.py to load this data")
    print("4. Restart the Frappe server")
    print("\nTo integrate with the AI system:")
    print("- The ai_documentation_data.json file is formatted for direct integration")
    print("- Simply replace the DOCUMENTATION_CACHE in ai_help.py with this data")

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