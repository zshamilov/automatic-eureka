*** Settings ***
Documentation       Agnostic Diagrams testing RPA

Library             Browser
Resource            ../Keywords/Libs/Decision/DecisionE2ELibrary.robot    # custom keywords
Resource            ../Keywords/Libs/Decision/DecisionAPI.robot    # custom api actions
Library             ScreenCapLibrary    # default library
Library             OperatingSystem    # default library
Resource            ../Keywords/VariablesLib.resource

Test Setup          New API Client
Test Teardown       Close Browser
Test Template       Login with invalid credentials should fail


*** Test Cases ***    USERNAME    PASSWORD
Invalid User Name    invalid    ${VALID PASSWORD}
Invalid Password    ${VALID USER}    invalid
Invalid User Name and Password    invalid    invalid
Empty User Name    ${EMPTY}    ${VALID PASSWORD}
Empty Password    ${VALID USER}    ${EMPTY}
Empty User Name and Password    ${EMPTY}    ${EMPTY}


*** Keywords ***
Login with invalid credentials should fail
    [Arguments]    ${username}    ${password}
    Log Many    ${username}    ${password}
