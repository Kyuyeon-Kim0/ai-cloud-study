# A1-M5: 텍스트 전처리 · 한국어 형태소 분석 · OOV

## 프로젝트 연결 원칙
- A1-M2의 `rules.csv`, `rule_tree.csv`를 **원본 그대로 복사**해 `data/`에서 재사용합니다.
- 원본 CSV는 절대 덮어쓰지 않습니다. 새 규칙 CSV/YAML/Git 이력 실습이 아닙니다.
- A1-M3에서 검색한 `title`, `description`, `reason`, `limitation`은 검색 본문이며,
  `rule_id`, `rule_version`, `status`, `scope`, `reference_url`, 트리 연결 등은 메타데이터로 유지합니다.
- `applied` 7건이 기본 대상이고 `proposed` 1건은 기본에서 제외합니다.
- 원본/정제본과 `preprocess_version`을 함께 관리하는 **메모리상의 미리보기**를 생성합니다.
- HF 토크나이저·임베딩·RAG 생성 코드는 A1-M5 범위에 포함하지 않습니다.

## Python 실행

```powershell
python 01_cleaning_basics.py
python 02_oov_and_units.py
python 05_prepare_m2_documents.py
python -m unittest discover -s tests -v
```

### 선택 실습

```powershell
python -m pip install kiwipiepy
python 03_kiwi_pos_optional.py
python 04_kiwi_dictionary_optional.py
```

Kiwi 분석 결과는 버전/사전에 따라 달라지므로 정해진 출력값을 외우지 않습니다.
Kiwi는 `add_user_word(word, tag, score)`를 지원합니다.
공식 참고: https://github.com/bab2min/kiwipiepy

### M3 검색 결과 전후 비교 (선택)

```powershell
python -m pip install scikit-learn
python 06_compare_m3_search_optional.py
```

검색 성능이 개선됐다고 단정하지 마세요. M4의 평가 질문·정답셋으로
다양한 질의에서 Recall@k/MRR을 비교하고, 규칙 ID·부정 표현 보존을 점검해야 합니다.

## 업무 시나리오
1. M2의 CSV 규칙을 작성하고 판정한다.
2. M3의 동일 CSV 검색 본문에 공백·유니코드·표기 차이가 생기는지 관찰한다.
3. M5에서는 텍스트 **복사본**에만 최소 정규화 적용, 원본과 식별자는 보존한다.
4. OOV가 발생한 업무 용어를 설명하고 형태소 분석기 사용자 사전 등록 필요성을 판단한다.
5. M6에서 규칙 검사/검색 통합 시 `preprocess_version`을 캐시·색인 버전의 일부로 검토한다.

© 2026 부성순. All rights reserved. W3C/Kiwi 등 외부 자료의 권리는 각각의 권리자에게 있습니다.
