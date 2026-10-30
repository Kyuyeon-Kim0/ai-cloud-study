# A3-M1 토크나이저와 유사도 실습 폴더

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate  /  macOS·Linux: source .venv/bin/activate
pip install -r requirements.txt
python make_corpus.py
```
노트북은 01 → 06 순서로 실행합니다. 03·05는 02에서 만든 `shop_wordpiece.json`을 씁니다.
06의 OpenAI 셀은 이 폴더의 `.env`에 `OPENAI_API_KEY=...`가 있어야 합니다.
