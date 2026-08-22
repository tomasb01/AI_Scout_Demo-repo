"""Underwriting risk scoring experiment.

Analyzes client transaction history with a LOCAL model (Ollama) —
financial data never leaves our infrastructure.
"""

import csv
import json
from pathlib import Path

import ollama

MODEL = "qwen2.5-coder:7b"

PROMPT_TEMPLATE = (
    "You are a risk analyst. Given this client's financial profile, "
    "return a JSON object with fields risk_band (low/medium/high) and "
    "reasons (list of short strings).\n\nProfile:\n{profile}"
)


def load_profiles(path: str) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def score(profile: dict) -> dict:
    # profile contains: iban, account_balance, monthly_income, transactions
    response = ollama.generate(
        model=MODEL,
        prompt=PROMPT_TEMPLATE.format(profile=json.dumps(profile)),
        format="json",
    )
    return json.loads(response["response"])


def main() -> None:
    profiles = load_profiles(str(Path(__file__).parent / "clients.csv"))
    results = [{"iban": p["iban"], **score(p)} for p in profiles]
    out = Path(__file__).parent / "risk_bands.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"Scored {len(results)} clients -> {out}")


if __name__ == "__main__":
    main()
