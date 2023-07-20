FROM python:3.11-slim

RUN mkdir -p app/src/services/matching
RUN touch app/src/__init__.py
RUN touch app/src/services/__init__.py

WORKDIR /app

COPY matching.py /app
COPY matching_utils.py /app/src/services/matching/
COPY .env  /app/src/services/matching/
COPY __init__.py /app/src/services/matching/
COPY requirements.txt /app/src/services/matching/
WORKDIR /app/src/services/matching

RUN pip install  --no-cache-dir -r requirements.txt
WORKDIR /app
EXPOSE 8000

CMD ["python", "matching.py"]
