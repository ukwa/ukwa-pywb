## Single-Concurrent Lock System

The single-concurrent lock system allows ukwa-pywb to 'lock' access to an individual url, such that only a single session can access the resource,
in accordance with UK Legal Deposit restrictions. The restriction applies to 'top-level' pages only, and
can be cleared manually. An admin interface is available to view all locked resources and sessions and to clear them as needed.

The system is implemented using a Redis server (or Redis mock-up) for cacheing, which provides key expiry support. The use of Redis ensures
that session information is persisted across application restarts.

## Usage

To enable the single-concurrent lock, set the `single-use-lock: true` in the desired collections.

```
collection:
    ukwa:
        ...
        single-use-lock: true
```


The locks are per-url per-collection. (Embedded resources and AJAX requests are also excluded from the lock).

### Setting Up Redis

The REDIS_URL should be set to a url representing the redis server. A default setting for a local server on database 0 might be:
`redis://localhost/0`.

If REDIS_URL is not set, an internal redis mock (using Python `fakeredis`) will be created and a warning printed on startup.
It's possible to use the fakeredis mock, but the session data will not be persisted across restarts.

Configuring the Redis container with Docker Compose can be done as follows. Any recent version of Redis should work.

```
pywb:
   ...
   depends_on:
       - redis
       
   environment:
       - REDIS_URL=redis://redis:6379/0
       
redis:
   image: redis:3.2.4
```

## Session Expiry Time

Redis automatically handles the expiration of session keys, clearing the locks. The expiry time is rounded up to the end of the next day by default.
For testing, it is possible to set a shorter expiry time by setting `TEST_SESSION_LOCK_INTERVAL` environment variable.
For example, it is set to `TEST_SESSION_LOCK_INTERVAL=30` to allow for testing expiry after 30 seconds.

This environment variable should not be set for production.

## Admin Page and API

The admin page to view all locked urls and user sessions is available at `http://<pywb-host>/_locks`.
If any sessions exist, it provides urls to clear all sessions, clear all urls in a session, clear individual url, or clear current
user session (logout).

The following routes are provided:
- `/_locks` -- Admin Page
- `/_locks/reset` -- Clear All Sessions
- `/_locks/clear/<id>` -- Clears session <id>
- `/_locks/clear_url/<url>` -- Clears locked url <url>
- `/_logout` -- Clears current session, logout current user

### Restricting Access to Admin API

Access to the admin API paths (except `/_logout`) can be restricted by defining the 
`LOCKS_AUTH` environment in the username:password form, eg. `LOCKS_AUTH=admin:password`

If `LOCKS_AUTH` is properly set, access to any of the `/_locks*` paths will return a 401 unless the username and password are provided as Basic Auth.

## Error Messages

When accessing a locked resource, a 403 error code is returned.
When accessing an admin page without proper credentials, a 401 error code is returned.

These are used to set customized error messages in the [error.html](https://github.com/ukwa/ukwa-pywb/blob/master/templates/error.html)
template.

The template can be customized further as needed.
