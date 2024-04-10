import uuid

import allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import ScriptFullView, DataSourceType1, ScriptVariableViewWithoutVersionIdDto, \
    ResponseDto, CommunicationChannelFullViewDto, CommunicationChannelShortInfoDto, CommunicationPage
from products.Decision.framework.steps.decision_steps_communication_api import get_communication_channel, \
    get_channel_list
from products.Decision.utilities.communication_constructors import *


@allure.epic("Каналы коммуникации")
@allure.feature("Добавление канала")
class TestCommunicationCreate:

    @allure.story("Канал коммуникаций можно создать, если заполнить поля:название  канала, идентификатор"
                  " версии пользовательского кода, поля канала и входные переменные пользовательского кода")
    @allure.title("Создать канал, запросить информацию, проверить, что найден")
    @pytest.mark.smoke
    @pytest.mark.scenario("DEV-10141")
    def test_create_communication(self, super_user,
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
        with allure.step("Поиск канала коммуникаций по идентификатору версии"):
            search_result = get_communication_channel(super_user, version_id=create_response.uuid)
        with allure.step("Проверка, что канал коммуникаций найден"):
            assert search_result.status == 200

    @allure.story("Созданная Latest версия канала коммуникаций появляется в списке каналов коммуникаций")
    @allure.title("Создать канал, проверить, что появился в списке каналов")
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_created_channel_appeared_in_list(self, super_user,
                                              create_python_code_int_vars,
                                              create_communication_gen):
        channel_found = False
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
        with allure.step("Получение списка каналов коммуникаций"):
            channel_list = []
            comms_page: CommunicationPage = CommunicationPage.construct(**get_channel_list(super_user).body)
            for channel in comms_page.content:
                channel_list.append(CommunicationChannelShortInfoDto.construct(**channel))
        with allure.step("Проверка, что созданный канал найден в списке"):
            for channel in channel_list:
                if channel.versionId == create_response.uuid:
                    channel_found = True
            assert channel_found

    @allure.story("На базе созданной версии канала коммуникаций, возможно создать пользовательскую версию канала "
                  "коммуникаций")
    @pytest.mark.skip(reason="functional is not ready")
    @pytest.mark.scenario("DEV-727")
    @allure.title("Создать канал, из него создать пользовательскую версию запросить информацию, проверить, что найдена")
    @pytest.mark.smoke
    def test_create_communication_user_version(self, super_user,
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
            uv_body = channel_user_version_construct(communication_channel_name=channel_name,
                                                     script_version_id=script_view.versionId,
                                                     communication_variables=[var],
                                                     description=None,
                                                     version_name="user_vers" + channel_name,
                                                     version_description="user_version")
        with allure.step("Создание пользовательской версии канала"):
            create_uv_response: ResponseDto = create_communication_gen.create_user_version(
                version_id=create_response.uuid, user_version_body=uv_body)
        with allure.step("Поиск канала коммуникаций по идентификатору версии"):
            search_response = CommunicationChannelFullViewDto.construct(
                **get_communication_channel(super_user, version_id=create_uv_response.uuid).body)
        with allure.step("Проверка, что канал коммуникаций найден и его имя соответствует заданному"):
            assert search_response.communicationChannelName == "user_vers" + channel_name

    @allure.story("При добавлении канала коммуникаций скрипт должен быть существующим")
    @allure.issue("DEV-6739")
    @pytest.mark.scenario("DEV-10141")
    @allure.title("Нельзя создать канал коммуникаций с несуществующим скриптом")
    def test_create_communication_bad_script_vers(self, super_user,
                                                  create_python_code_int_vars,
                                                  create_communication_gen):
        with allure.step("Создание пользовательского кода"):
            script_view: ScriptFullView = create_python_code_int_vars["code_view"]
            inp_var: ScriptVariableViewWithoutVersionIdDto = create_python_code_int_vars["inp_var"]
        with allure.step("Задание параметров канала коммуникаций с существующей версией скрипта"):
            channel_name = "channel_" + generate_string()
            var = communication_var_construct(variable_name="comm_v",
                                              script_var_name=inp_var.variableName,
                                              primitive_type_id=inp_var.primitiveTypeId,
                                              data_source_type=DataSourceType1.USER_INPUT)
            comm = communication_construct(communication_channel_name=channel_name,
                                           script_version_id=str(uuid.uuid4()),
                                           communication_variables=[var],
                                           description="made_in_test")
        with allure.step("Проверка, что канал коммуникаций не создан"):
            with pytest.raises(HTTPError, match="404"):
                assert create_communication_gen.try_create_communication_channel(
                    communication_channel_body=comm)

    @allure.story("При добавлении канала коммуникаций имя пользовательского кода и тип кода должны совпадать с "
                  "идентификатором версии пользовательского кода и её типом")
    @allure.issue("DEV-6731")
    @pytest.mark.scenario("DEV-10141")
    @allure.title("Нельзя создать канал коммуникаций, у которого маппинг переменных не совпадает с переменными, "
                  "указанными в скрипте канала")
    def test_create_communication_bad_script_vars(self, super_user,
                                                  create_python_code_int_vars,
                                                  create_communication_gen):
        with allure.step("Создание пользовательского кода"):
            script_view: ScriptFullView = create_python_code_int_vars["code_view"]
            inp_var: ScriptVariableViewWithoutVersionIdDto = create_python_code_int_vars["inp_var"]
        with allure.step("Задание параметров канала коммуникаций с существующей версией скрипта"):
            channel_name = "channel_" + generate_string()
            var = communication_var_construct(variable_name="comm_v",
                                              script_var_name="not_a_name",
                                              primitive_type_id="25",
                                              data_source_type=DataSourceType1.USER_INPUT)
            comm = communication_construct(communication_channel_name=channel_name,
                                           script_version_id=script_view.versionId,
                                           communication_variables=[var],
                                           description="made_in_test")
        with allure.step("Создание канала коммуникаций"):
            create_response = create_communication_gen.try_create_communication_channel(
                communication_channel_body=comm)
        with allure.step("Проверка, что канал коммуникаций не создан"):
            with pytest.raises(HTTPError, match="400"):
                assert create_communication_gen.try_create_communication_channel(
                    communication_channel_body=comm)

    @allure.story("При добавлении канала коммуникаций имя пользовательского кода и тип кода должны совпадать с "
                  "идентификатором версии пользовательского кода и её типом")
    @allure.title("Создать канал с недопустимымм именем")
    @pytest.mark.scenario("DEV-10141")
    @allure.issue("DEV-6730")
    @pytest.mark.parametrize('name, status', [("1chanel_name_starts_with_number", 400),
                                              (generate_string(101), 400)])
    def test_create_communication_bad_name(self, super_user,
                                           create_python_code_int_vars,
                                           create_communication_gen,
                                           name, status):
        with allure.step("Создание пользовательского кода"):
            script_view: ScriptFullView = create_python_code_int_vars["code_view"]
            inp_var: ScriptVariableViewWithoutVersionIdDto = create_python_code_int_vars["inp_var"]
        with allure.step("Задание параметров канала коммуникаций"):
            var = communication_var_construct(variable_name="comm_v",
                                              script_var_name=inp_var.variableName,
                                              primitive_type_id=inp_var.primitiveTypeId,
                                              data_source_type=DataSourceType1.USER_INPUT)
            comm = communication_construct(communication_channel_name=name,
                                           script_version_id=script_view.versionId,
                                           communication_variables=[var],
                                           description="made_in_test")
        with allure.step("Проверка, что канал коммуникаций найден и его имя соответствует заданному"):
            with pytest.raises(HTTPError):
                assert create_communication_gen.try_create_communication_channel(
                    communication_channel_body=comm).status == status
