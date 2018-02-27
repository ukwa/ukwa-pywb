FROM ukwa/pywb

USER root
WORKDIR /pywb

ADD requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /webarchive

ADD ukwa_pywb /ukwa_pywb
ADD templates /webarchive/templates

USER archivist


