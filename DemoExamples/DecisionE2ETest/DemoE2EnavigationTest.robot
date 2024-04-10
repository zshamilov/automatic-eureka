*** Settings ***
Resource            ../Keywords/Libs/Decision/DecisionE2ELibrary.robot
Resource            ../Keywords/Libs/Decision/ClickKeywords.robot

Suite Setup         Open Browser And Set Viewport
Suite Teardown      Close Browser
Test Setup          Navigate To URL    https://decision-qa.k8s.datasapience.ru


*** Test Cases ***
Navigate And Interact With Custom Codes
    [Documentation]    This test navigates to the Custom Codes section and simulates interactions within it.
    Navigate To URL    https://decision-qa.k8s.datasapience.ru/development/custom-codes
    Click On Custom Codes
    # Additional steps to interact with elements within the Custom Codes section

Interact With Data Types
    [Documentation]    This test focuses on interactions within the Data Types section, such as creating or modifying data types.
    Navigate To URL    https://decision-qa.k8s.datasapience.ru/development/data-types
    Click On Data Types
    # Steps to create a new data type or modify an existing one

Explore Communication Channels
    [Documentation]    Tests the exploration and configuration of communication channels.
    Navigate To URL    https://decision-qa.k8s.datasapience.ru/development/communication-channels
    Click On Communication Channels
    # Steps to explore or configure communication channels


*** Keywords ***
Click On Communication Channels
    ${selector}=    Set Variable    aria/Каналы коммуникации
    Click On Element    ${selector}
