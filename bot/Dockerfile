FROM python:3.9-slim

MAINTAINER Sid Viscous

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY wenmoon wenmoon

ENV RUN_MODE=docker
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "wenmoon"]
