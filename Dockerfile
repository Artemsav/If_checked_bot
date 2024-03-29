# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
COPY requirements.txt /opt/
WORKDIR /opt/
RUN pip install -r requirements.txt
COPY . .
CMD [ "python3", "main.py" ]