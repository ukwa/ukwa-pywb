#!/bin/bash

# local paths to cdx and warc data
UKWA_INDEX=./integration-test/test-data/ \
UKWA_ARCHIVE=./integration-test/test-data/ \
python ukwa_pywb/ukwa_app.py $@


