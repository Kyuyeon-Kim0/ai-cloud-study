import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent

def make_report(source: Path, destination: Path, min_total: int = 0) -> int:
    """입력 CSV를 수정하지 않고, 주문 금액을 계산해 결과 CSV로 저장한다."""
    if min_total < 0:
        raise ValueError("최소 금액은 음수일 수 없습니다")
    with source.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("주문 데이터가 비어 있습니다")

    seen = set()
    result = []
    for row in rows:
        order_id = row["order_id"].strip()
        if not order_id or order_id in seen:
            raise ValueError("주문 ID가 비어 있거나 중복되었습니다")
        seen.add(order_id)
        quantity, unit_price = int(row["quantity"]), int(row["unit_price"])
        if quantity <= 0 or unit_price < 0:
            raise ValueError("수량 또는 단가가 유효하지 않습니다")
        total_amount = quantity * unit_price
        if total_amount >= min_total:
            result.append({"order_id": order_id, "product": row["product"],
                           "quantity": quantity, "unit_price": unit_price,
                           "total_amount": total_amount})

    destination.parent.mkdir(parents=True, exist_ok=True)
    fields = ["order_id", "product", "quantity", "unit_price", "total_amount"]
    with destination.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result)
    return len(result)

if __name__ == "__main__":
    count = make_report(BASE / "orders.csv", BASE / "output" / "report.csv")
    print(f"보고서 {count}건 생성: output/report.csv")