import glamor as allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import (
    StateStoreServerType,
    ResponseDto,
    EnvironmentFullViewDto,
)
from products.Decision.framework.steps.decision_steps_environments_api import (
    create_environment,
    get_environment_by_id,
    delete_environment_by_id,
    update_environment,
)
from products.Decision.tests.diagrams.test_add_diagrams import (
    generate_diagram_name_description,
)
from products.Decision.utilities.environment_constructors import *


@allure.epic("Настройка окружений")
@allure.feature("Окружения")
@pytest.mark.scenario("DEV-15469")
class TestAdministrationEnvs:
    @allure.story("Возможно создать окружение с заданными параметрами")
    @allure.title("Создать окружение, проверить, что появилось в списке")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_create_env(self, super_user, fake_env_model, create_environment_gen):
        env_created = False
        with allure.step("Подготовка параметров окружения"):
            env = fake_env_model
        with allure.step("Создание окружения"):
            create_env_resp: ResponseDto = create_environment_gen.create_env(env)
            env_id = create_env_resp.uuid
        with allure.step("Получение списка окружений"):
            env_list = []
            for environment in get_environments_list(super_user).body:
                env_list.append(EnvironmentShortInfoDto.construct(**environment))
            for environment in env_list:
                if environment.environmentId == env_id:
                    env_created = True
        with allure.step("Проверка, что окружение появилось в списке"):
            assert env_created

    @allure.story("Возможно получить информацию по окружению")
    @allure.title(
        "Проверить, что возвращается корректная информация о созданном окружении"
    )
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_get_env_by_id(self, super_user, create_environment_gen):
        with allure.step("Подготовка параметров окружения"):
            integration_env_settings = integration_platform_env_settings(
                generate_diagram_name_description(8, 1)["rand_name"]
            )
            state_env_settings = state_store_env_settings(
                state_store_username="decision_root",
                state_store_password="decision_root",
                state_store_schema="11",
                state_store_server_name="1231",
                state_store_server_port="1231",
                state_store_server_type=StateStoreServerType.POSTGRESQL,
                state_store_additional_properties="",
            )
            str_env_settings = streaming_platform_env_settings(
                streaming_platform_url=generate_diagram_name_description(8, 1)[
                    "rand_name"
                ],
                streaming_platform_username="",
                streaming_platform_password="",
            )
            kafka_settings = kafka_env_settings(
                kafka_url="11", kafka_environment_additional_settings=[]
            )
            env_name = "env_" + generate_diagram_name_description(8, 1)["rand_name"]
            env = env_construct(
                environment_name=env_name,
                integration_platform_environment_settings=integration_env_settings,
                state_store_environment_settings=state_env_settings,
                streaming_platform_environment_settings=str_env_settings,
                default_flag=False,
                kafka_environment_settings=kafka_settings,
            )
        with allure.step("Создание окружения"):
            create_env_resp: ResponseDto = create_environment_gen.create_env(env)
            env_id = create_env_resp.uuid
        with allure.step("Получение информации об окружении"):
            environment = EnvironmentFullViewDto.construct(
                **get_environment_by_id(super_user, environment_id=env_id).body
            )
        with allure.step(
            "Проверка, что об окружении возвращается корректная информация"
        ):
            assert (
                environment.environmentId == env_id
                and environment.environmentName == env_name
                and environment.integrationPlatformEnvSettings is not None
                and environment.streamingPlatformEnvSettings is not None
                and environment.stateStoreEnvSettings is not None
                and environment.kafkaEnvSettings is not None
            )

    @allure.story("Окружение возможно удалить")
    @allure.title("Проверить, что удалённое окружение не найдено")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_delete_env(self, super_user, fake_env_model):
        with allure.step("Подготовка параметров окружения"):
            env = fake_env_model
        with allure.step("Создание окружения"):
            create_env_resp: ResponseDto = ResponseDto.construct(
                **create_environment(super_user, body=env).body
            )
            env_id = create_env_resp.uuid
        with allure.step("Удаление окружения"):
            delete_environment_by_id(super_user, env_id)
        with allure.step("Проверка, что не найдено"):
            with pytest.raises(HTTPError, match="404"):
                assert get_environment_by_id(super_user, environment_id=env_id)

    @allure.story("Окружению возможно обновить параметры")
    @allure.title("Обновить имя окружения")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_update_env(self, super_user, create_environment_gen):
        with allure.step("Подготовка параметров окружения"):
            integration_env_settings = integration_platform_env_settings(
                generate_diagram_name_description(8, 1)["rand_name"]
            )
            state_env_settings = state_store_env_settings(
                state_store_username="decision_root",
                state_store_password="decision_root",
                state_store_schema="11",
                state_store_server_name="1231",
                state_store_server_port="1231",
                state_store_server_type=StateStoreServerType.POSTGRESQL,
                state_store_additional_properties="",
            )
            str_env_settings = streaming_platform_env_settings(
                streaming_platform_url=generate_diagram_name_description(8, 1)[
                    "rand_name"
                ],
                streaming_platform_username="",
                streaming_platform_password="",
            )
            kafka_settings = kafka_env_settings(
                kafka_url="11", kafka_environment_additional_settings=[]
            )
            env_name = "env_" + generate_diagram_name_description(8, 1)["rand_name"]
            env = env_construct(
                environment_name=env_name,
                integration_platform_environment_settings=integration_env_settings,
                state_store_environment_settings=state_env_settings,
                streaming_platform_environment_settings=str_env_settings,
                default_flag=False,
                kafka_environment_settings=kafka_settings,
            )
        with allure.step("Создание окружения"):
            create_env_resp: ResponseDto = create_environment_gen.create_env(env)
            env_id = create_env_resp.uuid
        with allure.step("Обновление окружения"):
            update_body = env_update_construct(
                environment_name=env_name + "_updated",
                integration_platform_environment_settings=integration_env_settings,
                state_store_environment_settings=state_env_settings,
                streaming_platform_environment_settings=str_env_settings,
                default_flag=False,
                kafka_environment_settings=kafka_settings,
            )
            update_environment(super_user, environment_id=env_id, body=update_body)
        with allure.step("Получение информации об окружении"):
            environment = EnvironmentFullViewDto.construct(
                **get_environment_by_id(super_user, environment_id=env_id).body
            )
        with allure.step("Проверка, что окружение обновилось"):
            assert environment.environmentName == env_name + "_updated"

    @allure.story("В списке окружений отображается необходимая информация")
    @allure.title("Проверить, что список окружений содержит необходимые поля")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_env_list(self, super_user):
        env_list = []
        with allure.step("Получение списка окружений"):
            for environment in get_environments_list(super_user).body:
                env_list.append(EnvironmentShortInfoDto.construct(**environment))
            envs_contain_req_fields = next(
                (
                    env
                    for env in env_list
                    if env.environmentId is not None
                    and env.environmentName is not None
                    and env.kafkaUrl is not None
                    and env.integrationUrl is not None
                ),
                True,
            )
        with allure.step(
            "Проверка, что каждое окружение в списке содержить необходимую информацию"
        ):
            assert envs_contain_req_fields

    @allure.story("В окружении в kafka settings можно выставить secure parameter")
    @allure.title(
        "После выставления параметра защиты, увидеть, что значение отображается, как null"
    )
    @pytest.mark.sdi
    @pytest.mark.smoke
    @allure.issue("DEV-19404")
    def test_env_secure_param(self, super_user, create_environment_gen):
        secured_field = False
        not_secured_filed = False
        with allure.step("Подготовка параметров окружения"):
            integration_env_settings = integration_platform_env_settings(
                generate_diagram_name_description(8, 1)["rand_name"]
            )
            state_env_settings = state_store_env_settings(
                state_store_username="decision_root",
                state_store_password="decision_root",
                state_store_schema="11",
                state_store_server_name="1231",
                state_store_server_port="1231",
                state_store_server_type=StateStoreServerType.POSTGRESQL,
                state_store_additional_properties="",
            )
            str_env_settings = streaming_platform_env_settings(
                streaming_platform_url=generate_diagram_name_description(8, 1)[
                    "rand_name"
                ],
                streaming_platform_username="",
                streaming_platform_password="",
            )
            kafka_add_settings_not_secure = kafka_additional_settings_construct(
                property_name="name1", property_value="1111", property_secure=False
            )
            kafka_add_settings_secure = kafka_additional_settings_construct(
                property_name="name2", property_value="2222", property_secure=True
            )
            kafka_settings = kafka_env_settings(
                kafka_url="11",
                kafka_environment_additional_settings=[
                    kafka_add_settings_not_secure,
                    kafka_add_settings_secure,
                ],
            )
            env_name = "env_" + generate_diagram_name_description(8, 1)["rand_name"]
            env = env_construct(
                environment_name=env_name,
                integration_platform_environment_settings=integration_env_settings,
                state_store_environment_settings=state_env_settings,
                streaming_platform_environment_settings=str_env_settings,
                default_flag=False,
                kafka_environment_settings=kafka_settings,
            )
        with allure.step("Создание окружения"):
            create_env_resp: ResponseDto = create_environment_gen.create_env(env)
            env_id = create_env_resp.uuid
        with allure.step("Получение информации об окружении"):
            environment = EnvironmentFullViewDto.construct(
                **get_environment_by_id(super_user, environment_id=env_id).body
            )
            for additional_setting in environment.kafkaEnvSettings[
                "kafkaEnvironmentAdditionalSettings"
            ]:
                if (
                    additional_setting["propertySecure"] == False
                    and additional_setting["propertyValue"] == "1111"
                ):
                    secured_field = True
                if (
                    additional_setting["propertySecure"]
                    and additional_setting["propertyValue"] == "2222"
                ):
                    not_secured_filed = True
        with allure.step(
            "Проверка, что у защищённого параметра значение скрыто, а у незащищённого открыто"
        ):
            assert secured_field and not_secured_filed

    @allure.issue("DEV-6095")
    @allure.story(
        "При создании второго окружения по умолчанию с первого снимается флаг по умолчанию"
    )
    @allure.title(
        "Создать окружение с флагом по умолчанию, проверить. что с default-dev снялся флаг"
    )
    @pytest.mark.sdi
    def test_env_default_flag_draft(self, super_user, create_environment_gen):
        # TODO следить за доработками DEV-6095, доделать проверку на снятие флага по готовности
        with allure.step("Подготовка параметров окружения"):
            integration_env_settings = integration_platform_env_settings(
                generate_diagram_name_description(8, 1)["rand_name"]
            )
            state_env_settings = state_store_env_settings(
                state_store_username="decision_root",
                state_store_password="decision_root",
                state_store_schema="11",
                state_store_server_name="1231",
                state_store_server_port="1231",
                state_store_server_type=StateStoreServerType.POSTGRESQL,
                state_store_additional_properties="",
            )
            str_env_settings = streaming_platform_env_settings(
                streaming_platform_url=generate_diagram_name_description(8, 1)[
                    "rand_name"
                ],
                streaming_platform_username="",
                streaming_platform_password="",
            )
            kafka_settings = kafka_env_settings(
                kafka_url="11", kafka_environment_additional_settings=[]
            )
            env_name = "env_" + generate_diagram_name_description(8, 1)["rand_name"]
            env = env_construct(
                environment_name=env_name,
                integration_platform_environment_settings=integration_env_settings,
                state_store_environment_settings=state_env_settings,
                streaming_platform_environment_settings=str_env_settings,
                default_flag=True,
                kafka_environment_settings=kafka_settings,
            )
        with allure.step(
            "Проверка. что создание запрещено, так как уже есть окружение с дефолт флагом"
        ):
            with pytest.raises(HTTPError, match="400"):
                assert create_environment_gen.try_create_env(env)
