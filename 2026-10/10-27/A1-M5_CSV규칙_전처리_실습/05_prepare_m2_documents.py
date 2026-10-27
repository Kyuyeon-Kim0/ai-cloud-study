"""05. M2 규칙 원본 CSV와 트리를 그대로 사용해 RAG용 '미리보기'를 메모리에 만든다.

이 파일은 규칙을 변경하지 않으며 새 지식 CSV도 만들지 않는다.
검색 본문과 메타데이터를 구분한 dict를 반환한다.
"""
from __future__ import annotations
import csv
from pathlib import Path
from cleaner import clean_text, PREPROCESS_VERSION

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
TEXT_FIELDS = ("title", "description", "reason", "limitation")
META_FIELDS = ("rule_id", "rule_version", "status", "scope", "policy_id", "wcag_ref", "kwcag_ref", "reference_url", "effective_from")


def read_csv(filename: str) -> list[dict[str,str]]:
    if filename not in {"rules.csv", "rule_tree.csv"}:
        raise ValueError("허용되지 않은 파일")
    with (DATA / filename).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def tree_map() -> dict[str,dict[str,str]]:
    nodes = {r["node_id"]:r for r in read_csv("rule_tree.csv")}
    if len(nodes) != len(read_csv("rule_tree.csv")):
        raise ValueError("트리 노드 ID 중복")
    return nodes


def make_tree_path(node_id: str, nodes: dict[str,dict[str,str]]) -> str:
    parts = []
    seen = set()
    while node_id:
        if node_id in seen:
            raise ValueError("트리 부모 순환")
        seen.add(node_id)
        if node_id not in nodes:
            raise ValueError("존재하지 않는 부모 ID")
        node = nodes[node_id]
        parts.append(node["label"])
        node_id = node["parent_id"]
    return " > ".join(reversed(parts))


def prepare(*, include_proposed: bool = False) -> list[dict]:
    rows = read_csv("rules.csv")
    nodes = tree_map()
    if len({r["rule_id"] for r in rows}) != len(rows):
        raise ValueError("규칙 ID 중복")
    linked = {}
    for node in nodes.values():
        if node["node_type"] == "rule":
            if node["file"] != "rules.csv" or not node["rule_id"]:
                raise ValueError("트리 규칙 노드의 파일/규칙 ID 오류")
            if node["rule_id"] in linked:
                raise ValueError("규칙 ID에 트리 노드가 중복 연결")
            linked[node["rule_id"]] = node
    missing = set(linked) - {r["rule_id"] for r in rows}
    if missing:
        raise ValueError(f"트리에만 있는 규칙: {sorted(missing)}")

    documents = []
    for row in rows:
        if row["status"] != "applied" and not include_proposed:
            continue
        # M3와 같은 '필드명: 값' 서식을 사용한다. M3 규칙 원본은 변경하지 않는다.
        raw_text = "\n".join(f"{key}: {row[key]}" for key in TEXT_FIELDS if row[key])
        node = linked.get(row["rule_id"])
        metadata = {field: row[field] for field in META_FIELDS}
        metadata.update({
            "source_file": "rules.csv",
            "node_id": node["node_id"] if node else "",
            "parent_id": node["parent_id"] if node else "",
            "tree_path": make_tree_path(node["node_id"],nodes) if node else "",
            "preprocess_version": PREPROCESS_VERSION,
        })
        documents.append({
            "document_id": row["rule_id"],
            "raw_text": raw_text,
            "clean_text": clean_text(raw_text),
            "metadata": metadata,
        })
    return documents

if __name__ == "__main__":
    docs = prepare()
    print(f"적용 중 규칙 {len(docs)}건 (proposed 기본 제외)")
    for d in docs:
        print("\n규칙:",d["document_id"])
        print("원본:", repr(d["raw_text"][:85]))
        print("정제:", repr(d["clean_text"][:85]))
        print("메타데이터:", {k:d["metadata"][k] for k in ("rule_id","status","scope","preprocess_version","tree_path")})
