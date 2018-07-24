## HTTP/S Proxy Mode

This deployment is configured with HTTP/S proxy mode enabled, which is provided by the following config.yaml block:

```
proxy:
    # collection for proxy mode
    coll: qa-access
    ca_name: UKWA pywb HTTPS Proxy CA
    ca_file_cache: ./proxy-certs/pywb-ca.pem
```

In the default [config.yaml](https://github.com/ukwa/ukwa-pywb/blob/master/config.yaml), the `qa-access` collection is used as the proxy collection.
At this time, only a single collection can be used for proxy mode at a time.

To use the HTTPS proxy mode, a client must accept the Certificate Authority created by pywb, or ignore certificates.

See [the latest pywb docs for instructions on configuring HTTP/S Certificate Authority](http://pywb.readthedocs.io/en/latest/manual/configuring.html#https-proxy-and-pywb-certificate-authority)

### Memento and Proxy Mode

Memento `Accept-Datetime` and the new `Prefer` header are fully supported in proxy mode as well.

They can be used to select a particular capture/memento and in a particular format.

By default, with no memento headers, the latest capture is served and a banner is inserted into the replay in proxy mode.

To request an earlier memento, the following request can be made, with a proxy running at `pywb:8080` to obtain
a memento at timestamp 20140716200243 in raw, unrewritten format:

```
curl -x pywb:8080 -H "Prefer: raw" -H "Accept-Datetime: Wed, 16 Jul 2014 20:02:43 GMT" http://example.com/
```
