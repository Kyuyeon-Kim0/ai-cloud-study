# OWLv2 개방형 어휘 객체 탐지

Hugging Face Transformers의 OWLv2 모델로 이미지에서 텍스트로 지정한 항목을 찾는 예제입니다. 일반적인 고정 클래스 분류와 달리, 코드의 `texts` 목록에 탐지할 대상을 문장으로 지정합니다.

## 폴더 구성

```text
owlv2_object_detection/
├── work/
│   ├── run_owlv2.py       # 모델 실행 및 탐지 결과 저장
│   └── coco_sample.jpg    # 실행 시 URL에서 다운로드되는 입력 이미지
├── outputs/
│   ├── owlv2_detections.json  # 탐지 결과와 경계 상자 좌표
│   └── owlv2_annotated.png    # 탐지 상자를 그린 이미지
└── README.md
```

## 설치

PowerShell에서 `owlv2_object_detection` 폴더로 이동해 필요한 패키지를 설치합니다.

```powershell
python -m pip install torch transformers pillow requests
```

## 실행

```powershell
python work/run_owlv2.py
```

처음 실행할 때 입력 이미지와 OWLv2 모델 파일을 인터넷에서 다운로드합니다. 모델이 커서 다운로드와 첫 실행에 시간이 걸릴 수 있습니다.

## 탐지 대상 바꾸기

`work/run_owlv2.py`의 `texts` 목록을 수정합니다. 현재 예제는 얼굴, 로켓, NASA 배지, 성조기를 탐지하도록 설정되어 있습니다.

```python
texts = [["human face", "rocket", "nasa badge", "star-spangled banner"]]
```

## 결과

- `outputs/owlv2_detections.json`: 탐지한 항목, 점수, 경계 상자 좌표를 저장합니다. `threshold=0.1` 기준의 결과가 기록됩니다.
- `outputs/owlv2_annotated.png`: 점수가 `0.3` 이상인 항목의 상자를 표시한 이미지입니다.
- `work/coco_sample.jpg`: 실행할 때 지정된 URL에서 다시 내려받는 입력 이미지입니다.

경계 상자 좌표는 `[왼쪽, 위쪽, 오른쪽, 아래쪽]` 순서의 픽셀 좌표입니다. 탐지 결과는 모델의 추정이며, 점수가 낮거나 이미지에 따라 틀릴 수 있습니다.
