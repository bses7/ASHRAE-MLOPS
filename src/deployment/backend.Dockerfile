FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgomp1 \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pymysql cryptography

COPY ../src/ ./src/
COPY ../configs/ ./configs/
COPY ../saved_models/ ./saved_models/
COPY ../app/backend/ ./app/backend/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.backend.server:app", "--host", "0.0.0.0", "--port", "8000"]