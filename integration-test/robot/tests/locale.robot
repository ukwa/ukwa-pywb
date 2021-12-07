*** Settings ***
Documentation     Verify locale-specific routes and localized strings
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
    Page Should Contain    System fynediad Archif We y DG

Check EN Replay Acid Test
    Go To    ${HOST}/en/qa-access/2018/http://acid.matkelly.com/
    Wait Until Page Contains    Language:    timeout=10s
    Page Should Contain    Back to Calendar

Check CY Replay Acid Test
    Go To    ${HOST}/cy/qa-access/2018/http://acid.matkelly.com/
    Wait Until Page Contains    Iaith:    timeout=10s
    Page Should Contain    Dychwelyd i'r Calendr

    
