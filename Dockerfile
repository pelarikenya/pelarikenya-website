# -------------------------------------------
# Stage 1: Build
# -------------------------------------------
FROM python:3.14-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# -------------------------------------------
# Stage 2: Production
# -------------------------------------------
FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

RUN mkdir -p /app/database && \
    adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

USER appuser

RUN chmod +x start.sh

EXPOSE 5000

CMD ["./start.sh"]
