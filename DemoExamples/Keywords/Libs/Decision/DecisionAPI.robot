*** Settings ***
Documentation       This is a resource file, that can contain variables and keywords.
...                 Keywords defined here can be used where this Keywords.resource in loaded.

Library             ./DecisionAPILibrary.py    tc_session_reset=False
Library             JSONLibrary
Library             RequestsLibrary
Library             Collections


*** Variables ***
${settings}     ${EMPTY}


*** Keywords ***
New API Client
    [Arguments]    ${settings.AUTH}    ${settings.ENDPOINT}    ${USER}
    Set Auth    ${settings.AUTH}    ${settings.REALM}
    Set Endpoint    ${settings.ENDPOINT}
    Set User    ${USER.LOGIN}    ${USER.PASSWORD}
    Add API client    decision.frontend    ${EMPTY}
    Login User

Collect Diagrams
    ${response}=    Get Deploys
    RETURN    ${response}[content]

Input Message with Integration Module
    [Arguments]    ${uri}    ${input}
    Log To Console    ${input}
    ${input_json}=    Convert String To Json    ${input}
    ${response}=    Input Message Uri    ${uri}    ${input_json}    ${settings.INT_ENDPOINT}
    Log To Console    ${response.json()}
    RETURN    ${response.json()}
