*** Settings ***
Documentation     Proxy Access, via HTTP and HTTPS, using Requests and Firefox
Resource          resource.robot
Suite setup       Run Keywords    Reset Browsers
Suite teardown    Run Keywords    Close All Browsers    Delete All Sessions


*** Test Cases ***
Init Requests HTTP
    ${proxies} =    Evaluate    {"https": "https://pywb:8080/", "http": "http://pywb:8080/"}
    Create Session    acidtest    http://acid.matkelly.com    proxies=${proxies}

Requests: HTTP Proxy Get Latest Memento (Default)
    ${resp}=    Get Request    acidtest    /
    Should Be Equal As Strings    ${resp.status_code}    200
    Should Be Equal As Strings    ${resp.headers['Memento-Datetime']}    Sat, 03 Feb 2018 00:41:47 GMT

Requests: HTTP Proxy Get Older Memento (with Accept-Datetime)
    &{headers}=    Create Dictionary    Accept-Datetime=Sat, 04 Jan 2014 00:00:00 GMT
    ${resp}=    Get Request    acidtest    /    headers=${headers}
    Should Be Equal As Strings    ${resp.status_code}    200
    Should Be Equal As Strings    ${resp.headers['Memento-Datetime']}    Wed, 16 Jul 2014 20:02:43 GMT

Requests: HTTPS Proxy Get Latest Memento (Default)
    ${proxies} =    Evaluate    {"https": "https://pywb:8080/", "http": "http://pywb:8080/"}
    Create Session    acidtest_https    https://acid.matkelly.com    proxies=${proxies}    verify=${CA_CERTS}
    &{headers}=    Create Dictionary    Connection=close
    ${resp}=    Get Request    acidtest_https    /    headers=${headers}
    Should Be Equal As Strings    ${resp.status_code}    200
    Should Be Equal As Strings    ${resp.headers['Memento-Datetime']}    Sat, 03 Feb 2018 00:41:47 GMT

Requests: HTTPS Proxy Get Older Memento (with Accept-Datetime)
    ${proxies} =    Evaluate    {"https": "https://pywb:8080/", "http": "http://pywb:8080/"}
    Create Session    acidtest_https_2    https://acid.matkelly.com    proxies=${proxies}    verify=${CA_CERTS}
    &{headers}=    Create Dictionary    Accept-Datetime=Sat, 04 Jan 2014 00:00:00 GMT
    ${resp}=    Get Request    acidtest_https_2    /    headers=${headers}
    Should Be Equal As Strings    ${resp.status_code}    200
    Should Be Equal As Strings    ${resp.headers['Memento-Datetime']}    Wed, 16 Jul 2014 20:02:43 GMT

Firefox: Proxy Open Browser
    Open Browser With Proxy

Firefox: HTTP Proxy Load
    Go To    http://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    The Archival Acid Test
    Page Should Contain     Back to Calendar

Firefox: HTTP Acid Test No Red
    Sleep   1s
    Execute JavaScript    window.scroll(0, 100)
    Sleep   2s
    Page Should Contain Element    //img[@src='red.png']    limit=0

Firefox: HTTPS Proxy Load (Acid-Test)
    Go To    https://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    The Archival Acid Test
    Page Should Contain     Back to Calendar

Firefox: HTTPS Proxy Load (httpbin)
    Go To    https://httpbin.org/anything/something
    Page Should Not Contain Element    //b[@id='title_or_url']




