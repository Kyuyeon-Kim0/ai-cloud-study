# A3-M2 FAISS 실습 폴더

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate  /  macOS·Linux: source .venv/bin/activate
pip install -r requirements.txt
```
노트북은 01 → 09 순서로 실행합니다. 모든 노트북은 이 폴더 안에서 실행해야 `shop_faq.py`, `embedder.py`를 찾습니다.
`embedder.py`는 처음 실행할 때 `intfloat/multilingual-e5-small`을 내려받고, 실패하면 글자 n-gram 방식으로 대신 계산합니다.
다시 처음부터 하려면 `store/` 폴더를 지웁니다.
