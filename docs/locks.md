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

## Default Session Expiry Time

Redis automatically handles the expiration of session keys, clearing the locks. The expiry time is rounded up to the end of the next day by default.
For testing, it is possible to set a shorter expiry time by setting `TEST_SESSION_LOCK_INTERVAL` environment variable.
For example, it is set to `TEST_SESSION_LOCK_INTERVAL=30` to allow for testing expiry after 30 seconds.

This environment variable should not be set for production.

## Ping Session Refresh

The locks can be expired more quickly via a client-side ping mechanism.

A client-side ping to `/_locks/ping` is made to reset the expiry for the current page, based on the referrer.

If the `LOCK_PING_EXPIRE` env var is set, and the current session owns the referring page, the expiry is set
to `LOCK_PING_EXPIRE` seconds into the future.

The client-side ping is performed every `LOCK_PING_INTERVAL` seconds (defaulting to 30)


## Select/Copy Restrictions

The `SELECT_WORD_LIMIT` env variable can be set to limit selection to a specified number of words
to restrict clipboard copying.

On modern browsers that support the Clipboard APIs, the restriction is made at the time of copying the text.

As a fallback and on other browsers, a restriction is applied when selecting the text. In this mode,
the selection is shrunk until it is no more than `SELECT_WORD_LIMIT` words.

As a worse case, the clipboard copy operation fails altogether instead of allowing unrestricted copy.


## Add Extra Headers

Extra headers can be added to all responses via the main `config.yaml`


```yaml
collection:
    ukwa:
        ...
        add_headers:
            Cache-Control: 'max-age=0, no-cache, must-revalidate, proxy-revalidate, private'
            Expires: 'Thu, 01 Jan 1970 00:00:00 GMT'
```

This option can apply to all collections, not only those that have `single-use-lock: true` set.


## Content-Type and Download Redirects

The following config option allows for intercepting certain content types and issueing a redirect
to a designated page.

```yaml
collection:
    ukwa:
        ...
        content_type_redirects:
            'text/rtf': 'https://example.com/viewer?{query}'
            'application/pdf': 'https://example.com/viewer?{query}'
            'application/': 'https://example.com/blocked?{query}'
            '<any-download>': 'https://example.com/blocked?{query}'
```

With this config, any `text/rtf` resource or `application/pdf` resources encountered during replay are redirected to `https://example.com/viewer?{query}`,
where the `{query}` expands to the pywb url for downloading the raw/identity resource (with the `id_` modifier).
(The raw urls are not redirected to allow a viewer to access the data).

For example, a request to `https://myarchive.example.com/ukwa/2020010203mp_/http://example.com/myfile.rtf` might result in a redirect to `http://example.com/viewer?url=http://myarchive.example.com/ukwa/2020010203id_/http://example.com/myfile.rtf`

If an exact match is not found, the MIME prefix, such as `application/` is also checked to allow for restricting a class of mime types.


To prevent arbitrary downloads, the `<any-download>` match is made for any response that contains a `Conteent-Disposition: attachment...` regardless of mime type.
For example, a `text/plain` document with `Content-Dispositon` would get redirected to `https://example.com/blocked?...`

The `content_type_redirects` field is available to all collections, not only those that have `single-use-lock: true` set.

The single-use lock does apply to the initial url, and will result in a 403 instead of a redirect if the lock can not be acquired. The lock will last for the full session expiry time (end of the day), as there is no client-side ping happening for redirects.




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
