UKWA PYWB Deployment
====================

This repo represents a customized deployment of [pywb](https://github.com/webrecorder/pywb) for the UK Web Archive.

Running with Integration Tests
------------------------------

See [integration-test](integration-test) for more info on running the full test suite in Docker.

After starting the test suite, the UKWA pywb server will be running at `http://localhost:8081/`


Running Locally
---------------

The deployment can also be run locally using sample data from [integration-test/test-data](integration-test/test-data)

1) Install the [UKWA fork of pywb](https://github.com/ukwa/pywb) and run `python setup.py install` in a Python 3 environment.

2) Run `run-ukwa-pywb.sh`. This will start the server on default port (8080).

   (To choose a different port, run `run-ukwa-pywb.sh -p 8060`

   The script accepts all the params of default `wayback` or `pywb` commands)
    
