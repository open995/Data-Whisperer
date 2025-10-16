"""
Relationship rules engine for entity connections
"""

import dns.resolver
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict


class RelationshipEngine:
    """Build relationships between entities using modular rules"""
    
    def __init__(self, enable_dns_lookup: bool = True):
        self.enable_dns_lookup = enable_dns_lookup
        self.relationships = []
        
    def build_relationships(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build all relationships between entities
        
        Args:
            entities: List of classified entities
            
        Returns:
            List of relationships
        """
        self.relationships = []
        
        # Apply various relationship rules
        self._email_to_domain(entities)
        self._url_to_domain(entities)
        self._shared_domains(entities)
        self._shared_ips(entities)
        self._credential_to_email(entities)
        
        # DNS-based relationships (optional)
        if self.enable_dns_lookup:
            self._domain_to_ip(entities)
        
        return self.relationships
    
    def _add_relationship(self, rel_type: str, source: str, target: str, 
                         confidence: float = 0.9, metadata: Dict = None):
        """Add a relationship to the list"""
        
        # Avoid duplicates
        if any(r['source'] == source and r['target'] == target and r['type'] == rel_type 
               for r in self.relationships):
            return
        
        self.relationships.append({
            'type': rel_type,
            'source': source,
            'target': target,
            'confidence': confidence,
            'metadata': metadata or {}
        })
    
    def _email_to_domain(self, entities: List[Dict[str, Any]]):
        """Create email -> domain relationships"""
        for entity in entities:
            if entity['type'] == 'email':
                domain = entity['metadata'].get('domain')
                if domain:
                    self._add_relationship(
                        'email_to_domain',
                        entity['value'],
                        domain,
                        confidence=entity['confidence']
                    )
    
    def _url_to_domain(self, entities: List[Dict[str, Any]]):
        """Create URL -> domain relationships"""
        for entity in entities:
            if entity['type'] == 'url':
                domain = entity['metadata'].get('domain')
                if domain:
                    self._add_relationship(
                        'url_to_domain',
                        entity['value'],
                        domain,
                        confidence=entity['confidence']
                    )
    
    def _shared_domains(self, entities: List[Dict[str, Any]]):
        """Find shared domains between different entity types"""
        
        # Collect domains by source type
        email_domains = defaultdict(list)
        url_domains = defaultdict(list)
        
        for entity in entities:
            if entity['type'] == 'email':
                domain = entity['metadata'].get('domain')
                if domain:
                    email_domains[domain].append(entity['value'])
            
            elif entity['type'] == 'url':
                domain = entity['metadata'].get('domain')
                if domain:
                    url_domains[domain].append(entity['value'])
        
        # Find shared domains
        shared = set(email_domains.keys()).intersection(set(url_domains.keys()))
        
        for domain in shared:
            for email in email_domains[domain]:
                for url in url_domains[domain]:
                    self._add_relationship(
                        'shared_domain',
                        email,
                        url,
                        confidence=0.85,
                        metadata={'via_domain': domain}
                    )
    
    def _shared_ips(self, entities: List[Dict[str, Any]]):
        """Find entities sharing IP addresses"""
        
        # Group domains by their resolved IPs (if available)
        ip_to_domains = defaultdict(list)
        
        for entity in entities:
            if entity['type'] in ['ipv4', 'ipv6']:
                # This IP is explicitly mentioned
                ip_to_domains[entity['value']].append(('ip', entity['value']))
        
        # Create relationships for domains sharing IPs
        for ip, entities_list in ip_to_domains.items():
            if len(entities_list) > 1:
                for i, (type1, val1) in enumerate(entities_list):
                    for type2, val2 in entities_list[i+1:]:
                        self._add_relationship(
                            'shared_ip',
                            val1,
                            val2,
                            confidence=0.8,
                            metadata={'shared_ip': ip}
                        )
    
    def _domain_to_ip(self, entities: List[Dict[str, Any]]):
        """Resolve domains to IPs using DNS lookup"""
        
        # Collect all unique domains
        domains = set()
        
        for entity in entities:
            if entity['type'] == 'email':
                domain = entity['metadata'].get('domain')
                if domain:
                    domains.add(domain)
            
            elif entity['type'] == 'url':
                domain = entity['metadata'].get('domain')
                if domain:
                    domains.add(domain)
        
        # Perform DNS lookups
        for domain in domains:
            try:
                # Try A record (IPv4)
                answers = dns.resolver.resolve(domain, 'A', lifetime=2)
                for rdata in answers:
                    ip = str(rdata)
                    self._add_relationship(
                        'domain_to_ip',
                        domain,
                        ip,
                        confidence=0.95,
                        metadata={'record_type': 'A'}
                    )
            except Exception:
                pass  # DNS lookup failed, skip
            
            try:
                # Try AAAA record (IPv6)
                answers = dns.resolver.resolve(domain, 'AAAA', lifetime=2)
                for rdata in answers:
                    ip = str(rdata)
                    self._add_relationship(
                        'domain_to_ip',
                        domain,
                        ip,
                        confidence=0.95,
                        metadata={'record_type': 'AAAA'}
                    )
            except Exception:
                pass  # DNS lookup failed, skip
    
    def _credential_to_email(self, entities: List[Dict[str, Any]]):
        """Link credentials to emails if username matches"""
        
        emails = [e for e in entities if e['type'] == 'email']
        credentials = [e for e in entities if e['type'] == 'credential']
        
        for cred in credentials:
            username = cred['metadata'].get('username', '').lower()
            
            for email in emails:
                email_user = email['value'].split('@')[0].lower()
                
                # Check if username matches email user part
                if username == email_user:
                    self._add_relationship(
                        'credential_to_email',
                        cred['value'],
                        email['value'],
                        confidence=0.8,
                        metadata={'matched_username': username}
                    )
    
    def get_relationship_summary(self) -> Dict[str, int]:
        """Get summary of relationship types"""
        summary = defaultdict(int)
        
        for rel in self.relationships:
            summary[rel['type']] += 1
        
        return dict(summary)
    
    def get_connected_entities(self, entity_value: str) -> List[Dict[str, Any]]:
        """Get all entities connected to a specific entity"""
        connected = []
        
        for rel in self.relationships:
            if rel['source'] == entity_value:
                connected.append({
                    'entity': rel['target'],
                    'relationship': rel['type'],
                    'confidence': rel['confidence']
                })
            elif rel['target'] == entity_value:
                connected.append({
                    'entity': rel['source'],
                    'relationship': rel['type'],
                    'confidence': rel['confidence']
                })
        
        return connected

