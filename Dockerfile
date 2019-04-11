FROM python:2.7-slim-stretch

RUN pip install --no-cache-dir geni-lib

COPY entrypoint.sh /usr/bin
COPY geni.py /root/

ENTRYPOINT ["entrypoint.sh"]
