FROM ukwa/pywb

USER root

WORKDIR /webarchive

ADD setup.py .
ADD setup.cfg .
ADD README.md .
ADD ukwa_pywb/ ./ukwa_pywb/

RUN python setup.py install

ADD . .

RUN ./i18n/update-loc.sh

USER archivist

CMD ukwa_pywb
