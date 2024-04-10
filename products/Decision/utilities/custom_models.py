from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal

import sqlalchemy

from products.Decision.framework.model import AttributeCreate


class IntValueType(str, Enum):
    """
    Числовой идентификатор типа
    """

    float = "0"
    int = "1"
    str = "2"
    date = "3"
    bool = "4"
    dateTime = "5"
    time = "6"
    long = "7"
    complex_type_rule = "4d16435a-7bdb-4b0b-96cb-3d40ccac3260"


class SystemCTypes(str, Enum):
    """
    Идентификаторы системных типов(для интеграций и набора правил)
    """

    task = "fedf1b3f-743e-4ce4-be11-38a229e87e00"
    task_root = "d0b2502e-dddf-4288-be4d-a82e04fe11c5"
    check_policy_result = "6086758f-2c90-4bb9-aac7-e85ac6645fd2"
    offer = "7ff5da96-20b2-4b07-986e-7448782a8f02"
    rule = "4d16435a-7bdb-4b0b-96cb-3d40ccac3260"


class StrValueType(str, Enum):
    """
    Фронтовое название типа
    """

    float = "Дробный"
    int = "Целочисленный (INT)"
    str = "Строковый"
    date = "Дата"
    bool = "Логический"
    dateTime = "Дата_время"
    time = "Время"
    long = "Целочисленный (LONG)"


@dataclass
class AttrInfo:
    attrName: str
    intAttrType: IntValueType
    isArray: bool = False
    isComplex: bool = False
    complexTypeVersionId = None


@dataclass
class VariableParams:
    """
    Класс для описания переменных конструктора диаграмм(diagram_constructor) в маркере @pytest.mark.variable_data
    Attributes
    ----------
    varName : str
        Название переменной
    varType : str
        Тип внешней переменной ("in","out","in_out" или значение класса ParameterType)
    varDataType : Any, optional
        Тип данных переменной (число 0-7, uuid комплексного типа или значение класса IntValueType)
    isArray : bool, optional
        Флаг массива (по-умолчанию False)
    isComplex : bool, optional
        Флаг комплексного типа (по-умолчанию False)
    isConst : bool, optional
        Флаг константы в узле завершения, отвечает за значение выходной(сквозной) переменной(по-умолчанию True).
        Если False требует заполнения VarValue
    varValue : str, optional
        Значение для выходной(сквозной) переменной (по-умолчанию None)
    cmplxAttrInfo : list[AttrInfo], optional
        атрибутный состав комплексной переменной (по-умолчанию None)
    """
    varName: str
    varType: str
    varDataType: Any = None
    isArray: bool = False
    isComplex: bool = False
    isConst: bool = True
    varValue: str = None
    cmplxAttrInfo: list[AttrInfo] = None


@dataclass
class KafkaSettings:
    startOffset = None
    stopOffsets = None
    topic: str
    properties = None
    parallelism = None
    serde = None
    schema: dict = None
    security = None


# @dataclass
# class OracleSettings:
@dataclass
class PostgresSettings:
    table: str
    slot: str
    timeZone: str
    plugin: str
    debesium = None


@dataclass
class SourceSettings:
    sourceType: Literal["kafka", "postgres", "oracle"]
    postgresSettings: PostgresSettings = None
    # oracleSettings: OracleSettings = None
    kafkaSettings: KafkaSettings = None


@dataclass
class TargetSettings:
    sourceType: Literal["kafka", "postgres", "oracle"]
    isSameAsSource: bool
    postgresSettings: PostgresSettings = None
    # oracleSettings: OracleSettings = None
    kafkaSettings: KafkaSettings = None


class NodeType(str, Enum):
    """
    Тип узла
    """

    varCalc = 'var_calc'
    scorecard = 'scorecard'
    communication = 'communication'
    jdbcWrite = 'insert'
    jdbcRead = 'read'
    offer = 'offer'
    externalService = 'ext_serv'
    customCode = 'script'
    rule = 'rule'
    branch = 'branch'
    fork = 'fork'
    join = 'join'
    subdiagram = 'subdiagram'
    aggregateRead = 'aggr_read'
    aggregateCompute = 'aggr_comp'
    tarantoolRead = 'tarantool_read'
    tarantoolWrite = 'tarantool_write'


class IntNodeType(int, Enum):
    """
    Числовой идентификатор узла
    """

    customCode = 1
    start = 2
    finish = 3
    jdbcRead = 4
    jdbcWrite = 5
    varCalc = 6
    rule = 7
    externalService = 8
    scorecard = 9
    branch = 10
    aggregateCompute = 11
    aggregateRead = 13
    subdiagram = 14
    communication = 16
    fork = 17
    join = 18
    offer = 19
    tarantoolRead = 20
    tarantoolWrite = 21
    offerStorageWrite = 22
    communicationHub = 23
    commHubRead = 24
    offerStorageRead = 25
    policyRead = 26
    kafkaSource = 102
    postgresCdcSource = 113
    oracleCdcSource = 115
    transformMap = 104
    transformFilter = 105
    transformConnection = 106
    transformJdbcEnrich = 109
    transformGroovy = 111
    kafkaSinc = 103


@dataclass
class NodeFullInfo:
    # TODO доделать полное описание ноды
    nodeType: IntNodeType
    nodeName: str
    linksFrom: list[str] = None
    linksTo: list[str] = None
    coordinates: tuple[int, int] = None


class PytestMarkers(str, Enum):
    variableMarker = "variable_data"
    nodeInfoMarker = "node_full_info"
    nodesMarker = 'nodes'
    saveMarker = 'save_diagram'


class BasicPrimitiveValues(Enum):
    floatBasic = 222.1
    intBasic = 111
    strBasic = "privet udachnik"
    dateBasic = "2021-11-22"
    boolBasic = True
    dateTimeBasic = "2021-11-22 15:15:45.000"
    timeBasic = "15:15:45"
    longBasic = 234


class PrimitiveToDatabaseTypeMappings:
    primitive_to_pg = {"0": sqlalchemy.Double(),
                       "1": sqlalchemy.Integer(),
                       "2": sqlalchemy.String(),
                       "3": sqlalchemy.Date(),
                       "4": sqlalchemy.Boolean(),
                       "5": sqlalchemy.DateTime(),
                       "6": sqlalchemy.Time(),
                       "7": sqlalchemy.BigInteger()}

# @dataclass
# class CommsParams:
