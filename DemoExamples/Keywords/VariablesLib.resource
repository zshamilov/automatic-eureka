*** Settings ***
Documentation       This is a resource file, that can contain variables and keywords.
...                 Keywords for manipulating browser


*** Variables ***
&{GPB}      env=GPB
...         URL=https://decision.gpb-stress.datasapience.ru
...         DIAGRAMS_PAGE=https://decision-qa.k8s.datasapience.ru/administration/deploy-diagram
...         ENDPOINT=https://decision.gpb-stress.datasapience.ru/api
...         AUTH=https://auth.gpb-stress.datasapience.ru
...         REALM=cmocean
...         LOGIN=writer
...         PASSWORD=writer
...         INT_ENDPOINT=https://decision-integration.gpb-stress.datasapience.ru
...         TOKEN=${EMPTY}
&{QA}       env=QA
...         URL=https://decision-qa.k8s.datasapience.ru
...         DIAGRAMS_PAGE=https://decision-qa.k8s.datasapience.ru/administration/deploy-diagram
...         ENDPOINT=https://decision-qa.k8s.datasapience.ru/api
...         AUTH=https://auth.k8s.datasapience.ru/auth
...         REALM=qa
...         LOGIN=urza
...         PASSWORD=g6a6d6za
...         INT_ENDPOINT=https://decision-integration-qa.k8s.datasapience.ru
...         TOKEN=${EMPTY}
