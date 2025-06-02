#!/usr/bin/env python3
"""
Script to replace ERPNext branding with OMEX in documentation files
"""

import json
import re
import os
import shutil

def replace_branding(text):
    """Replace ERPNext with OMEX in text while preserving case"""
    # Handle different case variations
    replacements = [
        ('ERPNext', 'OMEX'),
        ('Erpnext', 'OMEX'),
        ('erpnext', 'omex'),
        ('ERPNEXT', 'OMEX')
    ]
    
    for old, new in replacements:
        text = text.replace(old, new)
    
    return text

def update_json_file(filename):
    """Update branding in a JSON file"""
    print(f"Processing {filename}...")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # For documentation JSON
        if isinstance(data, dict):
            updated_data = {}
            for key, value in data.items():
                # Update key
                new_key = replace_branding(key)
                
                # Update values recursively
                if isinstance(value, dict):
                    new_value = {}
                    for k, v in value.items():
                        new_k = replace_branding(k)
                        if isinstance(v, str):
                            new_value[new_k] = replace_branding(v)
                        elif isinstance(v, dict):
                            new_value[new_k] = {
                                replace_branding(sk): replace_branding(sv) if isinstance(sv, str) else sv
                                for sk, sv in v.items()
                            }
                        else:
                            new_value[new_k] = v
                elif isinstance(value, str):
                    new_value = replace_branding(value)
                else:
                    new_value = value
                
                updated_data[new_key] = new_value
        
        # Write back the updated data
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Successfully updated {filename}")
        
    except FileNotFoundError:
        print(f"✗ File not found: {filename}")
    except json.JSONDecodeError:
        print(f"✗ Invalid JSON in {filename}")
    except Exception as e:
        print(f"✗ Error processing {filename}: {str(e)}")

def update_text_file(filename):
    """Update branding in a text file"""
    print(f"Processing {filename}...")
    
    try:
        # Create backup
        backup_file = filename + '.backup'
        if not os.path.exists(backup_file):
            shutil.copy2(filename, backup_file)
            print(f"Created backup: {backup_file}")
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated_content = replace_branding(content)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✓ Successfully updated {filename}")
        
    except FileNotFoundError:
        print(f"✗ File not found: {filename}")
    except Exception as e:
        print(f"✗ Error processing {filename}: {str(e)}")

def main():
    """Main function to update all documentation files"""
    # JSON files
    json_files = [
        'erpnext_documentation.json',
        'erpnext_documentation_summary.json',
        'ai_documentation_data.json',
        'integration_summary.json'
    ]
    
    # Text files
    text_files = [
        'AI_HELP_SYSTEM_README.md',
        'frappe/frappe/utils/ai_help.py',
        'frappe/frappe/public/js/frappe/utils/help_links.js',
        'frappe/frappe/public/js/frappe/ui/toolbar/toolbar.js',
        'erpnext/erpnext/public/js/help_links.js'
    ]
    
    print("Starting branding update...")
    print("="*60)
    
    print("\nUpdating JSON files...")
    for filename in json_files:
        update_json_file(filename)
    
    print("\nUpdating text files...")
    for filename in text_files:
        update_text_file(filename)
    
    print("\nBranding update completed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review the updated files")
    print("2. Run the integration script to update the AI help system")
    print("3. Restart the Frappe server")
    print("\nBackups have been created with .backup extension")

if __name__ == "__main__":
    main() 