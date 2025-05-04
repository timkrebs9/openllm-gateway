FROM python:3.12-slim

WORKDIR /app/
COPY . /app

RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc libpq-dev 
RUN rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
COPY templates/ /app/templates/
COPY static/ /app/static/

RUN pip install --no-cache-dir -r requirements.txt



EXPOSE 8000
CMD ["python", "app/app.py"]