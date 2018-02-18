*** Settings ***
Documentation     A resource file with reusable keywords and variables.
...
...               The system specific keywords created here form our own
...               domain specific language. They utilize keywords provided
...               by the imported SeleniumLibrary.
Library           SeleniumLibrary

*** Variables ***
${SELENIUM}          http://hub:4444/wd/hub
${APPLICATION}       http://pywb:8080
${BROWSER}           Firefox
${DELAY}             0
${VALID USER}        demo
${VALID PASSWORD}    mode
${WELCOME URL}       ${APPLICATION}/test/
${ERROR URL}         ${APPLICATION}/error.html

*** Keywords ***
Reset Browsers
    Log To Console    Waiting for 20s for browser startup
    Sleep     20s     Wait for browser startup
    Close All Browsers

Open Browser To Collection Page
    [Arguments]    ${coll}=test    ${browser}=firefox
    Open Browser    ${APPLICATION}/${coll}/    browser=${browser}    remote_url=${SELENIUM}
    Set Selenium Speed    ${DELAY}

Open Browser To Home Page
    Open Browser    ${APPLICATION}/    browser=${BROWSER}    remote_url=${SELENIUM}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}

Check Excluded
    [Arguments]    ${url}
    Go To   ${url}
    Page Should Contain    Url Not Found

Check Blocked
    [Arguments]    ${url}
    Go To   ${url}
    Page Should Contain    Access Blocked

Check Allowed
    [Arguments]    ${url}   ${text}
    Go To   ${url}
    Page Should Not Contain    Url Not Found
    Page Should Not Contain    Access Blocked
    Page Should Contain    ${text}

Login Page Should Be Open
    Title Should Be    Login Page

Go To Login Page
    Go To    ${LOGIN URL}
    Login Page Should Be Open

Input Username
    [Arguments]    ${username}
    Input Text    username_field    ${username}

Input Password
    [Arguments]    ${password}
    Input Text    password_field    ${password}

Submit Credentials
    Click Button    login_button

Welcome Page Should Be Open
    Location Should Be    ${WELCOME URL}
    Title Should Be    Welcome Page
