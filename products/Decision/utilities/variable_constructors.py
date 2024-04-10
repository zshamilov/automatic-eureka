import random
import uuid
from typing import Union

from faker import Faker

from common.generators import generate_string
from products.Decision.framework.model import DiagramInOutParameterFullViewDto, ParameterType, InOutParamMetaInfo, \
     JsonGenerationVariableDto
from products.Decision.utilities.custom_models import IntValueType


def variable_construct(array_flag: bool = False, complex_flag: bool = False,
                       default_value="0", is_execute_status=True,
                       order_num=0, param_name: str = "diagram_execute_status",
                       parameter_type: str = "out",
                       parameter_version_id: str = None, type_id=2,
                       parameter_id=None, dict_flag: bool = False, dict_id=None, dict_name=None,
                       function_ids=None):
    param_type_enum = None

    if parameter_type == "in":
        param_type_enum = ParameterType.IN
    if parameter_type == "out":
        param_type_enum = ParameterType.OUT
    if parameter_type == "in_out":
        param_type_enum = ParameterType.IN_OUT

    if parameter_version_id is None:
        parameter_version_id = str(uuid.uuid4())
    if parameter_id is None:
        parameter_id = str(uuid.uuid4())

    meta_info = InOutParamMetaInfo()

    if order_num is not None:
        meta_info.orderNum = order_num

    if is_execute_status is not None:
        meta_info.isExecuteStatus = is_execute_status

    parameters = DiagramInOutParameterFullViewDto.construct(arrayFlag=array_flag,
                                                            complexFlag=complex_flag,
                                                            dictFlag=dict_flag,
                                                            dictId=dict_id,
                                                            dictName=dict_name,
                                                            metaInfo=meta_info,
                                                            parameterName=param_name,
                                                            parameterType=param_type_enum,
                                                            functionIds=function_ids,
                                                            parameterVersionId=parameter_version_id,
                                                            typeId=type_id)

    if default_value is not None:
        parameters.defaultValue = default_value

    if parameter_id is not None:
        parameters.parameterId = parameter_id

    return parameters


def validation_variable_construct(variable_name: str = generate_string(), type_id: Union[IntValueType, str] = '2',
                                  is_array: bool = False, is_complex: bool = False,
                                  is_dict: bool = False):
    parameters = JsonGenerationVariableDto.construct(variableName=variable_name,
                                                     typeId=type_id,
                                                     isArray=is_array,
                                                     isComplex=is_complex,
                                                     isDict=is_dict)
    return parameters


def primitive_value_message_contsructor(value_type: str, number_of_values: int = 1):
    fake = Faker()
    result_values = []

    if value_type == IntValueType.float.value:
        for val in range(number_of_values):
            result_values.append(fake.random_int(0, 1000000) / 1000)
    elif value_type == IntValueType.int.value:
        for val in range(number_of_values):
            result_values.append(fake.random_int(0, 1000000))
    elif value_type == IntValueType.str.value:
        for val in range(number_of_values):
            result_values.append(fake.pystr(min_chars=7, max_chars=50))
    elif value_type == IntValueType.date.value:
        for val in range(number_of_values):
            result_values.append(fake.date())
    elif value_type == IntValueType.bool.value:
        for val in range(number_of_values):
            result_values.append(random.choice([True, False]))
    elif value_type == IntValueType.dateTime.value:
        for val in range(number_of_values):
            dt = fake.date_time()
            result_values.append(dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    elif value_type == IntValueType.time.value:
        for val in range(number_of_values):
            dt = fake.date_time()
            result_values.append(fake.time())
    elif value_type == IntValueType.long.value:
        for val in range(number_of_values):
            result_values.append(fake.random_int(1000000, 1000000000))

    return result_values
