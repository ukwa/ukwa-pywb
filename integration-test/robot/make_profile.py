def make_profile():
    from selenium import webdriver
    fp = webdriver.FirefoxProfile()
    fp.set_preference("network.proxy.http", "pywb");
    fp.set_preference("network.proxy.http_port", 8080);
    fp.set_preference("network.proxy.share_proxy_settings", True);
    fp.set_preference("network.proxy.ssl", "pywb");
    fp.set_preference("network.proxy.ssl_port", 8080);
    fp.set_preference("network.proxy.type", 1);

    fp.update_preferences()
    return fp.path

