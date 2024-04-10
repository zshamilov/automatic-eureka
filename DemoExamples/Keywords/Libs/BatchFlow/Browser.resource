*** Settings ***
Library     Browser


*** Variables ***
${BROWSER}              chromium
${VIEWPORT_WIDTH}       1980
${VIEWPORT_HEIGHT}      1060


*** Keywords ***
Open Browser And Set Viewport
    New Browser    ${BROWSER}    headless=False
    New Context    viewport={'width': ${VIEWPORT_WIDTH}, 'height': ${VIEWPORT_HEIGHT}}
    New Page

Navigate To URL
    [Arguments]    ${url}
    Go To    ${url}
