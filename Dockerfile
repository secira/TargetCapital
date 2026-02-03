FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["sh", "-c", "python railway_migrate.py && gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --worker-class gthread --timeout 120 main:app"]
