<div align="center">

<img src="Power.png" alt="UmaxBooks Power Email Validator" width="120"/>

# ⚡ UmaxBooks Power Email Validator

**Enterprise-grade email validation desktop app — no internet subscription, no per-email fees, runs fully offline on any Windows machine.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows)](https://github.com/itsalexwilliam-pixel/UmaxBooks-Email-Validator)
[![License](https://img.shields.io/badge/License-Free%20to%20Use-brightgreen)](LICENSE)
[![Build](https://img.shields.io/badge/Build-PyInstaller%20EXE-orange)](https://pyinstaller.org)

</div>

---

## 🧠 What is This?

UmaxBooks Power Email Validator is a **professional-grade, multi-layer email validation platform** built for marketing teams, data analysts, CRM managers, and developers.

Unlike simple regex checkers, this tool runs a **9-step deep validation pipeline** — verifying syntax, DNS records, MX servers, SPF/DKIM configuration, catch-all behavior, SMTP deliverability, and domain reputation — then produces a **confidence score (0–100%)** for every email.

> ✅ **One-click EXE** — no Python, no pip, no dependencies needed on target machines.

---

## 🚀 Key Features & USPs

### ⚙️ Multi-Layer Validation Engine (Not Just Regex)
Most tools only check email *format*. This tool validates **9 layers deep**:

| Layer | What It Checks |
|-------|---------------|
| 1️⃣ Syntax | Format correctness (local + domain structure) |
| 2️⃣ Disposable Check | Detects temp/throwaway email providers |
| 3️⃣ DNS Resolution | Domain exists and is reachable |
| 4️⃣ MX Records | Mail servers are properly configured |
| 5️⃣ SPF Record | Sender Policy Framework trust signal |
| 6️⃣ DKIM Signal | Domain Keys Identified Mail authentication |
| 7️⃣ Catch-All Detection | Identifies domains accepting all addresses |
| 8️⃣ SMTP Verification | Live check against the actual mail server |
| 9️⃣ Confidence Score | 0–100% score from all combined signals |

---

### 📊 Actionable Confidence Scoring

Every email returns a **confidence score**, not just pass/fail:

| Score | Meaning | Action |
|-------|---------|--------|
| 🟢 80–100% | High confidence — deliverable | Safe to send |
| 🟡 50–79% | Medium confidence | Review before campaign |
| 🔴 0–49% | Low confidence | Skip or investigate |

---

### ⚡ Parallel Batch Processing
- Validates **hundreds of emails simultaneously** using multi-threaded processing
- Real-time progress bar, live status table, and throughput metrics
- Automatically scales with available CPU cores

---

### 🖥️ Enterprise Desktop GUI
A modern, theme-aware desktop interface with:
- **Dark / Light / Ocean themes** — switch with one click
- **Dashboard** with live KPI cards (total validated, valid %, deliverable %, avg confidence)
- **Single Validation tab** — deep-dive results panel with color-coded signals
- **Batch Validation tab** — import file → validate → export in one flow
- **Reports tab** — full analytics summary with exportable report
- **Live Logs tab** — real-time validation event feed

---

### 📂 Universal Import + Same-Format Export
Import emails from any format:
- `.txt` plain list
- `.csv` spreadsheet
- `.xls` / `.xlsx` Excel files

Column mapper dialog auto-detects the email field. After validation, exports enriched results **back in the same file format** with appended columns:
- `validation_is_valid`
- `validation_deliverable`
- `validation_confidence`
- `validation_status`
- `validation_messages`

---

### 🔌 Multi-Interface Architecture

| Interface | Best For |
|-----------|---------|
| 🖥️ **Desktop GUI** | Business users, marketing teams |
| ⌨️ **CLI** | Automation scripts, ops pipelines |
| 🌐 **REST API** | Developer integrations, web apps |
| 🐍 **Python API** | Embedding in custom Python projects |

---

### 🛡️ Production-Friendly Behavior
- DNS result caching (avoids duplicate lookups)
- Built-in rate limiting (prevents IP blocks)
- Timeout handling on all network operations
- Structured logging with timestamps
- Robust exception handling at every layer

---

### 📦 Zero-Dependency EXE Distribution
- Ships as a single **self-contained `.exe`** (~65 MB)
- No Python installation needed
- No pip, no virtual environment, no setup
- Just double-click and run on any Windows machine

---

## 📁 Project Structure

```
UmaxBooks Email Validator/
├── gui_app.py               # Main desktop GUI (Tkinter)
├── email_validator.py       # Core 9-layer validation engine
├── advanced_email_validator.py  # Enhanced enterprise validation logic
├── parallel_processor.py    # Multi-threaded batch processing
├── advanced_reporter.py     # Analytics & report generation
├── domain_reputation.py     # Domain risk scoring
├── api_server.py            # Flask REST API server
├── cli_app.py               # Command-line interface
├── Power.png                # App logo
├── app_icon.ico             # Windows EXE icon
├── UmaxBooksEmailValidator.spec  # PyInstaller build spec
└── requirements.txt         # Python dependencies
```

---

## 🖥️ Installation & Usage

### Option 1 — Run the EXE (Recommended, No Python Needed)

> Download `PowerEmailValidation.exe` from [Releases](https://github.com/itsalexwilliam-pixel/UmaxBooks-Email-Validator/releases) and double-click. That's it.

---

### Option 2 — Run from Source (Python Required)

**Prerequisites:** Python 3.8+

```bash
# 1. Clone the repository
git clone https://github.com/itsalexwilliam-pixel/UmaxBooks-Email-Validator.git
cd UmaxBooks-Email-Validator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the GUI
python gui_app.py
```

---

### Option 3 — Command Line Interface

```bash
# Single email
python cli_app.py user@example.com

# With SMTP deep check
python cli_app.py user@example.com --smtp

# Bulk validation from file → save as CSV
python cli_app.py --bulk -i emails.txt -o results.csv

# Bulk with SMTP + JSON output
python cli_app.py --bulk --smtp -i emails.txt -o results.json
```

**CLI flags:**
| Flag | Description |
|------|-------------|
| `-b, --bulk` | Enable bulk mode |
| `-i, --input` | Input file path |
| `-o, --output` | Output file (`.csv`, `.json`, `.txt`) |
| `-s, --smtp` | Enable SMTP verification |
| `-t, --timeout` | Timeout in seconds |
| `-v, --verbose` | Show detailed output |

---

### Option 4 — REST API Server

```bash
python api_server.py
# Runs at http://localhost:5000
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Server health check |
| GET | `/api/info` | API capabilities |
| POST | `/api/validate` | Single email validation |
| POST | `/api/validate/batch` | Batch validation (up to 1000) |
| POST | `/api/analyze` | Full analytics report |
| POST | `/api/domains` | Domain grouping analysis |

```bash
# Example: validate a single email
curl -X POST http://localhost:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "check_smtp": true}'
```

---

### Option 5 — Python API (Embed in Your Code)

```python
from email_validator import EmailValidator

validator = EmailValidator(timeout=10)

# Single email
result = validator.validate_email("user@example.com", check_smtp=True)
print(f"Valid: {result['is_valid']}")
print(f"Confidence: {result['confidence']}%")
print(f"Deliverable: {result['deliverable']}")

# Bulk
emails = ["alice@example.com", "bob@company.org"]
results = validator.validate_bulk(emails, check_smtp=False)
for r in results:
    print(f"{r['email']} → {r['confidence']}% confident")
```

---

## 📤 Output Fields

Every validated email returns:

```json
{
  "email": "user@example.com",
  "is_valid": true,
  "deliverable": true,
  "confidence": 90,
  "syntax_valid": true,
  "domain_exists": true,
  "mx_records": ["mail.example.com"],
  "smtp_status": "accepted",
  "is_disposable": false,
  "is_catchall": false,
  "has_spf": true,
  "has_dkim": true,
  "messages": ["Syntax valid", "MX found", "SPF present", "SMTP accepted"],
  "validation_time": 1.84
}
```

---

## 🎯 Business Use Cases

| Use Case | How This Helps |
|----------|---------------|
| 📣 Email Marketing | Clean lists before campaigns — reduce bounce rate |
| 🗄️ CRM Hygiene | Periodic database quality audits |
| 🧲 Lead Generation | Verify collected leads before outreach |
| 📝 User Signup | Real-time validation in onboarding flows |
| ✅ Compliance | Data quality checks for ops & compliance teams |

---

## ⚠️ Important Notes

- **SMTP Verification** is optional — some mail servers block probing; enabling it is slower but more accurate
- **Catch-all domains** (e.g., custom business domains) may show 90% confidence even for non-existent mailboxes — this is expected behavior
- **Gmail/Yahoo** confidence is capped at 40–50% when SMTP probing is blocked by those providers
- All validation runs **locally** — no emails are sent to third parties

---

## 🔒 Privacy & Security

- ✅ No emails stored or sent to external servers
- ✅ All DNS/SMTP checks connect directly from your machine to mail servers
- ✅ No telemetry, no analytics collection
- ✅ Fully offline-capable (except DNS/SMTP checks which require internet)

---

## 🛠️ Build EXE from Source

```bash
# Install PyInstaller
pip install pyinstaller

# Build single-file EXE
pyinstaller UmaxBooksEmailValidator.spec
# Output: dist/PowerEmailValidation.exe
```

---

## 🤝 Contributing

Issues and pull requests are welcome! For major changes, open an issue first to discuss what you'd like to change.

---

## 👨‍💻 Built By

**UmaxBooks** — [umaxbooks.in](https://umaxbooks.in)

---

<div align="center">

**⚡ Validate smarter. Send better.**

</div>
