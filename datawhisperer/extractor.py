"""
Entity extraction module using regex patterns
"""

import re
from typing import List, Dict, Any
import tldextract
import phonenumbers
from .utils import (
    sanitize_text, get_context_snippet, get_line_number,
    calculate_confidence, validate_hash
)


class EntityExtractor:
    """Extract entities from unstructured text"""
    
    # Regex patterns for various entity types
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ipv4': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
        'ipv6': r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}',
        'url': r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
        'md5': r'\b[a-fA-F0-9]{32}\b',
        'sha1': r'\b[a-fA-F0-9]{40}\b',
        'sha256': r'\b[a-fA-F0-9]{64}\b',
        'sha512': r'\b[a-fA-F0-9]{128}\b',
        'bitcoin': r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
        'ethereum': r'\b0x[a-fA-F0-9]{40}\b',
        'credentials': r'\b[a-zA-Z0-9._-]+:[^\s:]{4,}\b',
        'api_key': r'\b(?:api[_-]?key|apikey|api[_-]?secret|token)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?\b',
        'jwt': r'\beyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\b',
    }
    
    def __init__(self):
        self.entities = []
        
    def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract all entities from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of extracted entities with metadata
        """
        self.entities = []
        
        # Sanitize input
        clean_text = sanitize_text(text)
        
        # Extract each entity type
        self._extract_emails(clean_text)
        self._extract_ips(clean_text)
        self._extract_urls(clean_text)
        self._extract_hashes(clean_text)
        self._extract_crypto_wallets(clean_text)
        self._extract_phone_numbers(clean_text)
        self._extract_credentials(clean_text)
        self._extract_api_keys(clean_text)
        
        return self.entities
    
    def _add_entity(self, entity_type: str, value: str, position: int, 
                    text: str, method: str = 'regex', metadata: Dict = None):
        """Add an entity to the results"""
        
        # Avoid duplicates
        if any(e['value'] == value and e['type'] == entity_type for e in self.entities):
            return
        
        entity = {
            'type': entity_type,
            'value': value,
            'line': get_line_number(text, position),
            'context': get_context_snippet(text, position),
            'method': method,
            'confidence': 0.0,
            'metadata': metadata or {}
        }
        
        self.entities.append(entity)
    
    def _extract_emails(self, text: str):
        """Extract email addresses"""
        for match in re.finditer(self.PATTERNS['email'], text, re.IGNORECASE):
            email = match.group(0).lower()
            
            # Basic validation
            parts = email.split('@')
            if len(parts) == 2 and '.' in parts[1]:
                domain = parts[1]
                self._add_entity('email', email, match.start(), text, 
                               metadata={'domain': domain})
    
    def _extract_ips(self, text: str):
        """Extract IP addresses (IPv4 and IPv6)"""
        # IPv4
        for match in re.finditer(self.PATTERNS['ipv4'], text):
            ip = match.group(0)
            
            # Validate octets
            octets = [int(x) for x in ip.split('.')]
            if all(0 <= octet <= 255 for octet in octets):
                self._add_entity('ipv4', ip, match.start(), text)
        
        # IPv6
        for match in re.finditer(self.PATTERNS['ipv6'], text, re.IGNORECASE):
            ip = match.group(0)
            self._add_entity('ipv6', ip, match.start(), text)
    
    def _extract_urls(self, text: str):
        """Extract URLs and domains"""
        for match in re.finditer(self.PATTERNS['url'], text, re.IGNORECASE):
            url = match.group(0)
            
            # Extract domain using tldextract
            extracted = tldextract.extract(url)
            domain = f"{extracted.domain}.{extracted.suffix}" if extracted.suffix else extracted.domain
            
            self._add_entity('url', url, match.start(), text,
                           metadata={'domain': domain.lower(), 'subdomain': extracted.subdomain})
    
    def _extract_hashes(self, text: str):
        """Extract hash values (MD5, SHA1, SHA256, SHA512)"""
        hash_types = [
            ('md5', self.PATTERNS['md5']),
            ('sha1', self.PATTERNS['sha1']),
            ('sha256', self.PATTERNS['sha256']),
            ('sha512', self.PATTERNS['sha512'])
        ]
        
        for hash_type, pattern in hash_types:
            for match in re.finditer(pattern, text):
                hash_value = match.group(0).lower()
                
                # Validate hash format
                if validate_hash(hash_value, hash_type):
                    self._add_entity(hash_type, hash_value, match.start(), text)
    
    def _extract_crypto_wallets(self, text: str):
        """Extract cryptocurrency wallet addresses"""
        # Bitcoin addresses
        for match in re.finditer(self.PATTERNS['bitcoin'], text):
            wallet = match.group(0)
            # Basic validation: starts with 1 or 3, correct length
            if wallet[0] in '13' and 25 <= len(wallet) <= 34:
                self._add_entity('bitcoin_wallet', wallet, match.start(), text,
                               metadata={'currency': 'BTC'})
        
        # Ethereum addresses
        for match in re.finditer(self.PATTERNS['ethereum'], text, re.IGNORECASE):
            wallet = match.group(0)
            # Validate length (42 characters including 0x)
            if len(wallet) == 42:
                self._add_entity('ethereum_wallet', wallet.lower(), match.start(), text,
                               metadata={'currency': 'ETH'})
    
    def _extract_phone_numbers(self, text: str):
        """Extract phone numbers using phonenumbers library"""
        # Try to find phone numbers (default to US region)
        try:
            for match in phonenumbers.PhoneNumberMatcher(text, "US"):
                phone = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
                self._add_entity('phone', phone, match.start, text,
                               metadata={
                                   'country': phonenumbers.region_code_for_number(match.number),
                                   'type': phonenumbers.number_type(match.number)
                               })
        except Exception:
            # Fallback to simple pattern if phonenumbers fails
            simple_phone = r'\+?[1-9]\d{1,14}'
            for match in re.finditer(simple_phone, text):
                phone = match.group(0)
                if 10 <= len(phone.replace('+', '')) <= 15:
                    self._add_entity('phone', phone, match.start(), text)
    
    def _extract_credentials(self, text: str):
        """Extract potential credential patterns (user:pass)"""
        for match in re.finditer(self.PATTERNS['credentials'], text):
            cred = match.group(0)
            parts = cred.split(':')
            
            # Validate credential format
            if len(parts) == 2:
                username, password = parts
                
                # Avoid false positives (URLs, timestamps, etc.)
                if not any(x in username.lower() for x in ['http', 'https', 'ftp']):
                    if 3 <= len(username) <= 50 and 4 <= len(password) <= 100:
                        self._add_entity('credential', cred, match.start(), text,
                                       metadata={'username': username})
    
    def _extract_api_keys(self, text: str):
        """Extract API keys and JWT tokens"""
        # API Keys
        for match in re.finditer(self.PATTERNS['api_key'], text, re.IGNORECASE):
            if match.groups():
                key = match.group(1)
                if len(key) >= 20:
                    self._add_entity('api_key', key, match.start(), text)
        
        # JWT Tokens
        for match in re.finditer(self.PATTERNS['jwt'], text):
            jwt = match.group(0)
            parts = jwt.split('.')
            if len(parts) == 3:  # Valid JWT structure
                self._add_entity('jwt_token', jwt, match.start(), text,
                               metadata={'parts': len(parts)})
    
    def get_summary(self) -> Dict[str, int]:
        """
        Get summary counts of extracted entities
        
        Returns:
            Dictionary with entity type counts
        """
        summary = {}
        for entity in self.entities:
            entity_type = entity['type']
            summary[entity_type] = summary.get(entity_type, 0) + 1
        return summary

