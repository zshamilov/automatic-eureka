import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import ScriptFullView, ScriptVariableViewWithoutVersionIdDto, ResponseDto, \
    CommunicationChannelFullViewDto, DataSourceType1
from products.Decision.framework.steps.decision_steps_communication_api import get_communication_channel, update_channel
from products.Decision.utilities.communication_constructors import *


@allure.epic("Каналы коммуникации")
@allure.feature("Обновление канала")
@pytest.mark.scenario("DEV-10141")
class TestCommunicationUpdate:

    @allure.story("Каналу коммуникаций можно обновить поля имя и описание")
    @allure.title("Обновить имя и описание канала, проверить, что обновилось")
    @pytest.mark.smoke
    def test_update_communication_name_descr(self, super_user,
                                             create_python_code_int_vars,
                                             create_communication_gen):
        with allure.step("Создание пользовательского кода"):
            script_view: ScriptFullView = create_python_code_int_vars["code_view"]
            inp_var: ScriptVariableViewWithoutVersionIdDto = create_python_code_int_vars["inp_var"]
        with allure.step("Задание параметров канала коммуникаций"):
            channel_name = "channel_" + generate_string()
            var = communication_var_construct(variable_name="comm_v",
                                              script_var_name=inp_var.variableName,
                                              primitive_type_id=inp_var.primitiveTypeId,
                                              data_source_type=DataSourceType1.USER_INPUT)
            comm = communication_construct(communication_channel_name=channel_name,
                                           script_version_id=script_view.versionId,
                                           communication_variables=[var],
                                           description="made_in_test")
        with allure.step("Создание канала коммуникаций"):
            create_response: ResponseDto = create_communication_gen.create_communication_channel(
                communication_channel_body=comm)
        with allure.step("Обновление имени и описание канала коммуникаций"):
            up_body = update_channel_construct(communication_channel_name="updated_" + channel_name,
                                               script_version_id=script_view.versionId,
                                               communication_variables=[var],
                                               description="updated")
            update_channel(super_user,
                           version_id=create_response.uuid,
                           body=up_body)
        with allure.step("Поиск канала коммуникаций по идентификатору версии"):
            search_response = CommunicationChannelFullViewDto.construct(
                **get_communication_channel(super_user, version_id=create_response.uuid).body)
        with allure.step("Проверка, что имя и описание обновлены"):
            assert search_response.objectName == "updated_" + channel_name \
                   and search_response.description == "updated"

    @allure.story("В канале коммуникаций можно заменить один пользовательский код на другой, изменив поля имя "
                  "скрипта, версия скрипта, переменные")
    @allure.title("Обновить скрипт в канале, проверить, что обновлён")
    @pytest.mark.smoke
    def test_update_communication_custom_code(self, super_user,
                                              create_python_code_int_vars,
                                              create_groovy_code_int_vars,
                                              create_communication_gen):
        with allure.step("Создание первого пользовательского кода"):
            p_script_view: ScriptFullView = create_python_code_int_vars["code_view"]
            p_inp_var: ScriptVariableViewWithoutVersionIdDto = create_python_code_int_vars["inp_var"]
        with allure.step("Создание второго пользовательского кода"):
            g_script_view: ScriptFullView = create_groovy_code_int_vars["code_view"]
            g_inp_var: ScriptVariableViewWithoutVersionIdDto = create_groovy_code_int_vars["inp_var"]
        with allure.step("Задание параметров канала коммуникаций"):
            channel_name = "channel_" + generate_string()
            var = communication_var_construct(variable_name="comm_v",
                                              script_var_name=p_inp_var.variableName,
                                              primitive_type_id=p_inp_var.primitiveTypeId,
                                              data_source_type=DataSourceType1.USER_INPUT)
            comm = communication_construct(communication_channel_name=channel_name,
                                           script_version_id=p_script_view.versionId,
                                           communication_variables=[var],
                                           description="made_in_test")
        with allure.step("Создание канала коммуникаций"):
            create_response: ResponseDto = create_communication_gen.create_communication_channel(
                communication_channel_body=comm)
        with allure.step("Обновление со сменой скрипта в канале коммуникаций"):
            up_var = communication_var_construct(variable_name="comm_v",
                                                 script_var_name=g_inp_var.variableName,
                                                 primitive_type_id=g_inp_var.primitiveTypeId,
                                                 data_source_type=DataSourceType1.USER_INPUT)
            up_body = update_channel_construct(communication_channel_name="updated_" + channel_name,
                                               script_version_id=g_script_view.versionId,
                                               communication_variables=[up_var],
                                               description="updated")
            update_channel(super_user,
                           version_id=create_response.uuid,
                           body=up_body)
        with allure.step("Поиск канала коммуникаций по идентификатору версии"):
            search_response = CommunicationChannelFullViewDto.construct(
                **get_communication_channel(super_user, version_id=create_response.uuid).body)
        with allure.step("Проверка, что скрипт обновлён"):
            assert search_response.scriptVersionId == g_script_view.versionId \
                   and search_response.communicationVariables[0]["scriptVariableName"] == g_inp_var.variableName
