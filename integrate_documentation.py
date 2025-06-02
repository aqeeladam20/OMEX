#!/usr/bin/env python3
"""
Documentation Integration Script
This script integrates scraped documentation with the AI help system
"""

import json
import os
import shutil
from pathlib import Path

def load_scraped_documentation():
    """Load the scraped documentation data"""
    ai_data_file = 'ai_documentation_data.json'
    
    if not os.path.exists(ai_data_file):
        print(f"Error: {ai_data_file} not found!")
        print("Please run the enhanced_scraper.py first to generate the documentation data.")
        return None
    
    with open(ai_data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_ai_help_system(documentation_data):
    """Update the AI help system with scraped documentation"""
    ai_help_file = 'frappe/frappe/utils/ai_help.py'
    
    if not os.path.exists(ai_help_file):
        print(f"Error: {ai_help_file} not found!")
        print("Make sure you're running this from the correct directory.")
        return False
    
    # Create backup
    backup_file = ai_help_file + '.backup'
    shutil.copy2(ai_help_file, backup_file)
    print(f"Created backup: {backup_file}")
    
    # Read the current file
    with open(ai_help_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the DOCUMENTATION_CACHE definition
    start_marker = 'DOCUMENTATION_CACHE = {'
    end_marker = '\t}'
    
    start_index = content.find(start_marker)
    if start_index == -1:
        print("Error: Could not find DOCUMENTATION_CACHE in ai_help.py")
        return False
    
    # Find the end of the dictionary
    brace_count = 0
    end_index = start_index
    for i, char in enumerate(content[start_index:], start_index):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_index = i + 1
                break
    
    # Generate new documentation cache
    new_cache = "DOCUMENTATION_CACHE = " + json.dumps(documentation_data, indent=2, ensure_ascii=False)
    
    # Replace the old cache with new one
    new_content = content[:start_index] + new_cache + content[end_index:]
    
    # Write the updated file
    with open(ai_help_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Successfully updated {ai_help_file} with {len(documentation_data)} documentation entries")
    return True

def create_integration_summary(documentation_data):
    """Create a summary of the integration"""
    summary = {
        'total_topics': len(documentation_data),
        'topics_by_module': {},
        'integration_date': str(Path().cwd()),
        'topics': []
    }
    
    for topic_name, topic_data in documentation_data.items():
        topic_info = {
            'name': topic_name,
            'description': topic_data.get('description', ''),
            'subtopics_count': len(topic_data.get('topics', {}))
        }
        summary['topics'].append(topic_info)
        
        # Categorize by module (basic categorization)
        if any(keyword in topic_name.lower() for keyword in ['selling', 'sales', 'customer', 'quotation']):
            module = 'Selling'
        elif any(keyword in topic_name.lower() for keyword in ['buying', 'purchase', 'supplier']):
            module = 'Buying'
        elif any(keyword in topic_name.lower() for keyword in ['stock', 'inventory', 'item', 'warehouse']):
            module = 'Stock'
        elif any(keyword in topic_name.lower() for keyword in ['account', 'finance', 'ledger', 'tax']):
            module = 'Accounts'
        elif any(keyword in topic_name.lower() for keyword in ['manufacturing', 'bom', 'work order']):
            module = 'Manufacturing'
        elif any(keyword in topic_name.lower() for keyword in ['crm', 'lead', 'opportunity']):
            module = 'CRM'
        elif any(keyword in topic_name.lower() for keyword in ['user', 'permission', 'role']):
            module = 'Users & Permissions'
        elif any(keyword in topic_name.lower() for keyword in ['setting', 'config', 'setup']):
            module = 'Setup'
        else:
            module = 'General'
        
        if module not in summary['topics_by_module']:
            summary['topics_by_module'][module] = 0
        summary['topics_by_module'][module] += 1
    
    with open('integration_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("Integration summary saved to integration_summary.json")
    return summary

def validate_integration():
    """Validate that the integration was successful"""
    ai_help_file = 'frappe/frappe/utils/ai_help.py'
    
    try:
        with open(ai_help_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the file is valid Python
        compile(content, ai_help_file, 'exec')
        
        # Check if DOCUMENTATION_CACHE exists and is not empty
        if 'DOCUMENTATION_CACHE = {' in content and len(content.split('DOCUMENTATION_CACHE = {')[1].split('}')[0]) > 10:
            print("✓ Integration validation successful")
            return True
        else:
            print("✗ Integration validation failed - DOCUMENTATION_CACHE appears empty")
            return False
            
    except SyntaxError as e:
        print(f"✗ Integration validation failed - Syntax error: {e}")
        return False
    except Exception as e:
        print(f"✗ Integration validation failed - Error: {e}")
        return False

def main():
    """Main integration function"""
    print("="*60)
    print("DOCUMENTATION INTEGRATION SCRIPT")
    print("="*60)
    
    # Step 1: Load scraped documentation
    print("\n1. Loading scraped documentation...")
    documentation_data = load_scraped_documentation()
    if not documentation_data:
        return
    
    print(f"   ✓ Loaded {len(documentation_data)} documentation topics")
    
    # Step 2: Update AI help system
    print("\n2. Updating AI help system...")
    if not update_ai_help_system(documentation_data):
        print("   ✗ Failed to update AI help system")
        return
    
    # Step 3: Create integration summary
    print("\n3. Creating integration summary...")
    summary = create_integration_summary(documentation_data)
    print(f"   ✓ Topics by module: {summary['topics_by_module']}")
    
    # Step 4: Validate integration
    print("\n4. Validating integration...")
    if not validate_integration():
        print("   ✗ Integration validation failed")
        return
    
    print("\n" + "="*60)
    print("INTEGRATION COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\nNext steps:")
    print("1. Restart your Frappe server: bench restart")
    print("2. Test the AI help system by clicking help links in ERPNext")
    print("3. The system now has comprehensive ERPNext documentation")
    print("\nFiles created/updated:")
    print("- frappe/frappe/utils/ai_help.py (updated with new documentation)")
    print("- frappe/frappe/utils/ai_help.py.backup (backup of original)")
    print("- integration_summary.json (summary of integration)")
    
    print(f"\nDocumentation coverage:")
    for module, count in summary['topics_by_module'].items():
        print(f"  {module}: {count} topics")

if __name__ == "__main__":
    main() 