*** Settings ***
Documentation       This is a resource file, that can contain variables and keywords.
...                 Keywords for manipulating browser

Library             Browser
Resource            ./Browser.resource


*** Keywords ***
Open BatchFlow UI
    Open Browser And Set Viewport
    Fill Login Form