"""
Utility functions for Data Whisperer
"""

import re
import hashlib
from typing import Optional, List
import pyperclip


def sanitize_text(text: str) -> str:
    """
    Sanitize and normalize input text
    
    Args:
        text: Raw input text
        
    Returns:
        Sanitized text
    """
    # Remove null bytes and other control characters
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\r\n', '\n', text)
    
    return text


def calculate_confidence(entity_value: str, entity_type: str, validation_passed: bool) -> float:
    """
    Calculate confidence score for an entity
    
    Args:
        entity_value: The extracted entity value
        entity_type: Type of entity (email, ip, hash, etc.)
        validation_passed: Whether validation checks passed
        
    Returns:
        Confidence score between 0 and 1
    """
    base_score = 0.5
    
    if validation_passed:
        base_score = 0.9
    
    # Adjust based on entity characteristics
    if entity_type == 'email':
        if '@' in entity_value and '.' in entity_value.split('@')[1]:
            base_score = min(base_score + 0.1, 1.0)
    
    elif entity_type == 'ip':
        # IPv4 with valid octets gets higher confidence
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', entity_value):
            base_score = min(base_score + 0.1, 1.0)
    
    elif entity_type in ['md5', 'sha1', 'sha256', 'sha512']:
        # Hash lengths must be exact
        expected_lengths = {'md5': 32, 'sha1': 40, 'sha256': 64, 'sha512': 128}
        if len(entity_value) == expected_lengths.get(entity_type, 0):
            base_score = 1.0
    
    return round(base_score, 2)


def get_context_snippet(text: str, position: int, window: int = 50) -> str:
    """
    Extract a context snippet around a position in text
    
    Args:
        text: Full text
        position: Character position
        window: Characters to include before/after
        
    Returns:
        Context snippet
    """
    start = max(0, position - window)
    end = min(len(text), position + window)
    snippet = text[start:end]
    
    # Add ellipsis if truncated
    if start > 0:
        snippet = '...' + snippet
    if end < len(text):
        snippet = snippet + '...'
    
    return snippet.strip()


def get_line_number(text: str, position: int) -> int:
    """
    Get line number for a character position
    
    Args:
        text: Full text
        position: Character position
        
    Returns:
        Line number (1-indexed)
    """
    return text[:position].count('\n') + 1


def read_from_clipboard() -> Optional[str]:
    """
    Read text from clipboard
    
    Returns:
        Clipboard text or None if error
    """
    try:
        return pyperclip.paste()
    except Exception as e:
        print(f"Error reading clipboard: {e}")
        return None


def validate_hash(value: str, hash_type: str) -> bool:
    """
    Validate hash format
    
    Args:
        value: Hash string
        hash_type: Type of hash (md5, sha1, sha256, sha512)
        
    Returns:
        True if valid format
    """
    hash_lengths = {
        'md5': 32,
        'sha1': 40,
        'sha256': 64,
        'sha512': 128
    }
    
    if hash_type not in hash_lengths:
        return False
    
    # Check length and hex characters
    if len(value) != hash_lengths[hash_type]:
        return False
    
    return bool(re.match(r'^[a-fA-F0-9]+$', value))


def extract_domain_from_email(email: str) -> Optional[str]:
    """
    Extract domain from email address
    
    Args:
        email: Email address
        
    Returns:
        Domain or None
    """
    if '@' in email:
        return email.split('@')[1].lower()
    return None


def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain from URL
    
    Args:
        url: URL string
        
    Returns:
        Domain or None
    """
    # Simple domain extraction
    match = re.search(r'(?:https?://)?(?:www\.)?([^/:\s]+)', url)
    if match:
        return match.group(1).lower()
    return None


def normalize_ip(ip: str) -> str:
    """
    Normalize IP address format
    
    Args:
        ip: IP address string
        
    Returns:
        Normalized IP
    """
    # Remove leading zeros from IPv4
    if '.' in ip and ':' not in ip:
        parts = ip.split('.')
        return '.'.join(str(int(p)) for p in parts)
    return ip


def is_private_ip(ip: str) -> bool:
    """
    Check if IP is private/internal
    
    Args:
        ip: IP address
        
    Returns:
        True if private IP
    """
    private_ranges = [
        r'^10\.',
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',
        r'^192\.168\.',
        r'^127\.',
        r'^169\.254\.',
        r'^::1$',
        r'^fe80:',
        r'^fc00:',
        r'^fd00:'
    ]
    
    for pattern in private_ranges:
        if re.match(pattern, ip):
            return True
    return False

