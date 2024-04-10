import base64
import datetime
import time

import glamor as allure
import pytest
import requests

from products.Decision.framework.model import (
    DeployViewDto,
    DeployConfigurationFullDto,
    ResponseDto,
    DeployPage,
    DeployStatus, DiagramViewDto,
)
from products.Decision.framework.steps.decision_steps_deploy import (
    deploy_list,
    deploy_config,
    find_deploy_id, check_deploy_status, deploy_delete, deploy_list_by_name_resp, deploy_list_by_name,
)
from products.Decision.framework.steps.decision_steps_diagram import (
    put_diagram_submit,
    stop_deploy, start_deploy_async)
from sdk.clients.api import ApiClient
from sdk.user import User
from sdk.user.interface.api.request import ApiRequest


@allure.epic("Развёртывание диаграмм")
@allure.feature("Развёртка")
class TestAdministrationDeploy:

    @allure.story("Можно получить конфигурации развертывания конкретного деплоя и они совпадают с заданными")
    @allure.title("Получить параметры развёрнутого деплоя")
    @allure.issue("DEV-15733")
    @pytest.mark.scenario("DEV-15470")
    @pytest.mark.smoke
    def test_get_deploy_config(
            self,
            super_user,
            get_env,
            simple_diagram,
            deploy_diagrams_gen,
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            create_and_save_result = (
                simple_diagram
            )
            diagram_id = create_and_save_result["template"]["diagramId"]
            diagram_name = create_and_save_result["diagram_name"]
        with allure.step("Отправка диаграммы на сабмит"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Запомнить деплой айди"):
            deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
        with allure.step("Деплой подготовленной диаграммы и получение конфига"):
            env_id = get_env.get_env_id("default_dev")
            config: DeployConfigurationFullDto = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["config"]
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
        with allure.step("Получить настройки развёрнутого деплоя"):
            actual_config: DeployConfigurationFullDto = DeployConfigurationFullDto.construct(
                **deploy_config(super_user, deploy_version_id=deploy_id)
            )
        with allure.step("Проверить, что актуальные настройки соответствуют заданным"):
            assert (
                    actual_config.parallelism == config.parallelism
                    and actual_config.detailedLogging == config.detailedLogging
                    and actual_config.taskManagerMemory == config.taskManagerMemory
                    and actual_config.jobManagerMemory == config.jobManagerMemory
                    and actual_config.taskManagerCpuLimit == config.taskManagerCpuLimit
                    and actual_config.taskManagerCpu == config.taskManagerCpu
                    and actual_config.jobManagerCpuLimit == config.jobManagerCpuLimit
                    and actual_config.jobManagerCpu == config.jobManagerCpu
                    and actual_config.parallelDeployFlag == config.parallelDeployFlag
                    and actual_config.timeout == config.timeout
                    and actual_config.replicationCount == config.replicationCount
                    and actual_config.callUri == config.callUri
            )

    @allure.story("Можно получить стандартные конфигурации деплоя")
    @allure.title("Получить базовые параметры деплоя")
    @pytest.mark.scenario("DEV-15470")
    def test_get_base_config_for_deploy(self,
                                        super_user,
                                        get_env,
                                        simple_diagram
                                        ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            create_and_save_result = (
                simple_diagram
            )
            diagram_id = create_and_save_result["template"]["diagramId"]
            diagram_name = create_and_save_result["diagram_name"]
        with allure.step("Отправка диаграммы на сабмит"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Запомнить деплой айди"):
            deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
        with allure.step("Получить базовые настройки развёртывания"):
            config: DeployConfigurationFullDto = DeployConfigurationFullDto(
                **deploy_config(super_user, deploy_version_id=deploy_id)
            )
        assert (
                config.parallelism == 1
                and config.detailedLogging is True
                and config.taskManagerMemory is not None
                and config.jobManagerMemory is not None
                and config.taskManagerCpuLimit is not None
                and config.taskManagerCpu is not None
                and config.jobManagerCpuLimit is not None
                and config.jobManagerCpu is not None
                and config.parallelDeployFlag is False
                and config.callUri is not None
                and config.timeout is not None
                and config.replicationCount == 1
        )

    @allure.story("Для развернутого деплоя можно отменитть развертывание")
    @allure.title("Снять с развёртки развёрнутый деплой")
    @pytest.mark.scenario("DEV-15470")
    @pytest.mark.smoke
    def test_undeploy_diagram(
            self,
            super_user,
            diagram_deployed,
    ):
        with allure.step("отправка валидной диаграммы на деплой и развёртка"):
            deploy_ready = diagram_deployed
            diagram_id = deploy_ready["diagram_id"]
            deploy_id = deploy_ready["deploy_id"]
            diagram_name = diagram_deployed["diagram_name"]
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
        with allure.step("Остановка развёрнутого деплоя"):
            stop_deploy_response = stop_deploy(super_user, deploy_id)
        with allure.step("Проверка, что статус деплоя STOPPED"):
            stopped = check_deploy_status(user=super_user,
                                          diagram_name=diagram_name,
                                          diagram_id=diagram_id,
                                          status="STOPPED")
            assert stopped and stop_deploy_response.status == 200

    @allure.story("При повторном деплое остановленной диаграммы - статус развернуто")
    @allure.title("Повторно запустить остановленный деплой")
    @pytest.mark.scenario("DEV-15470")
    @allure.issue("DEV-19473")
    # @pytest.mark.skip('long')
    def test_deploy_stopped_diagram(
            self,
            super_user,
            get_env,
            diagram_deployed,
            deploy_diagrams_gen,
    ):
        super_user.with_api.make_refresh_token()
        with allure.step("отправка валидной диаграммы на деплой и развёртка"):
            deploy_ready = diagram_deployed
            diagram_id = deploy_ready["diagram_id"]
            version_id = deploy_ready["version_id"]
            deploy_id = deploy_ready["deploy_id"]
            diagram_name = deploy_ready["diagram_name"]
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
        with allure.step("Остановить развёрнутую диаграмму"):
            stop_deploy_response = stop_deploy(super_user, deploy_id)
            stop_deploy_result: ResponseDto = stop_deploy_response.body
        with allure.step("Получить идентификатор окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Повторно развернуть диаграмму"):
            deploy_response = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["deploy_reponse"]
        with allure.step("Проверить, что статус диаграммы DEPLOYED"):
            deployed = check_deploy_status(user=super_user,
                                           diagram_name=diagram_name,
                                           diagram_id=diagram_id,
                                           status="DEPLOYED")
            assert deployed and deploy_response.deployStatus == DeployStatus.DEPLOYED

    @allure.story(
        "Фильтры должны корректно отрабатывать для columnName: deployStatus и ChangeDt"
    )
    @allure.title(
        "При запросе списка деплоев выставить фильтр даты, проверить, что элементы выдачи корректны"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-6400")
    def test_send_deploy_list_filter_date(self, super_user):
        filter_wrong = False
        start_date_pure = datetime.date.today() - datetime.timedelta(days=15)
        finish_date_pure = datetime.date.today()
        start_date = start_date_pure.strftime("%Y-%m-%d 00:00:00.000")
        finish_date = finish_date_pure.strftime("%Y-%m-%d 00:00:00.000")
        filtered_deploys = []
        list_query_str = f'{{"filters":[{{"columnName":"deployDt","operator":"BETWEEN","value":"{start_date}","valueTo":"{finish_date}"}}],' \
                         f'"sorts":[],"searchBy":"","page":1,"size":20}}'
        list_query = base64.b64encode(bytes(list_query_str, "utf-8"))
        print(list_query.decode("utf-8"))
        with allure.step("Получение списка деплоев"):
            deploy_page: DeployPage = DeployPage.construct(
                **deploy_list(
                    super_user, query={"searchRequest": list_query.decode("utf-8")}
                ).body
            )
        for deploy in deploy_page.content:
            filtered_deploys.append(DeployViewDto.construct(**deploy))
        with allure.step(
                "Проверка, что все элементы выдачи попали в границы фильтрации"
        ):
            for deploy in filtered_deploys:
                current_date = datetime.datetime.strptime(
                    f"{deploy.deployDt}", "%Y-%m-%d %H:%M:%S.%f"
                ).date()
                if not (start_date_pure <= current_date <= finish_date_pure):
                    filter_wrong = True
        assert not filter_wrong

    @allure.story(
        "Фильтры должны корректно отрабатывать для columnName: deployStatus и ChangeDt"
    )
    @allure.title(
        "При запросе списка деплоев выставить фильтр статуса, проверить, что элементы выдачи корректны"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.parametrize(
        "filter_value, result",
        [
            ("READY_FOR_DEPLOY", DeployStatus.READY_FOR_DEPLOY),
            ("STOPPED", DeployStatus.STOPPED),
            ("ERROR", DeployStatus.ERROR),
        ],
    )
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-6400")
    def test_send_deploy_list_filter_state(self, super_user, filter_value, result):
        filtered_deploys = []
        list_query_str = f'{{"filters":[{{"columnName":"deployStatus","operator":"IN","values":["{filter_value}"]}}],"sorts":[],"searchBy":"","page":1,"size":20}}'
        list_query = base64.b64encode(bytes(list_query_str, "utf-8"))
        print(list_query.decode("utf-8"))
        with allure.step("Получение списка деплоев"):
            deploy_page: DeployPage = DeployPage.construct(
                **deploy_list(
                    super_user, query={"searchRequest": list_query.decode("utf-8")}
                ).body
            )
        for deploy in deploy_page.content:
            filtered_deploys.append(DeployViewDto.construct(**deploy))
        print(type(filtered_deploys[0].deployDt))
        with allure.step(
                "Проверка, что все у всех элементов выдачи статус соответствует фильтрации"
        ):
            assert all(deploy.deployStatus == result for deploy in filtered_deploys)

    @allure.story(
        "В ответе корректно возвращаются поля totalElements, totalPages, currentPageNumber"
    )
    @allure.title(
        "Получить список всех деплоев, проверить, что totalElements соответствует длине списка"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.skip("gets all deploys")
    @pytest.mark.scenario("DEV-6400")
    def test_deploy_total_elements_correct(self, super_user):
        with allure.step("Получение списка деплоев"):
            deploy_page: DeployPage = DeployPage.construct(
                **deploy_list(super_user).body
            )
            assert deploy_page.totalElements == len(deploy_page.content)

    @allure.story(
        "В ответе корректно возвращаются поля totalElements, totalPages, currentPageNumber"
    )
    @allure.title(
        "Получить список всех деплоев, проверить, что totalPages соответствует длине списка, делённой на 20 плюс 1"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.skip("gets all deploys")
    @pytest.mark.scenario("DEV-6400")
    def test_deploy_total_pages_correct(self, super_user):
        list_query_str = '{"filters":[],"sorts":[{"direction":"DESC","columnName":"deployDt"}],"searchBy":"","page":1,"size":20}'
        list_query = base64.b64encode(bytes(list_query_str, "utf-8"))
        with allure.step("Получение списка всех деплоев"):
            deploy_page: DeployPage = DeployPage.construct(
                **deploy_list(super_user).body
            )
        with allure.step("Получение ограниченного списка деплоев для проверки"):
            deploy_page1: DeployPage = DeployPage.construct(
                **deploy_list(
                    super_user, query={"searchRequest": list_query.decode("utf-8")}
                ).body
            )
            assert deploy_page1.totalPages == len(deploy_page.content) // 20 + 1

    @allure.story(
        "В ответе для base64 с параметром page в ответ приходит current page = page-1"
    )
    @allure.title(
        "Получить список деплоев с заданной страницей, проверить, что текущая страница такая же, как указано в параметре минус 1"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-6400")
    def test_deploy_current_page_correct(self, super_user):
        page_num = 2
        list_query_str = (
            f'{{"filters":[],"sorts":[],"searchBy":"","page":{page_num},"size":10}}'
        )
        list_query = base64.b64encode(bytes(list_query_str, "utf-8"))
        print(list_query.decode("utf-8"))
        with allure.step("Получение списка деплоев с фильтром по выдаче"):
            deploy_page: DeployPage = DeployPage.construct(
                **deploy_list(
                    super_user, query={"searchRequest": list_query.decode("utf-8")}
                ).body
            )
            assert deploy_page.currentPageNumber == page_num - 1

    @allure.story(
        "При отсутствии query - кол-во элементов 20, если totalElements не меньше 20"
    )
    @allure.title(
        "Проверка, что возможно получить список деплоев без указания параметров выдачи"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-6400")
    def test_deploy_page_defaults(self, super_user):
        with allure.step("Получение списка деплоев без указания параметров выдачи"):
            deploy_page_response = deploy_list(super_user, query={})
        with allure.step("Проверка, что успешно"):
            assert len(deploy_page_response.body["content"]) <= 20

    @allure.story(
        "поле searchBy корректно осуществляет поиск по полям diagramName, по принципу: "
        "diagramlName LIKE %<searchByValue>% OR diagramId LIKE %<searchByValue>% "
    )
    @allure.title("Получить список деплоев с ограничением выдачи по имени элемента")
    @pytest.mark.environment_dependent
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-6400")
    def test_deploy_page_search_by(self, super_user):
        with allure.step("Получение списка деплоев"):
            query_str_search = '{"filters":[],"sorts":[{"direction":"DESC","columnName":"changeDt"}],"searchBy":"","page":1,"size":20}'
            query_search = base64.b64encode(bytes(query_str_search, "utf-8"))
            deploys: [DeployViewDto] = deploy_list(
                super_user, query={"searchRequest": query_search.decode("utf-8")}).body["content"]
        with allure.step("Задание критериев отбора выдачи"):
            reference_deploy_name = deploys[0]["diagram"]["objectName"]
            list_query_str_search = f'{{"filters":[],"sorts":[],"searchBy":"{reference_deploy_name}","page":1,"size":20}}'
            list_query_search = base64.b64encode(bytes(list_query_str_search, "utf-8"))
        with allure.step(
                "Получение списка деплоев с ограничением выдачи по имени элемента"
        ):
            deploys_page_up: DeployPage = DeployPage.construct(
                **deploy_list(
                    super_user,
                    query={"searchRequest": list_query_search.decode("utf-8")},
                ).body
            )
        with allure.step(
                "Получение списка деплоев с ограничением выдачи по имени элемента"
        ):
            assert len(deploys_page_up.content) != 0 and all(
                deploy["diagram"]["objectName"] == reference_deploy_name
                for deploy in deploys_page_up.content
            )

    @allure.story("При получении конфигураций развертывания для диаграммы с поддиаграммой возвращаются настройки "
                  "для диаграммы и поддиаграммы")
    @allure.title("Отправить на развертывание диаграмму с узлом поддиаграммы, получить параметры развертывания")
    @pytest.mark.scenario("DEV-10878")
    @pytest.mark.smoke
    def test_get_base_config_for_deploy_with_child(self,
                                                   super_user,
                                                   diagram_subdiagram_working
                                                   ):
        with allure.step("Получить необходимого для отправки на развертывание идентификатора диаграммы"):
            diagram_id = diagram_subdiagram_working["outer_diagram_template"].diagramId
            diagram_name = diagram_subdiagram_working["outer_diagram_name"]
        with allure.step("Отправить диаграмму на развертывание"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Запомнить идентификатор деплоя"):
            deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
        with allure.step("Получить базовые настройки развёртывания для головной диаграммы"):
            config: DeployConfigurationFullDto = DeployConfigurationFullDto.construct(
                **deploy_config(super_user, deploy_version_id=deploy_id)
            )
        with allure.step("Проверить что присутствуют настройки дочерних деплоев"):
            assert config.subDiagramConfigurations != []

    @allure.story("При повторном получении настроек по ранее развернутому деплою - они совпадают "
                  "с настройками под которыми диаграмма была развернута")
    @allure.title("Получить настройки остановленного деплоя")
    @pytest.mark.scenario("DEV-10878")
    def test_get_base_config_stopped_diagram(self,
                                             super_user,
                                             diagram_deployed
                                             ):
        with allure.step("Получить идентификатора деплоя и первичных конфигураций развертывания"):
            diagram_id = diagram_deployed["diagram_id"]
            deploy_id = diagram_deployed["deploy_id"]
            diagram_name = diagram_deployed["diagram_name"]
            first_deploy_config = diagram_deployed["deploy_configuration"]
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
        with allure.step("Остановить развёрнутый деплой диаграммы"):
            stop_deploy_response = stop_deploy(super_user, deploy_id)
            stop_deploy_result: ResponseDto = stop_deploy_response.body
        with allure.step("Запросить параметры развертывания остановленного деплоя"):
            new_deploy_config: DeployConfigurationFullDto = DeployConfigurationFullDto.construct(
                **deploy_config(super_user, deploy_version_id=deploy_id)
            )
        with allure.step("Проверить, что конфигурации развертывания остановленной диаграммы совпадают с конфигурациями "
                         "при первичном развертывании"):
            assert new_deploy_config == first_deploy_config

    @allure.story("При получении настроек по новому деплою ранее развернутой диаграмм - они совпадают "
                  "с настройками под которыми диаграмма была развернута первично")
    @allure.title("Получить настройки остановленного деплоя")
    @pytest.mark.scenario("DEV-10878")
    def test_get_new_deploy_base_config_stopped_diagram(self,
                                                        super_user,
                                                        diagram_deployed):
        with allure.step("Получить конфигураций развертывания, имени и идентификаторов диаграммы и деплоя"):
            diagram_id = diagram_deployed["diagram_id"]
            deploy_id = diagram_deployed["deploy_id"]
            diagram_name = diagram_deployed["diagram_name"]
            first_deploy_config = diagram_deployed["deploy_configuration"]
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
        with allure.step("Остановить развёрнутую диаграмму"):
            stop_deploy_response = stop_deploy(super_user, deploy_id)
        with allure.step("Повторно отправить диаграммы на развертывание(создание нового деплоя)"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Запомнить новый деплой айди"):
            new_deploy_id = find_deploy_id(super_user, diagram_name, diagram_id, sorting=True)
        with allure.step("Запросить параметры развертывания нового деплоя диаграммы"):
            new_deploy_config: DeployConfigurationFullDto = DeployConfigurationFullDto.construct(
                **deploy_config(super_user, deploy_version_id=new_deploy_id)
            )
        with allure.step("Проверить, что конфигурации развертывания нового деплоя диаграммы совпадают с конфигурациями "
                         "при первичном развертывании"):
            assert (first_deploy_config.parallelism == new_deploy_config.parallelism
                    and first_deploy_config.detailedLogging == new_deploy_config.detailedLogging
                    and first_deploy_config.taskManagerMemory == new_deploy_config.taskManagerMemory
                    and first_deploy_config.jobManagerMemory == new_deploy_config.jobManagerMemory
                    and first_deploy_config.taskManagerCpuLimit == new_deploy_config.taskManagerCpuLimit
                    and first_deploy_config.taskManagerCpu == new_deploy_config.taskManagerCpu
                    and first_deploy_config.jobManagerCpu == new_deploy_config.jobManagerCpu
                    and first_deploy_config.parallelDeployFlag == new_deploy_config.parallelDeployFlag
                    and first_deploy_config.callUri == new_deploy_config.callUri
                    and first_deploy_config.timeout == new_deploy_config.timeout
                    and first_deploy_config.replicationCount == new_deploy_config.replicationCount
                    and first_deploy_config.diagramId == new_deploy_config.diagramId)

    @allure.story("Возможно развернуть несколько диаграмм")
    @allure.title("Отправить на развертывание 2 диаграммы, развернуть их в одном запросе, проверить, что развернуто")
    @pytest.mark.save_diagram(True)
    @pytest.mark.scenario("DEV-10878")
    @pytest.mark.skip("long")
    def test_deploy_multiple_diagram(self,
                                     super_user,
                                     deploy_diagrams_gen,
                                     get_env,
                                     simple_diagram,
                                     diagram_constructor):
        with allure.step("Получить окружение, имена и идентификаторы диаграмм"):
            first_diagram_id = simple_diagram["template"]["diagramId"]
            first_diagram_name = simple_diagram["diagram_name"]
            second_diagram_name = diagram_constructor["saved_data"].objectName
            second_diagram_id = diagram_constructor["saved_data"].diagramId
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Отправить на развертывание обе диаграммыайди"):
            put_diagram_submit(super_user, first_diagram_id)
            put_diagram_submit(super_user, second_diagram_id)
        with allure.step("Запомнить идентификатор деплоя обеих диаграмм"):
            first_deploy_id = find_deploy_id(super_user, first_diagram_name, first_diagram_id)
            second_deploy_id = find_deploy_id(super_user, second_diagram_name, second_diagram_id)
        with allure.step("Развернуть деплои обеих диаграмм"):
            deploy_results = deploy_diagrams_gen.deploy_multiple_diagram(deploy_ids=[first_deploy_id, second_deploy_id],
                                                                         env_id=env_id)["deploy_response"]
        with allure.step("Проверить, что статус обеих диаграмм - развернуто"):
            assert all(deploy_result.deployStatus == DeployStatus.DEPLOYED
                       for deploy_result in deploy_results)

    @allure.story("Можно удалить деплой в статусе 'STOPPED'")
    @allure.title("Создать диаграмму, сохранить, отправить на сабмит, удалить")
    @pytest.mark.scenario("DEV-14227")
    def test_delete_deploy_stopped(
            self,
            super_user,
            get_env,
            simple_diagram
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            create_and_save_result = (
                simple_diagram
            )
            diagram_id = create_and_save_result["template"]["diagramId"]
            diagram_name = create_and_save_result["diagram_name"]
        with allure.step("Отправка диаграммы на сабмит"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Запомнить деплой айди"):
            deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
        with allure.step("Деплой подготовленной диаграммы и получение конфига"):
            env_id = get_env.get_env_id("default_dev")
            config: DeployConfigurationFullDto = DeployConfigurationFullDto.construct(
                **deploy_config(super_user, deploy_version_id=deploy_id))
            config.taskManagerCpuLimit = 0.5
            config.jobManagerCpuLimit = 0.5
            config.taskManagerMemory = 1524
            config.jobManagerMemory = 1524
            start_deploy_async(super_user, deploy_id, env_id, body=[config])
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
        with allure.step("Остановить развёрнутую диаграмму"):
            stop_deploy(super_user, deploy_id)
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="STOPPED")
        with allure.step("Удаление деплоя в статусе 'STOPPED'"):
            deploy_delete(super_user, ids=deploy_id)
        with allure.step("Удаленный деплой отсутствует в списке деплоев"):
            find = deploy_list_by_name_resp(super_user, diagram_name=diagram_name)
            assert find.status == 204

    @allure.story("Можно удалить деплой в статусе 'READY_FOR_DEPLOY'")
    @allure.title("Создать диаграмму, сохранить, отправить на сабмит, удалить")
    @pytest.mark.scenario("DEV-14227")
    def test_delete_ready_for_deploy(self,
                                     super_user,
                                     get_env,
                                     simple_diagram
                                     ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            create_and_save_result = (
                simple_diagram
            )
            diagram_id = create_and_save_result["template"]["diagramId"]
            diagram_name = create_and_save_result["diagram_name"]
        with allure.step("Отправка диаграммы на сабмит"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Запомнить деплой айди"):
            deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
        with allure.step("Удаление деплоя в статусе 'READY_FOR_DEPLOY'"):
            deploy_delete(super_user, ids=deploy_id)
        with allure.step("Удаленный деплой отсутствует в списке деплоев"):
            find = deploy_list_by_name_resp(super_user, diagram_name=diagram_name)
            assert find.status == 204

    @allure.story("Для развёрнутых деплоев доступна ссылка на flink-ui и по ней можно перейти")
    @allure.title("Получить ссылку на flink-ui для развёрнутого деплоя и перейти по ней")
    @pytest.mark.scenario("DEV-18815")
    def test_flink_ui_link_for_diagram_deployed_deploy(self,
                                                       super_user,
                                                       diagram_deployed):
        with allure.step("Получение конфигурации развертывания, имени и идентификатора диаграммы и деплоя"):
            diagram_id = diagram_deployed["diagram_id"]
            diagram_name = diagram_deployed["diagram_name"]
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
        with allure.step("Получение ссылки на flink ui"):
            deploy_info: DeployViewDto = deploy_list_by_name(super_user, diagram_name)[0]
            flink_link = deploy_info.flinkTrackingUrl
        with allure.step("Переход по ссылке"):
            flink_resp = requests.get(flink_link, verify=False)
        with allure.step("Для развёрнутого деплоя можно перейти по ссылке"):
            assert flink_resp.status_code == 200
            assert deploy_info.flinkTrackingUrl is not None

    @allure.story("Для остановленного деплоя ссылка на flink-ui недоступна")
    @allure.title("Остановить развёрнутый деплой, перейти по ссылке на flink-ui")
    @pytest.mark.scenario("DEV-18815")
    @allure.issue("DEV-22578")
    def test_flink_ui_link_for_diagram_stopped_deploy(self,
                                                      super_user,
                                                      diagram_deployed):
        with allure.step("Получение конфигурации развертывания, имени и идентификатора диаграммы и деплоя"):
            diagram_id = diagram_deployed["diagram_id"]
            deploy_id = diagram_deployed["deploy_id"]
            diagram_name = diagram_deployed["diagram_name"]
        with allure.step("Остановка развёртывания"):
            stop_deploy(super_user, deploy_id)
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="STOPPED")
        with allure.step("Получение информации об остановленном деплое"):
            time.sleep(10)
            deploy_info_stopped: DeployViewDto = deploy_list_by_name(super_user, diagram_name)[0]
            flink_link = deploy_info_stopped.flinkTrackingUrl
        with allure.step("Переход по ссылке"):
            flink_resp = requests.get(flink_link, verify=False)
        with allure.step("Для остановленного деплоя ссылка недоступна"):
            assert flink_resp.status_code == 404

    @allure.story("Для незапущенного деплоя ссылка на flink ui не возвращается")
    @allure.title("Сделать сабмит диаграммы, получить ссылку на flink-ui")
    @pytest.mark.scenario("DEV-18815")
    @pytest.mark.save_diagram(True)
    def test_flink_ui_link_for_diagram_ready_deploy(self,
                                                    super_user,
                                                    diagram_constructor):
        with allure.step("Получение конфигурации развертывания, имени и идентификатора диаграммы и деплоя"):
            diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
            diagram_id = diagram_data.diagramId
            diagram_name = diagram_data.objectName
        with allure.step("Сабмит диаграммы"):
            put_diagram_submit(super_user, diagram_id)
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="READY_FOR_DEPLOY")
        with allure.step("Получение ссылки на flink ui"):
            deploy_info: DeployViewDto = deploy_list_by_name(super_user, diagram_name)[0]
        with allure.step("Для диаграммы, которая ещё не была развёрнута, ссылка не возвращается"):
            assert deploy_info.flinkTrackingUrl is None
