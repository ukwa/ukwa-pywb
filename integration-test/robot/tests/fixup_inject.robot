*** Settings ***
Documentation     Ensure fixup.js script included in rewriting replay, proxy replay, but not top frame
Resource          resource.robot
Suite teardown    Run Keywords    Delete All Sessions


*** Test Cases ***
Init Requests
    Create Session    pywb    ${HOST}

Fix-Up Included In Replay
    ${resp}=    Get Request    pywb    /qa-access/20180203004147mp_/http://acid.matkelly.com/
    Should Contain    ${resp.text}    <script src="http://pywb:8080/static/fixup.js">
 
Fix-Up Not Included Top Frame
    ${resp}=    Get Request    pywb    /qa-access/20180203004147/http://acid.matkelly.com/
    Should Not Contain    ${resp.text}    /static/fixup.js

Fix-Up Included In HTTP Proxy Replay
    ${proxies} =    Evaluate    {"https": "https://pywb:8080/", "http": "http://pywb:8080/"}
    Create Session    proxy    http://acid.matkelly.com    proxies=${proxies}
    ${resp}=    Get Request    proxy    /
    Should Contain    ${resp.text}    <script src="http://pywb.proxy/static/fixup.js">
 
Fix-Up Included In HTTPS Proxy Replay
    ${proxies} =    Evaluate    {"https": "https://pywb:8080/", "http": "http://pywb:8080/"}
    Create Session    proxy    https://acid.matkelly.com    proxies=${proxies}
    ${resp}=    Get Request    proxy    /
    Should Contain    ${resp.text}    <script src="https://pywb.proxy/static/fixup.js">
  
