*** Settings ***
Library                 OpenApiDriver
...                     source=decision.json
...                     origin=https://decision-qa.k8s.datasapience.ru/api
...                     disable_server_validation=True

Test Template       Validate Using Test Endpoint Keyword


*** Test Cases ***
Test Endpoint for ${method} on ${path} where ${status_code} is expected


*** Keywords ***
Validate Using Test Endpoint Keyword
    [Arguments]    ${path}    ${method}    ${status_code}
    Test Endpoint
    ...    path=${path}    method=${method}    status_code=${status_code}
