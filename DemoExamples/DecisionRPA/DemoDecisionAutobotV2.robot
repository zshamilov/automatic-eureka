*** Settings ***
Documentation       This is RPA test suite for collecting all existing diagrams and performing checks on nodes.

Library             Browser
Resource            ../Keywords/Libs/Decision/DecisionE2ELibrary.robot
Resource            ../Keywords/VariablesLib.resource
Resource            ../Keywords/Libs/Decision/DecisionAPI.robot    # custom api actions

Suite Setup         New API Client    ${settings.AUTH}    ${settings.ENDPOINT}    ${USER}
Test Setup          Open Decision UI
Test Teardown       Close Browser


*** Variables ***
${settings}     ${QA}
&{USER}         LOGIN=0wmdl9my@testrestapi.com
...             PASSWORD=password


*** Test Cases ***
Collect And Process Diagrams
    ${diagrams}=    Collect Diagrams
    FOR    ${diagram}    IN    @{diagrams}
        ${diagram_id}=    Set Variable    ${diagram}[diagram][versionId]
        Open Diagram Editor    ${diagram_id}
        Collect And Check Nodes
    END


*** Keywords ***
Open Decision UI
    Open Browser And Set Viewport
    Go To    ${settings.URL}
    Type Text    [name="username"]    ${USER.LOGIN}
    Type Text    [name="password"]    ${USER.PASSWORD}
    Click    [name="login"]

Open Diagrams Page
    Go To    ${settings.DIAGRAMS_PAGE}

Click And Validate Node
    [Arguments]    ${node}
    Click    css=[data-testid="rf__node-${node}"]
    Log To Console    Validating node editor for: ${node}
    Browser.Take Screenshot    output${/}${node}-result.png    selector=css=[data-testid="rf__node-${node}"]

Collect Nodes
    ${nodes}=    Get Elements    css=[data-testid^="rf__node-"]
    Log To Console    ${nodes}
    RETURN    @{nodes}

Navigate To Diagrams Catalog
    Go To    ${settings.DIAGRAMS_PAGE}

Take Screenshot And Return To Catalog
    Take Screenshot
    Navigate To Diagrams Catalog

Open Diagram Editor
    [Arguments]    ${version_id}
    Log To Console    ${version_id}
    Go To    https://decision-qa.k8s.datasapience.ru/development/diagrams/view/${version_id}/diagram

Collect And Check Nodes
    ${nodes}=    Collect Nodes
    FOR    ${node}    IN    @{nodes}
        ${nodeId}=    Get Attribute    ${node}    data-id
        Perform check for node type    ${nodeId}
        Click And Validate Node    ${nodeId}
    END

Perform check for node type
    [Arguments]    ${nodeId}
    ${node_type}=    Get Text    css=[data-id="${nodeId}"] >> span.custom-diagram-node__type:nth-child(1)
    IF    '${node_type}' == 'conditional'
        Check Conditional Node    ${nodeId}
    ELSE IF    '${node_type}' == 'process'
        Check Process Node    ${nodeId}
    ELSE
        Log    Unknown node type: ${node_type}
    END

Check Conditional Node
    [Arguments]    ${nodeId}
    Log    Performing checks for a conditional node

Check Process Node
    [Arguments]    ${nodeId}
    Log    Performing checks for a process node
