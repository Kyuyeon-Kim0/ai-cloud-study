#이미지를 어떻게 빌드할지 정의
# 1. 파이썬 기초 환경 (반드시 이게 1번 줄이어야 합니다)
FROM python:3.10-slim

# 2. 작업 공간 설정
WORKDIR /app

# 3. 라이브러리 목록 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 현재 폴더의 모든 파일 복사 (json, py 파일 포함)
# .dockerignore가 venv310 폴더를 자동으로 걸러줄 겁니다.
COPY . .

# 5. 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]