# Contract Risk Intelligence

A Python contract-review tool with an interactive dashboard.

It reads contract PDFs, sends the extracted text to Claude, scores each contract for business risk, flags risky clauses, and saves the output to JSON and CSV.

Then the dashboard turns those results into a clear executive view.

Know the risk before you sign.

---

## What This Project Does

- Reads every PDF inside the `contracts/` folder.
- Extracts contract text with `pdfplumber`.
- Sends each contract to the Claude API for structured risk analysis.
- Produces detailed results in `results.json`.
- Produces a spreadsheet summary in `results.csv`.
- Shows the results in a single-page dashboard: `index.html`.
- Keeps API keys private through `.env` and `.gitignore`.

---

## Dashboard

The dashboard is built as one self-contained HTML file:

`index.html`

It loads:

- `results.csv` for the contract register and KPI counts.
- `results.json` for detailed summaries, red flags, and clause-level findings.

Dashboard views include:

- Executive summary
- Risk distribution
- Priority contracts
- Recurring risk areas
- Full contract register
- Contract detail drawer

Risk tiers are standardized and transparent:

```text
Low    0-39
Medium 40-69
High   70-100
```

The dashboard also derives the displayed tier from the score, so the visual counts stay consistent with the data.

---

## Risk-Tier Logic

The risk score comes from Claude's contract analysis.

The final risk tier is controlled by Python.

This means the model does not decide the final tier label. The script applies fixed thresholds after the score is returned:

```python
Low    = 0-39
Medium = 40-69
High   = 70-100
```

This keeps `results.json`, `results.csv`, and the dashboard aligned.

Current reconciled sample counts:

| Tier | Count |
|---|---:|
| Low | 7 |
| Medium | 11 |
| High | 7 |
| Total | 25 |

---

## Files

| File | Purpose |
|---|---|
| `analyze_contracts.py` | Main Python script that extracts text, calls Claude, applies risk-tier thresholds, and writes outputs |
| `index.html` | Interactive dashboard for reviewing the results |
| `results.json` | Full detailed analysis for each contract |
| `results.csv` | Flattened spreadsheet summary |
| `requirements.txt` | Python dependencies |
| `.env.example` | Shows the required API key format |
| `.gitignore` | Keeps `.env`, virtual environments, and cache files out of Git |
| `contracts/` | Folder for PDF contracts |

---

## Requirements

You need:

- Python 3
- An Anthropic API key
- Contract PDFs

Install the Python packages:

```bash
pip3 install -r requirements.txt
```

---

## Add Your API Key

Create a file named `.env` in the project folder:

```text
ANTHROPIC_API_KEY=your_key_here
```

Replace `your_key_here` with your real Anthropic key.

Do not commit `.env`.

It is already ignored by Git.

---

## Run The Contract Analyzer

Place PDF contracts in:

```text
contracts/
```

Then run:

```bash
python3 analyze_contracts.py
```

The script will create or update:

```text
results.json
results.csv
```

---

## Run The Dashboard Locally

Because the dashboard loads local CSV and JSON files, open it through a local server.

From the project folder:

```bash
python3 -m http.server 8011
```

Then open:

```text
http://localhost:8011/index.html
```

Do not double-click `index.html`.

Most browsers block local file loading from `file://`.

---

## Security Notes

- The real API key belongs only in `.env`.
- `.env` is ignored by Git.
- `.env.example` shows the format without exposing secrets.
- Sample contracts are fictional and used for testing.

---

## Current Status

This project includes:

- A working Python analyzer
- Standardized risk-tier logic
- Reconciled JSON and CSV outputs
- A polished single-page dashboard
- 25 sample contracts for testing

Built by Acey Magallanes as a practical AI automation portfolio project.
