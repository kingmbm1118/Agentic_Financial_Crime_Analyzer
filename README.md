# Saudi Bank Fraud Detection System
## نظام كشف الاحتيال للبنوك السعودية

AI-powered fraud detection with explainable reasoning and SAMA compliance.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the system
python main.py
```

**That's it!** Check `reports/` folder for Word documents and text files.

---

## 📊 System Flow

```
Transaction → AI Analysis → Team Review → Investigation → Reports
   (SAR)      (Classify)    (Decision)   (Deep Check)  (Word+Text)
```

### Complete Flow Explanation

#### **Step 1: Transaction Monitoring**
- Bank's SAS system detects transaction
- Calculates ML fraud score (0-1)
- Flags anomalies (amount, location, time)
- **Example**: Mohammed Ahmed transfers 25,000 SAR to UAE at 2:30 AM

#### **Step 2: AI Alerting Agent** (LLaMA)
- Analyzes transaction with AI
- Checks: amount, time, country, customer history
- **Classifies as**: FLAGGED / INVESTIGATE / NON_FRAUD
- Provides explainable reasoning
- **Example**: "FLAGGED - Amount 12.5x above average, unusual time"

#### **Step 3: Monitoring Agent**
- Reviews AI classification
- **Decides**: CREATE_CASE / CLOSE / REQUEST_MORE_INFO
- Assigns priority (HIGH/MEDIUM/LOW)
- **Example**: "Create case CASE_00000001 - HIGH priority"

#### **Step 4: Investigator Agent**
- Deep analysis using multiple sources:
  - Customer profile (KYC, PEP, nationality)
  - Login history (countries, devices, 2FA)
  - Device fingerprints (trusted/suspicious)
  - Transaction patterns
- **Final decision**: CONFIRMED_FRAUD / SUSPECTED_FRAUD / LEGITIMATE
- **Example**: "SUSPECTED_FRAUD - Contact customer for verification"

#### **Step 5: Report Generation**
Two types created automatically:
- **Word Document** (.docx): Professional case report with SAMA compliance
- **Text File** (.txt): Quick reference report

---

## 🇸🇦 Saudi-Specific Features

### Data
- **Currency**: SAR (Saudi Riyal)
- **Customer IDs**: SA00000123 format
- **Names**: Arabic names (Mohammed Ahmed, Abdullah Khalid, etc.)
- **Cities**: Riyadh, Jeddah, Mecca, Medina, Dammam, Khobar
- **Countries**: Saudi Arabia, UAE, Kuwait, Bahrain, Qatar (GCC focus)

---

## 🎯 Usage Examples

```bash
# Basic run (50 transactions)
python main.py

# Process 100 transactions
python main.py --num-transactions 100 --batch-size 20

# Use existing data
python main.py --skip-data-generation

# Use different model (no approval needed)
python main.py --model microsoft/Phi-3-mini-4k-instruct
```

---

## 🔧 Customization

### Change Bank Name
Edit `agentic_orchestrator.py` line 48:
```python
self.word_report_generator = WordReportGenerator(
    bank_name="Your Bank Name Here"
)
```

### Add Bank Logo
```python
self.word_report_generator = WordReportGenerator(
    bank_name="Your Bank Name",
    bank_logo_path="assets/logo.png"
)
```

### Adjust AML Threshold
Edit `data_generator.py` line 97:
```python
'sama_aml_flag': amount > 50000,  # Change threshold
```

### Modify Risk Countries
Edit `data_generator.py` line 30:
```python
self.risk_countries = ['Iran', 'Yemen', 'Your Countries']
```

---

## ⚙️ System Requirements

**Minimum**:
- 8GB RAM
- 10GB storage
- Any modern CPU

**Recommended**:
- NVIDIA GPU 6GB+ VRAM
- 16GB RAM
- CUDA 11.8+

---

## 🎯 Key Features

● Saudi Bank Fraud Detection System - Simple Explanation

  What is this system?

  This is an AI-powered system that helps Saudi banks detect fraudulent money transfers automatically. Think of it
  as a smart assistant that reviews every transfer and flags suspicious ones for investigation.

  ---
  How does it work? (Step by step)

  1. Transfer Happens

  - Customer initiates a money transfer (e.g., 50,000 SAR to UAE)
  - System receives the transfer details: amount, beneficiary, country, etc.

  2. AI Analysis (Happens in seconds)

  The system uses 3 AI agents working together:

  Agent 1: Alert Agent

  - Reviews the transfer
  - Checks: Is the amount unusual? Is the country risky? Is the beneficiary new?
  - Decision: FLAGGED (high risk) / INVESTIGATE (medium risk) / NON_FRAUD (safe)

  Agent 2: Monitoring Agent

  - Reviews Agent 1's decision
  - Decision:
    - If suspicious → Creates a case for investigation
    - If safe → Closes automatically

  Agent 3: Investigator Agent

  - Deep analysis if case is created
  - Checks multiple sources:
    - Customer profile (KYC, previous fraud history)
    - Login history (which countries, devices used)
    - Device fingerprints (trusted/suspicious devices)
    - Transfer patterns
  - Final Decision: CONFIRMED_FRAUD / SUSPECTED_FRAUD / LEGITIMATE

  3. Reports Generated

  - Word Document (.docx) - Professional case report for managers
  - Text Report (.txt) - Quick reference
  - Both include:
    - Why it was flagged
    - What was checked
    - Recommended actions

  ---
  Real Example

  Transfer: Ahmed transfers 45,000 SAR to Syria at 2 AM

  AI Analysis:
  1. ✅ Amount is 10x his average (red flag)
  2. ✅ Syria is high-risk country (red flag)
  3. ✅ Transfer at 2 AM unusual time (red flag)
  4. ✅ Customer's KYC not verified (red flag)

  Result: FLAGGED → Case created → Investigation → SUSPECTED_FRAUD

  Action: Block transfer, contact customer, verify identity
