FROM python:3.9-slim

# Nécessaire pour faire tourner TweetyProject
RUN apt-get update && \
    apt-get install -y default-jre && \
    apt-get clean;

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
