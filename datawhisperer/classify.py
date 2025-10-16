"""
Entity classification and validation module
"""

import re
from typing import List, Dict, Any
from collections import defaultdict
from .utils import (
    calculate_confidence, extract_domain_from_email,
    extract_domain_from_url, is_private_ip
)


class EntityClassifier:
    """Classify and validate extracted entities"""
    
    def __init__(self):
        self.entities = []
        self.classified = {}
        
    def classify(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Classify and validate entities
        
        Args:
            entities: List of extracted entities
            
        Returns:
            Classified entities with validation and grouping
        """
        self.entities = entities
        self.classified = {
            'entities': [],
            'groups': {},
            'relationships': [],
            'statistics': {}
        }
        
        # Validate and score each entity
        validated_entities = []
        for entity in entities:
            validated = self._validate_entity(entity)
            if validated:
                validated_entities.append(validated)
        
        self.classified['entities'] = validated_entities
        
        # Group entities by type and attributes
        self._group_entities(validated_entities)
        
        # Extract relationships
        self._extract_relationships(validated_entities)
        
        # Generate statistics
        self._generate_statistics(validated_entities)
        
        return self.classified
    
    def _validate_entity(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and score an entity"""
        entity_type = entity['type']
        value = entity['value']
        
        validation_passed = True
        
        # Type-specific validation
        if entity_type == 'email':
            validation_passed = self._validate_email(value)
            
        elif entity_type in ['ipv4', 'ipv6']:
            validation_passed = self._validate_ip(value, entity_type)
            entity['metadata']['is_private'] = is_private_ip(value)
            
        elif entity_type == 'url':
            validation_passed = self._validate_url(value)
            
        elif entity_type in ['md5', 'sha1', 'sha256', 'sha512']:
            validation_passed = self._validate_hash(value, entity_type)
            
        elif entity_type == 'bitcoin_wallet':
            validation_passed = self._validate_bitcoin(value)
            
        elif entity_type == 'ethereum_wallet':
            validation_passed = self._validate_ethereum(value)
            
        elif entity_type == 'credential':
            validation_passed = self._validate_credential(value)
            
        elif entity_type == 'phone':
            validation_passed = self._validate_phone(value)
        
        # Calculate confidence score
        entity['confidence'] = calculate_confidence(value, entity_type, validation_passed)
        entity['validated'] = validation_passed
        
        return entity if validation_passed else None
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        # RFC 5322 simplified validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Z|a-z]{2,}$'
        if not re.match(pattern, email):
            return False
        
        # Check for common false positives
        invalid_tlds = ['.local', '.test', '.example', '.invalid']
        if any(email.lower().endswith(tld) for tld in invalid_tlds):
            return False
        
        return True
    
    def _validate_ip(self, ip: str, ip_type: str) -> bool:
        """Validate IP address"""
        if ip_type == 'ipv4':
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            
            try:
                octets = [int(p) for p in parts]
                if not all(0 <= octet <= 255 for octet in octets):
                    return False
                
                # Reject obviously invalid IPs
                if octets[0] == 0 or octets[0] >= 240:
                    return False
                
                return True
            except ValueError:
                return False
        
        elif ip_type == 'ipv6':
            # Basic IPv6 validation
            if '::' in ip:
                parts = ip.split('::')
                if len(parts) > 2:
                    return False
            
            return True
        
        return False
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format"""
        # Must have protocol and valid structure
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Check for common false positives
        if any(x in url.lower() for x in ['example.com', 'localhost']):
            return False
        
        return True
    
    def _validate_hash(self, value: str, hash_type: str) -> bool:
        """Validate hash format"""
        expected_lengths = {
            'md5': 32,
            'sha1': 40,
            'sha256': 64,
            'sha512': 128
        }
        
        if hash_type not in expected_lengths:
            return False
        
        # Check length and hex format
        if len(value) != expected_lengths[hash_type]:
            return False
        
        if not re.match(r'^[a-fA-F0-9]+$', value):
            return False
        
        # Reject all-zeros or all-same-digit hashes (likely false positives)
        if len(set(value.lower())) <= 2:
            return False
        
        return True
    
    def _validate_bitcoin(self, address: str) -> bool:
        """Validate Bitcoin address"""
        # Basic validation: length and format
        if not (25 <= len(address) <= 34):
            return False
        
        if address[0] not in '13':
            return False
        
        # Check for valid base58 characters
        valid_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        if not all(c in valid_chars for c in address):
            return False
        
        return True
    
    def _validate_ethereum(self, address: str) -> bool:
        """Validate Ethereum address"""
        # Must be 42 characters (0x + 40 hex)
        if len(address) != 42:
            return False
        
        if not address.startswith('0x'):
            return False
        
        # Check hex format
        if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
            return False
        
        return True
    
    def _validate_credential(self, credential: str) -> bool:
        """Validate credential format"""
        parts = credential.split(':')
        if len(parts) != 2:
            return False
        
        username, password = parts
        
        # Username validation
        if len(username) < 3 or len(username) > 50:
            return False
        
        # Password validation
        if len(password) < 4 or len(password) > 100:
            return False
        
        # Reject common false positives
        false_positives = ['http', 'https', 'ftp', 'port', 'time']
        if any(fp in username.lower() for fp in false_positives):
            return False
        
        return True
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number"""
        # Remove formatting
        digits = re.sub(r'[^\d]', '', phone)
        
        # Valid phone number length
        if not (10 <= len(digits) <= 15):
            return False
        
        return True
    
    def _group_entities(self, entities: List[Dict[str, Any]]):
        """Group entities by type and attributes"""
        groups = defaultdict(list)
        
        # Group by type
        for entity in entities:
            groups[entity['type']].append(entity)
        
        # Additional grouping by domain for emails
        email_domains = defaultdict(list)
        for entity in groups.get('email', []):
            domain = entity['metadata'].get('domain')
            if domain:
                email_domains[domain].append(entity['value'])
        
        # Group URLs by domain
        url_domains = defaultdict(list)
        for entity in groups.get('url', []):
            domain = entity['metadata'].get('domain')
            if domain:
                url_domains[domain].append(entity['value'])
        
        # Group IPs by subnet (for IPv4)
        ip_subnets = defaultdict(list)
        for entity in groups.get('ipv4', []):
            parts = entity['value'].split('.')
            subnet = '.'.join(parts[:3]) + '.0/24'
            ip_subnets[subnet].append(entity['value'])
        
        self.classified['groups'] = {
            'by_type': {k: [e['value'] for e in v] for k, v in groups.items()},
            'email_domains': dict(email_domains),
            'url_domains': dict(url_domains),
            'ip_subnets': dict(ip_subnets)
        }
    
    def _extract_relationships(self, entities: List[Dict[str, Any]]):
        """Extract relationships between entities"""
        relationships = []
        
        # Email -> Domain relationships
        for entity in entities:
            if entity['type'] == 'email':
                domain = entity['metadata'].get('domain')
                if domain:
                    relationships.append({
                        'type': 'email_to_domain',
                        'source': entity['value'],
                        'target': domain,
                        'confidence': entity['confidence']
                    })
        
        # URL -> Domain relationships
        for entity in entities:
            if entity['type'] == 'url':
                domain = entity['metadata'].get('domain')
                if domain:
                    relationships.append({
                        'type': 'url_to_domain',
                        'source': entity['value'],
                        'target': domain,
                        'confidence': entity['confidence']
                    })
        
        # Find shared domains between emails and URLs
        email_domains = set()
        url_domains = set()
        
        for entity in entities:
            if entity['type'] == 'email':
                domain = entity['metadata'].get('domain')
                if domain:
                    email_domains.add(domain)
            elif entity['type'] == 'url':
                domain = entity['metadata'].get('domain')
                if domain:
                    url_domains.add(domain)
        
        # Create relationships for shared domains
        shared_domains = email_domains.intersection(url_domains)
        for domain in shared_domains:
            relationships.append({
                'type': 'shared_domain',
                'source': 'email',
                'target': 'url',
                'via': domain,
                'confidence': 0.9
            })
        
        self.classified['relationships'] = relationships
    
    def _generate_statistics(self, entities: List[Dict[str, Any]]):
        """Generate statistics about entities"""
        stats = {
            'total_entities': len(entities),
            'by_type': {},
            'confidence_avg': 0,
            'high_confidence': 0,
            'validation_rate': 0
        }
        
        # Count by type
        for entity in entities:
            entity_type = entity['type']
            stats['by_type'][entity_type] = stats['by_type'].get(entity_type, 0) + 1
        
        # Calculate averages
        if entities:
            total_confidence = sum(e['confidence'] for e in entities)
            stats['confidence_avg'] = round(total_confidence / len(entities), 2)
            
            high_conf = sum(1 for e in entities if e['confidence'] >= 0.8)
            stats['high_confidence'] = high_conf
            
            validated = sum(1 for e in entities if e.get('validated', False))
            stats['validation_rate'] = round(validated / len(entities), 2)
        
        self.classified['statistics'] = stats
    
    def get_summary_text(self) -> str:
        """Generate human-readable summary"""
        stats = self.classified.get('statistics', {})
        by_type = stats.get('by_type', {})
        
        summary_parts = []
        
        # Entity counts
        if by_type:
            counts = [f"{count} {etype}(s)" for etype, count in sorted(by_type.items())]
            summary_parts.append(f"Found: {', '.join(counts)}")
        else:
            summary_parts.append("No entities found")
        
        # Statistics
        total = stats.get('total_entities', 0)
        if total > 0:
            avg_conf = stats.get('confidence_avg', 0)
            summary_parts.append(f"Total entities: {total}")
            summary_parts.append(f"Average confidence: {avg_conf}")
            summary_parts.append(f"High confidence entities: {stats.get('high_confidence', 0)}")
        
        return '\n'.join(summary_parts)

