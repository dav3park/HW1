# 1. Base Image: 슬림 버전을 사용해 불필요한 OS 패키지 최소화
FROM python:3.10-slim

# 2. 필수 시스템 패키지만 설치 후 캐시 삭제 (OpenCV 동작에 필요한 라이브러리 포함)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 의존성 파일만 먼저 복사 (Docker 빌드 캐시를 활용해 재빌드 속도 단축)
COPY requirements.txt .

# 5. 캐시 없이 의존성 설치 (이미지 용량 증가 방지)
RUN pip install --no-cache-dir -r requirements.txt

# 6. 비로소 소스 코드를 복사 (소스 코드만 변경됐을 때 4번 레이어 빌드 과정을 건너뜀)
COPY . .

# 7. 보안: 컨테이너 탈취 대비 root 계정이 아닌 일반 사용자로 실행
RUN useradd -m appuser \
    && chown -R appuser:appuser /app
USER appuser

# 8. FastAPI 실행
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
