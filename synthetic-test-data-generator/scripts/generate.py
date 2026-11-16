#!/usr/bin/env python3
"""Generate reproducible, obviously fake test data (standard library only).

Examples:
  python generate.py --entity users --count 50 --locale IN --seed 42 --format csv
  python generate.py --entity orders --count 20 --seed 7 --format json
  python generate.py --entity users --count 20 --with-edge-cases
"""
import argparse
import csv
import io
import json
import random
import sys
from datetime import datetime, timedelta

FIRST = ["Aarav", "Diya", "Kabir", "Meera", "Rohan", "Sara", "Arjun", "Zoya", "Ishaan", "Anaya",
         "Liam", "Emma", "Noah", "Olivia", "Lucas", "Mia"]
LAST = ["Sharma", "Khan", "Iyer", "Patel", "Reddy", "Das", "Nair", "Singh", "Smith", "Garcia", "Brown", "Lee"]
CITIES = {"IN": [("Bengaluru", "KA", "560"), ("Mumbai", "MH", "400"), ("Delhi", "DL", "110"), ("Pune", "MH", "411"),
                 ("Hyderabad", "TS", "500"), ("Chennai", "TN", "600")],
          "US": [("Austin", "TX", "787"), ("Denver", "CO", "802"), ("Seattle", "WA", "981"), ("Boston", "MA", "021")]}
PHONE = {"IN": "+91 00000 {:05d}", "US": "+1 555-01{:02d}"}  # all-zero / 555-01xx fictional ranges
CURRENCY = {"IN": "INR", "US": "USD"}
PRODUCTS = ["Oak Bed", "Fabric Sofa", "Study Table", "Office Chair", "Wardrobe", "Bookshelf", "Dining Set", "TV Unit"]
STATUSES = ["created", "paid", "shipped", "delivered", "cancelled"]

EDGE_NAMES = ["A", "Anne-Marie O'Neil", "José Núñez", "मोहम्मद", "X" * 50]
EDGE_EMAILS = ["a+filter@example.com", "first.last@sub.example.org", ("x" * 64) + "@example.com"]
NEGATIVE = [("", "not-an-email", "abc"), ("   ", "two@@example.com", "123"), ("<script>alert(1)</script>", "trailing.@example.com", "+91 12")]


def users(rng, count, locale, edge):
    rows = []
    for i in range(1, count + 1):
        first, last = rng.choice(FIRST), rng.choice(LAST)
        city, state, pin = rng.choice(CITIES[locale])
        row = {
            "id": f"TEST-U{i:05d}",
            "case_type": "valid",
            "name": f"{first} {last}",
            "email": f"{first.lower()}.{last.lower()}.{i}@example.com",
            "phone": PHONE[locale].format(i % (100000 if locale == "IN" else 100)),
            "city": city,
            "state": state,
            "postcode": f"{pin}{rng.randint(0, 999):03d}" if locale == "IN" else f"{pin}{rng.randint(0, 99):02d}",
            "created_at": (datetime(2026, 1, 1) + timedelta(minutes=rng.randint(0, 400000))).isoformat(timespec="seconds"),
        }
        rows.append(row)
    if edge:
        for j, name in enumerate(EDGE_NAMES):
            r = dict(rows[j % len(rows)]); r.update(id=f"TEST-UE{j:03d}", case_type="boundary", name=name,
                                                    email=EDGE_EMAILS[j % len(EDGE_EMAILS)])
            rows.append(r)
        for j, (name, email, phone) in enumerate(NEGATIVE):
            r = dict(rows[j % len(rows)]); r.update(id=f"TEST-UN{j:03d}", case_type="negative", name=name, email=email, phone=phone)
            rows.append(r)
    return rows


def products(rng, count, locale):
    return [{"id": f"TEST-P{i:04d}", "case_type": "valid", "name": f"{rng.choice(PRODUCTS)} {i}",
             "price": round(rng.randint(5, 300) * 100.0, 2), "currency": CURRENCY[locale],
             "stock": rng.choice([0, 0, 1, 5, 20, 100])} for i in range(1, count + 1)]


def orders(rng, count, locale):
    catalogue = products(rng, 20, locale)
    out = []
    for i in range(1, count + 1):
        lines = []
        for k in range(rng.randint(1, 4)):
            p = rng.choice(catalogue)
            qty = rng.randint(1, 3)
            lines.append({"line": k + 1, "product_id": p["id"], "unit_price": p["price"], "quantity": qty,
                          "amount": round(p["price"] * qty, 2)})
        created = datetime(2026, 1, 1) + timedelta(minutes=rng.randint(0, 400000))
        status = rng.choice(STATUSES)
        out.append({
            "id": f"TEST-O{i:05d}", "case_type": "valid", "user_id": f"TEST-U{rng.randint(1, max(1, count)):05d}",
            "status": status, "currency": CURRENCY[locale],
            "total": round(sum(l["amount"] for l in lines), 2),  # always equals the sum of lines
            "created_at": created.isoformat(timespec="seconds"),
            "updated_at": (created + timedelta(hours=rng.randint(1, 72))).isoformat(timespec="seconds"),
            "lines": lines,
        })
    return out


def to_csv(rows):
    flat = [{k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in r.items()} for r in rows]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(flat[0].keys()))
    w.writeheader()
    w.writerows(flat)
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entity", choices=["users", "orders", "products"], required=True)
    ap.add_argument("--count", type=int, default=20)
    ap.add_argument("--locale", choices=list(CITIES), default="IN")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--format", choices=["csv", "json"], default="csv")
    ap.add_argument("--with-edge-cases", action="store_true", help="add boundary and negative user records")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    if a.entity == "users":
        rows = users(rng, a.count, a.locale, a.with_edge_cases)
    elif a.entity == "orders":
        rows = orders(rng, a.count, a.locale)
    else:
        rows = products(rng, a.count, a.locale)
    sys.stdout.write(json.dumps(rows, indent=2, ensure_ascii=False) + "\n" if a.format == "json" else to_csv(rows))


if __name__ == "__main__":
    main()
