*** Settings ***
Documentation     Check Memento Prefer header using Requests to redirect to raw or rewritten resources
Resource          resource.robot
Suite teardown    Run Keywords    Delete All Sessions


*** Test Cases ***
Init Requests HTTP
    Create Session    pywb    ${HOST}

Prefer Raw from TimeGate
    &{headers}=    Create Dictionary    Prefer=raw
    ${resp}=    Get Request    pywb    /qa-access/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Raw    ${resp}    /qa-access/20180203004147id_/http://acid.matkelly.com/

Prefer Rewritten from TimeGate
    &{headers}=    Create Dictionary    Prefer=rewritten
    ${resp}=    Get Request    pywb    /qa-access/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Rewritten    ${resp}     /qa-access/20180203004147mp_/http://acid.matkelly.com/

Prefer Raw from Memento Url
    &{headers}=    Create Dictionary    Prefer=raw
    ${resp}=    Get Request    pywb    /qa-access/2018/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Raw    ${resp}    /qa-access/20180203004147id_/http://acid.matkelly.com/

Prefer Rewritten from Memento Url
    &{headers}=    Create Dictionary    Prefer=rewritten
    ${resp}=    Get Request    pywb    /qa-access/2017/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Rewritten    ${resp}     /qa-access/20180203004147mp_/http://acid.matkelly.com/

Prefer Raw from Memento Url (Exact Timestamp)
    &{headers}=    Create Dictionary    Prefer=raw
    ${resp}=    Get Request    pywb    /qa-access/20180203004147mp_/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Raw    ${resp}    /qa-access/20180203004147id_/http://acid.matkelly.com/

Prefer Rewritten from Memento Url (Exact Timestamp)
    &{headers}=    Create Dictionary    Prefer=rewritten
    ${resp}=    Get Request    pywb    /qa-access/20180203004147id_/http://acid.matkelly.com/    headers=${headers}
    Check Response Is Rewritten    ${resp}     /qa-access/20180203004147mp_/http://acid.matkelly.com/

Prefer Error Invalid Prefer
    &{headers}=    Create Dictionary    Prefer=invalid
    ${resp}=    Get Request    pywb    /qa-access/20180203004147mp_/http://acid.matkelly.com/    headers=${headers}
    Should Be Equal As Strings    ${resp.status_code}    400
    


