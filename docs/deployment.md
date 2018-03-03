## Deployment

This repository provides a number of deployment options.

### Docker Standalone Deployment

The Dockerfile can be built and deployed as a standalone image:

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

### Docker Deployment with Custom Config Directory

The above settings leave the default [config.yaml](https://github.com/ukwa/ukwa-pywb/blob/master/config.yaml) in place.

It's also possible to further customize the deployment by adding a custom config.yaml, with different set of collections,
different access rules, etc.. This is probably ideal for the production deployment.

To add a different config, mount the config directory to the `/webarchive` path as a volume:

```
pywb:
   image: ukwa/ukwa-pywb
   ports:
     - 8080:8080
   
   volumes:
     ./pywb:/webarchive
```

See [Configuration Format](configuration] for more details on setting up the config directory.

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

And adding a following nginx configuration:

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
This is not necessary, but should improve performance.







   
