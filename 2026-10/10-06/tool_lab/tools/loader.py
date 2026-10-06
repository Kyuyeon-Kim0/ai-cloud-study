import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "sales.csv"

def load_rows(path: str | None = None) -> list[dict]:
    """CSV를 읽어 숫자 열을 변환한 뒤 리스트로 돌려준다."""
    target = Path(path) if path else DATA
    rows = []
    with open(target, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["quantity"] = int(row["quantity"])
            row["price"] = float(row["price"])
            row["amount"] = row["quantity"] * row["price"]
            rows.append(row)
    return rows

# import json
# from datetime import datetime
# from decimal import Decimal

# json.dumps({"now": datetime.now()})     # TypeError
# json.dumps({"price": Decimal("10.5")})  # TypeError
# json.dumps({"now": datetime.now().isoformat()})
# json.dumps({"price": float(Decimal("10.5"))})
