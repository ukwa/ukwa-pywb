
*** Settings ***
Documentation     A test suite that verifies the behaviour of the single-concurrent-usage lock functionality
...
...               This test has a workflow that is created using keywords in
...               the imported resource file.
Resource          resource.robot

*** Test Cases ***
Reset Browsers
    Log To Console    Waiting for 20s for browser startup
    Sleep     20s     Wait for browser startup
    Close All Browsers

1st Browser: Open Collection Page
    Open Browser To Collection Page
    Location Should Be     http://pywb:8080/test/
    Page Should Contain    test Search Page

1st Browser: Clear All Locks
    Go To    http://pywb:8080/_locks/reset
    Location Should Be     http://pywb:8080/_locks

1st Browser: Index Page
    Go To    http://pywb:8080/test/*/http://acid.matkelly.com
    Wait Until Page Contains Element    //b[@id='count']
    Element Text Should Be    //b[@id='count']    3 captures

1st Browser: Acid Test Replay
    Go To    http://pywb:8080/test/20180203004147/http://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    "The Archival Acid Test"

1st Browser: Acid Test No Red Dots
    Execute JavaScript    window.scroll(0, 100)
    Sleep   1s
    Page Should Contain Element    //img[@src='red.png']    limit=0

1st Browser: Confirm One Page Locked
    Go To    http://pywb:8080/_locks
    Page Should Contain    Sessions and Locks
    Page Should Contain Element    //li[@class='url-lock']    limit=1

2nd Browser: Open, Acid Test Page Replay LOCKED
    Open Browser To Collection Page    browser=chrome
    Go To    http://pywb:8080/test/20180203004147/http://acid.matkelly.com/
    Page Should Contain    Not Allowed

2nd Browser: Logout Different Session, Replay Still LOCKED
    Go To    http://pywb:8080/_logout
    Location Should Be     http://pywb:8080/
    Go To    http://pywb:8080/test/20180203004147/http://acid.matkelly.com/
    Page Should Contain    Not Allowed

1st Browser: Acid Test Page Replay UNLOCKED (Original Session)
    Switch Browser    1
    Go To    http://pywb:8080/test/20180203004147/http://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    "The Archival Acid Test"

2nd Browser: Wait for Lock Expiry, Acid Test Page Replay UNLOCKED, New Lock Aquired
    Switch Browser    2
    Log To Console    Wait for 30s for lock expiry
    Sleep   30s  Wait for lock expiry
    Go To    http://pywb:8080/test/20180203004147/http://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    "The Archival Acid Test"

2nd Browser: Verify Lock, Logout, Lock Released
    Go To    http://pywb:8080/_locks
    Page Should Contain Element    //li[@class='url-lock']    limit=1
    Go To    http://pywb:8080/_logout
    Location Should Be     http://pywb:8080/
    Go To    http://pywb:8080/_locks
    Page Should Contain    No Session Locks

1st Browser: Acid Test Page Replay UNLOCKED
    Switch Browser    1
    Go To    http://pywb:8080/test/20180203004147/http://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    "The Archival Acid Test"
    [Teardown]    Close All Browsers


