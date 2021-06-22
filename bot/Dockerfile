FROM python:3.9-slim

MAINTAINER Sid Viscous

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY wenmoon wenmoon

CMD ["python", "-m", "wenmoon"]
