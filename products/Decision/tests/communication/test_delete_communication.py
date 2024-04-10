import allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import DataSourceType1, ScriptFullView, ResponseDto, \
    ScriptVariableViewWithoutVersionIdDto, CommunicationChannelShortInfoDto, CommunicationPage
from products.Decision.framework.steps.decision_steps_communication_api import create_communication, \
    delete_communication, get_communication_channel, get_channel_list, get_channel_list_content
from products.Decision.utilities.communication_constructors import communication_var_construct, communication_construct


@allure.epic("Каналы коммуникации")
@allure.feature("Удаление канала")
@pytest.mark.scenario("DEV-10141")
class TestCommunicationDelete:

    @allure.story("Невозможно получить информацию об удалённом канале коммуникаций")
    @allure.title("Удалить канал коммуникаций, проверить, что не найден")
    @pytest.mark.smoke
    def test_deleted_communication_not_found(self, super_user, create_python_code_int_vars):
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
            create_response: ResponseDto = ResponseDto.construct(
                **create_communication(super_user, body=comm).body)
        with allure.step("Удаление канала коммуникаций по идентификатору версии"):
            delete_communication(super_user, version_id=create_response.uuid)
        with allure.step("Проверка, что не найден"):
            with pytest.raises(HTTPError, match="404"):
                assert get_communication_channel(super_user, version_id=create_response.uuid)

    @allure.story("Удалённый канал пропадает из списка каналов коммуникаций")
    @allure.title("Удалить канал коммуникаций, проверить, что пропал из списка каналов")
    @pytest.mark.smoke
    def test_deleted_communication_not_found_in_list(self, super_user, create_python_code_int_vars):
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
            create_response: ResponseDto = ResponseDto.construct(
                **create_communication(super_user, body=comm).body)
        with allure.step("Удаление канала коммуникаций по идентификатору версии"):
            delete_communication(super_user, version_id=create_response.uuid)
        with allure.step("Получение списка каналов коммуникаций"):
            channel_list = get_channel_list_content(super_user)
        with allure.step("Проверка, что удалённый канал не найден в списке"):
            for channel in channel_list:
                if channel["versionId"] == create_response.uuid:
                    channel_found = True
            assert not channel_found
