
# Based on standard pywb fork
FROM webrecorder/pywb:2.4.2-beta

USER root
WORKDIR /ukwa_pywb

# Add in source files and build:
ADD setup.py .
ADD setup.cfg .
ADD README.md .
ADD ukwa_pywb/ ./ukwa_pywb/

RUN python setup.py install

COPY i18n/ i18n/
RUN python setup.py compile_catalog

COPY acl/ acl/
COPY proxy-certs/ proxy-certs/

COPY uwsgi.ini .

COPY static/ static/
COPY templates/ templates/

#USER archivist

RUN mkdir /ukwa_pywb/collections
COPY config.yaml /webarchive
#ADD integration-test/test-data/ /webarchive/integration-test/test-data/

ENV PYWB_CONFIG_FILE=/webarchive/config.yaml
ENV UKWA_INDEX=/webarchive/integration-test/test-data/
ENV UKWA_ARCHIVE=/webarchive/integration-test/test-data/

CMD ["uwsgi", "uwsgi.ini"]

