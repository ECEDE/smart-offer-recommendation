FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY upgrade_tariffs.py ./upgrade_tariffs.py
EXPOSE 8000
CMD ["sh", "-c", "python upgrade_tariffs.py && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
