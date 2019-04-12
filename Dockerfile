FROM python:2.7-slim-jessie

RUN pip install --no-cache-dir geni-lib

COPY entrypoint.sh /usr/bin
COPY geni_util.py /root/

ENTRYPOINT ["entrypoint.sh"]
