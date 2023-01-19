## NPLD Access Controls

The NPLD system access controls provide a conditional access control, where a resource is accessible only if an appropriate HTTP-header is provided with the request.

This can be done by filtering block rules by a specific user, and setting the user via an nginx frontend, based on additional options.

For pages which should not be publicly accessible, the following access control rules can be added with a special `public` user:

```shell
wb-manager acl add ./npld.acl -u public https://example.com/ block

Added new Rule:
    com,example)/ - {"access": "block", "url": "https://example.com/", "user": "public"}
```

This rule signifies that `https://example.com/` will be blocked if the user is set to `public`.


## Nginx Filtering

nginx rule blocks can be used to configure access, based on several options, including a combination of ip-based rule and custom header.


### IP-based Only Filtering

For example, the following rule configures if access based on IP of the incoming request.

In this example, if an IP is from one of the local ranges, the user is set to `internal`, and the above block rule will not apply.

Otherwise, the user is set to `public` by default, and access will be blocked.


```
geo $remote_addr $user_access {
  127.0.0.0/8     internal;
  172.16.0.0/12   internal;
  192.168.0.0/16  internal;
  10.0.0.0/8      internal;

  default         public;
}
```

### Header-Based Only Filtering

Filtering can also be done by matching HTTP headers.

In this example, access can be granted if the header `X-NPLD-Player-Auth-Token` is provided and has a value of `auth-value-1` or `auth-value-2`

by setting the `$user_access` variable to `internal`, and `public` otherwise.

```
map $http_x_npld_player_auth_token $user_access {
  auth-value-1    internal;
  auth-value-2    internal;
  default         public;
}
```

The value of `$user_access` is then passed in as a uwsgi param:


```
uwsgi {
...
    uwsgi_param HTTP_X_PYWB_ACL_USER $user_access;
}
```


### IP + Header Based Filtering

IP and Header based checks can be combined to create more complex rules, as illustrated below

- If accessed from the wrong IP range, the request is treated as `public`.

- If accessed from the correct IP range, the request may be treated `internal` only if correct
header value is also provided.

- Otherwise, the user access token is set to a third state, `need-auth:public`.

The special user `need-auth:public` to indicate that a custom error page should be shown,
requesting authentication.

This can be set through several nginx `map` rules.


```
geo $remote_addr $access {
  127.0.0.0/8     internal;
  172.16.0.0/12   internal;
  192.168.0.0/16  internal;
  10.0.0.0/8      internal;

  default         public;
}

map $http_x_npld_player_auth_token $token {
  auth-value-1    allowed;
  auth-value-2    allowed;
  default         not-allowed;
}


map $access-$token $user_access {
  internal-allowed      "internal";
  internal-not-allowed  "need-auth:public";
  default               "public";
}
```

## UKWA Pywb Specific Changes

Most of the above functionality is part of standard pywb.

The UKWA Pywb implementation adds special handling of a user with `need-auth:` prefix.

The authentication is performed after dropping this prefix, and if the request is blocked, a special error
page including an `npld-viewer://` link is provided to load the same URL via a previously installed NPLD Player.

## Testing Block Rules

The `integration-tests` directory provides a sample setup based on the above, using the `docker-compose-test-acl.yml`
the nginx config in `nginx/pywb.conf`, and the block rules in `./acl/blocks.aclj`.

A test is provided for verifying the application of the block rules

Running `py.test -s -vv ukwa_pywb/test/test_npld_block.py` will launch docker-compose to build the local image, and orchestrate with an instance of nginx to perform these tests.

(Docker Compose should be installed before running this test).

