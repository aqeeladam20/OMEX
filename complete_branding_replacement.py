#!/usr/bin/env python3
"""
Complete branding replacement script to replace all ERPNext references with OMEX
Handles JSON files, Python files, and text files comprehensively
"""

import json
import re
import os
import glob
from pathlib import Path

def replace_erpnext_in_text(text):
    """Replace all variations of ERPNext with OMEX in text"""
    replacements = [
        # Direct replacements
        ('ERPNext', 'OMEX'),
        ('Erpnext', 'OMEX'),
        ('erpnext', 'OMEX'),
        ('ERPNEXT', 'OMEX'),
        
        # Context-aware replacements
        ('ERPNext ERP', 'OMEX ERP'),
        ('ERPNext system', 'OMEX ERP system'),
        ('ERPNext application', 'OMEX ERP application'),
        ('ERPNext software', 'OMEX ERP software'),
        ('ERPNext platform', 'OMEX ERP platform'),
        ('in ERPNext', 'in OMEX ERP'),
        ('to ERPNext', 'to OMEX ERP'),
        ('from ERPNext', 'from OMEX ERP'),
        ('using ERPNext', 'using OMEX ERP'),
        ('with ERPNext', 'with OMEX ERP'),
        
        # Technical references
        ('ERPNext will', 'OMEX ERP will'),
        ('ERPNext allows', 'OMEX ERP allows'),
        ('ERPNext uses', 'OMEX ERP uses'),
        ('ERPNext provides', 'OMEX ERP provides'),
        ('ERPNext has', 'OMEX ERP has'),
        ('ERPNext can', 'OMEX ERP can'),
        ('ERPNext enables', 'OMEX ERP enables'),
        ('ERPNext supports', 'OMEX ERP supports'),
        
        # Documentation specific
        ('ERPNext documentation', 'OMEX ERP documentation'),
        ('ERPNext manual', 'OMEX ERP manual'),
        ('ERPNext help', 'OMEX ERP help'),
        ('ERPNext guide', 'OMEX ERP guide'),
        
        # Version references
        ('ERPNext v', 'OMEX ERP v'),
        ('ERPNext version', 'OMEX ERP version'),
        
        # Installation and setup
        ('install ERPNext', 'install OMEX ERP'),
        ('setup ERPNext', 'setup OMEX ERP'),
        ('configure ERPNext', 'configure OMEX ERP'),
    ]
    
    for old, new in replacements:
        text = text.replace(old, new)
    
    return text

def process_json_file(filepath):
    """Process a JSON file and replace ERPNext references"""
    print(f"Processing JSON file: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to string, replace, and convert back
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        updated_str = replace_erpnext_in_text(json_str)
        updated_data = json.loads(updated_str)
        
        # Write back the updated data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated {filepath}")
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")

def process_text_file(filepath):
    """Process a text file and replace ERPNext references"""
    print(f"Processing text file: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated_content = replace_erpnext_in_text(content)
        
        if content != updated_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ Updated {filepath}")
        else:
            print(f"ℹ️ No changes needed in {filepath}")
            
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")

def main():
    """Main function to process all relevant files"""
    print("🔄 Starting comprehensive ERPNext to OMEX branding replacement...")
    
    # Current directory (apps folder)
    base_dir = Path('.')
    
    # Files to process
    files_to_process = [
        # AI documentation files
        'ai_documentation_data.json',
        'erpnext_documentation.json',
        'erpnext_documentation_summary.json',
        
        # AI help system files
        'frappe/frappe/utils/ai_help.py',
        'erpnext/erpnext/ai_assistant/ai_chat.py',
        
        # JavaScript files
        'erpnext/erpnext/public/js/ai_assistant.js',
        'erpnext/erpnext/public/js/help_links.js',
        
        # Documentation files
        'AI_HELP_SYSTEM_README.md',
    ]
    
    # Process specific files
    for filepath in files_to_process:
        full_path = base_dir / filepath
        if full_path.exists():
            if filepath.endswith('.json'):
                process_json_file(full_path)
            else:
                process_text_file(full_path)
        else:
            print(f"⚠️ File not found: {filepath}")
    
    # Process all Python files in erpnext/ai_assistant directory
    ai_assistant_dir = base_dir / 'erpnext' / 'erpnext' / 'ai_assistant'
    if ai_assistant_dir.exists():
        for py_file in ai_assistant_dir.glob('*.py'):
            process_text_file(py_file)
    
    print("\n✅ Comprehensive branding replacement completed!")
    print("🔄 Please rebuild assets: bench build --app erpnext")

if __name__ == "__main__":
    main() 