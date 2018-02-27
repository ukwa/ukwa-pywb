*** Settings ***
Documentation     Verify different access settings in reading-room, open-access and qa-access collections
Resource          resource.robot
Suite setup       Run Keywords    Reset Browsers
Suite teardown    Run Keywords    Close All Browsers


*** Test Cases ***
Open Browser
    Open Browser To Home Page

Check EN Home Page
    Go To    ${HOST}/en
    Page Should Contain    UK Web Archive Access System

Check CY Home Page
    Go To    ${HOST}/cy
    Page Should Contain    System Mynediad Archif Gwe'r DU

Check EN Replay Acid Test
    Go To    ${HOST}/en/qa-access/2018/http://acid.matkelly.com/
    Wait Until Page Contains    Archived On:    timeout=10s

Check CY Replay Acid Test
    Go To    ${HOST}/cy/qa-access/2018/http://acid.matkelly.com/
    Wait Until Page Contains    Archif Ar:    timeout=10s

    
