#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json


def parse_amount(value):
    """Amounts are normally JSON numbers, but some exports quote them with
    thousands separators, e.g. "3,218.81"."""
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace(",", "").strip())


# A payment may be attempted several times; only the latest attempt counts.
latest = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(event, dict):
            continue
        txn_id = event.get("txn_id")
        if not txn_id:
            continue
        # Keep the most recent attempt for this txn_id.
        if txn_id not in latest or event["ts"] > latest[txn_id]["ts"]:
            latest[txn_id] = event

total = 0.0
count = 0
for event in latest.values():
    if event["status"] == "success":
        total += parse_amount(event["amount"])
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
