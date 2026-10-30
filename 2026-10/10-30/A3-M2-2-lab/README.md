# A3-M2-2: FAQ 검색과 RAG 평가 실습

쇼핑몰 FAQ 데이터를 임베딩하고 FAISS로 검색한 뒤, 검색 품질을 평가하고 리랭커를 적용해 보는 실습 자료입니다. 노트북은 **01 → 02 → 03** 순서로 실행합니다. `04_실습과제.ipynb`는 02번 노트북 실행 후 진행합니다.

## 파일 안내

| 파일 | 설명 |
|---|---|
| `01_데이터와_임베딩.ipynb` | FAQ CSV 확인, 문서 텍스트 생성, 임베딩 및 코사인 유사도 확인 |
| `02_FAISS_검색과_메타데이터.ipynb` | FAISS 검색, 카테고리 필터, 검색기 저장 및 재로드 |
| `03_RAG평가와_리랭킹.ipynb` | Hit@1·Hit@3·MRR 평가, 답변 보류 기준, 프롬프트 구성, 리랭킹 비교 |
| `04_실습과제.ipynb` | 카테고리 필터·리랭킹 후보 수·평가 데이터 확장 과제 |
| `shop_faq.csv` | 실습용 FAQ 데이터 |
| `shop_faq_tests.csv` | 검색 평가 질문과 정답 FAQ ID |
| `emb.py` | 임베딩 및 모델 설정 함수 |
| `faq_vectors.npy` | 01번 노트북에서 생성하는 FAQ 임베딩 배열 (현재 폴더에 포함) |
| `faq_store/` | 02번 노트북에서 생성하는 FAISS 인덱스, 메타데이터, 설정 정보 |

## 환경 준비

Python 3.10 이상을 권장합니다. 가상 환경을 만든 뒤 필요한 패키지를 설치하세요.

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

```bash
python -m pip install --upgrade pip
python -m pip install jupyterlab pandas numpy faiss-cpu transformers torch
```

JupyterLab을 실행합니다.

```bash
jupyter lab
```

## 실습 순서

1. `01_데이터와_임베딩.ipynb`의 셀을 위에서 아래로 실행합니다. `faq_vectors.npy`를 저장합니다.
2. `02_FAISS_검색과_메타데이터.ipynb`를 실행합니다. `faq_store/` 아래에 검색 인덱스와 메타데이터가 생성됩니다.
3. `03_RAG평가와_리랭킹.ipynb`를 실행해 검색 성능과 리랭킹 결과를 비교합니다.
4. 선택 과제로 `04_실습과제.ipynb`를 실행합니다.

노트북과 데이터 파일은 같은 작업 폴더에서 실행해야 합니다. 최초 임베딩/리랭킹 모델 사용 시 Hugging Face에서 모델을 내려받으므로 네트워크 연결이 필요하며, 처음 실행은 시간이 걸릴 수 있습니다. 기본 모델은 `emb.py`에 설정되어 있습니다.

## 모델 설정

환경 변수로 모델을 바꿀 수 있습니다. 모델을 바꾸면 기존 임베딩 및 FAISS 인덱스와 호환되지 않을 수 있으므로, 이 경우 01번과 02번 노트북을 다시 실행하세요.

```bash
# 기본값: intfloat/multilingual-e5-small
EMB_MODEL=intfloat/multilingual-e5-small

# 기본값: cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
RERANK_MODEL=cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
```

Windows PowerShell에서는 `$env:EMB_MODEL = "모델명"` 형식으로 설정할 수 있습니다.

## 참고

- 임베딩은 E5 입력 규칙에 따라 검색어에 `query:`, FAQ 문서에 `passage:` 접두사를 붙입니다.
- 벡터를 L2 정규화한 뒤 FAISS 내적 검색을 사용하므로 내적 점수는 코사인 유사도와 같습니다.
- 03번 노트북은 생성형 LLM을 호출하지 않습니다. 검색 결과를 바탕으로 LLM에 전달할 프롬프트 형식을 만드는 단계까지 다룹니다.
