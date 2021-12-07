*** Settings ***
Documentation     Ensure client-side video transclusion is working, <video> tag is added to page dynamically
Resource          resource.robot
Suite setup       Run Keywords    Reset Browsers
Suite teardown    Run Keywords    Close All Browsers


*** Variables ***
${COLL}         vid-qa
${HOST_COLL}    ${HOST}/${COLL}



*** Test Cases ***
Open Collection Page
    Open Browser To Collection Page    coll=${COLL}
    Location Should Be     ${HOST_COLL}/
    Page Should Contain    ${COLL} Search Page

Visit Video Page
    Go To    ${HOST_COLL}/20150201050303/http://www.snp.org/blog/post/2012/feb/scottish-independence-good-england
    Select Frame    //iframe
    Wait Until Page Contains Element    //video    timeout=10s
    Wait Until Page Contains Element    //source    timeout=5s


