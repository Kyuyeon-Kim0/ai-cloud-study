# 사람 세그멘테이션 + Streamlit 히스토그램 + GPT

## 파일
- `app.py`: 실시간 웹캠, PyTorch 세그멘테이션, 배경 합성, S 캡처, 히스토그램, GPT 질의응답
- `back.jpg`: 원하는 배경 사진을 직접 넣으세요 (파일이 없으면 원본 프레임 표시)
- `.env.example`: `.env`로 복사하여 GPT API 키 입력
- `captures/`: 캡처 이미지를 자동 저장

## Windows PowerShell 실행
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# .env 파일을 열어 GPT_API_KEY를 설정
streamlit run app.py
```

## 사용 방법
1. 브라우저에서 `Start` 버튼을 누르고 카메라 사용을 허용합니다.
2. **S 키 입력** 칸을 클릭하고 `S`를 누르거나 **현재 프레임 저장** 버튼을 누릅니다.
3. 오른쪽에 캡처가 표시되고 `captures/`에 PNG가 저장됩니다.
4. 아래 히스토그램을 보고 **GPT로 히스토그램 요약하기** 또는 채팅 입력창을 사용합니다.

## 주의
- 브라우저 키보드 입력 제약으로 S 단축키는 **S 키 입력 칸에 포커스가 있을 때** 작동합니다. 저장 버튼은 언제나 사용할 수 있습니다.
- 첫 실행 때 PyTorch 모델 가중치를 다운로드합니다.
- DeepLabV3-ResNet50은 무거운 모델로 CPU에서 프레임 속도가 낮을 수 있습니다.
- GPT에는 사진 픽셀 자체를 보내지 않고 히스토그램의 통계 요약만 보냅니다. 물체/장면 의미는 알 수 없습니다.
- 원격 접속 시 카메라 접근을 위해 HTTPS가 필요할 수 있습니다. 로컬 localhost는 보통 사용 가능합니다.
- `.env`를 Git에 올리지 마세요.
