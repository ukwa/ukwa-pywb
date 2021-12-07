*** Settings ***
Documentation     Verify different access settings in reading-room, open-access and qa-access collections
Resource          resource.robot
Suite setup       Run Keywords    Reset Browsers
Suite teardown    Run Keywords    Close All Browsers


*** Test Cases ***
Open Browser
    Open Browser To Home Page


Reading Room -- Check Blocked (451)
    Check Blocked    ${HOST}/reading-room/httpbin.org/anything

Reading Room -- Check Excluded (404)
    Check Excluded    ${HOST}/reading-room/httpbin.org/anything/something

Reading Room -- Check Excluded, Sub-Path
    Check Excluded    ${HOST}/reading-room/httpbin.org/anything/something/else

Reading Room -- Check Allowed, Different Script
    Check Allowed    ${HOST}/reading-room/http://www.cs.odu.edu/~mkelly/acid/externalScript.js    text=wombat


Open Access -- Check Blocked (451)
    Check Blocked    ${HOST}/open-access/httpbin.org/anything

Open Access -- Check Excluded (404)
    Check Excluded    ${HOST}/open-access/httpbin.org/anything/something

Open Access -- Check Allowed Explicitly, Sub-path 
    Check Allowed    ${HOST}/open-access/httpbin.org/anything/something/else    text="http://httpbin.org/anything/something/else"
    
Open Access -- Check Blocked By Default (451)
    Check Blocked    ${HOST}/open-access/http://www.cs.odu.edu/~mkelly/acid/externalScript.js


QA Access -- All Allowed
    Check Allowed    ${HOST}/qa-access/httpbin.org/anything    text="http://httpbin.org/anything"
    Check Allowed    ${HOST}/qa-access/httpbin.org/anything/something    text="http://httpbin.org/anything/something"
    Check Allowed    ${HOST}/qa-access/httpbin.org/anything/something/else    text="http://httpbin.org/anything/something/else"
    Check Allowed    ${HOST}/qa-access/http://www.cs.odu.edu/~mkelly/acid/externalScript.js    text=wombat

