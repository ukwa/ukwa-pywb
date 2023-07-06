
# Based on standard pywb fork
FROM webrecorder/pywb:2.7.2

USER root
WORKDIR /ukwa_pywb

# Grab any security updates:
#RUN apt-get update && apt-get upgrade -y \
#  && rm -rf /var/lib/apt/lists/*

# Add in source files and build:
ADD setup.py .
ADD setup.cfg .
ADD README.md .
ADD ukwa_pywb/ ./ukwa_pywb/

RUN python setup.py install

COPY i18n/ i18n/
# Include 'fuzzy' translations (so we can see changes here)
# See https://stackoverflow.com/a/12555922
RUN python setup.py compile_catalog -f

COPY acl/ acl/
COPY proxy-certs/ proxy-certs/

COPY uwsgi.ini .

COPY static/ static/
COPY templates/ templates/

# Run as non-root user:
# USER archivist
# Parent image no longer uses this user.

RUN mkdir /ukwa_pywb/collections
RUN mkdir -p /webarchive
COPY config.yaml /webarchive
#ADD integration-test/test-data/ /webarchive/integration-test/test-data/

# Define environment variables:
ENV DEBUG=False
ENV PYWB_CONFIG_FILE=/webarchive/config.yaml
ENV UKWA_INDEX=/webarchive/integration-test/test-data/
ENV UKWA_ARCHIVE=/webarchive/integration-test/test-data/

CMD ["uwsgi", "uwsgi.ini"]

