# [Stage 1] 빌드 환경 (JDK 포함)
FROM gradle:8-jdk17 AS builder
WORKDIR /build

# 빌드 캐시를 위해 의존성 관련 파일만 다운로드 (소스코드 복사 전 수행)
COPY build.gradle settings.gradle ./
RUN gradle dependencies --no-daemon || true

# 소스코드 복사 후 jar 호를 빌드
COPY src src
RUN gradle bootJar --no-daemon

# [Stage 2] 실행 환경 (JRE만 포함)
FROM eclipse-temurin:17-jre-jammy
WORKDIR /app

# builder 스테이지에서 빌드된 최종 jar 파일만 복사
COPY --from=builder /build/build/libs/*.jar app.jar

# 보안을 위한 일반 유저 생성 및 권한 설정
RUN useradd -m appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
