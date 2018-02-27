FROM ukwa/pywb

WORKDIR /pywb
ADD requirements.txt .

USER root

RUN pip install -r requirements.txt

WORKDIR /webarchive

ADD ukwa_pywb /ukwa_pywb
ADD templates /webarchive/templates

USER archivist


