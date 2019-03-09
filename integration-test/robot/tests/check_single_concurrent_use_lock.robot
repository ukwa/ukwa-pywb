
*** Settings ***
Documentation     A test suite that verifies the behaviour of the single-concurrent-usage lock functionality. 
...               FIXME Convert to use http://rtomac.github.io/robotframework-selenium2library/doc/Selenium2Library.html#Switch%20Browser
...
...               This test has a workflow that is created using keywords in
...               the imported resource file.
Resource          resource.robot
Suite setup       Run Keywords    Reset Browsers
Suite teardown    Run Keywords    Close All Browsers


*** Variables ***
${COLL}         reading-room
${HOST_COLL}    ${HOST}/${COLL}


*** Test Cases ***
1st Browser: Open Collection Page
    Open Browser To Collection Page    coll=${COLL}
    Location Should Be     ${HOST_COLL}/
    Page Should Contain    ${COLL} Search Page

1st Browser: Clear All Locks
    Go To    ${HOST}/_locks/reset
    Location Should Be     ${HOST}/_locks

1st Browser: Index Page
    Go To    ${HOST_COLL}/*/http://acid.matkelly.com/
    Wait Until Page Contains    3 captures of http://acid.matkelly.com/

1st Browser: Acid Test Replay
    Go To    ${HOST_COLL}/20180203004147/http://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    The Archival Acid Test

1st Browser: Acid Test No Red Dots
    Execute JavaScript    window.scroll(0, 100)
    Sleep   1s
    Page Should Contain Element    //img[@src='red.png']    limit=0

1st Browser: Confirm One Page Locked
    Go To    ${HOST}/_locks
    Page Should Contain    Sessions and Locks
    Page Should Contain Element    //li[@class='url-lock']    limit=1

2nd Browser: Open, Acid Test Page Replay LOCKED
    Open Browser To Collection Page    browser=chrome
    Go To    ${HOST_COLL}/20180203004147/http://acid.matkelly.com/
    Select Frame    //iframe
    Page Should Contain    Access to this resource is currently not allowed.

2nd Browser: Acid Test Page Replay LOCKED, Using Different Locales (EN and CY)
    Go To    ${HOST}/cy/reading-room/20180203004147/http://acid.matkelly.com/
    Select Frame    //iframe
    Page Should Contain    Ni chaniateir mynediad i'r adnodd hwn ar hyn o bryd.
    Go To    ${HOST}/en/reading-room/20180203004147/http://acid.matkelly.com/
    Select Frame    //iframe
    Page Should Contain    Access to this resource is currently not allowed.

2nd Browser: Logout Different Session, Replay Still LOCKED
    Go To    ${HOST}/_logout
    Location Should Be     ${HOST}/
    Go To    ${HOST_COLL}/20180203004147/http://acid.matkelly.com/
    Select Frame    //iframe
    Page Should Contain    Access to this resource is currently not allowed.

1st Browser: Acid Test Page Replay UNLOCKED (Original Session)
    Switch Browser    1
    Go To    ${HOST_COLL}/20180203004147/http://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    The Archival Acid Test

2nd Browser: Wait for Lock Expiry, Acid Test Page Replay UNLOCKED, New Lock Aquired
    Switch Browser    2
    Log To Console    Wait for 30s for lock expiry
    Sleep   30s  Wait for lock expiry
    Go To    ${HOST_COLL}/20180203004147/http://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    The Archival Acid Test

2nd Browser: Verify Lock, Logout, Lock Released
    Go To    ${HOST}/_locks
    Page Should Contain Element    //li[@class='url-lock']    limit=1
    Go To    ${HOST}/_logout
    Location Should Be     ${HOST}/
    Go To    ${HOST}/_locks
    Page Should Contain    No Session Locks

1st Browser: Acid Test Page Replay UNLOCKED
    Switch Browser    1
    Go To    ${HOST_COLL}/20180203004147/http://acid.matkelly.com/
    Wait Until Page Contains Element    //b[@id='title_or_url']    timeout=10s
    Element Text Should Be    //b[@id='title_or_url']    The Archival Acid Test


