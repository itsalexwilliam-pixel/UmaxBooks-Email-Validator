"""
Power Email Validation - Advanced Edition
Enhanced with Catch-all Detection, Multiple MX Checks, and Confidence Scoring
"""

import re
import dns.resolver
import smtplib
import socket
import random
import time
from typing import Dict, Tuple, List
from datetime import datetime

class AdvancedEmailValidator:
    """Advanced Email Validator with Multiple Verification Methods"""
    
    # Disposable email domains
    DISPOSABLE_DOMAINS = {
        'tempmail.com', 'guerrillamail.com', '10minutemail.com',
        'mailinator.com', '0-mail.com', 'tempmail.org',
        'throwaway.email', 'yopmail.com', 'maildrop.cc',
        'fakeinbox.com', 'trashmail.com', 'spam4.me',
        'mytrashmail.com', 'temp-mail.org', 'mailnesia.com',
        'tempemailaddress.com', 'meltmail.com'
    }
    
    # Blocking domains (need special handling)
    BLOCKING_DOMAINS = {
        'yahoo.com', 'yahoo.co.in', 'yahoo.co.uk', 'yahoo.fr',
        'aol.com', 'hotmail.com', 'outlook.com', 'live.com',
        'comcast.net', 'verizon.net', 'att.net',
        'mail.com', 'gmx.com', 'protonmail.com'
    }
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.timeout = timeout
        self.dns_resolver.lifetime = timeout
    
    def validate_syntax(self, email: str) -> Tuple[bool, str]:
        """Validate email syntax"""
        if not email or not isinstance(email, str):
            return False, "Invalid email format"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, "Invalid email syntax"
        
        if email.count('@') != 1:
            return False, "Email must contain exactly one @ symbol"
        
        local, domain = email.split('@')
        
        if len(local) == 0 or len(local) > 64:
            return False, "Local part must be 1-64 characters"
        
        if len(domain) == 0 or len(domain) > 255:
            return False, "Domain must be 1-255 characters"
        
        return True, "Syntax is valid"
    
    def is_disposable_email(self, email: str) -> Tuple[bool, str]:
        """Check if email is using disposable email service"""
        domain = email.split('@')[1].lower()
        if domain in self.DISPOSABLE_DOMAINS:
            return True, "Uses disposable email service"
        return False, "Not a disposable email"
    
    def check_mx_records(self, domain: str) -> Tuple[bool, str, List[str]]:
        """Check MX records for domain"""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            # Sort by preference (lower is better) and ignore blank hosts
            mx_hosts = sorted(
                [
                    (int(r.preference), str(r.exchange).rstrip('.'))
                    for r in mx_records
                    if str(r.exchange).rstrip('.')
                ],
                key=lambda x: x[0]
            )
            mx_hosts = [host for _, host in mx_hosts]
            return True, f"Found {len(mx_hosts)} MX record(s)", mx_hosts
        except dns.resolver.NXDOMAIN:
            return False, "Domain does not exist", []
        except dns.resolver.NoAnswer:
            return False, "No MX records found", []
        except dns.resolver.Timeout:
            return False, "DNS lookup timeout", []
        except Exception as e:
            return False, f"DNS error: {str(e)}", []
    
    def check_spf_record(self, domain: str) -> Tuple[bool, str]:
        """Check if domain has SPF record"""
        try:
            spf_records = dns.resolver.resolve(domain, 'TXT')
            for record in spf_records:
                txt = str(record)
                if 'v=spf1' in txt:
                    return True, "SPF record found"
            return False, "No SPF record"
        except:
            return False, "Could not check SPF"
    
    def detect_catchall(self, domain: str, mx_host: str) -> Tuple[bool, str]:
        """
        Detect if domain is catch-all
        Test करो fake email देखो accept करता है या नहीं
        """
        fake_email = f"test_invalid_{random.randint(100000, 999999)}@{domain}"
        
        try:
            server = smtplib.SMTP(timeout=self.timeout)
            server.set_debuglevel(0)
            server.connect(mx_host)
            server.ehlo_or_helo_if_needed()
            server.mail('verify@umaxbooks.com')
            
            code, message = server.rcpt(fake_email)
            server.quit()
            
            if code == 250:
                return True, "Domain accepts all emails (Catch-all)"
            else:
                return False, "Domain filters emails"
        except:
            return False, "Could not detect catch-all"
    
    def verify_smtp(self, email: str, mx_hosts: List[str]) -> Tuple[bool, str, str, float]:
        """
        Verify email via SMTP with smart retry logic
        Try multiple MX servers
        Returns: (is_deliverable, message, status_type, confidence)
        """
        domain = email.split('@')[1].lower()
        is_blocking_domain = any(domain.endswith(d) for d in self.BLOCKING_DOMAINS)
        
        # Try each MX server
        for mx_host in mx_hosts[:5]:  # Try top 5
            try:
                server = smtplib.SMTP(timeout=self.timeout)
                server.set_debuglevel(0)
                server.connect(mx_host)
                server.ehlo_or_helo_if_needed()
                server.mail('verify@umaxbooks.com')
                
                code, message = server.rcpt(email)
                server.quit()
                msg_text = message.decode(errors='ignore') if hasattr(message, 'decode') else str(message)
                msg_lower = msg_text.lower()
                blocked_markers = [
                    'auth',
                    'authentication',
                    'access denied',
                    'not permitted',
                    'relay',
                    'relaying',
                    'client host rejected',
                    'policy',
                    'blocked'
                ]
                
                if code == 250:
                    return True, "Email exists and is deliverable", "confirmed", 0.98
                elif code == 550:
                    if any(marker in msg_lower for marker in blocked_markers):
                        return True, "Server blocks verification (auth/policy) - likely deliverable", "blocked", 0.75
                    return False, "Email does not exist", "not_found", 0.95
                elif code == 551:
                    return False, "User not local", "not_found", 0.85
                elif code == 552:
                    return False, "Mailbox full", "not_found", 0.70
                elif code == 553:
                    if any(marker in msg_lower for marker in blocked_markers):
                        return True, "Server blocks verification (auth/policy) - likely deliverable", "blocked", 0.75
                    return False, "Invalid mailbox", "not_found", 0.90
                elif code == 450:
                    # Server busy, retry next server
                    continue
                elif code == 451:
                    # Server error, try next
                    continue
                else:
                    # Other code, try next server
                    continue
                    
            except smtplib.SMTPServerDisconnected:
                if is_blocking_domain:
                    # For blocking domains, try next server
                    continue
                # Might be this server, try next
                continue
            except socket.timeout:
                # Timeout, try next server
                continue
            except:
                # Any other error, try next server
                continue
        
        # If all servers failed, check if blocking domain
        if is_blocking_domain:
            return True, "Server blocks verification (likely deliverable)", "blocked", 0.75
        else:
            return False, "Could not verify via SMTP", "error", 0.50
    
    def calculate_confidence(self, result: Dict) -> float:
        """
        Calculate confidence score (0-100)
        Based on verification methods passed
        """
        confidence = 0.0
        
        # Syntax check: 10%
        if result['syntax_valid']:
            confidence += 10
        
        # Domain exists: 20%
        if result['domain_exists']:
            confidence += 20
        
        # MX records: 20%
        if result['mx_records']:
            confidence += 20
        
        # SPF record: 10%
        if result.get('has_spf', False):
            confidence += 10
        
        # SMTP check: 30%
        if result.get('smtp_status') == 'confirmed':
            confidence += 30
        elif result.get('smtp_status') == 'blocked':
            confidence += 20  # Less confidence for blocked
        elif result.get('smtp_status') == 'trusted':
            confidence += 15  # Trusted override, but not fully confirmed
        elif result.get('smtp_status') == 'not_found':
            confidence -= 30  # Negative for not found
        
        # Not catch-all: 10%
        if result.get('is_catchall') == False:
            confidence += 10
        elif result.get('is_catchall') == True:
            confidence -= 15  # Less confidence for catch-all
        
        # Not disposable: 5%
        if result.get('is_disposable') == False:
            confidence += 5
        elif result.get('is_disposable') == True:
            confidence -= 10  # Less confidence for disposable
        
        # Clamp between 0 and 100
        confidence = max(0, min(100, confidence))
        
        return round(confidence)
    
    def validate_email(self, email: str, check_smtp=True, check_catchall=False, trusted_domains=None) -> Dict:
        """
        Comprehensive email validation with advanced checks
        """
        trusted_domains = {d.lower() for d in (trusted_domains or [])}
        result = {
            'email': email,
            'timestamp': datetime.now().isoformat(),
            'is_valid': False,
            'syntax_valid': False,
            'domain_exists': False,
            'mx_records': [],
            'is_disposable': False,
            'is_catchall': None,
            'has_spf': False,
            'smtp_check': False,
            'smtp_status': 'skipped',
            'deliverable': False,
            'confidence': 0,
            'messages': [],
            'verification_methods': []
        }
        
        # Step 1: Syntax validation
        syntax_valid, syntax_msg = self.validate_syntax(email)
        result['syntax_valid'] = syntax_valid
        result['messages'].append(f"✓ Syntax: {syntax_msg}" if syntax_valid else f"✗ Syntax: {syntax_msg}")
        result['verification_methods'].append('Syntax Check')
        
        if not syntax_valid:
            result['confidence'] = 10
            return result
        
        # Step 2: Disposable email check
        is_disposable, disp_msg = self.is_disposable_email(email)
        result['is_disposable'] = is_disposable
        if is_disposable:
            result['messages'].append(f"⚠ Disposable: {disp_msg}")
        
        # Extract domain
        domain = email.split('@')[1].lower()
        
        # Step 3: MX record check
        has_mx, mx_msg, mx_records = self.check_mx_records(domain)
        result['domain_exists'] = has_mx
        result['mx_records'] = mx_records
        result['messages'].append(f"{'✓' if has_mx else '✗'} MX Records: {mx_msg}")
        result['verification_methods'].append('MX Records Check')
        
        if not has_mx:
            result['confidence'] = self.calculate_confidence(result)
            return result
        
        # Step 4: SPF check
        has_spf, spf_msg = self.check_spf_record(domain)
        result['has_spf'] = has_spf
        if has_spf:
            result['messages'].append("✓ SPF record found")
        
        # Step 5: Catch-all detection (optional)
        if check_catchall and mx_records:
            is_catchall, catchall_msg = self.detect_catchall(domain, mx_records[0])
            result['is_catchall'] = is_catchall
            if is_catchall:
                result['messages'].append("⚠ Domain is catch-all (accepts all emails)")
            else:
                result['messages'].append("✓ Domain filters emails")
        
        # Step 6: SMTP verification
        if check_smtp and mx_records:
            smtp_valid, smtp_msg, status_type, smtp_confidence = self.verify_smtp(email, mx_records)
            result['smtp_check'] = True
            result['smtp_status'] = status_type
            result['deliverable'] = smtp_valid
            result['messages'].append(f"📧 SMTP: {smtp_msg}")
            result['verification_methods'].append('SMTP Verification')
            
            # Handle blocking domains
            if status_type == 'blocked':
                result['deliverable'] = True
                result['messages'].append("Note: Server blocks verification but MX exists")
            elif status_type == 'error':
                result['deliverable'] = True
                result['messages'].append("Note: SMTP verification failed; server may block checks. Marking as likely deliverable")
            elif status_type == 'not_found' and domain in trusted_domains:
                result['deliverable'] = True
                result['smtp_status'] = 'trusted'
                result['messages'].append("Note: Domain is trusted; treating as deliverable despite SMTP response")
        else:
            # Default to deliverable if MX exists
            result['deliverable'] = has_mx
            result['messages'].append("SMTP: Skipped (MX records sufficient)")
        
        # Set is_valid
        result['is_valid'] = result['syntax_valid'] and result['domain_exists']
        
        # Calculate confidence
        result['confidence'] = self.calculate_confidence(result)
        
        return result
    
    def validate_bulk(self, emails: list, check_smtp=True, check_catchall=False, trusted_domains=None) -> List[Dict]:
        """Validate multiple emails"""
        results = []
        for email in emails:
            result = self.validate_email(email.strip(), check_smtp, check_catchall, trusted_domains=trusted_domains)
            results.append(result)
        return results


def print_detailed_result(result: Dict):
    """Pretty print validation result with confidence"""
    print("\n" + "="*70)
    print(f"Email: {result['email']}")
    print("="*70)
    print(f"Valid: {'✓ YES' if result['is_valid'] else '✗ NO'}")
    print(f"Deliverable: {'✓ YES' if result['deliverable'] else '✗ NO'}")
    print(f"Confidence: {result['confidence']}%")
    print(f"Verification Methods: {', '.join(result['verification_methods'])}")
    
    print("\nDetailed Analysis:")
    for msg in result['messages']:
        print(f"  {msg}")
    
    if result['mx_records']:
        print(f"\nTop MX Servers:")
        for i, mx in enumerate(result['mx_records'][:3], 1):
            print(f"  {i}. {mx}")
    
    print("\nValidation Classification:")
    if result['is_valid'] and result['deliverable']:
        print(f"  ✅ VALID & DELIVERABLE (High Confidence)")
    elif result['is_valid']:
        print(f"  ⚠️  VALID BUT UNVERIFIED")
    elif result['syntax_valid']:
        print(f"  ⚠️  FORMAT VALID BUT DOMAIN ISSUES")
    else:
        print(f"  ❌ INVALID EMAIL")
    
    print("="*70)


if __name__ == "__main__":
    validator = AdvancedEmailValidator(timeout=10)
    
    # Test emails
    test_emails = [
        "test@gmail.com",
        "invalid.email@",
        "admin@yahoo.com",
        "user@tempmail.com",
    ]
    
    print("Power Email Validation - Advanced Edition")
    print("==================================\n")
    
    for email in test_emails:
        result = validator.validate_email(email, check_smtp=False, check_catchall=False)
        print_detailed_result(result)
