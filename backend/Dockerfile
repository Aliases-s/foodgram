FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

COPY data/ /data/

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && mkdir -p /backend_static/static && cp -r /app/collected_static/. /backend_static/static/ && gunicorn --bind 0.0.0.0:8000 foodgram.wsgi"]