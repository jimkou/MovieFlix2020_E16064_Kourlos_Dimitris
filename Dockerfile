FROM python:3.6
ADD . /mongo
WORKDIR /mongo
VOLUME /data/db
RUN pip install -r requirements.txt
