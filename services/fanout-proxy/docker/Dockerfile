FROM python:3.11-slim

WORKDIR /app

COPY ../python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../python/app.py .
COPY ../python/fanout_logic.py .
COPY ../python/retry.py .

EXPOSE 8080

CMD ["python", "app.py"]