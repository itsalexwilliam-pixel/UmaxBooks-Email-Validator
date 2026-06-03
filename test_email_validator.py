"""
Unit Tests for Power Email Validation
Tests core functionality and edge cases
"""

import unittest
import time
from email_validator import EmailValidator


class TestEmailValidator(unittest.TestCase):
    """Test cases for EmailValidator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = EmailValidator(timeout=5, enable_cache=False, rate_limit=100)

    def test_syntax_validation(self):
        """Test email syntax validation"""
        # Valid emails
        valid_emails = [
            "user@example.com",
            "test.email@domain.co.uk",
            "user+tag@domain.com",
            "123@domain.com"
        ]

        for email in valid_emails:
            with self.subTest(email=email):
                result = self.validator.validate_syntax(email)
                self.assertTrue(result[0], f"Expected {email} to be valid")
                self.assertIn("valid", result[1].lower())

        # Invalid emails
        invalid_emails = [
            "invalid",
            "@domain.com",
            "user@",
            "user@@domain.com",
            "user domain.com"
        ]

        for email in invalid_emails:
            with self.subTest(email=email):
                result = self.validator.validate_syntax(email)
                self.assertFalse(result[0], f"Expected {email} to be invalid")

    def test_disposable_email_detection(self):
        """Test disposable email detection"""
        disposable_emails = [
            "test@10minutemail.com",
            "user@guerrillamail.com",
            "temp@mailinator.com"
        ]

        for email in disposable_emails:
            with self.subTest(email=email):
                result = self.validator.is_disposable_email(email)
                self.assertTrue(result[0], f"Expected {email} to be detected as disposable")

        # Valid email
        result = self.validator.is_disposable_email("user@gmail.com")
        self.assertFalse(result[0], "Expected gmail.com to not be disposable")

    def test_mx_record_check(self):
        """Test MX record checking"""
        # Valid domain with MX records
        result = self.validator.check_mx_records("gmail.com")
        self.assertTrue(result[0], "gmail.com should have MX records")
        self.assertGreater(len(result[2]), 0, "Should return MX hosts")

        # Invalid domain
        result = self.validator.check_mx_records("nonexistent-domain-12345.com")
        self.assertFalse(result[0], "Non-existent domain should not have MX records")

    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Create validator with low rate limit for testing
        test_validator = EmailValidator(timeout=5, rate_limit=2)

        # First two validations should work
        result1 = test_validator.validate_email("test1@example.com", check_smtp=False)
        result2 = test_validator.validate_email("test2@example.com", check_smtp=False)

        self.assertNotIn('error', result1)
        self.assertNotIn('error', result2)

        # Third should be rate limited
        result3 = test_validator.validate_email("test3@example.com", check_smtp=False)
        self.assertEqual(result3.get('error'), 'rate_limit_exceeded')

    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        # High confidence case
        high_conf_result = {
            'syntax_valid': True,
            'domain_exists': True,
            'mx_records': ['mx1.example.com'],
            'smtp_status': 'confirmed',
            'is_catchall': False,
            'is_disposable': False,
            'has_spf': True,
            'has_dkim': True
        }

        confidence = self.validator.calculate_confidence(high_conf_result)
        self.assertGreaterEqual(confidence, 80, "High confidence case should score >= 80")

        # Low confidence case
        low_conf_result = {
            'syntax_valid': True,
            'domain_exists': True,
            'mx_records': [],
            'smtp_status': 'error',
            'is_catchall': True,
            'is_disposable': True,
            'has_spf': False,
            'has_dkim': False
        }

        confidence = self.validator.calculate_confidence(low_conf_result)
        self.assertLessEqual(confidence, 30, "Low confidence case should score <= 30")

    def test_validation_time_tracking(self):
        """Test that validation time is tracked"""
        start_time = time.time()
        result = self.validator.validate_email("test@example.com", check_smtp=False)
        end_time = time.time()

        self.assertIn('validation_time', result)
        self.assertGreater(result['validation_time'], 0)
        self.assertLess(result['validation_time'], end_time - start_time + 1)  # Allow some tolerance

    def test_bulk_validation(self):
        """Test bulk email validation"""
        emails = [
            "test@example.com",
            "invalid-email",
            "user@10minutemail.com"
        ]

        results = self.validator.validate_bulk(emails, check_smtp=False)

        self.assertEqual(len(results), 3, "Should return results for all emails")

        # Check individual results
        self.assertTrue(results[0]['syntax_valid'])  # valid email
        self.assertFalse(results[1]['syntax_valid'])  # invalid email
        self.assertTrue(results[2]['is_disposable'])  # disposable email


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise during tests

    # Run tests
    unittest.main(verbosity=2)