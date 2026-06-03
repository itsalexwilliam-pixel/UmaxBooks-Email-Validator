"""
Domain Reputation Checker for Email Validator
Provides domain reputation analysis and risk scoring
"""

import dns.resolver
import re
from typing import Dict, Tuple
import logging
from datetime import datetime, timedelta


class DomainReputationChecker:
    """Check domain reputation and age"""

    def __init__(self):
        self.logger = logging.getLogger('DomainReputationChecker')

        # Common DNS blocklists (simple check without actual queries)
        self.common_blocklists = [
            'spamhaus.org',
            'sorbs.net',
            'barracudacentral.org',
            'abuseipdb.com'
        ]

        # Suspicious TLDs (newly introduced or high-abuse)
        self.suspicious_tlds = {
            'xyz': 1, 'tk': 1, 'ml': 1, 'ga': 1,  # Free domains
            'click': 1, 'download': 1, 'review': 1,  # Suspicious
        }

        # Enterprise/legitimate TLDs
        self.trusted_tlds = {
            'com': 5, 'org': 5, 'net': 5, 'edu': 5, 'gov': 5,
            'co.uk': 4, 'de': 4, 'fr': 4, 'jp': 4, 'au': 4,
            'us': 4
        }

    def check_domain_reputation(self, domain: str) -> Dict:
        """
        Comprehensive domain reputation check
        
        Args:
            domain: Domain name to check
            
        Returns:
            Dictionary with reputation metrics
        """
        reputation = {
            'domain': domain,
            'reputation_score': 0,  # 0-100
            'risk_level': 'unknown',
            'indicators': []
        }

        try:
            # TLD check
            tld_score = self._check_tld(domain)
            reputation['reputation_score'] += tld_score
            if tld_score < 3:
                reputation['indicators'].append('⚠️ Suspicious TLD')

            # Domain structure check
            structure_score = self._check_domain_structure(domain)
            reputation['reputation_score'] += structure_score
            if structure_score < 3:
                reputation['indicators'].append('⚠️ Suspicious domain structure')

            # SPF/DKIM check
            has_security = self._check_domain_security(domain)
            if has_security:
                reputation['reputation_score'] += 10
                reputation['indicators'].append('✅ Security records found')
            else:
                reputation['indicators'].append('⚠️ No security records')

            # Enterprise domain check
            if self._is_enterprise_domain(domain):
                reputation['reputation_score'] += 15
                reputation['indicators'].append('✅ Enterprise domain')

            # Popular domain check
            if self._is_popular_domain(domain):
                reputation['reputation_score'] += 10
                reputation['indicators'].append('✅ Popular domain')

            # Determine risk level
            score = min(100, reputation['reputation_score'])
            if score >= 80:
                reputation['risk_level'] = 'low'
            elif score >= 60:
                reputation['risk_level'] = 'medium'
            elif score >= 40:
                reputation['risk_level'] = 'high'
            else:
                reputation['risk_level'] = 'critical'

            reputation['reputation_score'] = score

        except Exception as e:
            self.logger.warning(f"Error checking domain reputation for {domain}: {str(e)}")

        return reputation

    def _check_tld(self, domain: str) -> int:
        """Check TLD reputation"""
        parts = domain.lower().split('.')

        if len(parts) < 2:
            return 1

        tld = parts[-1]

        # Check for suspicious TLDs
        if tld in self.suspicious_tlds:
            return 1

        # Check for trusted TLDs
        if tld in self.trusted_tlds:
            return self.trusted_tlds[tld]

        # Check for country code TLDs (usually trustworthy)
        if len(tld) == 2:  # Country code
            return 3

        # Check for compound TLDs like .co.uk
        if len(parts) >= 3:
            compound_tld = f"{parts[-2]}.{parts[-1]}".lower()
            if compound_tld in self.trusted_tlds:
                return self.trusted_tlds[compound_tld]

        # Default for unknown TLDs
        return 2

    def _check_domain_structure(self, domain: str) -> int:
        """Check domain structure for suspicious patterns"""
        score = 3  # Base score

        # Check for excessive hyphens
        if domain.count('-') > 2:
            score -= 1

        # Check for numbers at end (often suspicious)
        if domain[-1].isdigit():
            score -= 1

        # Check for length (too short or too long can be suspicious)
        if len(domain) < 4 or len(domain) > 50:
            score -= 1

        # Check for common suspicious patterns
        suspicious_patterns = [
            r'.*\d{3,}.*',  # Multiple consecutive numbers
            r'.*[aeiou]{3,}.*',  # Multiple consecutive vowels
        ]

        for pattern in suspicious_patterns:
            if re.match(pattern, domain.lower()):
                score -= 1
                break

        return max(1, score)

    def _check_domain_security(self, domain: str) -> bool:
        """Check if domain has security records (SPF/DKIM)"""
        try:
            # Try to get TXT records
            txt_records = dns.resolver.resolve(domain, 'TXT')

            for record in txt_records:
                record_str = str(record).lower()
                if 'spf1' in record_str or 'dkim1' in record_str:
                    return True

            return False

        except:
            return False

    def _is_enterprise_domain(self, domain: str) -> bool:
        """Check if domain is an enterprise/company domain"""
        enterprise_domains = {
            'gmail.com', 'outlook.com', 'yahoo.com', 'aol.com',
            'microsoft.com', 'google.com', 'apple.com', 'amazon.com',
            'linkedin.com', 'facebook.com', 'twitter.com', 'github.com',
            'ibm.com', 'oracle.com', 'cisco.com', 'intel.com',
            'dell.com', 'hp.com', 'samsung.com', 'sony.com'
        }

        return domain.lower() in enterprise_domains

    def _is_popular_domain(self, domain: str) -> bool:
        """Check if domain is in top popular domains"""
        popular_domains = {
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
            'aol.com', 'mail.com', 'gmx.com', 'protonmail.com',
            'yandex.com', 'icloud.com', '163.com', 'qq.com'
        }

        return domain.lower() in popular_domains

    def estimate_domain_age(self, domain: str) -> Dict:
        """
        Estimate domain age (simplified - would use WHOIS in production)
        
        Args:
            domain: Domain name
            
        Returns:
            Dictionary with age estimation
        """
        # This is a simplified check
        # In production, you'd query WHOIS servers
        age_estimate = {
            'domain': domain,
            'estimated_age': 'unknown',
            'age_score': 0
        }

        try:
            # Check MX records age (indirect indicator)
            mx_records = dns.resolver.resolve(domain, 'MX')

            if mx_records:
                # Established domains tend to have stable MX records
                age_estimate['estimated_age'] = '1+ years'
                age_estimate['age_score'] = 8
            else:
                age_estimate['estimated_age'] = 'new/suspicious'
                age_estimate['age_score'] = 2

        except:
            age_estimate['estimated_age'] = 'unknown'
            age_estimate['age_score'] = 1

        return age_estimate

    def get_reputation_summary(self, domain: str) -> str:
        """Get human-readable reputation summary"""
        reputation = self.check_domain_reputation(domain)
        score = reputation['reputation_score']
        risk = reputation['risk_level']

        emoji = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }.get(risk, '⚪')

        return f"{emoji} {risk.upper()} Risk (Score: {score}/100)"
