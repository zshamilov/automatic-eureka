import base64
import datetime

import glamor as allure

from products.Decision.framework.model import (
    ScriptShortInfoDto,
    ScriptFullVersionView,
    ScriptWithIdWithVariables,
    ScriptPage, ObjectType, )
from products.Decision.framework.steps.decision_steps_communication_api import delete_communication
from products.Decision.framework.steps.decision_steps_diagram import (
    save_diagram,
)
from products.Decision.framework.steps.decision_steps_nodes import delete_node_by_id
from products.Decision.framework.steps.decision_steps_object_relation import get_objects_relation_by_object_id
from products.Decision.framework.steps.decision_steps_offer_api import delete_offer
from products.Decision.framework.steps.decision_steps_script_api import (
    get_script_list,
    get_scripts_types,
    get_script_versions_by_id,
    get_script_vars_by_id,
)
from products.Decision.runtime_tests.runtime_fixtures.custom_code_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, IntValueType


@allure.epic("Кастомные коды")
@allure.feature("Информация о кастомных кодах")
class TestCustomCodesInfo:
    @allure.story("Вся информация о кастомных кодах есть в списке")
    @allure.title("Получить список кодов, проверить наличие полей")
    @pytest.mark.scenario("DEV-15466")
    @pytest.mark.smoke
    def test_list_custom_codes(self, super_user):
        with allure.step("Получение списка кастом кодов"):
            script_list_body = get_script_list(super_user).body["content"]
            script_list = []
            for script in script_list_body:
                script_list.append(ScriptShortInfoDto.construct(**script))
        with allure.step("Проверка, что в списке содержится необходимая информация"):
            scripts_contain_req_fields = next(
                (
                    script
                    for script in script_list
                    if script.scriptId is not None
                       and script.scriptType is not None
                       and script.objectName is not None
                       and script.versionId is not None
                       and script.changeDt is not None
                ),
                True,
            )

            assert len(script_list) != 0 and scripts_contain_req_fields

    @allure.story("Сортировка по возрастанию корректно отрабатывает для columnName: "
                  "scriptName, scriptId, changeDt, createByUser")
    @allure.title("Получить список скриптов с сортировкой по возрастанию")
    @pytest.mark.scenario("DEV-6400")
    def test_scripts_sort_date_forward(self, super_user):
        list_query_str = '{"filters":[],"sorts":[{"columnName":"changeDt","direction":"ASC"}],"searchBy":"","page":1,"size":20}'
        list_query = base64.b64encode(bytes(list_query_str, "utf-8"))
        print(list_query.decode("utf-8"))
        filtered_scripts = []
        with allure.step("Получение списка скриптов"):
            script_page: ScriptPage = ScriptPage.construct(
                **get_script_list(
                    super_user, query={"searchRequest": list_query.decode("utf-8")}
                ).body
            )
        for script in script_page.content:
            filtered_scripts.append(ScriptShortInfoDto.construct(**script))
        with allure.step(
                "Проверка, что элементы в списке отсортированы по возрастанию по дате"
        ):
            sort_correct_counter = 0
            for i in range(len(filtered_scripts) - 1):
                current_date = datetime.datetime.strptime(
                    filtered_scripts[i].changeDt, "%Y-%m-%d %H:%M:%S.%f"
                )
                next_date = datetime.datetime.strptime(
                    filtered_scripts[i + 1].changeDt, "%Y-%m-%d %H:%M:%S.%f"
                )
                if current_date < next_date:
                    sort_correct_counter += 1
                else:
                    print(current_date == next_date)
                    print(current_date > next_date)
                    print("CURRENT ERROR SCRIPT")
                    print(filtered_scripts[i].objectName)
                    print(filtered_scripts[i].changeDt)
                    print("NEXT ERROR SCRIPT")
                    print(filtered_scripts[i + 1].objectName)
                    print(filtered_scripts[i + 1].changeDt)
            assert sort_correct_counter == len(filtered_scripts) - 1

    @allure.story("Фильтры должны корректно отрабатывать для columnName: createByUser и ChangeDt")
    @allure.title(
        "При запросе списка скриптов выставить фильтр даты, проверить, что элементы выдачи корректны"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_script_list_filter_date(self, super_user):
        filter_wrong = False
        start_date_pure = datetime.date.today() - datetime.timedelta(days=15)
        finish_date_pure = datetime.date.today()
        start_date = start_date_pure.strftime("%Y-%m-%d 00:00:00.000")
        finish_date = finish_date_pure.strftime("%Y-%m-%d 00:00:00.000")
        list_query_str = f'{{"filters":[{{"columnName":"changeDt","operator":"BETWEEN","value":"{start_date}","valueTo":"{finish_date}"}}],' \
                         f'"sorts":[],"searchBy":"","page":1,"size":20}}'
        list_query = base64.b64encode(bytes(list_query_str, "utf-8"))
        filtered_scripts = []
        with allure.step("Получение списка скриптов"):
            script_page: ScriptPage = ScriptPage.construct(
                **get_script_list(
                    super_user, query={"searchRequest": list_query.decode("utf-8")}
                ).body
            )
        for script in script_page.content:
            filtered_scripts.append(ScriptShortInfoDto.construct(**script))
        print(type(filtered_scripts[0].changeDt))
        with allure.step(
                "Проверка, что все элементы выдачи попали в границы фильтрации"
        ):
            for script in filtered_scripts:
                current_date = datetime.datetime.strptime(
                    f"{script.changeDt}", "%Y-%m-%d %H:%M:%S.%f"
                ).date()
                if not (start_date_pure <= current_date <= finish_date_pure):
                    filter_wrong = True
        assert not filter_wrong

    @allure.story("Сортировка по убыванию корректно отрабатывает для columnName:"
                  " scriptName, scriptId, changeDt, createByUser")
    @allure.title("Получить список скриптов с сортировкой по убыванию")
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_scripts_sort_date_backward(self, super_user):
        list_query_str = '{"filters":[],"sorts":[{"columnName":"changeDt","direction":"DESC"}],"searchBy":"","page":1,"size":20}'
        list_query = base64.b64encode(bytes(list_query_str, "utf-8"))
        print(list_query.decode("utf-8"))
        filtered_scripts = []
        with allure.step("Получение списка скриптов"):
            script_page: ScriptPage = ScriptPage.construct(
                **get_script_list(
                    super_user, query={"searchRequest": list_query.decode("utf-8")}
                ).body
            )
        for script in script_page.content:
            filtered_scripts.append(ScriptShortInfoDto.construct(**script))
        print(type(filtered_scripts[0].changeDt))
        with allure.step(
                "Проверка, что элементы в списке отсортированы по возрастанию по дате"
        ):
            sort_correct_counter = 0
            for i in range(len(filtered_scripts) - 1):
                current_date = datetime.datetime.strptime(
                    filtered_scripts[i].changeDt, "%Y-%m-%d %H:%M:%S.%f"
                )
                next_date = datetime.datetime.strptime(
                    filtered_scripts[i + 1].changeDt, "%Y-%m-%d %H:%M:%S.%f"
                )
                if current_date > next_date:
                    sort_correct_counter += 1
                else:
                    print(current_date == next_date)
                    print(current_date > next_date)
                    print("CURRENT ERROR SCRIPT")
                    print(filtered_scripts[i].objectName)
                    print(filtered_scripts[i].changeDt)
                    print("NEXT ERROR SCRIPT")
                    print(filtered_scripts[i + 1].objectName)
                    print(filtered_scripts[i + 1].changeDt)
            assert sort_correct_counter == len(filtered_scripts) - 1

    @allure.story(
        "В ответе корректно возвращаются поля totalElements, totalPages, currentPageNumber"
    )
    @allure.title(
        "Получить список всех скриптов, проверить, что totalElements соответствует длине списка"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_scripts_total_elements_correct(self, super_user):
        with allure.step("Получение списка скриптов"):
            script_page: ScriptPage = ScriptPage.construct(
                **get_script_list(super_user).body
            )
            assert script_page.totalElements == len(script_page.content)

    @allure.story(
        "В ответе корректно возвращаются поля totalElements, totalPages, currentPageNumber"
    )
    @allure.title(
        "Получить список всех скриптов, проверить, что totalPages соответствует длине списка, делённой на 20 плюс 1"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_scripts_total_pages_correct(self, super_user):
        list_query_str = '{"filters":[],"sorts":[],"searchBy":"","page":1,"size":20}'
        list_query = base64.b64encode(bytes(list_query_str, "utf-8"))
        with allure.step("Получение списка всех скриптов"):
            script_page: ScriptPage = ScriptPage.construct(
                **get_script_list(super_user).body
            )
        with allure.step("Получение ограниченного списка скриптов для проверки"):
            script_page1: ScriptPage = ScriptPage.construct(
                **get_script_list(
                    super_user, query={"searchRequest": list_query.decode("utf-8")}
                ).body
            )
            assert script_page1.totalPages == len(script_page.content) // 20 + 1

    @allure.story(
        "В ответе для base64 с параметром page в ответ приходит current page = page-1"
    )
    @allure.title(
        "Получить список скриптов с заданной страницей, проверить, что текущая страница такая же, как указано в параметре минус 1"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_scripts_current_page_correct(self, super_user):
        page_num = 2
        list_query_str = (
            f'{{"filters":[],"sorts":[],"searchBy":"","page":{page_num},"size":10}}'
        )
        list_query = base64.b64encode(bytes(list_query_str, "utf-8"))
        print(list_query.decode("utf-8"))
        with allure.step("Получение списка скриптов с фильтром по выдаче"):
            script_page: ScriptPage = ScriptPage.construct(
                **get_script_list(
                    super_user, query={"searchRequest": list_query.decode("utf-8")}
                ).body
            )
            assert script_page.currentPageNumber == page_num - 1

    @allure.story(
        "При отсутствии query - кол-во элементов 20, если totalElements не меньше 20"
    )
    @allure.title(
        "Проверка, что возможно получить список скриптов без указания параметров выдачи"
    )
    @pytest.mark.environment_dependent
    @pytest.mark.scenario("DEV-6400")
    def test_scripts_page_defaults(self, super_user):
        with allure.step("Получение списка скриптов без указания параметров выдачи"):
            script_page_response = get_script_list(super_user, query={})
        with allure.step("Проверка, что успешно"):
            assert (
                    script_page_response.status == 200
                    and len(script_page_response.body["content"]) <= 20
            )

    @allure.story(
        "Возможно получить список языков для скрипта, корректно формируются поля"
    )
    @allure.title("Получить список языков для скрипта")
    @pytest.mark.scenario("DEV-15466")
    @pytest.mark.smoke
    def test_languages_custom_codes(self, super_user):
        languages_python_and_groovy = 0
        body: [str] = get_scripts_types(super_user).body
        for lang in body:
            if lang == "PYTHON":
                languages_python_and_groovy += 1
            if lang == "GROOVY":
                languages_python_and_groovy += 1

        assert len(body) == 2 and languages_python_and_groovy == 2

    @allure.story(
        "В информации о конкретном Python скрипте отображаются все необходимые поля"
    )
    @allure.title(
        "В информации о конкретном Python скрипте отображаются все необходимые поля"
    )
    @pytest.mark.scenario("DEV-15466")
    @pytest.mark.smoke
    def test_find_python_script_by_id(self, super_user, create_python_code_int_vars):
        python_code_create_result: ScriptFullView = create_python_code_int_vars[
            "code_create_result"
        ]
        script_view = ScriptFullView.construct(
            **get_python_script_by_id(super_user, python_code_create_result.versionId).body
        )

        assert (
                script_view.scriptId is not None
                and script_view.objectName is not None
                and script_view.scriptText is not None
                and script_view.variables is not None
        )

    @allure.story(
        "В информации о конкретном Groovy скрипте отображаются все необходимые поля"
    )
    @allure.title(
        "В информации о конкретном Groovy скрипте отображаются все необходимые поля"
    )
    @pytest.mark.scenario("DEV-15466")
    @pytest.mark.smoke
    def test_find_groovy_script_by_id(self, super_user, create_groovy_code_int_vars):
        groovy_code_create_result: ScriptFullView = create_groovy_code_int_vars[
            "code_create_result"
        ]
        script_view = ScriptFullView.construct(
            **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body
        )

        assert (
                script_view.scriptId is not None
                and script_view.objectName is not None
                and script_view.scriptText is not None
                and script_view.variables is not None
        )

    @allure.story("Корректно формируется список версий скрипта")
    @allure.title("получить список версий скрипта")
    @pytest.mark.scenario("DEV-15466")
    @pytest.mark.smoke
    def test_get_script_versions_by_id(self, super_user, create_python_code_int_vars):
        python_code_create_result: ScriptFullView = create_python_code_int_vars[
            "code_create_result"
        ]
        script_id = ScriptFullView.construct(
            **get_python_script_by_id(super_user, python_code_create_result.versionId).body
        ).scriptId
        versions_body = get_script_versions_by_id(super_user, script_id).body
        versions: [ScriptFullVersionView] = []
        for version in versions_body:
            versions.append(ScriptFullVersionView.construct(**version))

        assert (
                len(versions) == 1
                and versions[0].versionId == python_code_create_result.versionId
                and versions[0].scriptId == script_id
        )

    @allure.story("Корректно формируется список переменных скрипта")
    @allure.title("получить список переменных скрипта")
    @pytest.mark.scenario("DEV-15466")
    @pytest.mark.smoke
    def test_get_script_variables_by_id(self, super_user, create_python_code_int_vars):
        python_code_create_result: ScriptFullView = create_python_code_int_vars[
            "code_create_result"
        ]
        script_id = ScriptFullView.construct(
            **get_python_script_by_id(super_user, python_code_create_result.versionId).body
        ).versionId
        vars_body = ScriptWithIdWithVariables.construct(
            **get_script_vars_by_id(super_user, script_id).body
        )
        variables: [ScriptVariableFullView] = []
        for variable in vars_body.variables:
            variables.append(ScriptVariableFullView.construct(**variable))
        vars_body.variables = variables
        var_contain_req_fields = next(
            (
                var
                for var in vars_body.variables
                if var.variableName is not None
                   and var.variableType is not None
                   and var.primitiveTypeId is not None
                   and var.arrayFlag is not None
                   and var.variableId is not None
            ),
            True,
        )
        assert len(vars_body.variables) == 2 and var_contain_req_fields

    @allure.story(
        "Связь с диаграммой появляется при сохранении диаграммы с 1 блоком кастомного кода"
    )
    @allure.title(
        "сохранить диаграмму с кастомным кодом и проверить наличие диаграммы в related objects"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["кастомный код"])
    @pytest.mark.scenario("DEV-8572")
    @allure.link("DEV-8572")
    @pytest.mark.smoke
    def test_check_code_diagram_in_relation(self,
                                            super_user,
                                            diagram_custom_code_python_2,
                                            ):
        with allure.step("Получение информации об объектах"):
            script_id = diagram_custom_code_python_2["script_view"].scriptId
            diagram_latest_id = diagram_custom_code_python_2["create_result"]["uuid"]
        with allure.step("Получение информации связях"):
            object_type = ObjectType.CUSTOM_CODE_RELATION.value
            related_objects_response = get_objects_relation_by_object_id(
                super_user, object_type, script_id
            ).body["content"]
        assert (
                related_objects_response[0]["objectToVersionId"] == diagram_latest_id
                and len(related_objects_response) == 1
        )

    @allure.story(
        "Связь удаляется для LATEST версии диаграммы после удаления"
    )
    @allure.title(
        "Удалить сохраненную диаграмму с кастомным кодом, проверить что список объектов пустой"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["кастомный код"])
    @pytest.mark.scenario("DEV-8572")
    @allure.link("DEV-8572")
    @pytest.mark.smoke
    def test_check_code_deleted_diagram_not_in_relation(self,
                                                        super_user,
                                                        diagram_custom_code_python_2,
                                                        ):
        with allure.step("Получение информации об объектах"):
            script_id = diagram_custom_code_python_2["script_view"].scriptId
            diagram_latest_id = diagram_custom_code_python_2["create_result"]["uuid"]
        with allure.step("Удаление диаграммы"):
            delete_diagram(super_user, str(diagram_latest_id))
        with allure.step("Получение информации связях"):
            object_type = ObjectType.CUSTOM_CODE_RELATION.value
            related_objects_response_body = get_objects_relation_by_object_id(
                super_user, object_type, script_id
            ).body
            related_objects_response_status = get_objects_relation_by_object_id(
                super_user, object_type, script_id
            ).status
        assert (
                related_objects_response_body == {}
                and related_objects_response_status == 204
        )

    @allure.story(
        "Связь удаляется после удаления узла из диаграммы")
    @allure.title(
        "Удалить узел в диаграмме с кастомным кодом, проверить что список объектов пустой")
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["кастомный код"])
    @pytest.mark.scenario("DEV-8572")
    @allure.link("DEV-8572")
    @pytest.mark.smoke
    def test_check_code_deleted_node_not_in_relation(self,
                                                     super_user,
                                                     diagram_custom_code_python_2,
                                                     ):
        with allure.step("Получение информации об объектах"):
            script_id = diagram_custom_code_python_2["script_view"].scriptId
            diagram_latest_id = diagram_custom_code_python_2["create_result"]["uuid"]
            temp_version_id = diagram_custom_code_python_2["temp_version_id"]
            temp_script_node_id = diagram_custom_code_python_2["temp_script_node_id"]
            diagram_id = diagram_custom_code_python_2["diagram_id"]
            diagram_name = diagram_custom_code_python_2["diagram_name"]
        with allure.step("Удаление узла и сохранение диаграммы"):
            delete_node_by_id(super_user, temp_script_node_id)
            diagram_data = DiagramCreateNewVersion(diagramId=diagram_id,
                                                   versionId=temp_version_id,
                                                   errorResponseFlag=False,
                                                   objectName=diagram_name,
                                                   diagramDescription="diagram created in test")
            save_diagram_again = save_diagram(super_user, body=diagram_data)
        with allure.step("Получение информации связях"):
            object_type = ObjectType.CUSTOM_CODE_RELATION.value
            related_objects_response_body = get_objects_relation_by_object_id(
                super_user, object_type, script_id
            ).body
            related_objects_response_status = get_objects_relation_by_object_id(
                super_user, object_type, script_id
            ).status
        assert (
                related_objects_response_body == {}
                and related_objects_response_status == 204
        )

    @allure.story(
        "2 связи с диаграммой появляется при сохранении диаграммы с 2 блоком кастомного кода"
    )
    @allure.title(
        "сохранить диаграмму с двумя блоками кастомного кода и проверить наличие диаграммы в related objects"
    )
    @pytest.mark.scenario("DEV-8572")
    @allure.link("DEV-8572")
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["кастомный код 1", "кастомный код 2"])
    @pytest.mark.smoke
    def test_check_code_2_diagram_in_relation(self,
                                              super_user,
                                              diagram_custom_code_groovy_2_nodes,
                                              ):
        with allure.step("Получение информации об объектах"):
            script_id = diagram_custom_code_groovy_2_nodes["script_view"].scriptId
            diagram_latest_id = diagram_custom_code_groovy_2_nodes["saved_version_id"]
        with allure.step("Получение информации связях"):
            object_type = ObjectType.CUSTOM_CODE_RELATION.value
            related_objects_response = get_objects_relation_by_object_id(
                super_user, object_type, script_id
            ).body["content"]
        assert len(related_objects_response) == 2
        assert related_objects_response[0]["objectToVersionId"] == diagram_latest_id \
               and related_objects_response[1]["objectToVersionId"] == diagram_latest_id

    @allure.story(
        "Связь с предложением появляется при сохранении предложения"
    )
    @allure.title(
        "Сохранить предложение и проверить наличие предложения в related objects"
    )
    @pytest.mark.scenario("DEV-8572")
    @allure.link("DEV-8572")
    @pytest.mark.smoke
    def test_check_code_offer_in_relation(self,
                                          super_user,
                                          diagram_offer_for_runtime
                                          ):
        with allure.step("Получение информации об объектах"):
            script_id = diagram_offer_for_runtime["script"].scriptId
            offer_version_id = diagram_offer_for_runtime["offer"].versionId
        with allure.step("Получение информации связях"):
            object_type = ObjectType.CUSTOM_CODE_RELATION.value
            related_objects_response = get_objects_relation_by_object_id(
                super_user, object_type, script_id
            ).body["content"]
        assert (
                related_objects_response[0]["objectToVersionId"] == offer_version_id
                and len(related_objects_response) == 1
        )

    @allure.story(
        "Связь с предложением удаляется после удаления предложения"
    )
    @allure.title(
        "Удалить сохраненное предложение с кастомным кодом, проверить что список объектов пустой"
    )
    @pytest.mark.scenario("DEV-8572")
    @allure.link("DEV-8572")
    @pytest.mark.smoke
    def test_check_code_deleted_offer_not_in_relation(self,
                                                      super_user,
                                                      diagram_offer_for_runtime
                                                      ):
        with allure.step("Получение информации об объектах"):
            script_id = diagram_offer_for_runtime["script"].scriptId
            offer_version_id = diagram_offer_for_runtime["offer"].versionId
        with allure.step("Удаление предложения"):
            delete_diagram(super_user, str(diagram_offer_for_runtime["create_result"].uuid))
            delete_offer(super_user, offer_version_id)
        with allure.step("Получение информации связях"):
            object_type = ObjectType.CUSTOM_CODE_RELATION.value
            related_objects_response_body = get_objects_relation_by_object_id(
                super_user, object_type, script_id
            ).body
            related_objects_response_status = get_objects_relation_by_object_id(
                super_user, object_type, script_id
            ).status
        assert (
                related_objects_response_body == {}
                and related_objects_response_status == 204
        )

    @allure.story(
        "Связь с коммуникацией появляется при сохранении коммуникацией"
    )
    @allure.title(
        "Сохранить коммуникацию и проверить наличие коммуникации в related objects"
    )
    @pytest.mark.scenario("DEV-8572")
    @allure.link("DEV-8572")
    @pytest.mark.smoke
    def test_check_code_communication_in_relation(self,
                                                  super_user,
                                                  create_standart_communication_channel
                                                  ):
        with allure.step("Получение информации об объектах"):
            script_id = create_standart_communication_channel["script"].scriptId
            communication_version_id = create_standart_communication_channel["communication"].versionId
        with allure.step("Получение информации связях"):
            object_type = ObjectType.CUSTOM_CODE_RELATION.value
            related_objects_response = get_objects_relation_by_object_id(
                super_user, object_type, script_id
            ).body["content"]
        assert (
                related_objects_response[0]["objectToVersionId"] == communication_version_id
                and len(related_objects_response) == 1
        )

    @allure.story(
        "Связь с коммуникацией удаляется после удаления коммуникации"
    )
    @allure.title(
        "Удалить сохраненную коммуникацию с кастомным кодом, проверить что список объектов пустой"
    )
    @pytest.mark.scenario("DEV-8572")
    @allure.link("DEV-8572")
    @pytest.mark.smoke
    def test_check_code_deleted_communication_not_in_relation(self,
                                                              super_user,
                                                              create_standart_communication_channel
                                                              ):
        with allure.step("Получение информации об объектах"):
            script_id = create_standart_communication_channel["script"].scriptId
            communication_version_id = create_standart_communication_channel["communication"].versionId
        with allure.step("Удаление коммуникации"):
            delete_communication(super_user, communication_version_id)
        with allure.step("Получение информации связях"):
            object_type = ObjectType.CUSTOM_CODE_RELATION.value
            related_objects_response_body = get_objects_relation_by_object_id(
                super_user, object_type, script_id
            ).body
            related_objects_response_status = get_objects_relation_by_object_id(
                super_user, object_type, script_id
            ).status
        assert (
                related_objects_response_body == {}
                and related_objects_response_status == 204
        )
