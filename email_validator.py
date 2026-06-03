import re
import dns.resolver
import smtplib
import socket
import random
import time
import logging
from typing import Dict, Tuple, List
from email.utils import parseaddr
from functools import lru_cache
import threading
from datetime import datetime, timedelta


class EmailValidator:
    def __init__(self, timeout=10, enable_cache=True, rate_limit=10):
        """Initialize the email validator with advanced features."""
        self.timeout = timeout
        socket.setdefaulttimeout(timeout)

        # DNS resolver with timeout
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.timeout = timeout
        self.dns_resolver.lifetime = timeout

        # DNS caching
        self.enable_cache = enable_cache
        self.dns_cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.cache_lock = threading.Lock()

        # Rate limiting
        self.rate_limit = rate_limit  # emails per minute
        self.rate_window = 60  # seconds
        self.request_times = []
        self.rate_lock = threading.Lock()

        # Logging
        self.logger = logging.getLogger('EmailValidator')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Domains where SMTP connections are blocked/dropped entirely
        # (server refuses connection or disconnects before responding)
        self.blocking_domains = {
            'yahoo.com', 'yahoo.co.uk', 'yahoo.co.in', 'yahoo.co.jp',
            'aol.com',
            'outlook.com', 'live.com', 'hotmail.com',
            'microsoft.com', 'msn.com', 'passport.com',
            'comcast.net', 'verizon.net', 'att.net', 'mail.com',
            'gmx.com', 'gmx.de', 'gmx.net',
            'protonmail.com', 'proton.me',
            # NOTE: gmail.com REMOVED — Google SMTP responds accurately
            # (250 for real addresses, 550 for fake), so treat it normally
        }

        # Domains that return 550/553 for ALL external RCPT TO probes,
        # even for VALID addresses (Apple, some Microsoft servers).
        # We must NOT trust their 550 as "user not found".
        self.smtp_reject_domains = {
            'icloud.com', 'me.com', 'mac.com',   # Apple — blocks all probing
            'hotmail.co.uk', 'live.co.uk',        # Some MS regional domains
        }

        self.disposable_domains = {
            'tempmail.com', 'guerrillamail.com', '10minutemail.com',
            'mailinator.com', '0-mail.com', 'tempmail.org',
            'throwaway.email', 'yopmail.com', 'maildrop.cc',
            'fakeinbox.com', 'trashmail.com', 'spam4.me',
            'mytrashmail.com', 'temp-mail.org', 'mailnesia.com',
            'tempemailaddress.com', 'meltmail.com',
            'sharklasers.com', 'guerrillamailblock.com', 'grr.la',
            'guerrillamail.info', 'guerrillamail.biz', 'guerrillamail.de',
            'guerrillamail.net', 'guerrillamail.org', 'spam4.me',
            'dispostable.com', 'mailnull.com', 'spamgourmet.com',
            'trashmail.at', 'trashmail.io', 'trashmail.me',
            'discard.email', 'spamhere.net', 'tempinbox.com',
            'mailnull.com', 'spamfree24.org', 'wegwerfmail.de',
            'einrot.com', 'filzmail.com', 'spamgrap.com',
        }

        # Role-based / generic local parts that are shared inboxes, not personal.
        # Emails using these should be flagged so marketers can filter them out.
        self.role_based_prefixes = {
            'admin', 'administrator', 'webmaster', 'hostmaster', 'postmaster',
            'abuse', 'support', 'help', 'helpdesk', 'contact', 'info',
            'noreply', 'no-reply', 'donotreply', 'do-not-reply',
            'sales', 'marketing', 'billing', 'accounts', 'accounting',
            'hr', 'careers', 'jobs', 'recruitment',
            'press', 'media', 'pr', 'news',
            'security', 'privacy', 'legal', 'compliance',
            'test', 'testing', 'demo', 'sample', 'example',
            'hello', 'hi', 'welcome', 'enquiries', 'enquiry',
            'office', 'mail', 'email', 'inbox',
            'root', 'system', 'daemon', 'mailer',
            'newsletter', 'subscribe', 'unsubscribe', 'bounce',
            'feedback', 'survey', 'notifications', 'alerts',
        }
    
    def validate_syntax(self, email: str) -> Tuple[bool, str]:
        """
        Validate email syntax using regex and basic checks.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not email or not isinstance(email, str):
            return False, "Email cannot be empty"
        
        # Basic regex pattern for email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, "Invalid email syntax"
        
        # Split email into local and domain parts
        try:
            local, domain = email.rsplit('@', 1)
        except ValueError:
            return False, "Invalid email format"
        
        # Check local part length
        if len(local) > 64:
            return False, "Local part (before @) is too long (max 64 characters)"
        
        # Check domain part length
        if len(domain) > 255:
            return False, "Domain part is too long (max 255 characters)"
        
        # Check for consecutive dots
        if '..' in email:
            return False, "Email cannot contain consecutive dots"
        
        return True, "Email syntax is valid"
    
    def check_mx_records(self, domain: str) -> Tuple[bool, str, list]:
        """
        Check if domain has valid MX records (with caching).
        
        Args:
            domain: Domain name to check
            
        Returns:
            Tuple of (has_mx, message, mx_hosts_list)
        """
        success, message, mx_hosts = self._get_cached_dns(domain, 'MX')
        return success, message, mx_hosts

    def _get_cached_dns(self, domain: str, record_type: str):
        """Get DNS record from cache or perform lookup."""
        if not self.enable_cache:
            return self._perform_dns_lookup(domain, record_type)

        cache_key = f"{domain}:{record_type}"
        current_time = datetime.now()

        with self.cache_lock:
            if cache_key in self.dns_cache:
                cached_time, cached_result = self.dns_cache[cache_key]
                if current_time - cached_time < timedelta(seconds=self.cache_ttl):
                    self.logger.debug(f"DNS cache hit for {cache_key}")
                    return cached_result
                else:
                    # Cache expired
                    del self.dns_cache[cache_key]

        # Perform lookup and cache result
        result = self._perform_dns_lookup(domain, record_type)

        with self.cache_lock:
            self.dns_cache[cache_key] = (current_time, result)

        self.logger.debug(f"DNS cache miss for {cache_key}")
        return result

    def _perform_dns_lookup(self, domain: str, record_type: str):
        """Perform actual DNS lookup."""
        try:
            if record_type == 'MX':
                mx_records = dns.resolver.resolve(domain, 'MX')
                mx_hosts = sorted(
                    [
                        (int(r.preference), str(r.exchange).rstrip('.'))
                        for r in mx_records
                        if str(r.exchange).rstrip('.')
                    ],
                    key=lambda x: x[0]
                )
                return True, f"Found {len(mx_hosts)} MX record(s)", [host for _, host in mx_hosts]
            elif record_type == 'TXT':
                txt_records = dns.resolver.resolve(domain, 'TXT')
                return True, f"Found {len(txt_records)} TXT record(s)", [str(r) for r in txt_records]
            else:
                return False, f"Unsupported record type: {record_type}", []
        except dns.resolver.NXDOMAIN:
            return False, "Domain does not exist (NXDOMAIN)", []
        except dns.resolver.NoAnswer:
            return False, f"No {record_type} records found for domain", []
        except dns.resolver.Timeout:
            return False, "DNS query timed out", []
        except Exception as e:
            return False, f"DNS lookup error: {str(e)}", []

    def check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        if self.rate_limit <= 0:
            return True  # No rate limiting

        current_time = time.time()

        with self.rate_lock:
            # Remove old requests outside the window
            self.request_times = [
                t for t in self.request_times
                if current_time - t < self.rate_window
            ]

            # Check if we're under the limit
            if len(self.request_times) < self.rate_limit:
                self.request_times.append(current_time)
                return True
            else:
                # Calculate wait time
                oldest_request = min(self.request_times)
                wait_time = self.rate_window - (current_time - oldest_request)
                self.logger.warning(f"Rate limit exceeded. Wait {wait_time:.1f} seconds")
                return False

    def detect_catchall(self, domain: str, mx_hosts: List[str]) -> Tuple[bool, str]:
        """
        Detect if domain is catch-all (accepts all emails including fake ones).

        Args:
            domain: Domain to check
            mx_hosts: List of MX hosts to try

        Returns:
            Tuple of (is_catchall, message)
        """
        fake_email = f"nonexistent_test_{random.randint(100000, 999999)}@{domain}"

        for mx_host in mx_hosts[:3]:  # Try top 3 MX servers
            try:
                server = smtplib.SMTP(timeout=self.timeout)
                server.connect(mx_host)
                server.ehlo_or_helo_if_needed()
                server.mail('verify@example.com')

                code, message = server.rcpt(fake_email)
                server.quit()

                if code == 250:
                    return True, "Domain accepts all emails (Catch-all server)"

            except (smtplib.SMTPException, socket.timeout, OSError):
                continue  # Try next MX server

        return False, "Domain filters emails (not catch-all)"

    def check_spf_record(self, domain: str) -> Tuple[bool, str]:
        """Check if domain has SPF record."""
        success, message, txt_records = self._get_cached_dns(domain, 'TXT')

        if not success:
            return False, "Could not check SPF"

        for record in txt_records:
            if 'v=spf1' in record.lower():
                return True, "SPF record found"
        return False, "No SPF record"

    def check_dkim_record(self, domain: str) -> Tuple[bool, str]:
        """Check for DKIM records (common selectors)."""
        common_selectors = ['default', 'dkim', 'mail', 'selector1', 'selector2']

        for selector in common_selectors:
            dkim_domain = f"{selector}._domainkey.{domain}"
            success, message, txt_records = self._get_cached_dns(dkim_domain, 'TXT')

            if success and txt_records:
                for record in txt_records:
                    if 'v=dkim1' in record.lower():
                        return True, f"DKIM record found (selector: {selector})"

        return False, "No DKIM record found"

    def check_domain_reputation(self, domain: str) -> Dict[str, any]:
        """Check domain reputation indicators."""
        reputation = {
            'has_spf': False,
            'has_dkim': False,
            'domain_age_score': 0,  # Placeholder for future WHOIS integration
            'score': 0
        }

        # Check SPF
        reputation['has_spf'], _ = self.check_spf_record(domain)
        if reputation['has_spf']:
            reputation['score'] += 10

        # Check DKIM
        reputation['has_dkim'], _ = self.check_dkim_record(domain)
        if reputation['has_dkim']:
            reputation['score'] += 10

        return reputation

    def is_disposable_email(self, email: str) -> Tuple[bool, str]:
        """Check if email is from disposable email service."""
        domain = email.split('@')[1].lower()
        if domain in self.disposable_domains:
            return True, "Uses disposable email service"
        return False, "Not a disposable email"

    def is_role_based_email(self, email: str) -> Tuple[bool, str]:
        """
        Detect role-based / generic email addresses (shared inboxes).
        These are not personal mailboxes and are unsuitable for marketing.
        Examples: admin@, info@, support@, noreply@, test@
        """
        local = email.split('@')[0].lower()
        # Strip common delimiters and check the base prefix
        base = local.replace('-', '').replace('_', '').replace('.', '')
        if local in self.role_based_prefixes or base in self.role_based_prefixes:
            return True, f"Role-based address ('{local}') — shared inbox, not a personal mailbox"
        return False, "Personal email address (not role-based)"

    def verify_smtp_multi_mx(self, email: str, mx_hosts: List[str]) -> Tuple[bool, str, str, float]:
        """
        Verify email via SMTP with multi-MX retry logic and better error handling.

        Args:
            email: Email address to verify
            mx_hosts: List of MX hosts to try

        Returns:
            Tuple of (is_deliverable, message, status_type, confidence)
        """
        domain = email.split('@')[1].lower()
        is_blocking_domain = any(domain.endswith(d) for d in self.blocking_domains)
        # smtp_reject_domains: servers that return 550/553 for ALL external probes
        # (even valid addresses). Do NOT treat their 550 as "user not found".
        is_reject_domain = any(domain.endswith(d) for d in self.smtp_reject_domains)

        blocked_markers = [
            'auth', 'authentication', 'access denied', 'not permitted',
            'relay', 'relaying', 'client host rejected', 'policy', 'blocked',
            'spam', 'blacklist', 'denied', 'prohibited',
        ]

        # Try each MX server (up to 5)
        for mx_host in mx_hosts[:5]:
            for attempt in range(2):  # Retry once on failure
                try:
                    server = smtplib.SMTP(timeout=self.timeout)
                    server.connect(mx_host)
                    server.ehlo_or_helo_if_needed()
                    server.mail('verify@example.com')

                    code, message = server.rcpt(email)
                    server.quit()

                    # Decode message if bytes
                    msg_text = message.decode(errors='ignore') if hasattr(message, 'decode') else str(message)
                    msg_lower = msg_text.lower()

                    # Analyze SMTP response codes
                    if code == 250:
                        # Explicit acceptance — confirmed deliverable
                        return True, "Email exists and is deliverable", "confirmed", 0.98

                    elif code in (550, 553):
                        # 550/553 = rejection, BUT some domains (Apple iCloud etc.) return
                        # 550 for ALL external probes even for valid addresses.
                        # For those, skip and let the final fallback handle it.
                        if is_reject_domain:
                            # Do not trust this 550 — skip to next server / fallback
                            break  # break inner retry loop, try next MX or fall through
                        if any(marker in msg_lower for marker in blocked_markers):
                            return True, "Server blocks verification (policy/relay) — likely deliverable", "blocked", 0.75
                        # Trusted 550 — user genuinely does not exist
                        return False, "Mailbox does not exist (SMTP 550)", "not_found", 0.95

                    elif code == 551:
                        return False, "User not local", "not_found", 0.85
                    elif code == 552:
                        # 552 = mailbox IS real but storage quota exceeded.
                        # The address exists — do NOT mark as not_found.
                        return True, "Mailbox exists but is full / over storage quota", "quota_exceeded", 0.85
                    elif code in (450, 451, 452):
                        # Transient — try next server
                        continue
                    else:
                        # Unexpected code — try next server
                        continue

                except smtplib.SMTPServerDisconnected:
                    continue  # Try next server
                except socket.timeout:
                    continue  # Try next server
                except (smtplib.SMTPException, OSError):
                    continue  # Try next server

        # All servers exhausted — classify by domain type
        if is_blocking_domain or is_reject_domain:
            # These domains are known to block / lie about SMTP probing
            return True, "Server blocks SMTP verification — likely deliverable", "blocked", 0.70
        else:
            # Domain has valid MX records but servers are unreachable from our IP
            # (firewall, geo-block, strict security policy). This is NOT evidence
            # that the mailbox doesn't exist — treat as "likely deliverable".
            return True, "Mail servers unreachable (firewall/geo-block) — likely deliverable", "unreachable", 0.65

    def verify_smtp(self, email: str, mx_host: str) -> Tuple[bool, str, str]:
        """
        Legacy method for backward compatibility.
        Use verify_smtp_multi_mx for better results.
        """
        # Extract domain from email
        domain = email.split('@')[1].lower()

        # Check if domain is in blocking list
        is_blocking_domain = any(domain.endswith(blocking) for blocking in self.blocking_domains)

        try:
            # Connect to SMTP server
            server = smtplib.SMTP(timeout=self.timeout)
            server.connect(mx_host)
            server.ehlo_or_helo_if_needed()
            server.mail('verify@example.com')
            code, message = server.rcpt(email)
            server.quit()

            # Check response code
            if code == 250:
                return True, "Email exists and is deliverable", "confirmed"
            elif code == 550:
                return False, "Email does not exist", "not_found"
            else:
                return False, f"SMTP returned code {code}", "error"

        except smtplib.SMTPServerDisconnected:
            if is_blocking_domain:
                return True, "Server blocks verification (common for Yahoo/AOL/Outlook) - MX exists, likely deliverable", "blocked"
            else:
                return False, "SMTP server disconnected", "error"

        except socket.timeout:
            if is_blocking_domain:
                return True, "Server timeout (common for Yahoo/AOL/Outlook) - MX exists, likely deliverable", "blocked"
            else:
                return False, "SMTP connection timed out", "error"

        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}", "error"
        except Exception as e:
            return False, f"Connection error: {str(e)}", "error"
    
    def validate_email(self, email: str, check_smtp=True) -> Dict:
        """
        Perform complete email validation with enhanced features.

        Args:
            email: Email address to validate
            check_smtp: Whether to perform SMTP verification

        Returns:
            Dictionary with validation results
        """
        result = {
            'email': email,
            'is_valid': False,
            'syntax_valid': False,
            'domain_exists': False,
            'mx_records': [],
            'smtp_check': False,
            'deliverable': False,
            'smtp_status': 'not_checked',
            'is_catchall': None,
            'is_disposable': False,
            'is_role_based': False,
            'has_spf': False,
            'has_dkim': False,
            'domain_reputation_score': 0,
            'confidence': 0.0,
            'messages': [],
            'validation_time': 0.0
        }

        start_time = time.time()
        self.logger.info(f"Starting validation for: {email}")

        # Check rate limiting
        if not self.check_rate_limit():
            self.logger.warning(f"Rate limit exceeded for: {email}")
            result['messages'] = ['Rate limit exceeded. Please wait before validating more emails.']
            result['error'] = 'rate_limit_exceeded'
            result['validation_time'] = time.time() - start_time
            return result

        try:
            # Step 1: Validate syntax
            syntax_valid, syntax_msg = self.validate_syntax(email)
            result['syntax_valid'] = syntax_valid
            result['messages'].append(syntax_msg)
            self.logger.debug(f"Syntax check for {email}: {syntax_valid}")

            if not syntax_valid:
                result['validation_time'] = time.time() - start_time
                return result

            # Step 2: Check if disposable email
            is_disposable, disposable_msg = self.is_disposable_email(email)
            result['is_disposable'] = is_disposable
            if is_disposable:
                result['messages'].append(disposable_msg)
                self.logger.info(f"Disposable email detected: {email}")

            # Step 2b: Check if role-based address
            is_role, role_msg = self.is_role_based_email(email)
            result['is_role_based'] = is_role
            if is_role:
                result['messages'].append(role_msg)
                self.logger.info(f"Role-based email detected: {email}")

            # Step 3: Extract domain and check MX records
            domain = email.split('@')[1]
            has_mx, mx_msg, mx_hosts = self.check_mx_records(domain)
            result['domain_exists'] = has_mx
            result['mx_records'] = mx_hosts
            result['messages'].append(mx_msg)
            self.logger.debug(f"MX check for {domain}: {len(mx_hosts)} records")

            if not has_mx:
                result['validation_time'] = time.time() - start_time
                return result

            # Step 4: Check domain reputation
            reputation = self.check_domain_reputation(domain)
            result['has_spf'] = reputation['has_spf']
            result['has_dkim'] = reputation['has_dkim']
            result['domain_reputation_score'] = reputation['score']

            if reputation['has_spf']:
                result['messages'].append("SPF record found")
            if reputation['has_dkim']:
                result['messages'].append("DKIM record found")

            # Step 5: Detect catch-all domain — ONLY when SMTP is enabled.
            # Catch-all detection requires an SMTP connection, so running it
            # without check_smtp would add 10-20s of latency for no benefit.
            if check_smtp and mx_hosts:
                is_catchall, catchall_msg = self.detect_catchall(domain, mx_hosts)
                result['is_catchall'] = is_catchall
                result['messages'].append(catchall_msg)
                self.logger.debug(f"Catch-all check for {domain}: {is_catchall}")
            elif not check_smtp:
                result['is_catchall'] = None  # Unknown without SMTP
                result['messages'].append("Catch-all check skipped (SMTP off)")

            # Step 6: SMTP verification (if enabled and MX records exist)
            if check_smtp and mx_hosts:
                # Use new multi-MX verification method
                smtp_valid, smtp_msg, status_type, confidence = self.verify_smtp_multi_mx(email, mx_hosts)
                result['smtp_check'] = True
                result['smtp_status'] = status_type
                result['deliverable'] = smtp_valid
                result['messages'].append(smtp_msg)
                self.logger.debug(f"SMTP check for {email}: {status_type}")

                # Adjust deliverable status based on catch-all detection
                if result['is_catchall'] and status_type == 'confirmed':
                    # If catch-all domain accepts the email, we can't be sure it's real
                    result['deliverable'] = False
                    result['messages'].append("Warning: Domain is catch-all - email existence cannot be verified")
                    confidence = min(confidence, 0.60)  # Reduce confidence for catch-all
            else:
                # SMTP was not requested — mailbox existence is UNKNOWN.
                # Do NOT mark deliverable=True; that would be a false positive.
                result['deliverable'] = False
                result['smtp_status'] = 'skipped'
                result['messages'].append(
                    "SMTP check skipped — enable SMTP for mailbox confirmation"
                )

            # Step 7: Calculate overall confidence score
            result['confidence'] = self.calculate_confidence(result)

            # Step 8: Set overall validity
            result['is_valid'] = result['syntax_valid'] and result['domain_exists'] and not result['is_disposable']

            result['validation_time'] = time.time() - start_time
            self.logger.info(f"Validation completed for {email}: valid={result['is_valid']}, confidence={result['confidence']:.1f}%")

        except Exception as e:
            self.logger.error(f"Unexpected error validating {email}: {str(e)}")
            result['messages'].append(f"Validation error: {str(e)}")
            result['validation_time'] = time.time() - start_time

        return result

    def calculate_confidence(self, result: Dict) -> float:
        """
        Calculate confidence score (0-100) based on validation results.

        Args:
            result: Validation result dictionary

        Returns:
            Confidence score as percentage (0-100)
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

        # Domain reputation: SPF (+10%) and DKIM (+10%)
        if result.get('has_spf'):
            confidence += 10
        if result.get('has_dkim'):
            confidence += 10

        # SMTP check results: 30%
        smtp_st = result.get('smtp_status', '')
        if smtp_st == 'confirmed':
            confidence += 30
        elif smtp_st == 'quota_exceeded':
            confidence += 28  # Mailbox confirmed real, just full
        elif smtp_st == 'blocked':
            confidence += 20  # Server blocked probe — likely real
        elif smtp_st == 'unreachable':
            confidence += 15  # Domain has MX infra, servers just unreachable
        elif smtp_st == 'not_found':
            confidence -= 30  # Server confirmed: mailbox does not exist
        elif smtp_st == 'error':
            confidence += 5   # Genuine unexpected error — small boost
        elif smtp_st == 'skipped':
            confidence -= 25  # No SMTP check at all — significant penalty

        # Catch-all detection: -15% if catch-all
        if result.get('is_catchall') == True:
            confidence -= 15
        elif result.get('is_catchall') == False:
            confidence += 10  # Bonus for non-catch-all

        # Disposable email: -20%
        if result.get('is_disposable') == True:
            confidence -= 20

        # Role-based address: -10% (shared inbox, marketing unsuitable)
        if result.get('is_role_based') == True:
            confidence -= 10

        # Ensure confidence is within 0-100 range
        confidence = max(0, min(100, confidence))

        return round(confidence, 1)
    
    def validate_bulk(self, emails: list, check_smtp=True) -> list:
        """
        Validate multiple email addresses.
        
        Args:
            emails: List of email addresses to validate
            check_smtp: Whether to perform SMTP verification
            
        Returns:
            List of validation result dictionaries
        """
        results = []
        for email in emails:
            result = self.validate_email(email, check_smtp=check_smtp)
            results.append(result)
        return results


def print_validation_result(result: Dict):
    """
    Pretty print email validation results.
    
    Args:
        result: Validation result dictionary
    """
    print("\n" + "="*60)
    print(f"Email: {result['email']}")
    print("="*60)
    print(f"Valid: {result['is_valid']}")
    print(f"Syntax Valid: {result['syntax_valid']}")
    print(f"Domain Exists: {result['domain_exists']}")
    print(f"Deliverable: {result['deliverable']}")
    print(f"SMTP Status: {result['smtp_status']}")
    
    if result['mx_records']:
        print(f"MX Records: {', '.join(result['mx_records'][:3])}")
    
    print("\nValidation Messages:")
    for i, msg in enumerate(result['messages'], 1):
        print(f"  {i}. {msg}")
    print("="*60)


if __name__ == "__main__":
    # Example usage
    validator = EmailValidator(timeout=10)
    
    # Test emails
    test_emails = [
        "user@gmail.com",
        "test@yahoo.com",
        "invalid.email@",
        "user@nonexistentdomain12345.com",
        "contact@microsoft.com"
    ]
    
    print("Email Validator - Test Run")
    print("="*60)
    
    # Validate single email
    print("\n### Single Email Validation ###")
    result = validator.validate_email("user@gmail.com", check_smtp=True)
    print_validation_result(result)
    
    # Validate multiple emails
    print("\n\n### Bulk Email Validation ###")
    results = validator.validate_bulk(test_emails[:3], check_smtp=False)
    
    for result in results:
        print(f"\n{result['email']}: Valid={result['is_valid']}, Deliverable={result['deliverable']}")
    
    print("\n\nValidation complete!")
