UKWA PYWB Deployment
====================

This repo represents a customized deployment of [pywb](https://github.com/webrecorder/pywb) for the UK Web Archive.

Running with Integration Tests
------------------------------

See [integration-tests](integration-tests) for running a full test suite in Docker.


Running Locally
---------------

The deployment can also be run locally using sample data from [integration-tests/test-data](integration-tests/test-data)

1) Install the [UKWA fork of pywb](ukwa/pywb) and run `python setup.py install` in a Python 3 environment.

2) Run `run-ukwa-pywb.sh`. This will start the server on default port (8080).

   (To choose a different port, run `run-ukwa-pywb.sh -p 8060`

   The script accepts all the params of default `wayback` or `pywb` commands)
    
