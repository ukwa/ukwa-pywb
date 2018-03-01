*** Settings ***
Documentation     Check Memento Prefer header using Requests to redirect to raw or rewritten resources
Resource          resource.robot
Suite teardown    Run Keywords    Delete All Sessions


*** Test Cases ***
Init Requests
    Create Session    pywb    ${HOST}

# Prefer on TimeGate (redirects)
Prefer Raw from TimeGate
    &{headers}=    Create Dictionary    Prefer=raw
    ${resp}=    Get Request    pywb    /qa-access/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Raw    ${resp}    /qa-access/20180203004147id_/http://acid.matkelly.com/

Prefer Banner Only from TimeGate
    &{headers}=    Create Dictionary    Prefer=banner-only
    ${resp}=    Get Request    pywb    /qa-access/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Banner Only    ${resp}     /qa-access/20180203004147bn_/http://acid.matkelly.com/

Prefer Rewritten from TimeGate
    &{headers}=    Create Dictionary    Prefer=rewritten
    ${resp}=    Get Request    pywb    /qa-access/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Rewritten    ${resp}     /qa-access/20180203004147mp_/http://acid.matkelly.com/


# Prefer on Memento (redirects)
Prefer Raw from Memento Url
    &{headers}=    Create Dictionary    Prefer=raw
    ${resp}=    Get Request    pywb    /qa-access/2018/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Raw    ${resp}    /qa-access/20180203004147id_/http://acid.matkelly.com/

Prefer Banner Only from Memento Url
    &{headers}=    Create Dictionary    Prefer=banner-only
    ${resp}=    Get Request    pywb    /qa-access/20180203004147mp_/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Banner Only    ${resp}    /qa-access/20180203004147bn_/http://acid.matkelly.com/

Prefer Rewritten from Memento Url
    &{headers}=    Create Dictionary    Prefer=rewritten
    ${resp}=    Get Request    pywb    /qa-access/2017/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Rewritten    ${resp}     /qa-access/20180203004147mp_/http://acid.matkelly.com/


# Prefer on Memento (no redirect)
Prefer Raw from Memento Url (Exact Timestamp)
    &{headers}=    Create Dictionary    Prefer=raw
    ${resp}=    Get Request    pywb    /qa-access/20180203004147id_/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Raw    ${resp}    /qa-access/20180203004147id_/http://acid.matkelly.com/

Prefer Banner Only from Memento Url (Exact Timestamp)
    &{headers}=    Create Dictionary    Prefer=banner-only
    ${resp}=    Get Request    pywb    /qa-access/20180203004147id_/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Banner Only    ${resp}    /qa-access/20180203004147bn_/http://acid.matkelly.com/

Prefer Rewritten from Memento Url (Exact Timestamp)
    &{headers}=    Create Dictionary    Prefer=rewritten
    ${resp}=    Get Request    pywb    /qa-access/20180203004147mp_/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Rewritten    ${resp}     /qa-access/20180203004147mp_/http://acid.matkelly.com/


# Invalid Prefer
Prefer Error Invalid Prefer
    &{headers}=    Create Dictionary    Prefer=invalid
    ${resp}=    Get Request    pywb    /qa-access/20180203004147mp_/http://acid.matkelly.com/    headers=${headers}
    Should Be Equal As Strings    ${resp.status_code}    400


# Prefer In Proxy Mode
PROXY: Init Requests with Proxy
    ${proxies} =    Evaluate    {"https": "https://pywb:8080/", "http": "http://pywb:8080/"}
    Create Session    proxy    http://acid.matkelly.com    proxies=${proxies}

PROXY: Prefer Raw
    &{headers}=    Create Dictionary    Prefer=raw
    ${resp}=    Get Request    proxy    /    headers=${headers}
    Check Response Is Raw    ${resp}    /    http://acid.matkelly.com

PROXY: Prefer Banner Only
    &{headers}=    Create Dictionary    Prefer=banner-only
    ${resp}=    Get Request    proxy    /    headers=${headers}
    Check Response Is Banner Only    ${resp}    /    http://acid.matkelly.com

PROXY: Prefer Rewritten, Get Banner-Only
    &{headers}=    Create Dictionary    Prefer=rewritten
    ${resp}=    Get Request    proxy    /    headers=${headers}
    Check Response Is Banner Only    ${resp}    /    http://acid.matkelly.com

PROXY: Invalid Prefer
    &{headers}=    Create Dictionary    Prefer=raw-invalid
    ${resp}=    Get Request    proxy    /    headers=${headers}
    Should Be Equal As Strings    ${resp.status_code}    400


