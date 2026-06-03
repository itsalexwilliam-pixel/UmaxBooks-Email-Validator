"""
Advanced Reporting and Analytics for Email Validation
Provides detailed insights, patterns, and metrics
"""

import json
from typing import List, Dict
from datetime import datetime
from collections import Counter, defaultdict
import logging


class AdvancedReporter:
    """Generate advanced analytics and reports"""

    def __init__(self):
        self.logger = logging.getLogger('AdvancedReporter')

    def generate_full_report(self, results: List[Dict], title: str = "Email Validation Report") -> Dict:
        """
        Generate a comprehensive validation report
        
        Args:
            results: List of validation results
            title: Report title
            
        Returns:
            Comprehensive report dictionary
        """
        if not results:
            return self._empty_report(title)

        report = {
            'metadata': {
                'title': title,
                'generated_at': datetime.now().isoformat(),
                'total_emails': len(results)
            },
            'summary': self._generate_summary(results),
            'distribution': self._generate_distribution(results),
            'confidence_analysis': self._generate_confidence_analysis(results),
            'domain_insights': self._generate_domain_insights(results),
            'risk_assessment': self._generate_risk_assessment(results),
            'patterns': self._detect_patterns(results),
            'recommendations': self._generate_recommendations(results)
        }

        return report

    def export_to_csv(self, results: List[Dict]) -> str:
        """Export results to CSV format"""
        if not results:
            return ""

        lines = []
        headers = [
            'Email', 'Valid', 'Deliverable', 'Syntax Valid', 'Domain Exists',
            'Catch-all', 'Disposable', 'Has SPF', 'Has DKIM', 'Confidence',
            'SMTP Status', 'Messages'
        ]
        lines.append(','.join(headers))

        for result in results:
            row = [
                result.get('email', ''),
                str(result.get('is_valid', False)),
                str(result.get('deliverable', False)),
                str(result.get('syntax_valid', False)),
                str(result.get('domain_exists', False)),
                str(result.get('is_catchall', False)),
                str(result.get('is_disposable', False)),
                str(result.get('has_spf', False)),
                str(result.get('has_dkim', False)),
                str(result.get('confidence', 0)),
                result.get('smtp_status', ''),
                '|'.join(result.get('messages', []))
            ]
            lines.append(','.join([f'"{f}"' for f in row]))

        return '\n'.join(lines)

    def export_to_json(self, results: List[Dict], report: Dict = None) -> str:
        """Export results to JSON format"""
        export_data = {
            'results': results,
            'report': report,
            'exported_at': datetime.now().isoformat()
        }
        return json.dumps(export_data, indent=2)

    # ==================== Private Helper Methods ====================

    def _empty_report(self, title: str) -> Dict:
        """Generate empty report structure"""
        return {
            'metadata': {
                'title': title,
                'generated_at': datetime.now().isoformat(),
                'total_emails': 0
            },
            'error': 'No results to report'
        }

    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate high-level summary statistics"""
        total = len(results)
        valid = sum(1 for r in results if r.get('is_valid', False))
        deliverable = sum(1 for r in results if r.get('deliverable', False))
        with_errors = sum(1 for r in results if r.get('error', False))

        return {
            'total_emails': total,
            'valid_emails': valid,
            'deliverable_emails': deliverable,
            'quality_score': round((deliverable / total * 100), 2) if total > 0 else 0,
            'success_rate': round((valid / total * 100), 2) if total > 0 else 0,
            'error_rate': round((with_errors / total * 100), 2) if total > 0 else 0
        }

    def _generate_distribution(self, results: List[Dict]) -> Dict:
        """Generate distribution analysis"""
        categories = {
            'syntax_valid': 0,
            'syntax_invalid': 0,
            'domain_exists': 0,
            'domain_not_exists': 0,
            'deliverable': 0,
            'not_deliverable': 0,
            'disposable': 0,
            'catch_all': 0,
            'has_spf': 0,
            'has_dkim': 0
        }

        for result in results:
            if result.get('syntax_valid'):
                categories['syntax_valid'] += 1
            else:
                categories['syntax_invalid'] += 1

            if result.get('domain_exists'):
                categories['domain_exists'] += 1
            else:
                categories['domain_not_exists'] += 1

            if result.get('deliverable'):
                categories['deliverable'] += 1
            else:
                categories['not_deliverable'] += 1

            if result.get('is_disposable'):
                categories['disposable'] += 1

            if result.get('is_catchall'):
                categories['catch_all'] += 1

            if result.get('has_spf'):
                categories['has_spf'] += 1

            if result.get('has_dkim'):
                categories['has_dkim'] += 1

        return categories

    def _generate_confidence_analysis(self, results: List[Dict]) -> Dict:
        """Analyze confidence score distribution"""
        if not results:
            return {}

        confidences = [r.get('confidence', 0) for r in results]

        return {
            'average': round(sum(confidences) / len(confidences), 2),
            'min': round(min(confidences), 2),
            'max': round(max(confidences), 2),
            'median': round(sorted(confidences)[len(confidences) // 2], 2),
            'high_confidence_count': sum(1 for c in confidences if c >= 80),
            'medium_confidence_count': sum(1 for c in confidences if 60 <= c < 80),
            'low_confidence_count': sum(1 for c in confidences if c < 60)
        }

    def _generate_domain_insights(self, results: List[Dict]) -> Dict:
        """Analyze domain-related insights"""
        domain_stats = defaultdict(lambda: {'count': 0, 'valid': 0, 'deliverable': 0, 'has_spf': 0, 'has_dkim': 0})

        for result in results:
            if '@' in result.get('email', ''):
                domain = result['email'].split('@')[1].lower()
                domain_stats[domain]['count'] += 1

                if result.get('is_valid'):
                    domain_stats[domain]['valid'] += 1

                if result.get('deliverable'):
                    domain_stats[domain]['deliverable'] += 1

                if result.get('has_spf'):
                    domain_stats[domain]['has_spf'] += 1

                if result.get('has_dkim'):
                    domain_stats[domain]['has_dkim'] += 1

        # Sort by frequency
        sorted_domains = sorted(domain_stats.items(), key=lambda x: x[1]['count'], reverse=True)

        return {
            'total_unique_domains': len(domain_stats),
            'top_domains': [
                {
                    'domain': domain,
                    'email_count': stats['count'],
                    'valid_rate': round((stats['valid'] / stats['count'] * 100), 1) if stats['count'] > 0 else 0,
                    'deliverable_rate': round((stats['deliverable'] / stats['count'] * 100), 1) if stats['count'] > 0 else 0,
                    'spf_enabled': stats['has_spf'] > 0,
                    'dkim_enabled': stats['has_dkim'] > 0
                }
                for domain, stats in sorted_domains[:10]
            ]
        }

    def _generate_risk_assessment(self, results: List[Dict]) -> Dict:
        """Assess risk levels"""
        high_risk = sum(1 for r in results if r.get('is_disposable') or r.get('is_catchall'))
        medium_risk = sum(1 for r in results if r.get('confidence', 0) < 60 and not r.get('is_disposable'))
        low_risk = len(results) - high_risk - medium_risk

        return {
            'high_risk_emails': {
                'count': high_risk,
                'percentage': round((high_risk / len(results) * 100), 1) if results else 0,
                'details': 'Disposable emails and catch-all domains'
            },
            'medium_risk_emails': {
                'count': medium_risk,
                'percentage': round((medium_risk / len(results) * 100), 1) if results else 0,
                'details': 'Low confidence scores (<60%)'
            },
            'low_risk_emails': {
                'count': low_risk,
                'percentage': round((low_risk / len(results) * 100), 1) if results else 0,
                'details': 'Verified, high confidence emails'
            }
        }

    def _detect_patterns(self, results: List[Dict]) -> Dict:
        """Detect patterns in email list"""
        domains = [r['email'].split('@')[1].lower() for r in results if '@' in r.get('email', '')]
        domain_counter = Counter(domains)

        disposable_providers = Counter()
        invalid_patterns = []

        for result in results:
            if result.get('is_disposable') and '@' in result['email']:
                provider = result['email'].split('@')[1].lower()
                disposable_providers[provider] += 1

            if not result.get('syntax_valid'):
                invalid_patterns.append(result['email'])

        return {
            'most_common_domains': domain_counter.most_common(5),
            'disposable_email_providers': disposable_providers.most_common(5),
            'common_invalid_formats': invalid_patterns[:10],
            'total_unique_domains': len(domain_counter)
        }

    def _generate_recommendations(self, results: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        distribution = self._generate_distribution(results)

        # Syntax issues
        if distribution['syntax_invalid'] > 0:
            syntax_rate = distribution['syntax_invalid'] / len(results) * 100
            if syntax_rate > 10:
                recommendations.append(f"⚠️  High syntax error rate ({syntax_rate:.1f}%). Review email collection process.")

        # Non-existent domains
        if distribution['domain_not_exists'] > 0:
            domain_rate = distribution['domain_not_exists'] / len(results) * 100
            if domain_rate > 5:
                recommendations.append(f"⚠️  {domain_rate:.1f}% of emails have non-existent domains. Validate source data.")

        # Deliverability
        if distribution['not_deliverable'] > 0:
            undeliverable_rate = distribution['not_deliverable'] / len(results) * 100
            if undeliverable_rate > 20:
                recommendations.append(f"⚠️  {undeliverable_rate:.1f}% emails not deliverable. Consider data cleansing.")

        # Disposable emails
        if distribution['disposable'] > 0:
            disposable_rate = distribution['disposable'] / len(results) * 100
            if disposable_rate > 5:
                recommendations.append(f"⚠️  {disposable_rate:.1f}% are disposable emails. Filter before use.")

        # Low confidence
        confidence = self._generate_confidence_analysis(results)
        if confidence.get('low_confidence_count', 0) > len(results) * 0.3:
            recommendations.append("📊 Many emails have low confidence scores. Enable SMTP verification for better results.")

        # Security
        if distribution['has_spf'] < len(results) * 0.5:
            recommendations.append("🔐 Less than 50% of domains have SPF records. Consider domain reputation issues.")

        if not recommendations:
            recommendations.append("✅ Email list quality is good. No major issues detected.")

        return recommendations
