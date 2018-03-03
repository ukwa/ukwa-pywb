## Configruation

The configuration for ukwa-pywb consists of several environment variables and the main [config.yaml](https://github.com/ukwa/ukwa-pywb/blob/master/config.yaml) file.

### Environment Variables

The following environment variables can be used:

- `UKWA_INDEX` -- Points to the CDX/index source data. Required with the default [config.yaml](https://github.com/ukwa/ukwa-pywb/blob/master/config.yaml).

- `UKWA_ARCHIVE` -- Points to the WARC/archive source data. Required with the default [config.yaml](https://github.com/ukwa/ukwa-pywb/blob/master/config.yaml).

- `WEBHDFS_USER` -- For use with the `webhdfs://` archive source data to set the WebHDFS `user.name=` field.

- `WEBHDFS_TOKEN` -- For use with the `webhdfs://` archive source data to set the WebHDFS `delegation=` token.

- `REDIS_URL` -- A Redis url (eg. `redis://redis:6379/0`) pointing to a Redis instances for use with the [Single-Concurrent Lock](locks.md) system.

- `SESSION_LOCK_INTERVAL` -- a custom internval to override the concurrent-lock timeout. See [Single-Concurrent Lock](locks.md) for more details.

- `LOCKS_USERNAME` and `LOCKS_PASSWORD` -- If set, provide Basic Auth access restrictions to all session locks operations. See [Single-Concurrent Lock](locks.md) for more details.

### Configuration Format

The [default config.yaml](https://github.com/ukwa/ukwa-pywb/blob/master/config.yaml) is a good starting point for customizing the configuration.

The ukwa-pywb config supports [the default pywb configuration options](http://pywb.readthedocs.io/en/latest/manual/configuring.html) plus the following additional options:


### Enable Prefer Header

To enable Memento Prefer header support, set this option:

```
enable_prefer: true
```


### Localization:

To enable localization, the following entry is needed:

```
locales_root_dir: ./i18n/translations/
locales: ['en', 'cy']
```

See [Localization Docs](localization.md) for more info on localization.

### Single-Concurrent Lock

The single-concurrent lock mode can be enabled per-collection by setting `single-use-lock: true` in the collection config:

```
collection:
    ukwa:
        ...
        single-use-lock: true
```

See [Single-Concurrent Lock docs](locks.md) for more info.


### Access Controls

Access Controls files can be added to any collection, eg:

```
collections:
   ukwa:
      ...
      acl_paths:
          - /webarchive/block_list.aclj
```

See [Access Controls](access_controls.md) for more info on the ACL configuration.

### Environment Variables in the Config

Environment variables `${...}` can be used in the config as needed, to define paths, etc...

```
ukwa:
   ...
   acl_paths:
     - ${BLOCK_ACL_PATH}
```

(This is how `UKWA_INDEX` and `UKWA_ARCHIVE` are used in the default config.)


### Note on Deployment

When mounting a custom config directory as `/webarchive` in Docker, it should contain a root `config.yaml` file.

Any paths to other files within the directory, such as access control files, should be absolute within /webarchive.

See [Deployment Docs](deployment.md) for more info on deployment options.
