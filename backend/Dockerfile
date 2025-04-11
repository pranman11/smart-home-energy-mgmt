# backend/Dockerfile

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /app

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY . .

# RUN adduser --disabled-password --no-create-home appuser
# USER appuser
# RUN chown -R appuser:appuser /app

EXPOSE 8000

