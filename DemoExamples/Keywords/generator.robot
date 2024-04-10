*** Settings ***
Library     FakerLibrary
Library     DateTime
Library     Collections
Library     String


*** Variables ***
@{CURRENCY_CHOICES}         810    100-999
@{CURRENCY_WEIGHTS}         80    20

@{COMMISSION_CHOICES}       0    1-5000
@{COMMISSION_WEIGHTS}       75    25

@{STATE_CHOICES}            HOLD    SUCCESS    REJECT
@{STATE_WEIGHTS}            10    80    10

@{SUBTYPE_CHOICES}          CREDIT    ZACHISLENIE    POKUPKA
@{SUBTYPE_WEIGHTS}          10    10    80

@{MCC_CHOICES}              4722    4723    1000-9999
@{MCC_WEIGHTS}              50    30    20

@{COUNTRY_CHOICES}          RUSSIAN FEDERATION    TODO
@{COUNTRY_WEIGHTS}          90    10

@{CITY_CHOICES}             MOSKVA    TODO
@{CITY_WEIGHTS}             70    10

@{REVERSAL_CHOICES}         true    false
@{REVERSAL_WEIGHTS}         15    85

@{CHANNEL_CHOICES}          mobile    ib    ufo    ufo-cc    ufo-dsa
@{CHANNEL_WEIGHTS}          20    20    20    20    20

@{CALLPOINT_CHOICES}        catalog    burst    showcase    063/01    063/02    063/03    TODO
@{CALLPOINT_WEIGHTS}        10    10    10    10    10    10    40

@{SERVICE_CODE_CHOICES}     123    456    21    22    32    10-999
@{SERVICE_CODE_WEIGHTS}     10    10    10    10    10    50

@{SERVICE_NAME_CHOICES}     тема для КК(1)    тема для КК(2)    тема для ПК(1)    тема для ПК(2)    тема для НС    TODO
@{SERVICE_NAME_WEIGHTS}     10    10    10    10    10    50


*** Keywords ***
Weighted Choice
    [Arguments]    ${choices}    ${weights}
    ${choice}=    Evaluate
    ...    random.choices(${choices}, weights=${weights}, k=1)[0]
    ...    random
    ...    choices=${choices}
    ...    weights=${weights}
    RETURN    ${choice}

Generate RTO Data
    [Arguments]    @{customers}
    ${utrnno}=    FakerLibrary.Random Int    100    99999
    ${virtual_number}=    FakerLibrary.Random Int    1    1000000
    ${auth_date}=    Get Current Date    result_format=%Y-%m-%d %H:%M:%S.%f    exclude_millis=3
    ${auth_amt}=    FakerLibrary.Random Int    0    2000000
    ${auth_curr}=    Weighted Choice    ${CURRENCY_CHOICES}    ${CURRENCY_WEIGHTS}
    ${trans_commission}=    Weighted Choice    ${COMMISSION_CHOICES}    ${COMMISSION_WEIGHTS}
    ${state_name}=    Weighted Choice    ${STATE_CHOICES}    ${STATE_WEIGHTS}
    ${trans_subtype}=    Weighted Choice    ${SUBTYPE_CHOICES}    ${SUBTYPE_WEIGHTS}
    ${mcc}=    Weighted Choice    ${MCC_CHOICES}    ${MCC_WEIGHTS}
    ${total_amt}=    FakerLibrary.Random Int    0    5000000
    ${country}=    Weighted Choice    ${COUNTRY_CHOICES}    ${COUNTRY_WEIGHTS}
    ${city}=    Weighted Choice    ${CITY_CHOICES}    ${CITY_WEIGHTS}
    ${reversal}=    Weighted Choice    ${REVERSAL_CHOICES}    ${REVERSAL_WEIGHTS}
    ${gold_customer_id}=    Weighted Choice    ${customers}    ${[95, 5]}
    &{data}=    Create Dictionary
    ...    UTRNNO=${utrnno}
    ...    VIRTUAL_NUMBER=${virtual_number}
    ...    AUTH_DATE=${auth_date}
    ...    AUTH_AMT=${auth_amt}
    ...    AUTH_CURR=${auth_curr}
    ...    TRANS_COMMISSION=${trans_commission}
    ...    STATE_NAME=${state_name}
    ...    TRANS_SUBTYPE=${trans_subtype}
    ...    MCC=${mcc}
    ...    TOTAL_AMT=${total_amt}
    ...    COUNTRY=${country}
    ...    CITY=${city}
    ...    REVERSAL=${reversal}
    ...    GOLD_CUSTOMER_ID=${gold_customer_id}
    RETURN    &{data}

Generate NBO Data
    [Arguments]    @{customers}
    ${gcid}=    Evaluate    random.choice(${customers})    random    customers=@{customers}
    ${channel}=    Weighted Choice    ${CHANNEL_CHOICES}    ${CHANNEL_WEIGHTS}
    ${callpoint}=    Weighted Choice    ${CALLPOINT_CHOICES}    ${CALLPOINT_WEIGHTS}
    ${service_code}=    Weighted Choice    ${SERVICE_CODE_CHOICES}    ${SERVICE_CODE_WEIGHTS}
    ${service_name}=    Weighted Choice    ${SERVICE_NAME_CHOICES}    ${SERVICE_NAME_WEIGHTS}
    ${birthdate}=    FakerLibrary.Date Between    1930-01-01    2007-01-01    format=%Y-%m-%d
    &{data}=    Create Dictionary
    ...    GCID=${gcid}
    ...    channel=${channel}
    ...    callpoint=${callpoint}
    ...    serviceCode=${service_code}
    ...    serviceName=${service_name}
    ...    birthdate=${birthdate}
    RETURN    &{data}

Generate Key
    ${key}=    Evaluate    str(uuid.uuid4())    uuid
    &{data}=    Create Dictionary    key=${key}
    RETURN    &{data}
