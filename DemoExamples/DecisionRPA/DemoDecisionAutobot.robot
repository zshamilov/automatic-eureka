*** Settings ***
Documentation       Agnostic Diagrams testing RPA

Library             Browser
Resource            ../Keywords/Libs/Decision/DecisionE2ELibrary.robot    # custom keywords
Resource            ../Keywords/Libs/Decision/DecisionAPI.robot    # custom api actions
Library             ScreenCapLibrary    # default library
Library             OperatingSystem    # default library
Resource            ../Keywords/VariablesLib.resource

Suite Setup         New API Client    ${settings.AUTH}    ${settings.ENDPOINT}    ${USER}
Suite Teardown      Close Browser


*** Variables ***
${settings}     ${QA}
&{USER}         LOGIN=0wmdl9my@testrestapi.com
...             PASSWORD=password


*** Test Cases ***
Analyze And Interact With Diagram
    Open Decision UI
    Open Diagrams Page
    ${diagrams}=    Collect Diagrams
    FOR    ${diagram}    IN    @{diagrams}
        Log To Console    ${diagram}
        ${diagram_version}=    Set Variable    ${diagram}[diagram][versionId]
        Open Diagram View    ${diagram_version}
        ${nodes}=    Collect Nodes
        FOR    ${node}    IN    @{nodes}
            ${nodeId}=    Get Attribute    ${node}    data-id
            Log To Console    ${nodeId}
            Click And Validate Node    ${nodeId}
        END
        # Exit For Loop
    END
