"""06. 선택형 비교: M3 검색기를 그대로 재사용해 전처리 전/후 순위를 비교한다.

성능 향상을 보장하지 않는다. M4 정답셋과 평가 코드는 변경하지 않는다.
설치: python -m pip install scikit-learn
"""
from search_engine import build_documents, rank_tfidf, SearchDoc
from cleaner import clean_text

query = "  링크   목적   확인  "
original = build_documents()
normalized = [SearchDoc(d.document_id,clean_text(d.text),d.metadata.copy()) for d in original]
for name,q,docs in [("원문", query, original),("정제 후", clean_text(query), normalized)]:
    print("\n",name)
    for doc,score in rank_tfidf(q,docs,top_k=3):
        print(doc.document_id, f"{score:.4f}")
print("원문/정제본의 유사도와 순위가 같거나 달라질 수 있습니다.")
