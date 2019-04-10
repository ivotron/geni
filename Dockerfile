FROM python:3.7-alpine3.8

RUN pip install --no-cache-dir geni-lib

COPY entrypoint.sh /usr/bin
COPY geni.py /root/

ENTRYPOINT ["entrypoint.sh"]
