"""
Unit tests for Data Whisperer entity extraction
"""

import unittest
from datawhisperer.extractor import EntityExtractor
from datawhisperer.classify import EntityClassifier
from datawhisperer.utils import (
    sanitize_text, 
    validate_hash,
    extract_domain_from_email,
    calculate_confidence
)


class TestEntityExtractor(unittest.TestCase):
    """Test entity extraction functionality"""
    
    def setUp(self):
        self.extractor = EntityExtractor()
    
    def test_email_extraction(self):
        """Test email address extraction"""
        text = "Contact us at support@example.com or info@test.org"
        entities = self.extractor.extract(text)
        
        emails = [e for e in entities if e['type'] == 'email']
        self.assertEqual(len(emails), 2)
        self.assertIn('support@example.com', [e['value'] for e in emails])
    
    def test_ipv4_extraction(self):
        """Test IPv4 address extraction"""
        text = "Server is at 192.168.1.1 and backup at 10.0.0.5"
        entities = self.extractor.extract(text)
        
        ips = [e for e in entities if e['type'] == 'ipv4']
        self.assertGreaterEqual(len(ips), 2)
    
    def test_url_extraction(self):
        """Test URL extraction"""
        text = "Visit https://example.com or http://test.org/path"
        entities = self.extractor.extract(text)
        
        urls = [e for e in entities if e['type'] == 'url']
        self.assertGreaterEqual(len(urls), 2)
    
    def test_hash_extraction(self):
        """Test hash extraction"""
        text = "MD5: 5d41402abc4b2a76b9719d911017c592"
        entities = self.extractor.extract(text)
        
        hashes = [e for e in entities if e['type'] == 'md5']
        self.assertEqual(len(hashes), 1)
        self.assertEqual(hashes[0]['value'], '5d41402abc4b2a76b9719d911017c592')
    
    def test_bitcoin_extraction(self):
        """Test Bitcoin wallet extraction"""
        text = "Send BTC to 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        entities = self.extractor.extract(text)
        
        wallets = [e for e in entities if e['type'] == 'bitcoin_wallet']
        self.assertGreaterEqual(len(wallets), 1)
    
    def test_ethereum_extraction(self):
        """Test Ethereum wallet extraction"""
        text = "ETH address: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        entities = self.extractor.extract(text)
        
        wallets = [e for e in entities if e['type'] == 'ethereum_wallet']
        self.assertGreaterEqual(len(wallets), 1)
    
    def test_credential_extraction(self):
        """Test credential pattern extraction"""
        text = "Login: admin:password123"
        entities = self.extractor.extract(text)
        
        creds = [e for e in entities if e['type'] == 'credential']
        self.assertGreaterEqual(len(creds), 1)


class TestEntityClassifier(unittest.TestCase):
    """Test entity classification and validation"""
    
    def setUp(self):
        self.classifier = EntityClassifier()
    
    def test_email_validation(self):
        """Test email validation"""
        self.assertTrue(self.classifier._validate_email('test@example.com'))
        self.assertFalse(self.classifier._validate_email('invalid.email'))
        self.assertFalse(self.classifier._validate_email('test@example.local'))
    
    def test_ipv4_validation(self):
        """Test IPv4 validation"""
        self.assertTrue(self.classifier._validate_ip('192.168.1.1', 'ipv4'))
        self.assertTrue(self.classifier._validate_ip('8.8.8.8', 'ipv4'))
        self.assertFalse(self.classifier._validate_ip('256.1.1.1', 'ipv4'))
        self.assertFalse(self.classifier._validate_ip('0.0.0.0', 'ipv4'))
    
    def test_hash_validation(self):
        """Test hash validation"""
        md5 = '5d41402abc4b2a76b9719d911017c592'
        self.assertTrue(self.classifier._validate_hash(md5, 'md5'))
        
        # Invalid: wrong length
        self.assertFalse(self.classifier._validate_hash('abc123', 'md5'))
        
        # Invalid: all same digit
        self.assertFalse(self.classifier._validate_hash('0' * 32, 'md5'))
    
    def test_bitcoin_validation(self):
        """Test Bitcoin address validation"""
        self.assertTrue(self.classifier._validate_bitcoin('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'))
        self.assertFalse(self.classifier._validate_bitcoin('invalid_btc_address'))
    
    def test_ethereum_validation(self):
        """Test Ethereum address validation"""
        self.assertTrue(self.classifier._validate_ethereum('0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0'))
        self.assertFalse(self.classifier._validate_ethereum('0xinvalid'))
        self.assertFalse(self.classifier._validate_ethereum('742d35Cc6634C0532925a3b844Bc9e7595f0bEb0'))


class TestUtils(unittest.TestCase):
    """Test utility functions"""
    
    def test_sanitize_text(self):
        """Test text sanitization"""
        text = "Hello\x00World\r\nTest"
        sanitized = sanitize_text(text)
        self.assertNotIn('\x00', sanitized)
        self.assertNotIn('\r\n', sanitized)
    
    def test_validate_hash(self):
        """Test hash validation utility"""
        self.assertTrue(validate_hash('5d41402abc4b2a76b9719d911017c592', 'md5'))
        self.assertFalse(validate_hash('invalid', 'md5'))
        self.assertFalse(validate_hash('5d41402abc4b2a76b9719d911017c592', 'sha1'))
    
    def test_extract_domain_from_email(self):
        """Test domain extraction from email"""
        self.assertEqual(extract_domain_from_email('test@example.com'), 'example.com')
        self.assertIsNone(extract_domain_from_email('invalid'))
    
    def test_calculate_confidence(self):
        """Test confidence calculation"""
        # High confidence for validated entity
        conf = calculate_confidence('test@example.com', 'email', True)
        self.assertGreater(conf, 0.8)
        
        # Lower confidence for non-validated
        conf = calculate_confidence('test', 'unknown', False)
        self.assertLess(conf, 0.9)


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests"""
    
    def test_full_pipeline(self):
        """Test complete extraction and classification pipeline"""
        text = """
        Contact: admin@example.com
        Server: 192.168.1.1
        Website: https://example.com
        Hash: 5d41402abc4b2a76b9719d911017c592
        """
        
        # Extract
        extractor = EntityExtractor()
        entities = extractor.extract(text)
        
        self.assertGreater(len(entities), 0)
        
        # Classify
        classifier = EntityClassifier()
        classified = classifier.classify(entities)
        
        self.assertIn('entities', classified)
        self.assertIn('statistics', classified)
        self.assertGreater(classified['statistics']['total_entities'], 0)
    
    def test_relationship_extraction(self):
        """Test relationship detection"""
        text = "Email admin@example.com and visit https://example.com"
        
        extractor = EntityExtractor()
        entities = extractor.extract(text)
        
        classifier = EntityClassifier()
        classified = classifier.classify(entities)
        
        # Should find shared domain relationship
        relationships = classified.get('relationships', [])
        self.assertGreater(len(relationships), 0)


if __name__ == '__main__':
    unittest.main()

