# AI Help System for ERPNext/Frappe

This system replaces external documentation links with a local AI-powered help system that provides contextual assistance without requiring internet access.

## What Was Changed

### 1. Removed External Documentation Links
- **Before**: Help links opened external websites (erpnext.com/docs, frappeframework.com/docs)
- **After**: Help links trigger local AI assistance with contextual information

### 2. Files Modified
- `erpnext/erpnext/public/js/help_links.js` - Main help links configuration
- `frappe/frappe/public/js/frappe/utils/help_links.js` - Frappe help links
- `frappe/frappe/public/js/frappe/ui/toolbar/toolbar.js` - Help dropdown handler
- `frappe/frappe/utils/ai_help.py` - New AI help backend system

## How It Works

### User Experience
1. **Click Help**: Users click on help links in any module
2. **AI Dialog**: A modal opens with AI-generated help content
3. **Interactive Chat**: Users can ask follow-up questions
4. **Contextual Responses**: AI provides module-specific guidance

### Technical Flow
```
User clicks help → JavaScript calls showAIHelp() → 
Backend frappe.utils.ai_help.get_help() → 
AI generates response → Modal displays content
```

## Features

### ✅ Current Features
- **Local Help System**: No external dependencies
- **Module-Aware**: Context changes based on current module
- **Interactive Chat**: Follow-up questions and answers
- **Fallback Responses**: Generic help when specific info unavailable
- **Error Handling**: Graceful degradation if AI system fails

### 🚀 Enhanced Features (After Documentation Scraping)
- **Comprehensive Knowledge**: Full ERPNext/Frappe documentation
- **Accurate Responses**: Based on official documentation
- **Search Capability**: Find specific topics quickly
- **Version-Specific**: Documentation matches your ERPNext version

## Documentation Scraping & Integration

### Step 1: Run the Enhanced Scraper
```bash
# Install required packages
pip install requests beautifulsoup4

# Run the enhanced scraper with specific ERPNext URLs
python enhanced_scraper.py
```

### Step 2: Review Scraped Data
The enhanced scraper creates three files:
- `erpnext_documentation.json` - Full scraped content
- `erpnext_documentation_summary.json` - Overview and statistics
- `ai_documentation_data.json` - Ready for AI integration

### Step 3: Integrate with AI System (Automated)
```bash
# Run the integration script
python integrate_documentation.py
```

### Step 4: Manual Integration (Alternative)
If you prefer manual integration:
1. Copy `ai_documentation_data.json` to your Frappe server
2. Replace the `DOCUMENTATION_CACHE` in `frappe/utils/ai_help.py` with the JSON data
3. Restart the Frappe server

### Step 5: Restart and Test
```bash
# Restart Frappe server
bench restart

# Test the AI help system by clicking help links in any ERPNext module
```

## Customization

### Adding New Help Topics
Edit `frappe/utils/ai_help.py` and add to `DOCUMENTATION_CACHE`:

```python
"Your Topic": {
    "description": "Brief description of the topic",
    "topics": {
        "Subtopic 1": "Detailed explanation...",
        "Subtopic 2": "Another explanation..."
    }
}
```

### Module-Specific Help
Add module mappings in `get_module_help_topics()`:

```python
module_topics = {
    'YourModule': ['Topic 1', 'Topic 2', 'Topic 3'],
    # ... existing modules
}
```

### Custom AI Responses
Enhance `generate_answer()` function with more keyword patterns:

```python
if 'your_keyword' in question_lower:
    return "Your custom response here"
```

## Benefits

### For Users
- **Faster Help**: No waiting for external pages to load
- **Offline Access**: Works without internet connection
- **Contextual**: Help is relevant to current module/page
- **Interactive**: Can ask specific questions

### For Administrators
- **No External Dependencies**: Fully self-contained
- **Customizable**: Add company-specific help content
- **Trackable**: Monitor what users need help with
- **Secure**: No data sent to external servers

## Troubleshooting

### Help Links Not Working
1. Check browser console for JavaScript errors
2. Verify `frappe/utils/ai_help.py` is accessible
3. Restart Frappe server after changes

### AI Responses Not Loading
1. Check Frappe error logs
2. Verify `@frappe.whitelist()` decorators are present
3. Test backend methods directly in console

### Missing Documentation
1. Run the scraper script to get more content
2. Add manual entries to `DOCUMENTATION_CACHE`
3. Check scraped JSON files for completeness

## Future Enhancements

### Planned Features
- **Search Integration**: Global search for help topics
- **User Feedback**: Rate help responses for improvement
- **Analytics**: Track most requested help topics
- **Multi-language**: Support for different languages

### AI Integration Options
- **OpenAI API**: For more sophisticated responses
- **Local LLM**: Run language models locally
- **Vector Search**: Semantic search through documentation
- **Learning System**: Improve responses based on usage

## File Structure

```
frappe/
├── frappe/
│   ├── public/js/frappe/
│   │   ├── ui/toolbar/toolbar.js          # Help dropdown handler
│   │   └── utils/help_links.js            # Frappe help links
│   └── utils/
│       └── ai_help.py                     # AI help backend
└── erpnext/
    └── erpnext/public/js/
        └── help_links.js                  # Main help links config

# Scraping files (run locally)
scrape_documentation.py                    # Documentation scraper
scraped_documentation.json                # Scraped content
documentation_summary.json                # Scraping summary
```

## Support

For issues or questions about the AI help system:
1. Check the error logs in Frappe
2. Review the browser console for JavaScript errors
3. Test individual components (backend methods, frontend functions)
4. Verify all files are properly updated and server is restarted

---

**Note**: This system provides a foundation for local AI help. The quality and comprehensiveness of responses will improve significantly after running the documentation scraper and integrating the scraped content. 