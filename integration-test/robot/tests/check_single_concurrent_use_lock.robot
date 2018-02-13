
*** Settings ***
Documentation     A test suite that verifies the behaviour of the single-concurrent-usage lock functionality
...
...               This test has a workflow that is created using keywords in
...               the imported resource file.
Resource          resource.robot

*** Test Cases ***
Check Collection Page
    Sleep     30s     Wait for browser startup
    Open Browser To Collection Page
    Location Should Be     http://pywb:8080/test/

Clear All Locks
    Go To    http://pywb:8080/_locks/reset
    Location Should Be     http://pywb:8080/_locks

Check Index Page
    Go To    http://pywb:8080/test/*/http://acid.matkelly.com
    Wait Until Page Contains Element    //b[@id='count']
    Element Text Should Be    //b[@id='count']    3 captures

Check Playback
    Go To    http://pywb:8080/test/20180203004147/http://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    "The Archival Acid Test"
    [Teardown]    Close Browser

Check Locks
    Open Browser To Collection Page
    Go To    http://pywb:8080/_locks
    Page Should Contain    Sessions and Locks
    Page Should Contain Element    //li[@class='url-lock']    limit=1

Check Playback Locked
    Go To    http://pywb:8080/test/20180203004147/http://acid.matkelly.com/
    Page Should Contain    Not Allowed
    [Teardown]    Close Browser

Check Lock Expired, Playback Allowed
    Open Browser To Collection Page
    Sleep   30s  Wait for lock expiry
    Go To    http://pywb:8080/test/20180203004147/http://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    "The Archival Acid Test"

Check Playback 2 Logout Release Lock
    Open Browser To Collection Page
    Go To    http://pywb:8080/test/20180203004147/http://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    "The Archival Acid Test"
    Go To   http://pywb:8080/_logout
    Location Should Be     http://pywb:8080/
    [Teardown]    Close Browser

Check Playback 3
    Open Browser To Collection Page
    Go To    http://pywb:8080/test/20180203004147/http://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    "The Archival Acid Test"
    [Teardown]    Close Browser


