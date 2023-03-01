#!/bin/bash

# local paths to cdx and warc data
UKWA_INDEX=./integration-test/test-data/ \
UKWA_ARCHIVE=./integration-test/test-data/ \
MUST_AGREE_TO_TERMS=true \
ukwa_pywb $@


