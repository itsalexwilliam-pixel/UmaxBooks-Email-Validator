"""
REST API Server for Power Email Validation
Provides HTTP endpoints for email validation services
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from email_validator import EmailValidator
from parallel_processor import ParallelBatchProcessor
import json
from datetime import datetime


# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize validators and processors
validator = EmailValidator(timeout=10, enable_cache=True, rate_limit=100)
batch_processor = ParallelBatchProcessor(max_workers=5, validator_timeout=10)


# ==================== Health & Info Endpoints ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    }), 200


@app.route('/api/info', methods=['GET'])
def info():
    """API information endpoint"""
    return jsonify({
        'name': 'Power Email Validation API',
        'version': '2.0.0',
        'description': 'Enterprise-grade email validation service',
        'features': [
            'Syntax validation',
            'DNS/MX record checking',
            'SMTP verification',
            'Catch-all detection',
            'Disposable email detection',
            'SPF/DKIM verification',
            'Confidence scoring',
            'Batch processing',
            'Rate limiting'
        ]
    }), 200


# ==================== Single Email Validation ====================

@app.route('/api/validate', methods=['POST'])
def validate_single():
    """
    Validate a single email address
    
    Request body:
    {
        "email": "user@example.com",
        "check_smtp": true
    }
    """
    try:
        data = request.get_json()

        if not data or 'email' not in data:
            return jsonify({'error': 'Email address required'}), 400

        email = data['email'].strip()
        check_smtp = data.get('check_smtp', False)

        if not email:
            return jsonify({'error': 'Email address cannot be empty'}), 400

        result = validator.validate_email(email, check_smtp=check_smtp)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'error': f'Validation error: {str(e)}'}), 500


# ==================== Batch Validation ====================

@app.route('/api/validate/batch', methods=['POST'])
def validate_batch():
    """
    Validate multiple email addresses in parallel
    
    Request body:
    {
        "emails": ["user1@example.com", "user2@example.com"],
        "check_smtp": false
    }
    """
    try:
        data = request.get_json()

        if not data or 'emails' not in data:
            return jsonify({'error': 'Email list required'}), 400

        emails = data['emails']
        check_smtp = data.get('check_smtp', False)

        if not isinstance(emails, list):
            return jsonify({'error': 'Emails must be a list'}), 400

        if len(emails) == 0:
            return jsonify({'error': 'Email list cannot be empty'}), 400

        if len(emails) > 1000:
            return jsonify({'error': 'Maximum 1000 emails per request'}), 400

        # Clean and validate email list
        emails = [e.strip() for e in emails if isinstance(e, str) and e.strip()]

        # Process batch with parallel processor
        batch_result = batch_processor.validate_batch_sync(emails, check_smtp=check_smtp)

        return jsonify({
            'job_id': batch_result['job_id'],
            'results': batch_result['results'],
            'statistics': batch_result['stats']
        }), 200

    except Exception as e:
        logger.error(f"Batch validation error: {str(e)}")
        return jsonify({'error': f'Validation error: {str(e)}'}), 500


# ==================== Reporting ====================

@app.route('/api/analyze', methods=['POST'])
def analyze_batch():
    """
    Analyze a batch of emails and return detailed report
    
    Request body:
    {
        "emails": ["user1@example.com", "user2@example.com"],
        "check_smtp": true
    }
    """
    try:
        data = request.get_json()

        if not data or 'emails' not in data:
            return jsonify({'error': 'Email list required'}), 400

        emails = data['emails']
        check_smtp = data.get('check_smtp', True)

        if not isinstance(emails, list) or len(emails) == 0:
            return jsonify({'error': 'Valid email list required'}), 400

        if len(emails) > 1000:
            return jsonify({'error': 'Maximum 1000 emails per request'}), 400

        emails = [e.strip() for e in emails if isinstance(e, str) and e.strip()]

        # Process batch
        batch_result = batch_processor.validate_batch_sync(emails, check_smtp=check_smtp)
        results = batch_result['results']
        stats = batch_result['stats']

        # Generate detailed report
        report = {
            'summary': {
                'total': stats['total_emails'],
                'valid': stats['valid'],
                'deliverable': stats['deliverable'],
                'quality_score': round((stats['deliverable'] / stats['total_emails'] * 100), 1) if stats['total_emails'] > 0 else 0
            },
            'details': {
                'high_confidence': stats['high_confidence'],
                'catch_all_domains': stats['catchall_domains'],
                'disposable_emails': stats['disposable_emails'],
                'errors': stats['errors'],
                'average_confidence': stats['average_confidence']
            },
            'performance': {
                'emails_per_second': stats['emails_per_second'],
                'total_time_seconds': stats['elapsed_time']
            },
            'categories': _categorize_results(results),
            'patterns': _detect_patterns(results),
            'results': results
        }

        return jsonify(report), 200

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': f'Analysis error: {str(e)}'}), 500


# ==================== Utilities ====================

@app.route('/api/domains', methods=['POST'])
def domain_analysis():
    """
    Analyze domains from a list of emails
    
    Request body:
    {
        "emails": ["user1@domain1.com", "user2@domain1.com", "user3@domain2.com"]
    }
    """
    try:
        data = request.get_json()

        if not data or 'emails' not in data:
            return jsonify({'error': 'Email list required'}), 400

        emails = data['emails']

        if not isinstance(emails, list) or len(emails) == 0:
            return jsonify({'error': 'Valid email list required'}), 400

        # Extract and group domains
        domain_stats = {}

        for email in emails:
            if not isinstance(email, str):
                continue
            email = email.strip()
            if '@' in email:
                domain = email.split('@')[1].lower()
                if domain not in domain_stats:
                    domain_stats[domain] = {'count': 0, 'emails': []}
                domain_stats[domain]['count'] += 1
                domain_stats[domain]['emails'].append(email)

        # Sort by frequency
        sorted_domains = sorted(domain_stats.items(), key=lambda x: x[1]['count'], reverse=True)

        return jsonify({
            'total_domains': len(domain_stats),
            'domains': [
                {
                    'domain': domain,
                    'count': stats['count'],
                    'percentage': round((stats['count'] / len(emails) * 100), 1),
                    'sample_emails': stats['emails'][:5]
                }
                for domain, stats in sorted_domains
            ]
        }), 200

    except Exception as e:
        logger.error(f"Domain analysis error: {str(e)}")
        return jsonify({'error': f'Analysis error: {str(e)}'}), 500


# ==================== Helper Functions ====================

def _categorize_results(results):
    """Categorize validation results"""
    categories = {
        'valid_deliverable': [],
        'valid_not_deliverable': [],
        'invalid_syntax': [],
        'disposable': [],
        'catch_all': [],
        'errors': []
    }

    for result in results:
        if result.get('error'):
            categories['errors'].append(result['email'])
        elif result.get('is_disposable'):
            categories['disposable'].append(result['email'])
        elif result.get('is_catchall'):
            categories['catch_all'].append(result['email'])
        elif not result.get('syntax_valid'):
            categories['invalid_syntax'].append(result['email'])
        elif result.get('deliverable'):
            categories['valid_deliverable'].append(result['email'])
        else:
            categories['valid_not_deliverable'].append(result['email'])

    return {
        'valid_deliverable': len(categories['valid_deliverable']),
        'valid_not_deliverable': len(categories['valid_not_deliverable']),
        'invalid_syntax': len(categories['invalid_syntax']),
        'disposable': len(categories['disposable']),
        'catch_all': len(categories['catch_all']),
        'errors': len(categories['errors'])
    }


def _detect_patterns(results):
    """Detect patterns in validation results"""
    patterns = {
        'common_invalid_domains': {},
        'common_disposable_providers': {},
        'high_confidence_rate': 0,
        'issues': []
    }

    high_confidence_count = 0

    for result in results:
        if result.get('confidence', 0) >= 80:
            high_confidence_count += 1

        if not result.get('deliverable') and not result.get('is_disposable'):
            domain = result['email'].split('@')[1].lower() if '@' in result['email'] else 'unknown'
            patterns['common_invalid_domains'][domain] = patterns['common_invalid_domains'].get(domain, 0) + 1

        if result.get('is_disposable'):
            provider = result['email'].split('@')[1].lower() if '@' in result['email'] else 'unknown'
            patterns['common_disposable_providers'][provider] = patterns['common_disposable_providers'].get(provider, 0) + 1

    patterns['high_confidence_rate'] = round((high_confidence_count / len(results) * 100), 1) if results else 0

    # Identify top issues
    if patterns['common_invalid_domains']:
        top_invalid = sorted(patterns['common_invalid_domains'].items(), key=lambda x: x[1], reverse=True)[:3]
        patterns['issues'].append(f"Top invalid domains: {', '.join([d[0] for d in top_invalid])}")

    if patterns['common_disposable_providers']:
        top_disposable = sorted(patterns['common_disposable_providers'].items(), key=lambda x: x[1], reverse=True)[:3]
        patterns['issues'].append(f"Top disposable providers: {', '.join([d[0] for d in top_disposable])}")

    return patterns


# ==================== Error Handlers ====================

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


# ==================== Main ====================

if __name__ == '__main__':
    print("=" * 70)
    print("Power Email Validation API Server v2.0")
    print("=" * 70)
    print("\nAvailable Endpoints:")
    print("  GET    /api/health              - Health check")
    print("  GET    /api/info                - API information")
    print("  POST   /api/validate            - Validate single email")
    print("  POST   /api/validate/batch      - Validate batch of emails")
    print("  POST   /api/analyze             - Detailed batch analysis")
    print("  POST   /api/domains             - Domain analysis")
    print("\nServer running on http://localhost:5000")
    print("=" * 70 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
