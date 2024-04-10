import glamor as allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import (
    Protocol,
    SyncType,
    Method,
    FileFormat,
    ServiceType,
    ResponseDto,
    ExternalServiceShortInfoDto,
    ExternalServiceFullViewDto,
    ExternalServiceShortInfoVersionDto,
    ExternalServiceUpdateUserVersionDto, ComplexTypeGetFullView, ObjectType, DiagramCreateNewVersion, )
from products.Decision.framework.steps.decision_steps_diagram import delete_diagram, save_diagram
from products.Decision.framework.steps.decision_steps_external_service_api import (
    create_service,
    services_list,
    delete_service,
    find_service_by_id,
    service_versions_list,
    update_service,
    update_service_user_version,
)
from products.Decision.framework.steps.decision_steps_nodes import delete_node_by_id
from products.Decision.framework.steps.decision_steps_object_relation import get_objects_relation_by_object_id
from products.Decision.utilities.external_service_constructors import *


@allure.epic("Доступ к внешним сервисам")
@allure.feature("Внешние сервисы")
class TestAdministrationExternalServ:
    @allure.story("Внешний сервис возможно создать при заполнении необходимых полей")
    @allure.title("Создать сервис, проверить, что создался")
    @pytest.mark.scenario("DEV-15462")
    @pytest.mark.smoke
    def test_create_service(self, super_user, get_env, create_service_gen):
        service_created = False
        with allure.step("получение идентификатора окружения по умолчанию"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Создание сервиса"):
            create_response: ResponseDto = create_service_gen.create_fake_valid_service(env_id)
        with allure.step("Получение списка сервисов"):
            serv_list = []
            for serv in services_list(super_user).body["content"]:
                serv_list.append(ExternalServiceShortInfoDto.construct(**serv))
        with allure.step("Проверка, что созданный сервис найден"):
            for external_service in serv_list:
                if external_service.versionId == create_response.uuid:
                    service_created = True
            assert service_created

    @allure.story("Сервис возможно удалить по айди версии")
    @allure.title("Удалить сервис, проверить, что нет в списке")
    @pytest.mark.scenario("DEV-15462")
    @pytest.mark.smoke
    def test_delete_service(self, super_user, get_env):
        with allure.step("получение идентификатора окружения по умолчанию"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Создание сервиса с заданными настройками"):
            setting = service_setting_construct(
                environment_settings_id=env_id,
                host="some_host",
                service_type=ServiceType.HTTPS,
                endpoint="/endpoint",
                port=11,
                second_attempts_cnt=4,
                transactions_per_second=3,
                interval=3,
                timeout=2,
            )
            header = service_header_construct(header_name="test", header_value='"test"')
            var_in = service_var_construct(
                variable_name="var_in",
                variable_type=VariableType2.IN,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression=None,
            )
            var_out = service_var_construct(
                variable_name="var_out",
                variable_type=VariableType2.OUT,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/path_to_service",
                expression=None,
            )
            var_calc = service_var_construct(
                variable_name="var_calc",
                variable_type=VariableType2.CALCULATED,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression="1+1",
            )
            service = service_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name="service_" + rnd_service_str(8),
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            create_response: ResponseDto = ResponseDto.construct(
                **create_service(super_user, body=service).body
            )
        with allure.step("Удаление сервиса"):
            delete_service(super_user, create_response.uuid)
        with allure.step("Проверка, что не найден"):
            with pytest.raises(HTTPError, match="404"):
                assert find_service_by_id(super_user, create_response.uuid)

    @allure.story("Возможно получить информацию о сервисе по айди версии")
    @allure.title(
        "Получить информацию о сервисе, проверить, что в ней возвращается корректная информация"
    )
    @pytest.mark.scenario("DEV-15462")
    @pytest.mark.smoke
    def test_get_service(self, super_user, get_env, create_service_gen):
        with allure.step("получение идентификатора окружения по умолчанию"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Создание сервиса с заданными настройками"):
            setting = service_setting_construct(
                environment_settings_id=env_id,
                host="some_host",
                service_type=ServiceType.HTTPS,
                endpoint="/endpoint",
                port=11,
                second_attempts_cnt=4,
                transactions_per_second=3,
                interval=3,
                timeout=2,
            )
            header = service_header_construct(header_name="test", header_value='"test"')
            var_in = service_var_construct(
                variable_name="var_in",
                variable_type=VariableType2.IN,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression=None,
            )
            var_out = service_var_construct(
                variable_name="var_out",
                variable_type=VariableType2.OUT,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/path_to_service",
                expression=None,
            )
            var_calc = service_var_construct(
                variable_name="var_calc",
                variable_type=VariableType2.CALCULATED,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression="1+1",
            )
            service_name = "service_" + rnd_service_str(8)
            service = service_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name=service_name,
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            create_response: ResponseDto = create_service_gen.create_service(service)
        with allure.step("Поиск информации о сервисе по идентификатору версии"):
            find_service_resp: ExternalServiceFullViewDto = (
                ExternalServiceFullViewDto.construct(
                    **find_service_by_id(super_user, create_response.uuid).body
                )
            )
        with allure.step("Проверка, что найден и с заданными данными"):
            assert (
                    find_service_resp.serviceId is not None
                    and find_service_resp.versionId == create_response.uuid
                    and find_service_resp.objectName == service_name
                    and find_service_resp.body == '{"param":${var_in}\n}'
                    and find_service_resp.method == "POST"
            )

    @allure.story("Возможно получить список сервисов")
    @allure.title("Проверить, что в списке сервисов есть необходимые поля")
    @pytest.mark.scenario("DEV-15462")
    @pytest.mark.smoke
    def test_service_list(self, super_user):
        with allure.step("Получение списка сервисов"):
            serv_list = []
            for serv in services_list(super_user).body["content"]:
                serv_list.append(ExternalServiceShortInfoDto.construct(**serv))
        with allure.step("Проверка, что у всех элементов есть необходимые поля"):
            list_contains_req_fields = next(
                (
                    serv
                    for serv in serv_list
                    if serv.serviceId is not None
                       and serv.objectName is not None
                       and serv.versionId is not None
                       and serv.changeDt is not None
                ),
                True,
            )
            assert list_contains_req_fields

    @allure.story("Возможно получить список версий сервиса")
    @allure.title("Получить версии, проверить, что информация корректна")
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_service_versions(self, super_user, get_env, create_service_gen):
        version_found = False
        with allure.step("Получение идентификатора окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Создание сервиса с заданными настройками"):
            setting = service_setting_construct(
                environment_settings_id=env_id,
                host="some_host",
                service_type=ServiceType.HTTPS,
                endpoint="/endpoint",
                port=11,
                second_attempts_cnt=4,
                transactions_per_second=3,
                interval=3,
                timeout=2,
            )
            header = service_header_construct(header_name="test", header_value='"test"')
            var_in = service_var_construct(
                variable_name="var_in",
                variable_type=VariableType2.IN,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression=None,
            )
            var_out = service_var_construct(
                variable_name="var_out",
                variable_type=VariableType2.OUT,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/path_to_service",
                expression=None,
            )
            var_calc = service_var_construct(
                variable_name="var_calc",
                variable_type=VariableType2.CALCULATED,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression="1+1",
            )
            service = service_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name="service_" + rnd_service_str(8),
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            create_response: ResponseDto = create_service_gen.create_service(service)
        with allure.step("Получение информации о созданном сервисе"):
            find_service_resp: ExternalServiceFullViewDto = (
                ExternalServiceFullViewDto.construct(
                    **find_service_by_id(super_user, create_response.uuid).body
                )
            )
            serv_id = find_service_resp.serviceId
        with allure.step("Получение списка версий сервиса"):
            vers_list = []
            for vers in service_versions_list(super_user, serv_id).body:
                vers_list.append(ExternalServiceShortInfoVersionDto.construct(**vers))
        with allure.step("Проверка, что созданная версия там отображается"):
            for version in vers_list:
                if version.versionId == create_response.uuid:
                    version_found = True
            assert len(vers_list) == 1 and version_found

    @allure.story("Возможно обновить сервис")
    @allure.title("Проверить, что после обновления отображаемая информация изменилась")
    @pytest.mark.scenario("DEV-15462")
    @pytest.mark.smoke
    def test_update_service(self, super_user, get_env, create_service_gen):
        with allure.step("Получение окружения по идентификатору"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Создание сервиса"):
            setting = service_setting_construct(
                environment_settings_id=env_id,
                host="some_host",
                service_type=ServiceType.HTTPS,
                endpoint="/endpoint",
                port=11,
                second_attempts_cnt=4,
                transactions_per_second=3,
                interval=3,
                timeout=2,
            )
            header = service_header_construct(header_name="test", header_value='"test"')
            var_in = service_var_construct(
                variable_name="var_in",
                variable_type=VariableType2.IN,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression=None,
            )
            var_out = service_var_construct(
                variable_name="var_out",
                variable_type=VariableType2.OUT,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/path_to_service",
                expression=None,
            )
            var_calc = service_var_construct(
                variable_name="var_calc",
                variable_type=VariableType2.CALCULATED,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression="1+1",
            )
            service = service_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name="service_" + rnd_service_str(8),
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            create_response: ResponseDto = create_service_gen.create_service(service)
        with allure.step("Обновление сервиса - имя и описание"):
            name_up = "service_updated_" + rnd_service_str(8)
            update_body = service_update_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name=name_up,
                batch_flag=True,
                description="updated",
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            update_service(super_user, service_id=create_response.uuid, body=update_body)
        with allure.step("Получение информации о сервисе"):
            find_service_resp: ExternalServiceFullViewDto = (
                ExternalServiceFullViewDto.construct(
                    **find_service_by_id(super_user, create_response.uuid).body
                )
            )
        with allure.step("Проверка, что имя и описание обновлены"):
            assert (
                    find_service_resp.objectName == name_up
                    and find_service_resp.description == "updated"
            )

    @allure.story(
        "При указании невалидной информации при обновлении, обновления не произойдёт"
    )
    @allure.title(
        "При обновлении указать невалидные значения, проверить, что клиенту запрещено отправить запрос"
    )
    @pytest.mark.scenario("DEV-15462")
    def test_update_service_bad_env(self, super_user, get_env, create_service_gen):
        with allure.step("Получение окружения по идентификатору"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Создание сервиса с заданными настройками"):
            setting = service_setting_construct(
                environment_settings_id=env_id,
                host="some_host",
                service_type=ServiceType.HTTPS,
                endpoint="/endpoint",
                port=11,
                second_attempts_cnt=4,
                transactions_per_second=3,
                interval=3,
                timeout=2,
            )
            header = service_header_construct(header_name="test", header_value='"test"')
            var_in = service_var_construct(
                variable_name="var_in",
                variable_type=VariableType2.IN,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression=None,
            )
            var_out = service_var_construct(
                variable_name="var_out",
                variable_type=VariableType2.OUT,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/path_to_service",
                expression=None,
            )
            var_calc = service_var_construct(
                variable_name="var_calc",
                variable_type=VariableType2.CALCULATED,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression="1+1",
            )
            service = service_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name="service_" + rnd_service_str(8),
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            create_response: ResponseDto = create_service_gen.create_service(service)
        with allure.step("Обновление сервиса с помощью добавления невалидной настройки"):
            name_up = "service_updated_" + rnd_service_str(8)
            setting_bad = service_setting_construct(
                environment_settings_id=env_id,
                host=None,
                service_type=ServiceType.HTTPS,
                endpoint=None,
                port=11,
                second_attempts_cnt=4,
                transactions_per_second=3,
                interval=3,
                timeout=2,
            )
            update_body = service_update_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name=name_up,
                batch_flag=True,
                description="updated",
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                service_settings=[setting, setting_bad],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
        with allure.step("Проверка, что обновления не произошло"):
            with pytest.raises(HTTPError, match="400"):
                assert update_service(super_user, service_id=create_response.uuid, body=update_body)

    @allure.story("Возможно создать пользовательскую версию сервиса")
    @allure.title("Создать юзер-версию, проверить, что появилась в версиях")
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_create_user_vers_service(self, super_user, get_env, create_service_gen):
        version_found = False
        fields_correct = False
        with allure.step("Получение окружения по идентификатору"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Создание сервиса с заданными настройками"):
            setting = service_setting_construct(
                environment_settings_id=env_id,
                host="some_host",
                service_type=ServiceType.HTTPS,
                endpoint="/endpoint",
                port=11,
                second_attempts_cnt=4,
                transactions_per_second=3,
                interval=3,
                timeout=2,
            )
            header = service_header_construct(header_name="test", header_value='"test"')
            var_in = service_var_construct(
                variable_name="var_in",
                variable_type=VariableType2.IN,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression=None,
            )
            var_out = service_var_construct(
                variable_name="var_out",
                variable_type=VariableType2.OUT,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/path_to_service",
                expression=None,
            )
            var_calc = service_var_construct(
                variable_name="var_calc",
                variable_type=VariableType2.CALCULATED,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression="1+1",
            )
            service = service_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name="service_" + rnd_service_str(8),
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            create_response: ResponseDto = create_service_gen.create_service(service)
        with allure.step("Получение информации о сервисе"):
            find_service_resp: ExternalServiceFullViewDto = (
                ExternalServiceFullViewDto.construct(
                    **find_service_by_id(super_user, create_response.uuid).body
                )
            )
            serv_id = find_service_resp.serviceId
        with allure.step("Создание пользовательской версии сервиса"):
            name_user_vers = "service_user_vers_" + rnd_service_str(8)
            vers_body = service_user_version_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name="service_" + rnd_service_str(8),
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                version_name=name_user_vers,
                version_description="user_version",
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            user_vers_resp: ResponseDto = create_service_gen.create_service_user_vers(
                serv_id, vers_body
            )
        with allure.step("Получение списков версий сервиса"):
            vers_list = []
            for vers in service_versions_list(super_user, serv_id).body:
                vers_list.append(ExternalServiceShortInfoVersionDto.construct(**vers))
        with allure.step("Проверка, что версия создана"):
            for version in vers_list:
                if version.versionId == user_vers_resp.uuid:
                    version_found = True
                    if (
                            version.versionName == name_user_vers
                            and version.versionDescription == "user_version"
                    ):
                        fields_correct = True
            assert version_found and fields_correct

    @allure.story("Возможно обновить имя и описание пользовательской версии")
    @allure.title("Обновить имя и описание юзер-версии, проверить, что обновлено")
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_update_user_vers_service(self, super_user, get_env, create_service_gen):
        version_found = False
        fields_correct = False
        with allure.step("Получение окружения по идентификатору"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Создание сервиса"):
            setting = service_setting_construct(
                environment_settings_id=env_id,
                host="some_host",
                service_type=ServiceType.HTTPS,
                endpoint="/endpoint",
                port=11,
                second_attempts_cnt=4,
                transactions_per_second=3,
                interval=3,
                timeout=2,
            )
            header = service_header_construct(header_name="test", header_value='"test"')
            var_in = service_var_construct(
                variable_name="var_in",
                variable_type=VariableType2.IN,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression=None,
            )
            var_out = service_var_construct(
                variable_name="var_out",
                variable_type=VariableType2.OUT,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/path_to_service",
                expression=None,
            )
            var_calc = service_var_construct(
                variable_name="var_calc",
                variable_type=VariableType2.CALCULATED,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression="1+1",
            )
            service = service_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name="service_" + rnd_service_str(8),
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            create_response: ResponseDto = create_service_gen.create_service(service)
        with allure.step("Получение информации о сервисе"):
            find_service_resp: ExternalServiceFullViewDto = (
                ExternalServiceFullViewDto.construct(
                    **find_service_by_id(super_user, create_response.uuid).body
                )
            )
            serv_id = find_service_resp.serviceId
        with allure.step("Создание пользовательской версии сервиса"):
            name_user_vers = "service_user_vers_" + rnd_service_str(8)
            vers_body = service_user_version_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name="service_" + rnd_service_str(8),
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                version_name=name_user_vers,
                version_description="user_version",
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            user_vers_resp: ResponseDto = create_service_gen.create_service_user_vers(
                serv_id, vers_body
            )
        with allure.step("Обновление сервиса"):
            up_body = ExternalServiceUpdateUserVersionDto(
                versionName=name_user_vers + "up", versionDescription="user_version_up"
            )
            update_service_user_version(
                super_user, version_id=user_vers_resp.uuid, body=up_body
            )
        with allure.step("Получение информации о версиях сервиса"):
            vers_list = []
            for vers in service_versions_list(super_user, serv_id).body:
                vers_list.append(ExternalServiceShortInfoVersionDto.construct(**vers))
        with allure.step("Проверка, что обновление юзер-версии произошло"):
            for version in vers_list:
                if version.versionId == user_vers_resp.uuid:
                    version_found = True
                    if (
                            version.versionName == name_user_vers + "up"
                            and version.versionDescription == "user_version_up"
                    ):
                        fields_correct = True
            assert version_found and fields_correct

    @allure.story(
        "Возможно создать глобал-версию внешнего сервиса"
    )
    @allure.title(
        "создать диаграмму с узлом вызова внешнего сервиса,"
        " создать глобальную версию, найти в списке версий ВС глобальную"
    )
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_create_global_vers_service(self, super_user,
                                        diagram_external_service_saved, save_diagrams_gen):
        saved_version_id = diagram_external_service_saved["saved_version_id"]
        diagram_id = diagram_external_service_saved["diagram_id"]
        new_diagram_name = diagram_external_service_saved["diagram_name"]
        service = diagram_external_service_saved["service"]
        with allure.step("Создание глобальной версии диаграммы"):
            gv_create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram_user_vers(
                    diagram_id=diagram_id,
                    saved_version_id=saved_version_id,
                    version_name="USER_GLOBAL",
                    diagram_name=new_diagram_name,
                    global_flag=True,
                ).body
            )
        with allure.step("Поиск в списке версий нешнего сервиса его глобальной версии"):
            vers_list = []
            for vers in service_versions_list(super_user, service.serviceId).body:
                vers_list.append(ExternalServiceShortInfoVersionDto.construct(**vers))
            assert any(vers.versionType == "USER_GLOBAL" for vers in vers_list)

    @allure.story(
        "Нельзя удалить глобал-версию внешнего сервиса")
    @allure.issue("DEV-12223")
    @allure.title(
        "создать диаграмму с узлом вызова внешнего сервиса,"
        " создать глобальную версию, найти в списке версий ВС глобальнуюб удалить - увидеть, что запрещено"
    )
    @pytest.mark.scenario("DEV-727")
    def test_delete_global_vers_service(self, super_user,
                                        diagram_external_service_saved, save_diagrams_gen):
        saved_version_id = diagram_external_service_saved["saved_version_id"]
        diagram_id = diagram_external_service_saved["diagram_id"]
        new_diagram_name = diagram_external_service_saved["diagram_name"]
        service = diagram_external_service_saved["service"]
        with allure.step("Создание глобальной версии диаграммы"):
            gv_create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram_user_vers(
                    diagram_id=diagram_id,
                    saved_version_id=saved_version_id,
                    version_name="USER_GLOBAL",
                    diagram_name=new_diagram_name,
                    global_flag=True,
                ).body
            )
        with allure.step("Удаление внешнего сервиса его глобальной версии"):
            vers_list = []
            for vers in service_versions_list(super_user, service.serviceId).body:
                vers_list.append(ExternalServiceShortInfoVersionDto.construct(**vers))
            for vers in vers_list:
                if vers.versionType == "USER_GLOBAL":
                    version_id = vers.versionId
        with allure.step("Нельзя удалять глобальные версии агрегатов"):
            with pytest.raises(HTTPError, match="400"):
                assert delete_service(super_user, version_id)

    @allure.story("Есть возможность в входную переменную подавать массив с complexFlag = false")
    @allure.title("Создать сервис с входной переменной примитивного типа с array_flag=True, проверить что создался"
                  )
    @pytest.mark.scenario("DEV-15462")
    @pytest.mark.smoke
    def test_create_service_in_var_array(self, super_user, get_env, create_service_gen):
        arr_var_found_and_correct = False
        with allure.step("Получение окружения по идентификатору"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Создание сервиса с заданными настройками"):
            setting = service_setting_construct(
                environment_settings_id=env_id,
                host="some_host",
                service_type=ServiceType.HTTPS,
                endpoint="/endpoint",
                port=11,
                second_attempts_cnt=4,
                transactions_per_second=3,
                interval=3,
                timeout=2,
            )
            header = service_header_construct(header_name="test", header_value='"test"')
            var_in = service_var_construct(
                variable_name="var_in",
                variable_type=VariableType2.IN,
                array_flag=True,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression=None,
            )
            var_out = service_var_construct(
                variable_name="var_out",
                variable_type=VariableType2.OUT,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/path_to_service",
                expression=None,
            )
            var_calc = service_var_construct(
                variable_name="var_calc",
                variable_type=VariableType2.CALCULATED,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression="1+1",
            )
            service_name = "service_" + rnd_service_str(8)
            service = service_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name=service_name,
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            create_response: ResponseDto = create_service_gen.create_service(service)
        with allure.step("Получение информации о сервисе"):
            external_service_info: ExternalServiceFullViewDto = (
                ExternalServiceFullViewDto.construct(
                    **find_service_by_id(super_user, create_response.uuid).body
                ))
        with allure.step("Проверка, что сервис создан и комплексный тип к нему корректно добавился"):
            for v in external_service_info.variables:
                if v["isArray"] and v["variableType"] == VariableType2.IN:
                    arr_var_found_and_correct = True
            assert create_response.httpCode == 201
            assert arr_var_found_and_correct

    @allure.story("Есть возможность в выходную переменную подавать массив с complexFlag = false")
    @allure.title("Создать сервис с выходной переменной примитивного типа с array_flag=True, проверить что создался"
                  )
    @pytest.mark.scenario("DEV-15462")
    @pytest.mark.smoke
    def test_create_service_out_var_array(self, super_user, get_env, create_service_gen):
        arr_var_found_and_correct = False
        with allure.step("Получение окружения по идентификатору"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Создание сервиса с заданныи настройками"):
            setting = service_setting_construct(
                environment_settings_id=env_id,
                host="some_host",
                service_type=ServiceType.HTTPS,
                endpoint="/endpoint",
                port=11,
                second_attempts_cnt=4,
                transactions_per_second=3,
                interval=3,
                timeout=2,
            )
            header = service_header_construct(header_name="test", header_value='"test"')
            var_in = service_var_construct(
                variable_name="var_in",
                variable_type=VariableType2.IN,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression=None,
            )
            var_out = service_var_construct(
                variable_name="var_out",
                variable_type=VariableType2.OUT,
                array_flag=True,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/path_to_service",
                expression=None,
            )
            var_calc = service_var_construct(
                variable_name="var_calc",
                variable_type=VariableType2.CALCULATED,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression="1+1",
            )
            service_name = "service_" + rnd_service_str(8)
            service = service_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name=service_name,
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            create_response: ResponseDto = create_service_gen.create_service(service)
        with allure.step("Получение информации о сервисе"):
            external_service_info: ExternalServiceFullViewDto = (
                ExternalServiceFullViewDto.construct(
                    **find_service_by_id(super_user, create_response.uuid).body
                ))
        with allure.step("Проверка, что сервис создан и комплексный тип к нему корректно добавился"):
            for v in external_service_info.variables:
                if v["isArray"] and v["variableType"] == VariableType2.OUT:
                    arr_var_found_and_correct = True
            assert create_response.httpCode == 201
            assert arr_var_found_and_correct

    @allure.story("Если тип обмена = “http://”/ “https://”, то должны быть доступны варианты SOAP / REST")
    @allure.title("Создаем сервис с типом обмена http и https и протоколом SOAP и REST,"
                  " проверяем что успешно создался")
    @pytest.mark.scenario("DEV-15462")
    @pytest.mark.parametrize("service_type", [ServiceType.HTTPS, ServiceType.HTTP])
    @pytest.mark.parametrize("protocol", [Protocol.REST, Protocol.SOAP])
    @pytest.mark.smoke
    def test_create_service_type_protocol(self, super_user, get_env, create_service_gen, service_type, protocol):
        with allure.step("Получение окружения по идентификатору"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Создание сервиса с заданныи настройками"):
            setting = service_setting_construct(
                environment_settings_id=env_id,
                host="some_host",
                service_type=service_type,
                endpoint="/endpoint",
                port=11,
                second_attempts_cnt=4,
                transactions_per_second=3,
                interval=3,
                timeout=2,
            )
            header = service_header_construct(header_name="test", header_value='"test"')
            var_in = service_var_construct(
                variable_name="var_in",
                variable_type=VariableType2.IN,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression=None,
            )
            var_out = service_var_construct(
                variable_name="var_out",
                variable_type=VariableType2.OUT,
                array_flag=True,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/path_to_service",
                expression=None,
            )
            var_calc = service_var_construct(
                variable_name="var_calc",
                variable_type=VariableType2.CALCULATED,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression="1+1",
            )
            service_name = "service_" + rnd_service_str(8)
            service = service_construct(
                protocol=protocol,
                sync_type=SyncType.ASYNC,
                service_name=service_name,
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            create_response: ResponseDto = create_service_gen.create_service(service)
        with allure.step("Получение информации о сервисе"):
            external_service_info: ExternalServiceFullViewDto = (
                ExternalServiceFullViewDto.construct(
                    **find_service_by_id(super_user, create_response.uuid).body
                ))
        with allure.step("Сервис создан с корректным протоколом и типом"):
            assert create_response.httpCode == 201 and \
                   external_service_info.protocol == protocol and \
                   external_service_info.serviceSettings[0]["serviceType"] == service_type

    @allure.story("Если  тип обмена = “http://”/ “https://”, то должны быть доступны варианты POST / GET / PUT")
    @allure.title("Создаем сервис с типом обмена http и https и методами POST / GET / PUT,"
                  " проверяем что успешно создался")
    @pytest.mark.scenario("DEV-17942")
    @pytest.mark.parametrize("service_type", [ServiceType.HTTPS, ServiceType.HTTP])
    @pytest.mark.parametrize("method", [Method.POST, Method.GET, Method.PUT, Method.PATCH])
    @pytest.mark.smoke
    def test_create_service_type_method(self, super_user, get_env, create_service_gen, service_type, method):
        with allure.step("Получение окружения по идентификатору"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Создание сервиса с заданныи настройками"):
            setting = service_setting_construct(
                environment_settings_id=env_id,
                host="some_host",
                service_type=service_type,
                endpoint="/endpoint",
                port=11,
                second_attempts_cnt=4,
                transactions_per_second=3,
                interval=3,
                timeout=2,
            )
            header = service_header_construct(header_name="test", header_value='"test"')
            var_in = service_var_construct(
                variable_name="var_in",
                variable_type=VariableType2.IN,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression=None,
            )
            var_out = service_var_construct(
                variable_name="var_out",
                variable_type=VariableType2.OUT,
                array_flag=True,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/path_to_service",
                expression=None,
            )
            var_calc = service_var_construct(
                variable_name="var_calc",
                variable_type=VariableType2.CALCULATED,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression="1+1",
            )
            service_name = "service_" + rnd_service_str(8)
            service = service_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name=service_name,
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=method,
                body='{"param":${var_in}\n}',
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            create_response: ResponseDto = create_service_gen.create_service(service)
        with allure.step("Получение информации о сервисе"):
            external_service_info: ExternalServiceFullViewDto = (
                ExternalServiceFullViewDto.construct(
                    **find_service_by_id(super_user, create_response.uuid).body
                ))
        with allure.step("Сервис создан с корректным методом и типом"):
            assert create_response.httpCode == 201 and \
                   external_service_info.method == method and \
                   external_service_info.serviceSettings[0]["serviceType"] == service_type

    @allure.story("Возможно создать сервис с входной переменной комплексного типа")
    @allure.title("Создать сервис с входной переменной комплексного типа, проверяем что создалась")
    @pytest.mark.scenario("DEV-15462")
    @pytest.mark.parametrize("array_flag", [True, False])
    @pytest.mark.smoke
    def test_create_service_complex_type(self, super_user, get_env,
                                         ctype_prim_attr, create_service_gen, array_flag):
        complex_var_found_and_coorect = False
        with allure.step("Создание кастом типа"):
            complex_type: ComplexTypeGetFullView = ctype_prim_attr
            attr_name = complex_type.attributes[0].attributeName
            attr_id = str(complex_type.attributes[0].attributeId)
            type_id = complex_type.attributes[0].primitiveTypeId
            custom_type_version_id = complex_type.versionId
        with allure.step("Получение окружения по идентификатору"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Создание сервиса с переменной комплексного типа на вход"):
            setting = service_setting_construct(
                environment_settings_id=env_id,
                host="some_host",
                service_type=ServiceType.HTTPS,
                endpoint="/endpoint",
                port=11,
                second_attempts_cnt=4,
                transactions_per_second=3,
                interval=3,
                timeout=2,
            )
            header = service_header_construct(header_name="test", header_value='"test"')
            var_in = service_var_construct(
                variable_name="var_in",
                variable_type=VariableType2.IN,
                array_flag=array_flag,
                is_compl=True,
                complex_type_version_id=custom_type_version_id,
                child_vars=[ExternalServiceVariableViewWithoutIdDto.construct(variableName=attr_name,
                                                                              variableID=attr_id,
                                                                              primitiveTypeId=type_id,
                                                                              isComplex=False,
                                                                              isArray=False,
                                                                              )]
            )
            var_out = service_var_construct(
                variable_name="var_out",
                variable_type=VariableType2.OUT,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/path_to_service",
                expression=None,
            )
            var_calc = service_var_construct(
                variable_name="var_calc",
                variable_type=VariableType2.CALCULATED,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression="1+1",
            )
            service = service_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name="service_" + rnd_service_str(8),
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            create_response: ResponseDto = create_service_gen.create_service(service)
        with allure.step("Получение информации о сервисе"):
            external_service_info: ExternalServiceFullViewDto = (
                ExternalServiceFullViewDto.construct(
                    **find_service_by_id(super_user, create_response.uuid).body
                ))
        with allure.step("Проверка, что сервис создан и комплексный тип к нему корректно добавился"):
            for v in external_service_info.variables:
                if v["isComplex"] and v["isArray"] == array_flag and len(v["childVariables"]) != 0 \
                        and v["variableType"] == VariableType2.IN:
                    complex_var_found_and_coorect = True
            assert create_response.httpCode == 201
            assert complex_var_found_and_coorect

    @allure.story("Возможно создать сервис с выходной переменной комплексного типа")
    @allure.title("Создаем сервис с выходной переменой комплексного типа, проверяем что создался")
    @pytest.mark.scenario("DEV-15462")
    @pytest.mark.parametrize("array_flag", [True, False])
    @pytest.mark.smoke
    def test_create_service_complex_type_var_out(self, super_user, get_env,
                                                 ctype_prim_attr, create_service_gen, array_flag):
        with allure.step("Создание кастом типа"):
            complex_type: ComplexTypeGetFullView = ctype_prim_attr
            attr_name = complex_type.attributes[0].attributeName
            attr_id = str(complex_type.attributes[0].attributeId)
            type_id = complex_type.attributes[0].primitiveTypeId
            custom_type_version_id = complex_type.versionId
        with allure.step("Получение идентификатора окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Создание сервиса с переменной комплексного типа на выход"):
            setting = service_setting_construct(
                environment_settings_id=env_id,
                host="some_host",
                service_type=ServiceType.HTTPS,
                endpoint="/endpoint",
                port=11,
                second_attempts_cnt=4,
                transactions_per_second=3,
                interval=3,
                timeout=2,
            )
            header = service_header_construct(header_name="test", header_value='"test"')
            var_in = service_var_construct(
                variable_name="var_in",
                variable_type=VariableType2.IN,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression=None,
            )
            var_out = service_var_construct(
                variable_name="var_out",
                variable_type=VariableType2.OUT,
                array_flag=array_flag,
                complex_type_version_id=custom_type_version_id,
                source_path="/path_to_service",
                expression=None,
                child_vars=[ExternalServiceVariableViewWithoutIdDto.construct(variableName=attr_name,
                                                                              variableID=attr_id,
                                                                              primitiveTypeId=type_id,
                                                                              isComplex=False,
                                                                              isArray=False,
                                                                              )]
            )
            var_calc = service_var_construct(
                variable_name="var_calc",
                variable_type=VariableType2.CALCULATED,
                array_flag=False,
                primitive_type_id="1",
                complex_type_version_id=None,
                source_path="/",
                expression="1+1",
            )
            service = service_construct(
                protocol=Protocol.REST,
                sync_type=SyncType.ASYNC,
                service_name="service_" + rnd_service_str(8),
                batch_flag=True,
                description=None,
                file_format=FileFormat.JSON,
                method=Method.POST,
                body='{"param":${var_in}\n}',
                service_settings=[setting],
                headers=[header],
                variables=[var_in, var_out, var_calc],
            )
            create_response: ResponseDto = create_service_gen.create_service(service)
        with allure.step("Получение информации о созданном сервисе"):
            external_service_info: ExternalServiceFullViewDto = (
                ExternalServiceFullViewDto.construct(
                    **find_service_by_id(super_user, create_response.uuid).body
                ))
        with allure.step("Сервис создан и выходная переменная является комплексной и содержит атрибут"):
            for v in external_service_info.variables:
                if v["isComplex"] and v["isArray"] == array_flag and len(v["childVariables"]) != 0 \
                        and v["variableType"] == VariableType2.OUT:
                    complex_var_found_and_coorect = True

            assert create_response.httpCode == 201
            assert complex_var_found_and_coorect

    @allure.story(
        "Связь сервиса с диаграммой появляется при сохранении диаграммы с 1 блоком вызова ВС"
    )
    @allure.title(
        "Сохранить диаграмму с сервисом и проверить наличие диаграммы в related objects"
    )
    @pytest.mark.scenario("DEV-8572")
    @allure.link("DEV-8572")
    @pytest.mark.smoke
    def test_check_service_diagram_in_relation(self,
                                               super_user,
                                               diagram_external_service_saved
                                               ):
        with allure.step("Получение информации об объектах"):
            service_id = diagram_external_service_saved["service"].serviceId
            diagram_latest_id = diagram_external_service_saved["saved_version_id"]
        with allure.step("Получение информации связях"):
            object_type = ObjectType.SERVICE_RELATION.value
            related_objects_response = get_objects_relation_by_object_id(
                super_user, object_type, service_id
            ).body["content"]
        assert (
                related_objects_response[0]["objectToVersionId"] == diagram_latest_id
                and len(related_objects_response) == 1
        )

    @allure.story(
        "Связь удаляется для LATEST версии диаграммы после удаления диаграммы"
    )
    @allure.title(
        "Удалить сохраненную диаграмму с сервисом, проверить, что список объектов пустой"
    )
    @pytest.mark.scenario("DEV-8572")
    @allure.link("DEV-8572")
    @pytest.mark.smoke
    def test_check_service_deleted_diagram_not_in_relation(self,
                                                           super_user,
                                                           diagram_external_service_saved,
                                                           ):
        with allure.step("Получение информации об объектах"):
            service_id = diagram_external_service_saved["service"].serviceId
            diagram_latest_id = diagram_external_service_saved["saved_version_id"]
        with allure.step("Удаление диаграммы"):
            delete_diagram(super_user, str(diagram_latest_id))
        with allure.step("Получение информации связях"):
            object_type = ObjectType.SERVICE_RELATION.value
            related_objects_response_body = get_objects_relation_by_object_id(
                super_user, object_type, service_id
            ).body
            related_objects_response_status = get_objects_relation_by_object_id(
                super_user, object_type, service_id
            ).status
        assert (
                related_objects_response_body == {}
                and related_objects_response_status == 204
        )

    @allure.story(
        "Связь удаляется после удаления узла из диаграммы")
    @allure.title(
        "Удалить узел в диаграмме с сервисом, проверить, что список объектов пустой")
    @pytest.mark.scenario("DEV-8572")
    @allure.link("DEV-8572")
    @pytest.mark.smoke
    def test_check_service_deleted_node_not_in_relation(self,
                                                        super_user,
                                                        diagram_external_service_saved,
                                                        ):
        with allure.step("Получение информации об объектах"):
            service_id = diagram_external_service_saved["service"].serviceId
            temp_version_id = diagram_external_service_saved["template"].versionId
            temp_service_node_id = diagram_external_service_saved["node_service"].uuid
            diagram_id = diagram_external_service_saved["diagram_id"]
            diagram_name = diagram_external_service_saved["diagram_name"]
        with allure.step("Удаление узла и сохранение диаграммы"):
            delete_node_by_id(super_user, temp_service_node_id)
            diagram_data = DiagramCreateNewVersion(diagramId=diagram_id,
                                                   versionId=temp_version_id,
                                                   errorResponseFlag=False,
                                                   objectName=diagram_name,
                                                   diagramDescription="diagram created in test")
            save_diagram(super_user, body=diagram_data)
        with allure.step("Получение информации связях"):
            object_type = ObjectType.SERVICE_RELATION.value
            related_objects_response_body = get_objects_relation_by_object_id(
                super_user, object_type, service_id
            ).body
            related_objects_response_status = get_objects_relation_by_object_id(
                super_user, object_type, service_id
            ).status
        assert (
                related_objects_response_body == {}
                and related_objects_response_status == 204
        )
