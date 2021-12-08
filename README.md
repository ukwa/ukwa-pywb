UKWA PYWB Access System
=======================

This repository represents a customized extension of [pywb](https://github.com/webrecorder/pywb) for use with the UK Web Archive. It includes:

- [Custom UI for UKWA](docs/ui.md)
- [Single-Concurrent Lock System](docs/locks.md)
- [Localization](docs/localization.md)
- [Access Controls](docs/access_controls.md)
- [HTTP/S Proxy Mode](docs/proxy.md)
- Memento Prefer Header initial implementation (See [this issue](https://github.com/mementoweb/rfc-extensions/issues/7) for further discussion)

This repository builds an `ukwa-pywb` container image, which extends the offical `pywb` container image release. 

In the past, additional PyWB functionality has been developed on the [ukwa/pywb fork of pywb](https://github.com/ukwa/pywb), but this has now all been merged upstream. This allows us to depend on PyWB directly rather than our own release.

## Upgrading PyWB

This project can be upgraded by simply the version of the PyWB docker container [referred to in the Dockerfile](https://github.com/ukwa/ukwa-pywb/blob/master/Dockerfile#L2-L3).  In general, upgrades should usually be smooth, but as in [this case](https://github.com/webrecorder/pywb/commit/f7bd84cdacdd665ff73ae8d09a202f60be2ebae9), sometimes changes have been made to PyWB that affects the things we've modified or extended, like the banner template handling.

To check this, the new image can be built and tested using the integration test system, as outlined below.

Once tested, the version can be tagged, using the PyWB version as a base. i.e. the version of `ukwa/ukwa-pywb` based on `webrecorder/pywb:2.6.2` should be `2.6.2`. If any further releases are required to resolve unexpected problems, while sticking to the same version of PyWB, a point suffix can be added, e.g. `2.6.2.1`, `2.6.2.2` and so on.

Once the image has been built, it should be rolled out across the relevant [ukwa-services](https://github.com/ukwa/ukwa-services). This includes the website, w3act and reading room service stacks.

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
