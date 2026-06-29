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

## ✅ Before you start (prerequisites)

You'll need three things:

1. **Python 3** installed — check by running `python3 --version` in a terminal. (Don't have it? Download from [python.org](https://www.python.org/downloads/).)
2. **An Anthropic API key** — sign up at [console.anthropic.com](https://console.anthropic.com) → **Settings → API Keys → Create Key**. (The analysis runs on Anthropic's paid API — typically a fraction of a cent per contract.)
3. **The contracts you want analyzed**, as PDF files.

> **Note:** This is a standalone command-line tool. You do **not** need the Claude Code app to run it — only Python and an API key.

---

## 🚀 How to run it

### 1. Download the project
Click the green **Code** button above → **Download ZIP**, then unzip it. (Or `git clone` it if you use git.)

Open a terminal **inside the project folder**:
```bash
cd path/to/contract-review-tool
```

### 2. Install the requirements
```bash
pip3 install -r requirements.txt
```
This installs the three libraries the tool needs (`anthropic`, `pdfplumber`, `python-dotenv`).

### 3. Add your Anthropic API key
Create a file named `.env` in the project folder (copy the format from `.env.example`):
```
ANTHROPIC_API_KEY=your_key_here
```
Replace `your_key_here` with your real key (it starts with `sk-ant-`). Your `.env` is git-ignored, so your key never gets committed or shared.

### 4. Add your contracts
Drop your PDF contracts into the **`contracts/`** folder. You can add as many as you like — the tool reads every PDF in there.

### 5. Run it
```bash
python3 analyze_contracts.py
```

You'll see live progress in the terminal:
```
-> Processing: vendor_agreement.pdf
   Risk tier: High  |  Score: 92/100
```

When it finishes, two result files appear in the folder:
- **`results.json`** — full detail (every clause, red flag, and recommendation)
- **`results.csv`** — one row per contract; opens in Excel, Numbers, or Google Sheets

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `No API key found` | Make sure the file is named exactly `.env` (not `.env.txt`) and contains `ANTHROPIC_API_KEY=...` |
| `No PDF files found` | Put your `.pdf` files inside the `contracts/` folder, then run again |
| A contract is "Skipped: no readable text" | That PDF is a scanned image. It needs OCR (a planned future feature) |
| `externally-managed-environment` error on install | Use a virtual environment: `python3 -m venv venv && source venv/bin/activate`, then re-run the install |
| `command not found: python3` | Python isn't installed — get it from [python.org](https://www.python.org/downloads/) |

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
