UKWA PYWB Access System
=======================

This repository represents a customized extension of [pywb](https://github.com/webrecorder/pywb) for use with the UK Web Archive. It includes:

- Custom UI for UKWA
- [Single-Concurrent Lock System](docs/locks.md)
- [Localization](docs/localization.md)
- [Access Controls](docs/access_controls.md)

This repository ships a custom package `ukwa_pywb`, which extends the `pywb`.

Currently, it is to be used with the [ukwa/pywb fork of pywb](https://github.com/ukwa/pywb) until this fork is merged into a future pywb release.

## Deployment and Configuration

The project can be deployed locally or in Docker.

- See [Deployment](docs/deployment.md) for more information about deploying this repository and running tests.

- See [Configuration](docs/configuration.md) for more information about the `config.yaml` file and its options.

- See [Integration Tests](integration-test/README.md) on how to run the included integration test suite.
