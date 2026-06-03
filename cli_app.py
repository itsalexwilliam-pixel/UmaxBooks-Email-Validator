"""
Power Email Validation - Command Line Interface
Simple CLI application for email validation
"""

import sys
import argparse
from email_validator import EmailValidator, print_validation_result
import csv
import json
from pathlib import Path


def validate_single(args):
    """Validate a single email"""
    validator = EmailValidator(timeout=args.timeout)
    result = validator.validate_email(args.email, check_smtp=args.smtp)
    print_validation_result(result)
    
    if args.output:
        save_result([result], args.output)
    
    return 0 if result['is_valid'] else 1


def validate_bulk(args):
    """Validate multiple emails from file or stdin"""
    validator = EmailValidator(timeout=args.timeout)
    
    # Read emails
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            if args.input.endswith('.csv'):
                reader = csv.reader(f)
                emails = [row[0] for row in reader if row]
            else:
                emails = [line.strip() for line in f if line.strip()]
    else:
        print("Enter email addresses (one per line, Ctrl+D to finish):")
        emails = [line.strip() for line in sys.stdin if line.strip()]
    
    if not emails:
        print("No emails to validate")
        return 1
    
    print(f"\nValidating {len(emails)} emails...\n")
    
    results = validator.validate_bulk(emails, check_smtp=args.smtp)
    
    # Display results
    valid_count = sum(1 for r in results if r['is_valid'])
    deliverable_count = sum(1 for r in results if r['deliverable'])
    
    print("="*60)
    print("BULK VALIDATION RESULTS")
    print("="*60)
    print(f"Total Emails: {len(results)}")
    print(f"Valid: {valid_count}")
    print(f"Deliverable: {deliverable_count}")
    print("="*60)
    
    if args.verbose:
        for result in results:
            print_validation_result(result)
    else:
        print("\nSummary:")
        for result in results:
            status = "✓" if result['deliverable'] else "✗"
            print(f"{status} {result['email']}")
    
    # Save results
    if args.output:
        save_result(results, args.output)
        print(f"\nResults saved to: {args.output}")
    
    return 0 if valid_count == len(emails) else 1


def save_result(results, output_file):
    """Save validation results to file"""
    ext = Path(output_file).suffix.lower()
    
    if ext == '.json':
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
    
    elif ext == '.csv':
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Email', 'Valid', 'Deliverable', 'Status'])
            for result in results:
                writer.writerow([
                    result['email'],
                    result['is_valid'],
                    result['deliverable'],
                    ' | '.join(result['messages'])
                ])
    
    else:  # txt
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(f"Email: {result['email']}\n")
                f.write(f"Valid: {result['is_valid']}\n")
                f.write(f"Deliverable: {result['deliverable']}\n")
                f.write(f"Messages: {', '.join(result['messages'])}\n")
                f.write("-" * 60 + "\n")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Power Email Validation - Validate email deliverability',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s user@example.com
  %(prog)s user@example.com --smtp
  %(prog)s --bulk -i emails.txt -o results.csv
  %(prog)s --bulk --smtp -i emails.csv -o results.json
        """
    )
    
    parser.add_argument(
        'email',
        nargs='?',
        help='Email address to validate'
    )
    
    parser.add_argument(
        '-b', '--bulk',
        action='store_true',
        help='Bulk validation mode'
    )
    
    parser.add_argument(
        '-i', '--input',
        help='Input file with emails (txt or csv)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file for results (txt, csv, or json)'
    )
    
    parser.add_argument(
        '-s', '--smtp',
        action='store_true',
        help='Perform deep SMTP verification'
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=10,
        help='Timeout in seconds (default: 10)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    try:
        if args.bulk:
            return validate_bulk(args)
        elif args.email:
            return validate_single(args)
        else:
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        print("\n\nValidation cancelled by user")
        return 130
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
