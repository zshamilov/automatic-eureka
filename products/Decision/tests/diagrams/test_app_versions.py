import glamor as allure
import pytest

from products.Decision.framework.steps.decision_steps_environments_api import get_environments_list
from products.Decision.framework.steps.decision_steps_versions_api import get_app_versions


@allure.epic("Диаграммы")
@allure.feature("Получение информации о сборке приложения")
class TestAppInfo:
    @allure.story("В информации о версии возвращается версия бэка")
    @allure.title("Получаем версии компонентом, смотрим, что информация о бэке не пуста")
    @pytest.mark.scenario("DEV-10573")
    @allure.link("DEV-10573")
    @pytest.mark.smoke
    def test_versions_backend_exists(self, super_user):
        with allure.step("Получение информации о версиях компонентов"):
            versions_body = get_app_versions(super_user).body
        with allure.step("Проверка, что в ответе присутствует информация о сборке бэка"):
            assert versions_body['decisionBackendVersion'] is not None

    @allure.story("В информации о версии возвращается версия sp и интмодуля для дефолтного окружения")
    @allure.title("Получаем версии компонентов, смотрим, ищем дефолтное окружение, смотрим, "
                  "что для него вернулись настройки")
    @pytest.mark.scenario("DEV-10573")
    @allure.link("DEV-10573")
    @pytest.mark.smoke
    def test_versions_sp_int_module_exists(self, super_user):
        with allure.step("Получение информации о версиях компонентов и списка окружений"):
            versions_body = get_app_versions(super_user).body
            environments_list = get_environments_list(super_user).body
        with allure.step("Получение дефолтного окружения и настроек инт модуля и sp для него"):
            for environment in environments_list:
                if environment["defaultFlag"]:
                    default_env_id = environment['environmentId']
            for environment_version in versions_body['environments']:
                if environment_version['environmentId'] == default_env_id:
                    sp_version = environment_version['spVersion']
                    integration_version = environment_version['integrationModuleVersion']
        with allure.step("Проверка, что все окружения возвращаются в ответе запроса списка версий"):
            assert sp_version is not None
            assert integration_version is not None

