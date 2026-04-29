# deploy/Dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 --prefix=/install -r requirements.txt -i https://repo.huaweicloud.com/repository/pypi/simple/

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /install /usr/local
COPY src/       ./src/
COPY artifacts/ ./artifacts/
COPY scripts/   ./scripts/
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
