*** Settings ***
Documentation       This is a resource file, that can contain variables and keywords.
...                 Keywords for manipulating browser

Library             Browser
Resource            ./Browser.resource


*** Keywords ***
Open Decision UI
    Open Browser And Set Viewport
    Fill Login Form

Open Diagram View
    [Arguments]    ${version_id}
    Log To Console    ${version_id}
    Go To    https://decision-qa.k8s.datasapience.ru/development/diagrams/view/${version_id}/diagram

Click And Validate Node
    [Arguments]    ${node}
    Click    css=[data-testid="rf__node-${node}"]
    Log To Console    Validating node editor for: ${node}
    Browser.Take Screenshot    output${/}${node}-result.png    selector=css=[data-testid="rf__node-${node}"]

Collect Nodes
    ${nodes}=    Get Elements    css=[data-testid^="rf__node-"]
    Log To Console    ${nodes}
    RETURN    @{nodes}

Fill Login Form
    Go To    ${settings.URL}
    Type Text    [name="username"]    ${USER.LOGIN}
    Type Text    [name="password"]    ${USER.PASSWORD}
    Click    [name="login"]

Open Diagrams Page
    Go To    ${settings.DIAGRAMS_PAGE}
