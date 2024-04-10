*** Settings ***
Documentation       [chrome_vnjKGWe0Xa.png]

Library             DataDriver    file=Zephyr_snapshot.xlsx    sheet_name=Сообщения через диаграмму рсб
Library             JSONLibrary
Library             Collections
Library             RequestsLibrary
Resource            ../Keywords/Libs/Decision/DecisionAPI.robot
Resource            ../Keywords/VariablesLib.resource

Suite Setup         New API Client    ${settings.AUTH}    ${settings.ENDPOINT}    ${USER}
Test Template       Ensure Result for Message


*** Variables ***
${settings}     ${QA}
&{USER}         LOGIN=0wmdl9my@testrestapi.com
...             PASSWORD=password


*** Test Cases ***
Message with content should return expected output QA    ${diagram_id}    ${input}    ${exptected_output}


*** Keywords ***
Ensure Result for Message
    [Tags]    snapshot
    [Arguments]    ${diagram_id}    ${input}    ${expected_output}
    ${call_uri}=    Set Variable    fcd24d69-6026-4ba2-a710-2a50068f5041
    ${fact_output}=    Input Message with Integration Module    ${call_uri}    ${input}
    ${expected_output_json}=    Convert String To Json    ${expected_output}
    Dictionaries Should Be Equal    ${fact_output}    ${expected_output_json}    ignore_keys=["initiationDate"]
