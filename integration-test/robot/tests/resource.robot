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
${LOGIN URL}         ${APPLICATION}/_login
${WELCOME URL}       ${APPLICATION}/test/
${ERROR URL}         ${APPLICATION}/error.html

*** Keywords ***
Open Browser To Collection Page
    [Arguments]    ${browser}=firefox
    Open Browser    ${WELCOME URL}    browser=${browser}    remote_url=${SELENIUM}

Open Browser To Login Page
    Open Browser    ${LOGIN URL}    browser=${BROWSER}    remote_url=${SELENIUM}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    Login Page Should Be Open

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
