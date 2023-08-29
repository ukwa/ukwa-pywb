## Deployment

This repository provides a number of deployment options.

### Local Python Deployment

This repository contains a standalone python package, which can be installed anr run locally:

```
python setup.py install
./run-ukwa-pywb.sh [ -p 8080]
```
A port can be supplied to start on a different port.

#### Testing

The package includes unit tests for custom functionality, available by running:
```
python setup.py test
```

More thorough testing is performed by the browser-based and network-based [Integration Tests](https://github.com/ukwa/ukwa-pywb/tree/master/integration-test)


### Docker Standalone Deployment

The easiest deployment is with the supplied Dockerfile can be built and deployed as a standalone image:

`docker build -t ukwa/ukwa-pywb .; docker run -it -p 8080:8080 ukwa/ukwa-pywb`

The ukwa-pywb instance can then be accessed via `http://localhost:8080/`

Note that the default test data from integration tests is added to the image to make it
runnable on its own.

### Docker Compose Deployment

For production use, it may be more convenient to deploy the image as part of docker-compose.
This make it easier to set the environment variables.

#### Setting UKWA_INDEX and UKWA_ARCHIVE

The UKWA_INDEX and UKWA_ARCHIVE env varibales are used in the default `config.yaml` and point to the internal test data by default.

They can be set to point to other index or archive source.


```
pywb:
   image: ukwa/ukwa-pywb
   ports:
     - 8080:8080

   environment:
     - "UKWA_INDEX=xmlquery+http://cdx:8080/tc"
     - "UKWA_ARCHIVE=webhdfs://hadoop:50070/"
```

This setting is used for the [integration-test](https://github.com/ukwa/ukwa-pywb/tree/master/integration-test) deployment
and allows for easy testing with different index and archival sources.

See [Configuration docs](configuration.md#environment-variables) for a full list of environment variables that can be set.

This setting leaves the default [config.yaml](https://github.com/ukwa/ukwa-pywb/blob/master/config.yaml) in place.

### Docker Deployment with Custom Config Directory

It's also possible to further customize the deployment by adding a custom `config.yaml`, with differnet access rules, collection names, etc...

To add a different config, mount the config directory to the `/webarchive` path as a volume:

```
pywb:
   image: ukwa/ukwa-pywb
   ports:
     - 8080:8080
   
   volumes:
     ./pywb:/webarchive
```

Note that any local paths used in `config.yaml` should be absolute paths in /webarchive as the working directory is not set to `/webarchive`

See [Configuration Format](configuration.md) for more details on setting up the configuration.

## UWSGI Production Deployment

The image is set up to use [uWSGI](http://uwsgi-docs.readthedocs.io/en/latest/) server application for production deployment, which provides a number
of scaling options.

The options are configured in [uwsgi.ini](https://github.com/ukwa/ukwa-pywb/blob/master/uwsgi.ini)

In particular, these settings control the number of concurrent processes (10) and gevent workers per process (400)
```
processes = 10
gevent = 400
```

They can be adjusted as needed.

### Running behind Nginx

uWSGI integrates well with Nginx. In addition to running on HTTP 8080, Nginx is able to communicate with uWSGI through the binary uwsgi protocol.
A listener for this is configured on port 8081 via `socket = 8081` setting in uwsgi.ini

To run with nginx, a possible configuration is as follows.
First, exposing the port in docker-compose.yml:
```
...
     pywb:
         ...
         ports:
             - 8081:8081
             - 8080:8080
``` 

And adding a following Nginx configuration:

```
server {
    listen 8100;

    location /static {
        alias /home/ubuntu/ukwa-pywb/static;
        try_files $uri @default;
    }

    location @default {
        uwsgi_pass localhost:8081;

        include uwsgi_params;
        uwsgi_param UWSGI_SCHEME $scheme;
    }

    location / {
        uwsgi_pass localhost:8081;

        include uwsgi_params;
        uwsgi_param UWSGI_SCHEME $scheme;
    }
}
```

This configuration sets up nginx to listen on 8100 and forward to uwsgi on 8081.

An additional ptimization is added to allow nginx to serve any static files from the [/static](https://github.com/ukwa/ukwa-pywb/tree/master/static)
directory in this repository directly. (The above assumes this repository is installed at `/home/ubuntu/ukwa-pywb/`)

This is recommended to improve performance.

## UKWA Production Deployment

### Deployment on the UKWA DEV Swarm for Integration Testing

To deploy in a more realistic environment, the service can be deployed on the DEV Swarm at UKWA.

The current process is optimized for contributions being worked on directly in GitHub. e.g. if changes are made to ukwa/ukwa-pywb on branches or tags that match [this](https://github.com/ukwa/ukwa-pywb/blob/4d323f170b1ad03859561490b2571db8c48caf52/.github/workflows/push-to-docker-hub.yml#L4-L10) then a Docker image will be built that can be deployed on DEV.  e.g. commit to master, wait for the container ukwa/ukwa-pywb:master to be built, deploy to DEV by logging into it and using an appropriate docker service update command, e.g.:

    docker service update access_website_pywb --image ukwa/ukwa-pywb:master

Deploying a locally-built Docker image is more difficult, as the service runs over two Swarm hosts, so if you build and tag the Docker image on one and the service tries to deploy on the other, it will grumble.  However, subsequent deployment attempts should try different hosts, so it should work eventually.

To do this, first build and tag the image locally, in the `ukwa-pywb` folder:

    docker build -t ukwa/ukwa-pywb:local-test .

Then use that tag for deployment:

    docker service update access_website_pywb --image ukwa/ukwa-pywb:local-test

Once the service gets deployed on the same node as the build, it should be possible to test it via the DEV system URL.

#### Local deployment across Swarm nodes

To ensure your service can run on any node, you can:

- Log into each node and run the same build command on each one.
- Use `docker export` to make a tar of the image, then `docker import` it on other nodes.
- Push the images to an internal registry and deploy from there instead, as per https://docs.gitlab.com/ee/user/packages/container_registry/build_and_push_images.html


### Deployment to BETA and PROD

Full deployment must be done via public tagged images, added or updated in the relevant stack from the `ukwa-services` repo(s). 
