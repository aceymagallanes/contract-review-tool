"""
analyze_contracts.py
--------------------
Reads every PDF contract in the ./contracts folder, sends each one to Claude
to be analyzed as a contract risk analyst, and saves the results to:
  - results.json  (full, detailed results)
  - results.csv   (one flattened row per contract, easy to open in Excel)

This file is written with lots of comments because you're learning Python.
Read it top to bottom — each section explains what it does and why.
"""

# ----------------------------------------------------------------------------
# SECTION 1: Imports
# These are the "toolboxes" we borrow code from instead of writing it ourselves.
# ----------------------------------------------------------------------------
import os          # lets us look at folders and file paths
import json        # lets us read/write JSON (the structured data format Claude returns)
import csv         # lets us write the flattened spreadsheet (CSV) file
import re          # "regular expressions" — used here to strip ```json fences
import sys         # lets us exit the program cleanly if something critical is missing

import pdfplumber                      # extracts text out of PDF files
from dotenv import load_dotenv         # loads your secret key from the .env file
from anthropic import Anthropic        # the official Claude API client


# ----------------------------------------------------------------------------
# SECTION 2: Configuration
# A few settings kept at the top so they're easy to find and change later.
# ----------------------------------------------------------------------------
CONTRACTS_FOLDER = "./contracts"               # where your PDFs live
RESULTS_JSON = "results.json"                   # detailed output file
RESULTS_CSV = "results.csv"                     # flattened spreadsheet output file
MODEL = "claude-sonnet-4-5-20250929"            # the Claude model we use
MAX_TOKENS = 4000                               # max length of Claude's reply


# ----------------------------------------------------------------------------
# SECTION 3: Load the API key securely
# We NEVER hardcode the key. load_dotenv() reads the hidden ".env" file and
# makes ANTHROPIC_API_KEY available via os.environ.
# ----------------------------------------------------------------------------
load_dotenv()  # reads ".env" in this folder, if present

api_key = os.environ.get("ANTHROPIC_API_KEY")

# If the key is missing, stop right away with a friendly message instead of
# crashing later with a confusing error.
if not api_key:
    print("ERROR: No API key found.")
    print("Create a file named '.env' in this folder containing:")
    print("    ANTHROPIC_API_KEY=your_real_key_here")
    print("(See .env.example for the exact format.)")
    sys.exit(1)  # exit code 1 means "stopped because of an error"

# Create the Claude client. This object is what we use to send requests.
client = Anthropic(api_key=api_key)


# ----------------------------------------------------------------------------
# SECTION 4: The prompt
# This is the instruction we send to Claude along with each contract's text.
# We're very strict about asking for ONLY valid JSON so we can parse it reliably.
# ----------------------------------------------------------------------------
def build_prompt(contract_name, contract_text):
    """Builds the full instruction string we send to Claude for one contract."""
    return f"""You are an experienced contract risk analyst. Analyze the contract below
and return ONLY valid JSON — no commentary, no markdown, no code fences — using EXACTLY
this structure:

{{
  "contract_name": "{contract_name}",
  "contract_type": "...",
  "overall_risk_score": 0,
  "risk_tier": "Low | Medium | High",
  "plain_english_summary": "2-3 sentence summary a business person can understand",
  "clauses": [
    {{
      "clause_type": "e.g. Limitation of Liability",
      "finding": "what the clause says, briefly",
      "risk_level": "Favorable | Neutral | Risky",
      "explanation": "why it matters in plain English",
      "recommendation": "what to do about it"
    }}
  ],
  "red_flags": ["list of the most serious issues"],
  "top_recommendation": "the single most important action"
}}

Rules:
- "overall_risk_score" is an integer from 0 (no risk) to 100 (extreme risk).
- "risk_tier" must be exactly one of: Low, Medium, High.
- Each clause "risk_level" must be exactly one of: Favorable, Neutral, Risky.
- Examine these clause types WHERE PRESENT: Termination, Limitation of Liability,
  Indemnification, Auto-Renewal, Fees/Payment, Confidentiality, IP Ownership,
  Exclusivity, Governing Law, and flag any unusual or non-standard terms.
- Keep explanations plain enough for a non-lawyer business owner to understand.
- Return valid JSON only. Do not wrap it in ```.

CONTRACT NAME: {contract_name}

CONTRACT TEXT:
\"\"\"
{contract_text}
\"\"\"
"""


# ----------------------------------------------------------------------------
# SECTION 5: Helper — read text out of a PDF
# pdfplumber opens the PDF, and we glue together the text from every page.
# ----------------------------------------------------------------------------
def extract_pdf_text(pdf_path):
    """Returns all text found in a PDF as one big string."""
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # extract_text() can return None for blank/image-only pages, so guard it
            text = page.extract_text() or ""
            pages_text.append(text)
    return "\n".join(pages_text)


# ----------------------------------------------------------------------------
# SECTION 6: Helper — clean Claude's reply
# Even when asked not to, models sometimes wrap JSON in ```json ... ``` fences.
# This strips those fences so json.loads() can parse the content.
# ----------------------------------------------------------------------------
def strip_code_fences(text):
    """Removes leading/trailing markdown code fences like ```json ... ```"""
    text = text.strip()
    # Remove an opening fence such as ``` or ```json (optionally followed by newline)
    text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
    # Remove a closing fence ``` at the very end
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


# ----------------------------------------------------------------------------
# SECTION 7: Helper — send one contract to Claude and get parsed JSON back
# ----------------------------------------------------------------------------
def analyze_contract(contract_name, contract_text):
    """Sends one contract to Claude and returns the analysis as a Python dict."""
    # Send the request to Claude.
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "user", "content": build_prompt(contract_name, contract_text)}
        ],
    )

    # Claude's text reply lives in response.content[0].text
    raw_reply = response.content[0].text

    # Clean off any markdown fences, then parse the JSON into a Python dict.
    cleaned = strip_code_fences(raw_reply)
    data = json.loads(cleaned)  # raises an error if the JSON is malformed

    # Make sure the contract_name is always correct, even if the model changed it.
    data["contract_name"] = contract_name
    return data


# ----------------------------------------------------------------------------
# SECTION 8: Helper — flatten one result into a single CSV row
# The JSON is nested; a spreadsheet needs flat columns. We summarize here.
# ----------------------------------------------------------------------------
def flatten_for_csv(result):
    """Turns one detailed result dict into a simple flat dict for the CSV."""
    clauses = result.get("clauses", []) or []
    red_flags = result.get("red_flags", []) or []

    # Count how many clauses Claude marked as "Risky"
    risky_count = sum(1 for c in clauses if c.get("risk_level") == "Risky")

    return {
        "contract_name": result.get("contract_name", ""),
        "contract_type": result.get("contract_type", ""),
        "overall_risk_score": result.get("overall_risk_score", ""),
        "risk_tier": result.get("risk_tier", ""),
        "risky_clause_count": risky_count,
        "red_flag_count": len(red_flags),
        "top_recommendation": result.get("top_recommendation", ""),
    }


# ----------------------------------------------------------------------------
# SECTION 9: Main program
# This is the part that actually runs everything in order.
# ----------------------------------------------------------------------------
def main():
    # 9a. Make sure the contracts folder exists.
    if not os.path.isdir(CONTRACTS_FOLDER):
        print(f"ERROR: Folder '{CONTRACTS_FOLDER}' does not exist.")
        print("Create it and put your PDF contracts inside, then run again.")
        sys.exit(1)

    # 9b. Find every PDF file in the folder (case-insensitive on ".pdf").
    pdf_files = [
        f for f in os.listdir(CONTRACTS_FOLDER)
        if f.lower().endswith(".pdf")
    ]
    pdf_files.sort()  # process them in a predictable, alphabetical order

    if not pdf_files:
        print(f"No PDF files found in '{CONTRACTS_FOLDER}'.")
        print("Add some .pdf contracts to that folder and run again.")
        sys.exit(0)

    print(f"Found {len(pdf_files)} PDF(s). Starting analysis...\n")

    results = []  # we'll collect every successful analysis here

    # 9c. Loop over each PDF, one at a time.
    for filename in pdf_files:
        pdf_path = os.path.join(CONTRACTS_FOLDER, filename)
        print(f"-> Processing: {filename}")

        # We wrap each contract in try/except so that if ONE fails,
        # the program keeps going with the rest instead of crashing.
        try:
            # Step 1: pull the text out of the PDF
            text = extract_pdf_text(pdf_path)

            # If the PDF had no extractable text (e.g. it's a scanned image),
            # warn and skip it — Claude can't analyze an empty string.
            if not text.strip():
                print(f"   ! Skipped: no readable text found (is it a scanned image?)\n")
                continue

            # Step 2: send it to Claude and get the structured analysis back
            result = analyze_contract(filename, text)

            # Step 3: print a clean one-line summary to the console
            tier = result.get("risk_tier", "Unknown")
            score = result.get("overall_risk_score", "?")
            print(f"   Risk tier: {tier}  |  Score: {score}/100\n")

            results.append(result)

        except json.JSONDecodeError:
            # This happens if Claude's reply wasn't valid JSON.
            print(f"   ! Skipped: Claude's response wasn't valid JSON.\n")
        except Exception as error:
            # Any other problem (bad PDF, network issue, etc.) lands here.
            print(f"   ! Skipped due to an error: {error}\n")

    # 9d. If nothing succeeded, there's nothing to save.
    if not results:
        print("No contracts were analyzed successfully. Nothing to save.")
        return

    # 9e. Save the full detailed results to results.json
    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # 9f. Save the flattened summary to results.csv
    fieldnames = [
        "contract_name",
        "contract_type",
        "overall_risk_score",
        "risk_tier",
        "risky_clause_count",
        "red_flag_count",
        "top_recommendation",
    ]
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(flatten_for_csv(result))

    # 9g. Final confirmation message.
    print("Done!")
    print(f"  - {len(results)} contract(s) analyzed")
    print(f"  - Detailed results saved to: {RESULTS_JSON}")
    print(f"  - Spreadsheet summary saved to: {RESULTS_CSV}")


# This line means: only run main() when you execute this file directly
# (not when it's imported as a module by another file).
if __name__ == "__main__":
    main()
