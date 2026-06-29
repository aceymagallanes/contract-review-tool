# 📑 AI Contract Risk Analyzer

A Python tool that reads contract PDFs and uses the Claude API to analyze each one like a contract risk analyst — scoring overall risk, flagging dangerous clauses in plain English, and exporting the results to JSON and a spreadsheet.

Built to show how AI can take a slow, expensive, expert task (legal contract review) and turn it into a fast, repeatable, automated workflow.

---

## ✨ What it does

- 📂 Reads **every PDF** in the `contracts/` folder and extracts the full text
- 🤖 Sends each contract to **Claude** (`claude-sonnet-4-5`) with a structured risk-analyst prompt
- 🎯 Returns a clean risk profile for each contract:
  - Overall **risk score (0–100)** and tier (Low / Medium / High)
  - A **plain-English summary** a non-lawyer can understand
  - Clause-by-clause findings (Termination, Liability, Indemnification, Auto-Renewal, IP, and more)
  - A list of the most serious **red flags**
  - The single **top recommendation**
- 💾 Saves results to **`results.json`** (full detail) and **`results.csv`** (one row per contract)
- 🛡️ Handles errors gracefully — if one PDF fails, the rest still process

---

## 🧪 Example output

Running the tool against a set of sample contracts produces a summary like this:

| Contract | Type | Risk Tier | Score | Risky Clauses | Red Flags |
|---|---|---|---|---|---|
| SaaS Standard | SaaS Agreement | 🟢 Low | 25 | 1 | 4 |
| Vendor (risky) | Master Vendor Services | 🔴 High | 92 | 7 | 7 |
| Mutual NDA | Non-Disclosure Agreement | 🟡 Medium | 45 | 3 | 5 |
| Consulting | Consulting Agreement | 🟢 Low | 25 | 0 | 0 |

> On the high-risk vendor contract, the tool correctly flagged a **$100 liability cap**, an **indemnity clause covering the vendor's own misconduct**, and a **24-month auto-renewal lock-in** — exactly the terms that cost businesses real money.

---

## 🚀 How to run it

### 1. Install the requirements
```bash
pip3 install -r requirements.txt
```

### 2. Add your Anthropic API key
Create a file named `.env` in the project folder (copy the format from `.env.example`):
```
ANTHROPIC_API_KEY=your_key_here
```
Get a key from [console.anthropic.com](https://console.anthropic.com). Your `.env` is git-ignored, so your key never gets committed.

### 3. Add contracts and run
Drop your PDF contracts into the `contracts/` folder, then:
```bash
python3 analyze_contracts.py
```

Results are written to `results.json` and `results.csv`.

---

## 🧰 Tech stack

- **Python 3**
- **[Anthropic Claude API](https://docs.anthropic.com/)** — the analysis engine
- **[pdfplumber](https://github.com/jsvine/pdfplumber)** — PDF text extraction
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** — secure key management

---

## 🔒 Security notes

- The `.env` file (your real API key) is **never** committed — it's listed in `.gitignore`.
- `.env.example` shows the required format without exposing any secret.
- The sample contracts in this repo are **fictional**, generated for testing.

---

## 💡 Possible extensions

- OCR support for scanned (image-only) PDFs
- A web dashboard to browse results
- Side-by-side comparison of multiple vendor contracts
- Email/Slack alerts when a High-risk contract is detected

---

*Built by Acey Magallanes — exploring AI automation for business and operations workflows.*
