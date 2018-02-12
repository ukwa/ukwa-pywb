
*** Settings ***
Documentation     A test suite with a single test for valid login.
...
...               This test has a workflow that is created using keywords in
...               the imported resource file.
Resource          resource.robot

*** Test Cases ***
Check Collection Page
    Sleep     5s     Wait for browser startup
    Open Browser To Collection Page
    Location Should Be     http://pywb:8080/test/

Clear Any Locks
    Go To    http://pywb:8080/_locks/clear
    Location Should Be     http://pywb:8080/_locks

Check Index Page
    Go To    http://pywb:8080/test/*/http://acid.matkelly.com
    Element Text Should Be    //b[@id='count']    3 captures

Check Playback
    Go To    http://pywb:8080/test/20180203004147/http://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    "The Archival Acid Test"
    [Teardown]    Close Browser

Check Playback Locked
    Open Browser To Collection Page
    Go To    http://pywb:8080/test/20180203004147/http://acid.matkelly.com/
    Page Should Contain    Not Allowed
    [Teardown]    Close Browser

