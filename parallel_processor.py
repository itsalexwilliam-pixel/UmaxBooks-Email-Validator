"""
Parallel Batch Processor for Power Email Validation
Optimized for high-volume email validation with concurrent processing
"""

import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Callable
import time
from dataclasses import dataclass
from email_validator import EmailValidator
import logging


@dataclass
class BatchJob:
    """Represents a batch validation job"""
    job_id: str
    emails: List[str]
    check_smtp: bool = True
    on_progress: Callable = None
    on_complete: Callable = None
    created_at: float = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class ParallelBatchProcessor:
    """Process email validation in parallel with progress tracking"""

    def _validate_single_email(self, email: str, check_smtp: bool) -> Dict:
        """Validate one email with an isolated validator instance."""
        validator = EmailValidator(
            timeout=self.validator_timeout,
            enable_cache=True,
            rate_limit=0
        )
        return validator.validate_email(email, check_smtp=check_smtp)

    def __init__(self, max_workers: int = 5, validator_timeout: int = 10):
        """
        Initialize parallel batch processor

        Args:
            max_workers: Number of concurrent validation threads
            validator_timeout: Timeout for network operations
        """
        self.max_workers = max_workers
        self.validator_timeout = validator_timeout
        self.logger = logging.getLogger('ParallelBatchProcessor')

        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Job tracking
        self.jobs = {}
        self.jobs_lock = threading.Lock()


    def validate_batch(self, emails: List[str], check_smtp: bool = True,
                      on_progress: Callable = None,
                      on_complete: Callable = None) -> Dict:
        """
        Validate a batch of emails in parallel

        Args:
            emails: List of email addresses to validate
            check_smtp: Whether to perform SMTP verification
            on_progress: Callback function(email, result, progress) during validation
            on_complete: Callback function(results, stats) when complete

        Returns:
            Dictionary with results and statistics
        """
        job_id = f"batch_{int(time.time() * 1000)}"
        start_time = time.time()

        self.logger.info(f"Starting batch job {job_id} with {len(emails)} emails")

        job = BatchJob(
            job_id=job_id,
            emails=emails,
            check_smtp=check_smtp,
            on_progress=on_progress,
            on_complete=on_complete
        )

        with self.jobs_lock:
            self.jobs[job_id] = {
                'status': 'processing',
                'total': len(emails),
                'completed': 0,
                'results': []
            }

        # Process emails in parallel
        results = []
        futures = {}

        try:
            # Submit all validation tasks
            for email in emails:
                future = self.executor.submit(
                    self._validate_single_email,
                    email,
                    check_smtp
                )
                futures[future] = email

            # Collect results as they complete
            for future in as_completed(futures):
                email = futures[future]
                try:
                    result = future.result(timeout=self.validator_timeout + 5)
                    results.append(result)

                    # Update progress
                    with self.jobs_lock:
                        self.jobs[job_id]['completed'] += 1
                        self.jobs[job_id]['results'].append(result)

                    # Call progress callback
                    if on_progress:
                        progress = (self.jobs[job_id]['completed'] / len(emails)) * 100
                        on_progress(email, result, progress)

                    self.logger.debug(f"Validated {email}: {result['confidence']}% confidence")

                except Exception as e:
                    self.logger.error(f"Error validating {email}: {str(e)}")
                    error_result = {
                        'email': email,
                        'is_valid': False,
                        'deliverable': False,
                        'confidence': 0.0,
                        'messages': [f"Validation error: {str(e)}"],
                        'error': True
                    }
                    results.append(error_result)

                    with self.jobs_lock:
                        self.jobs[job_id]['completed'] += 1
                        self.jobs[job_id]['results'].append(error_result)

                    if on_progress:
                        progress = (self.jobs[job_id]['completed'] / len(emails)) * 100
                        on_progress(email, error_result, progress)

        finally:
            elapsed_time = time.time() - start_time

            # Calculate statistics
            stats = self._calculate_stats(results, elapsed_time)

            # Mark job as complete
            with self.jobs_lock:
                self.jobs[job_id]['status'] = 'complete'

            # Call complete callback
            if on_complete:
                on_complete(results, stats)

            self.logger.info(f"Batch job {job_id} completed: {stats['total_emails']} emails in {elapsed_time:.2f}s")

        return {
            'job_id': job_id,
            'results': results,
            'stats': stats
        }

    def validate_batch_sync(self, emails: List[str], check_smtp: bool = True) -> Dict:
        """
        Synchronous batch validation (blocking call)

        Args:
            emails: List of email addresses
            check_smtp: Whether to perform SMTP verification

        Returns:
            Dictionary with results and statistics
        """
        return self.validate_batch(emails, check_smtp=check_smtp)

    def get_job_status(self, job_id: str) -> Dict:
        """Get status of a batch job"""
        with self.jobs_lock:
            if job_id in self.jobs:
                return self.jobs[job_id]
        return None

    def _calculate_stats(self, results: List[Dict], elapsed_time: float) -> Dict:
        """Calculate validation statistics"""
        total = len(results)
        valid_count = sum(1 for r in results if r.get('is_valid', False))
        deliverable_count = sum(1 for r in results if r.get('deliverable', False))
        high_confidence = sum(1 for r in results if r.get('confidence', 0) >= 80)
        catchall_count = sum(1 for r in results if r.get('is_catchall') == True)
        disposable_count = sum(1 for r in results if r.get('is_disposable') == True)
        error_count = sum(1 for r in results if r.get('error', False))

        avg_confidence = sum(r.get('confidence', 0) for r in results) / total if total > 0 else 0
        emails_per_second = total / elapsed_time if elapsed_time > 0 else 0

        return {
            'total_emails': total,
            'valid': valid_count,
            'deliverable': deliverable_count,
            'high_confidence': high_confidence,
            'catchall_domains': catchall_count,
            'disposable_emails': disposable_count,
            'errors': error_count,
            'average_confidence': round(avg_confidence, 1),
            'elapsed_time': round(elapsed_time, 2),
            'emails_per_second': round(emails_per_second, 2)
        }

    def shutdown(self):
        """Gracefully shutdown the executor"""
        self.executor.shutdown(wait=True)
        self.logger.info("Parallel batch processor shut down")
