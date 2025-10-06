FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ app/
COPY templates/ app/templates/
COPY static/ app/static/
COPY requirements.txt .

RUN mkdir -p logs

EXPOSE 5001

CMD ["python", "-m", "app.app"]
