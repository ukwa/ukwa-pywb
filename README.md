UKWA PYWB Access System
=======================

This repository represents a customized extension of [pywb](https://github.com/webrecorder/pywb) for use with the UK Web Archive. It includes:

- [Custom UI for UKWA](docs/ui.md)
- [Single-Concurrent Lock System](docs/locks.md)
- [Localization](docs/localization.md)
- [Access Controls](docs/access_controls.md)
- [HTTP/S Proxy Mode](docs/proxy.md)
- Memento Prefer Header initial implementation (See [this issue](https://github.com/mementoweb/rfc-extensions/issues/7) for further discussion)

This repository ships a custom package `ukwa_pywb`, which extends the offical `pywb` release. Where additional functionality is to be developed and then fed back to the upstream project, the [ukwa/pywb fork of pywb](https://github.com/ukwa/pywb) can be used.

## Development Setup

To build and run from a checked-out repository, you can use the integration test setup.  First

    cd integration-test/

Then you can use this to re-build the containerised version locally:

    docker-compose build pywb

And run it using:  

    docker-compose up populate pywb

The first time you do this, the `populate` container will make the test data available and populate the system with it. You will need to do this again if you fully remove the integration testing containers.  However, if you're just re-building `pywb` for testings, you can just do this:

    docker-compose up pywb

When running locally, the service should be available at: http://localhost:8081 and should contain:

* A copy of the The Archival Acid Test: http://localhost:8081/open-access/*/http://acid.matkelly.com/
* Example HTTP 451 resource: http://localhost:8081/open-access/20180203004147/http://www.cs.odu.edu/~mkelly/acid/externalScript.js

See [Integration Tests](integration-test/README.md) for more details.


## Deployment and Configuration

The project can be deployed locally or in Docker.

- See [Deployment](docs/deployment.md) for more information about deploying this repository and running tests.

- See [Configuration](docs/configuration.md) for more information about the `config.yaml` file and its options.

- See [Integration Tests](integration-test/README.md) on how to run the included integration test suite.
