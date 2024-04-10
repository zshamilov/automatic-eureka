*** Settings ***
Library     Browser


*** Keywords ***
Click On Element
    [Arguments]    ${selector}
    Click    ${selector}

Click On Diagrams
    ${selector}=    Set Variable    text=Диаграммы
    Click On Element    ${selector}

Click On Custom Codes
    ${selector}=    Set Variable    text=Кастомные коды
    Click On Element    ${selector}

Click On Development
    ${selector}=    Set Variable    aria/Разработка
    Click On Element    ${selector}

Click On Data Types
    ${selector}=    Set Variable    text=Пользовательские типы данных
    Click On Element    ${selector}
