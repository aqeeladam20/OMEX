import frappe

def get_openai_api_key():
    """Get OpenAI API key from site config or environment"""
    return frappe.conf.get("openai_api_key") or "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"

def get_ai_settings():
    """Get AI assistant settings"""
    return {
        "model": "gpt-3.5-turbo",
        "max_tokens": 500,
        "temperature": 0.7,
        "enabled": True
    } 