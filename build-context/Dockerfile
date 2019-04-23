FROM python:2.7-slim-jessie

RUN pip install --no-cache-dir geni-lib

ENV PYTHONUNBUFFERED=on

COPY entrypoint.sh /

ENTRYPOINT ["entrypoint.sh"]
