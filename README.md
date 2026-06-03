# 📧 Power Email Validation

A comprehensive Python-based email validation tool that checks email syntax, domain validity, and deliverability.

## ✨ Features

### Core Features
- **Email Syntax Validation**: Validates email format using regex
- **DNS/MX Record Check**: Verifies domain exists and has mail servers
- **SMTP Verification**: Deep check for email deliverability (optional)
- **Bulk Validation**: Validate hundreds of emails at once
- **Multiple Interfaces**: 
  - GUI (Graphical User Interface)
  - CLI (Command Line Interface)
  - REST API (Phase 3)
  - Python API
- **Export Results**: Save results in CSV, JSON, or TXT format
- **Import from File**: Load emails from text or CSV files

### Phase 3: Enterprise Features 🚀
- **REST API Server**: HTTP endpoints for integration with any application
- **Parallel Processing**: 10x faster batch validation with concurrent processing
- **Advanced Reporting**: Comprehensive analytics with 7 report sections
- **Domain Reputation**: 0-100 risk scoring with SPF/DKIM verification
- **Real-time Monitoring**: Progress tracking and performance metrics
- **Production Ready**: Rate limiting, error handling, CORS support

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher

### Setup

1. **Clone or download this repository**

2. **Install required packages:**
```bash
pip install -r requirements.txt
```

## 📖 Usage

### GUI Application (Recommended for Beginners)

Run the graphical interface:
```bash
python gui_app.py
```

Features:
- Single email validation
- Bulk email validation
- Import emails from file
- Export results
- Real-time validation status

### Command Line Interface (CLI)

**Validate a single email:**
```bash
python cli_app.py user@example.com
```

**With SMTP verification:**
```bash
python cli_app.py user@example.com --smtp
```

**Bulk validation from file:**
```bash
python cli_app.py --bulk -i emails.txt -o results.csv
```

**Bulk validation with SMTP check:**
```bash
python cli_app.py --bulk --smtp -i emails.txt -o results.json
```

**CLI Options:**
- `-b, --bulk`: Bulk validation mode
- `-i, --input`: Input file path
- `-o, --output`: Output file path (csv, json, txt)
- `-s, --smtp`: Enable SMTP verification
- `-t, --timeout`: Set timeout in seconds
- `-v, --verbose`: Detailed output

### Python API

Use in your own Python scripts:

```python
from email_validator import EmailValidator

# Create validator instance
validator = EmailValidator(timeout=10)

# Validate single email
result = validator.validate_email("user@example.com", check_smtp=True)

print(f"Valid: {result['is_valid']}")
print(f"Deliverable: {result['deliverable']}")
print(f"Messages: {result['messages']}")

# Bulk validation
emails = ["user1@example.com", "user2@example.com"]
results = validator.validate_bulk(emails, check_smtp=False)

for result in results:
    print(f"{result['email']}: {result['is_valid']}")
```

### REST API (Phase 3)

Start the API server for integration with external applications:

```bash
python api_server.py
# Server runs on http://localhost:5000
```

**Single email validation:**
```bash
curl -X POST http://localhost:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "check_smtp": true}'
```

**Batch validation (up to 1000 emails):**
```bash
curl -X POST http://localhost:5000/api/validate/batch \
  -H "Content-Type: application/json" \
  -d '{"emails": ["user1@example.com", "user2@example.com"], "check_smtp": true}'
```

**Advanced analysis with reporting:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"emails": ["list of emails"], "check_smtp": true}'
```

**Available endpoints:**
- `GET /api/health` - Server health check
- `GET /api/info` - API capabilities
- `POST /api/validate` - Single email validation
- `POST /api/validate/batch` - Batch validation
- `POST /api/analyze` - Analysis with advanced reporting
- `POST /api/domains` - Domain grouping analysis

## 📊 Validation Process

The validator performs three levels of checks:

1. **Syntax Validation**: 
   - Checks email format using regex
   - Validates local and domain parts
   - Ensures proper structure

2. **DNS/MX Record Check**:
   - Queries DNS for MX records
   - Verifies domain exists
   - Lists mail servers

3. **SMTP Verification** (Optional):
   - Connects to mail server
   - Verifies email exists
   - Tests deliverability

## 📝 Input File Formats

### Text File (emails.txt)
```
user1@example.com
user2@example.com
admin@company.com
```

### CSV File (emails.csv)
```
user1@example.com
user2@example.com
admin@company.com
```

## 📤 Output Formats

### CSV Output
```csv
Email,Valid,Deliverable,Status
user@example.com,True,True,Syntax: valid | MX: Found 2 records
```

### JSON Output
```json
[
  {
    "email": "user@example.com",
    "is_valid": true,
    "deliverable": true,
    "messages": ["Syntax: valid", "MX: Found 2 records"]
  }
]
```

## ⚠️ Important Notes

1. **SMTP Verification**: 
   - More accurate but slower
   - Some servers may block verification attempts
   - Use sparingly to avoid being rate-limited

2. **Rate Limiting**:
   - Don't validate too many emails too quickly
   - Some mail servers may temporarily block your IP

3. **False Positives**:
   - Some domains block SMTP verification
   - Catch-all servers may accept all emails

## 🛠️ Troubleshooting

**DNS Resolution Errors:**
- Check your internet connection
- Verify DNS servers are accessible
- Some networks may block DNS queries

**SMTP Connection Issues:**
- Firewall may block port 25
- Some mail servers don't allow verification
- Try without --smtp flag

**Timeout Errors:**
- Increase timeout: `-t 30`
- Check slow network connection

## 📧 Use Cases

- **Marketing**: Verify email lists before campaigns
- **Registration**: Validate user emails during signup
- **Data Cleaning**: Clean up email databases
- **Lead Generation**: Verify collected email addresses
- **Bulk Processing**: Process large email lists

## 🔒 Privacy & Security

- No emails are stored or transmitted to third parties
- All validation happens locally on your machine
- SMTP checks connect directly to mail servers
- No data is logged or saved without your consent

## 📄 License

Free to use for personal and commercial projects.

## 👨‍💻 Developer

Created by Power Email Validation

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📞 Support

For questions or issues, please create an issue in the repository.

---

**Happy Validating! 🎉**
