FROM python:2.7.15-slim-jessie

RUN pip install --no-cache-dir geni-lib

ADD cloudlab_util.py /usr/local/lib/python2.7/site-packages/geni/
