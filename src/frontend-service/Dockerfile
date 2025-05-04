FROM python:3.12-slim

WORKDIR /app

# Kopiere nur was du brauchst, strukturiert
COPY app/ app/
COPY templates/ app/templates/
COPY static/ app/static/
COPY requirements.txt ./

# Systemabhängigkeiten
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["python", "app/app.py"]