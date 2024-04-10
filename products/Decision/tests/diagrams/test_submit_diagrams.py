import glamor as allure
from requests import HTTPError

from products.Decision.framework.model import (
    DiagramShortInfoVersionsView,
    ScriptFullVersionView,
    VersionType,
    ComplexTypeGetFullView,
    ComplexTypeGetFullVersionView, )
from products.Decision.framework.steps.decision_steps_complex_type import (
    list_complex_type_versions,
)
from products.Decision.framework.steps.decision_steps_diagram import (
    get_diagram_versions,
    get_diagram_parameters,
)
from products.Decision.framework.steps.decision_steps_script_api import (
    get_script_versions_by_id,
)
from products.Decision.runtime_tests.runtime_fixtures.custom_code_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, IntValueType


@allure.epic("Диаграммы")
@allure.feature("Отправка на развёртывание диаграммы")
@pytest.mark.scenario("DEV-15470")
class TestDiagramsSubmit:
    @allure.story("Для невалидной диаграммы( например с узлами, но без линков)"
                  " - деплой неуспешен и не создается deploy версия")
    @allure.issue("DEV-4989")
    @allure.title(
        "Отправить невалидную диаграмму на submit, деплой версия не появилась"
    )
    @pytest.mark.nodes([])
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_submit_invalid_diagram(
        self,
        super_user,
        diagram_constructor,
    ):
        deploy_version_found = False
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_constructor["diagram_id"]
        with allure.step("Отправка диаграммы на сабмит"):
            with pytest.raises(HTTPError):
                put_diagram_submit(super_user, diagram_id)
            versions_response = get_diagram_versions(super_user, diagram_id)
            list_versions: [DiagramShortInfoVersionsView] = versions_response.body
            for version in list_versions:
                if version["versionType"] == "DEPLOYED":
                    deploy_version_found = True

            assert not deploy_version_found

    @allure.story("Для невалидной диаграммы( например с узлами, но без линков) -"
                  " деплой неуспешен и не создается deploy в списке деплоев")
    @allure.title(
        "Отправить невалидную диаграмму на submit, отправка на деплой запрещена"
    )
    @pytest.mark.nodes([])
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_submit_invalid_diagram_neg(
        self,
        super_user,
        diagram_constructor,
    ):
        with allure.step("Создание и сохранение диаграммы без связей - невалидной"):
            diagram_id = diagram_constructor["diagram_id"]
        with allure.step("Отправка невалидной диаграммы на развёртывание запрещена"):
            with pytest.raises(HTTPError, match="400"):
                assert put_diagram_submit(super_user, diagram_id)

    @allure.title(
        "Отправить диаграмму на submit, название деплой версии соответствует паттерну"
    )
    @allure.story(
        "При отправке диаграммы на развёртывание, в версиях диаграммы создаётся деплой версия с именем "
        "VersionName в формате  v.<current_dt>_deploy"
    )
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_submit_diagram_vers_name(self, super_user, diagram_constructor):
        version_name_correct = False
        with allure.step("Создание и сохранение простейшей параметрами"):
            diagram_id = diagram_constructor["diagram_id"]
            version_id = diagram_constructor["saved_data"].versionId
        with allure.step("Отправка диаграммы на деплой"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Получение списка версий диаграммы"):
            versions_response = get_diagram_versions(super_user, diagram_id)
            list_versions: [DiagramShortInfoVersionsView] = versions_response.body
            for version in list_versions:
                if version["versionType"] == "DEPLOYED":
                    if version["versionName"].startswith('v.') and version["versionName"].endswith('_deploy'):
                        version_name_correct = True
            with allure.step(
                "Проверка что имя деплой аерсии соответствует паттерну v.<current_dt>_deploy"
            ):
                assert version_name_correct

    @allure.title("Отправить диаграмму на submit, деплой версия появилась")
    @allure.story(
        "При отправке диаграммы на развёртывание, в версиях диаграммы отображается деплой версия ("
        "versionType: DEPLOYED)"
    )
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_submit_diagram_vers(self, super_user, diagram_constructor):
        version_found = False
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_constructor["diagram_id"]
            version_id = diagram_constructor["saved_data"].versionId
        with allure.step("Отправка диаграммы на деплой"):
            submit_response = put_diagram_submit(super_user, diagram_id)
        with allure.step("Получение списка версий диаграммы"):
            versions_response = get_diagram_versions(super_user, diagram_id)
            list_versions: [DiagramShortInfoVersionsView] = versions_response.body
            for version in list_versions:
                if version["versionType"] == "DEPLOYED":
                    version_found = True
            with allure.step(
                "Проверка что деплой версия появилась"
            ):
                assert version_found and \
                       submit_response.status == 201

    @allure.story(
        "При отправке диаграммы на развёртывание с узлом кастомного кода, для кастомного кода "
        "появляется версия с идентичным для диаграммы versionName"
    )
    @allure.title(
        "Получить деплой версию скрипта, проверить, что имя, как у деплой версии диаграммы"
    )
    def test_submit_script_node_script_vers_name(
        self, super_user, diagram_custom_code_submit
    ):
        script_deploy_version_name_correct = False
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_custom_code_submit["template"]["diagramId"]
            script_view: ScriptFullView = diagram_custom_code_submit["script_view"]
            # version_id = create_and_save_result["create_result"]["uuid"]
        with allure.step("Отправка диаграммы на деплой"):
            submit_response = put_diagram_submit(super_user, diagram_id)
        with allure.step("Получение списка версий диаграммы"):
            diagram_vers_name = None
            versions_response = get_diagram_versions(super_user, diagram_id)
            diagram_versions: [DiagramShortInfoVersionsView] = versions_response.body
            for version in diagram_versions:
                if version["versionType"] == "DEPLOYED":
                    diagram_vers_name = version["versionName"]
        with allure.step("Получение списка версий скрипта"):
            versions_body = get_script_versions_by_id(
                super_user, script_view.scriptId
            ).body
            script_versions: [ScriptFullVersionView] = []
            for version in versions_body:
                script_versions.append(ScriptFullVersionView.construct(**version))
            for version in script_versions:
                if (
                    version.versionType == VersionType.DEPLOYED
                    and version.versionName == diagram_vers_name
                ):
                    script_deploy_version_name_correct = True
        with allure.step(
            "Проверка, что имя деплой версии скрипта такое же, как и у диаграммы"
        ):
            assert script_deploy_version_name_correct

    @allure.story(
        "При отправке диаграммы на развёртывание с узлом кастомного кода, для кастомного кода появляется "
        "версия с versionType: DEPLOYED"
    )
    @allure.title(
        "Отправить на развёртывание диаграмму с узлом кастомного кода, деплой версия скрипта появилась"
    )
    def test_submit_script_node_script_vers(
        self, super_user, diagram_custom_code_submit
    ):
        script_deploy_version_found = False
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_custom_code_submit["template"]["diagramId"]
            script_view: ScriptFullView = diagram_custom_code_submit["script_view"]
            # version_id = create_and_save_result["create_result"]["uuid"]
        # with allure.step("Отправка диаграммы на деплой"):
        #     submit_response = put_diagram_submit(super_user, diagram_id)
        with allure.step("Получение списка версий скрипта"):
            versions_body = get_script_versions_by_id(
                super_user, script_view.scriptId
            ).body
            script_versions: [ScriptFullVersionView] = []
            for version in versions_body:
                script_versions.append(ScriptFullVersionView.construct(**version))
            for version in script_versions:
                if version.versionType == VersionType.DEPLOYED:
                    script_deploy_version_found = True
        with allure.step("Проверка, что деплой версия скрипта появилась"):
            assert script_deploy_version_found

    @allure.story(
        "При отправке диаграммы на развёртывание с узлом кастомного кода,"
        " для кастомного кода появляется версия с идентичным с versionId deploy версии"
        " диаграммы  rootObjectVersionId"
    )
    @allure.title("Получить деплой версию скрипта, проверить rootObject")
    @pytest.mark.skip("obsolete")
    def test_submit_script_node_script_vers_root(
        self, super_user, diagram_custom_code_submit
    ):
        script_deploy_version_root_object_correct = False
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_custom_code_submit["template"]["diagramId"]
            script_view: ScriptFullView = diagram_custom_code_submit["script_view"]
            # version_id = create_and_save_result["create_result"]["uuid"]
        # with allure.step("Отправка диаграммы на деплой"):
        #     submit_response = put_diagram_submit(super_user, diagram_id)
        with allure.step("Получение списка версий диаграммы"):
            diagram_deploy_version = None
            versions_response = get_diagram_versions(super_user, diagram_id)
            diagram_versions: [DiagramShortInfoVersionsView] = versions_response.body
            for version in diagram_versions:
                if version["versionType"] == "DEPLOYED":
                    diagram_deploy_version = version["versionId"]
        with allure.step("Получение списка версий скрипта"):
            versions_body = get_script_versions_by_id(
                super_user, script_view.scriptId
            ).body
            script_versions: [ScriptFullVersionView] = []
            for version in versions_body:
                script_versions.append(ScriptFullVersionView.construct(**version))
            for version in script_versions:
                if (
                    version.versionType == VersionType.DEPLOYED
                    and version.rootObjectVersionId == diagram_deploy_version
                ):
                    script_deploy_version_root_object_correct = True
        with allure.step(
            "Проверка, что root object скрипта совпадает с деплой версией диаграммы"
        ):
            assert script_deploy_version_root_object_correct

    @allure.story(
        "При отправке диаграммы на развёртывание с узлом кастомного кода, в ДЕПЛОЙ версии диаграммы в узле "
        "кастомного кода VersionId сменился на versionId созданной деплой версии скрипта"
    )
    @allure.title(
        "Получить информацию о деплой версии диаграммы, проверить, что в узле кастом кода ссылка на деплой "
        "версию скрипта"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["кастомный код"])
    @pytest.mark.smoke
    def test_submit_script_node_vers_changed_in_node(
        self, super_user, diagram_custom_code_groovy_2
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_custom_code_groovy_2["diagram_id"]
            script_view: ScriptFullView = diagram_custom_code_groovy_2["script_view"]
            # version_id = create_and_save_result["create_result"]["uuid"]
        with allure.step("Отправка диаграммы на сабмит"):
            submit_response = put_diagram_submit(super_user, diagram_id)
        with allure.step("Получение списка версий диаграммы"):
            diagram_deploy_version = None
            versions_response = get_diagram_versions(super_user, diagram_id)
            diagram_versions: [DiagramShortInfoVersionsView] = versions_response.body
            for version in diagram_versions:
                if version["versionType"] == "DEPLOYED":
                    diagram_deploy_version = version["versionId"]
        with allure.step("Получение списка версий скрипта"):
            script_deploy_version = None
            versions_body = get_script_versions_by_id(
                super_user, script_view.scriptId
            ).body
            script_versions: [ScriptFullVersionView] = []
            for version in versions_body:
                script_versions.append(ScriptFullVersionView.construct(**version))
            for version in script_versions:
                if version.versionType == VersionType.DEPLOYED:
                    script_deploy_version = version.versionId
        with allure.step("Получение информации о деплой версии диаграммы"):
            deploy_diag_info = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, diagram_deploy_version).body
            )
            node_script_id=None
            for node in deploy_diag_info.nodes.values():
                if node["nodeTypeId"] == 1:
                    node_script_id = node["nodeId"]
            script_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_script_id).body)
        with allure.step(
            "Проверка, что в узле кастомного кода, узел ссылается на деплой версию скрипта"
        ):
            assert script_node_view.properties["versionId"] == script_deploy_version

    @allure.story(
        "При отправке диаграммы на развёртывание с узлом поддиаграммы, для вложенной диаграммы появляется "
        "версия с идентичным для верхней диаграммы versionName"
    )
    @allure.title(
        "Получить деплой версию поддиаграммы, проверить, что имя, как у деплой версии диаграммы"
    )
    def test_submit_subdiagram_node_subdiagram_vers_name(
        self, super_user, diagram_subdiagram_submit_working
    ):
        subdiagram_deploy_version_name_correct = False
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_subdiagram_submit_working["diagram_id"]
            subdiagram_version_id = diagram_subdiagram_submit_working["subdiagram_version_id"]
            get_subdiagram_by_version_response = get_diagram_by_version(
                super_user, subdiagram_version_id
            )
            subdiagram_info = DiagramViewDto.construct(
                **get_subdiagram_by_version_response.body
            )
            # version_id = create_and_save_result["create_result"]["uuid"]
        with allure.step("Отправка диаграммы на деплой"):
            submit_response = put_diagram_submit(super_user, diagram_id)
        with allure.step("Получение списка версий диаграммы"):
            diagram_vers_name = None
            versions_response = get_diagram_versions(super_user, diagram_id)
            diagram_versions: [DiagramShortInfoVersionsView] = versions_response.body
            for version in diagram_versions:
                if version["versionType"] == "DEPLOYED":
                    diagram_vers_name = version["versionName"]
        with allure.step("Получение списка версий поддиаграммы"):
            sub_versions_response = get_diagram_versions(
                super_user, str(subdiagram_info.diagramId)
            ).body
            subdiagram_versions: [DiagramShortInfoVersionsView] = []
            for version in sub_versions_response:
                subdiagram_versions.append(
                    DiagramShortInfoVersionsView.construct(**version)
                )
            for version in subdiagram_versions:
                if (
                    version.versionType == VersionType.DEPLOYED
                    and version.versionName == diagram_vers_name
                ):
                    subdiagram_deploy_version_name_correct = True
        with allure.step(
            "Проверка, что имя деплой версии поддиаграммы такое же, как и у диаграммы"
        ):
            assert subdiagram_deploy_version_name_correct

    @allure.story(
        "При отправке диаграммы на развёртывание с узлом поддиаграммы, для вложенной диаграммы появляется "
        "версия с идентичным с versionId deploy версии верхней диаграммы rootObjectVersionId"
    )
    @allure.title("Получить деплой версию поддиаграммы, проверить rootObject")
    @pytest.mark.skip("obsolete")
    def test_submit_subdiagram_node_subdiagram_vers_root(
        self, super_user, diagram_subdiagram_submit_working
    ):
        subdiagram_deploy_version_root_object_correct = False
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_subdiagram_submit_working["diagram_id"]
            subdiagram_version_id = diagram_subdiagram_submit_working["subdiagram_version_id"]
            get_subdiagram_by_version_response = get_diagram_by_version(
                super_user, subdiagram_version_id
            )
            subdiagram_info = DiagramViewDto.construct(
                **get_subdiagram_by_version_response.body
            )
            # version_id = create_and_save_result["create_result"]["uuid"]
        with allure.step("Отправка диаграммы на деплой"):
            submit_response = put_diagram_submit(super_user, diagram_id)
        with allure.step("Получение списка версий диаграммы"):
            diagram_deploy_version = None
            versions_response = get_diagram_versions(super_user, diagram_id)
            diagram_versions: [DiagramShortInfoVersionsView] = versions_response.body
            for version in diagram_versions:
                if version["versionType"] == "DEPLOYED":
                    diagram_deploy_version = version["versionId"]
        with allure.step("Получение списка версий поддиаграммы"):
            sub_versions_response = get_diagram_versions(
                super_user, str(subdiagram_info.diagramId)
            ).body
            subdiagram_versions: [DiagramShortInfoVersionsView] = []
            for version in sub_versions_response:
                subdiagram_versions.append(
                    DiagramShortInfoVersionsView.construct(**version)
                )
            for version in subdiagram_versions:
                if (
                    version.versionType == VersionType.DEPLOYED
                    and version.rootObjectVersionId == diagram_deploy_version
                ):
                    subdiagram_deploy_version_root_object_correct = True
        with allure.step(
            "Проверка, что root object поддиаграммы совпадает с деплой версией диаграммы"
        ):
            assert subdiagram_deploy_version_root_object_correct

    @allure.story(
        "При отправке диаграммы на развёртывание с узлом поддиаграммы, для вложенной диаграммы появляется "
        "версия с versionType: DEPLOYED"
    )
    @allure.title(
        "Отправить на развёртывание диаграмму с узлом поддиаграммы, деплой версия поддиаграммы появилась"
    )
    @pytest.mark.smoke
    def test_submit_subdiagram_node_subdiagram_deploy_vers(
        self, super_user, diagram_subdiagram_submit_working
    ):
        subdiagram_deploy_version_found = False
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_subdiagram_submit_working["diagram_id"]
            subdiagram_version_id = diagram_subdiagram_submit_working["subdiagram_version_id"]
            get_subdiagram_by_version_response = get_diagram_by_version(
                super_user, subdiagram_version_id
            )
            subdiagram_info = DiagramViewDto.construct(
                **get_subdiagram_by_version_response.body
            )
            # version_id = create_and_save_result["create_result"]["uuid"]
        with allure.step("Отправка диаграммы на деплой"):
            submit_response = put_diagram_submit(super_user, diagram_id)
        with allure.step("Получение списка версий поддиаграммы"):
            sub_versions_response = get_diagram_versions(
                super_user, str(subdiagram_info.diagramId)
            ).body
            subdiagram_versions: [DiagramShortInfoVersionsView] = []
            for version in sub_versions_response:
                subdiagram_versions.append(
                    DiagramShortInfoVersionsView.construct(**version)
                )
            for version in subdiagram_versions:
                if version.versionType == VersionType.DEPLOYED:
                    subdiagram_deploy_version_found = True
        with allure.step("Проверка, что деплой версия поддиаграммы появилась"):
            assert subdiagram_deploy_version_found

    @allure.story(
        "При отправке диаграммы на развёртывание с узлом поддиаграммы, в ДЕПЛОЙ версии диаграммы в узле "
        "поддиаграммы VersionId сменился на versionId созданной деплой версии вложенной диаграммы"
    )
    @allure.title(
        "Получить информацию о деплой версии диаграммы, проверить, что в узле поддиаграммы ссылка на деплой "
        "версию поддиаграммы"
    )
    def test_submit_subdiagram_node_subdiagram_node_vers_changed_in_node(
        self, super_user, diagram_subdiagram_submit_working
    ):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_subdiagram_submit_working["diagram_id"]
            subdiagram_version_id = diagram_subdiagram_submit_working["subdiagram_version_id"]
            get_subdiagram_by_version_response = get_diagram_by_version(
                super_user, subdiagram_version_id
            )
            subdiagram_info = DiagramViewDto.construct(
                **get_subdiagram_by_version_response.body
            )
            # version_id = create_and_save_result["create_result"]["uuid"]
        with allure.step("Отправка диаграммы на деплой"):
            submit_response = put_diagram_submit(super_user, diagram_id)
        with allure.step("Получение списка версий диаграммы"):
            diagram_deploy_version = None
            versions_response = get_diagram_versions(super_user, diagram_id)
            diagram_versions: [DiagramShortInfoVersionsView] = versions_response.body
            for version in diagram_versions:
                if version["versionType"] == "DEPLOYED":
                    diagram_deploy_version = version["versionId"]
        with allure.step("Получение списка версий поддиаграммы"):
            sub_versions_response = get_diagram_versions(
                super_user, str(subdiagram_info.diagramId)
            ).body
            subdiagram_versions: [DiagramShortInfoVersionsView] = []
            subdiagram_deploy_version_id = None
            for version in sub_versions_response:
                subdiagram_versions.append(
                    DiagramShortInfoVersionsView.construct(**version)
                )
            for version in subdiagram_versions:
                if version.versionType == VersionType.DEPLOYED:
                    subdiagram_deploy_version_id = version.versionId
        with allure.step("Получение информации о деплой версии диаграммы"):
            deploy_diag_info = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, diagram_deploy_version).body
            )
            for node in deploy_diag_info.nodes.values():
                if node["nodeTypeId"] == 14:
                    node_sub_id = node["nodeId"]
            sub_node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_sub_id).body)
        with allure.step(
            "Проверка, что в узле поддиаграммы, узел ссылается на деплой версию поддиаграммы"
        ):
            assert sub_node_view.properties["versionId"] == subdiagram_deploy_version_id

    @allure.story(
        "При отправке диаграммы на развёртывание с переменной комплексного типа, для вложенного типа "
        "появляется версия с идентичным для диаграммы versionName"
    )
    @allure.title(
        "Получить деплой версию пользовательского типа, проверить, что имя, как у деплой версии диаграммы"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_cmplx_type", varType="in", isComplex=True),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_submit_diagram_ctype_vers_name(self, super_user, diagram_constructor):
        ctype_deploy_version_name_correct = False
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_constructor["diagram_id"]
            complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]
        with allure.step("Отправка диаграммы на развёртывание"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Получение списка версий диаграммы"):
            diagram_vers_name = None
            versions_response = get_diagram_versions(super_user, diagram_id)
            diagram_versions: [DiagramShortInfoVersionsView] = versions_response.body
            for version in diagram_versions:
                if version["versionType"] == "DEPLOYED":
                    diagram_vers_name = version["versionName"]
        with allure.step("Получение списка версий"):
            versions_body = list_complex_type_versions(
                super_user, complex_type.typeId
            ).body
            type_versions: [ComplexTypeGetFullVersionView] = []
            for version in versions_body:
                type_versions.append(ComplexTypeGetFullVersionView.construct(**version))
            for vers in type_versions:
                if vers.versionName == diagram_vers_name:
                    ctype_deploy_version_name_correct = True
        with allure.step(
            "Проверка, что имя деплой версии типа такое же, как и у диаграммы"
        ):
            assert ctype_deploy_version_name_correct

    @allure.story(
        "При отправке диаграммы на развёртывание с переменной комплексного типа, для типа появляется версия "
        "с идентичным с versionId deploy версии диаграммы rootObjectVersionId"
    )
    @allure.title("Получить деплой версию комплекс типа, проверить rootObject")
    @pytest.mark.variable_data([VariableParams(varName="in_cmplx_type", varType="in", isComplex=True),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.save_diagram(True)
    @pytest.mark.skip("obsolete")
    def test_submit_diagram_ctype_vers_root(self, super_user, diagram_constructor):
        type_deploy_version_root_object_correct = False
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_constructor["diagram_id"]
            complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]
        with allure.step("Отправка диаграммы на деплой"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Получение списка версий диаграммы"):
            diagram_deploy_version = None
            versions_response = get_diagram_versions(super_user, diagram_id)
            diagram_versions: [DiagramShortInfoVersionsView] = versions_response.body
            for version in diagram_versions:
                if version["versionType"] == "DEPLOYED":
                    diagram_deploy_version = version["versionId"]
        with allure.step("Получение списка версий комплекс типа"):
            versions_body = list_complex_type_versions(
                super_user, complex_type.typeId
            ).body
            type_versions: [ComplexTypeGetFullVersionView] = []
            for version in versions_body:
                type_versions.append(ComplexTypeGetFullVersionView.construct(**version))
            for version in type_versions:
                if (
                    version.versionType == VersionType.DEPLOYED
                    and version.rootObjectVersionId == diagram_deploy_version
                ):
                    type_deploy_version_root_object_correct = True
        with allure.step(
            "Проверка, что root object типа совпадает с деплой версией диаграммы"
        ):
            assert type_deploy_version_root_object_correct

    @allure.story(
        "При отправке диаграммы на развёртывание с переменной комплексного типа, для вложенного типа "
        "появляется версия с versionType: DEPLOYED"
    )
    @allure.title(
        "Развёртывание диаграммы с переменной пользовательского типа, деплой версия типа появилась"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_cmplx_type", varType="in", isComplex=True),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_submit_diagram_ctype_deploy_vers(self, super_user, diagram_constructor):
        ctype_deploy_version_found = False
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_constructor["diagram_id"]
            complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]
        with allure.step("Отправка диаграммы на деплой"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Получение списка версий комплекс типа"):
            versions_body = list_complex_type_versions(
                super_user, complex_type.typeId
            ).body
            type_versions: [ComplexTypeGetFullVersionView] = []
            for version in versions_body:
                type_versions.append(ComplexTypeGetFullVersionView.construct(**version))
            for version in type_versions:
                if version.versionType == VersionType.DEPLOYED:
                    ctype_deploy_version_found = True
        with allure.step("Проверка, что деплой версия комплекс типа появилась"):
            assert ctype_deploy_version_found

    @allure.story(
        "При отправке диаграммы на развёртывание с переменной комплексного типа, в ДЕПЛОЙ версии диаграммы "
        "в переменной диаграммы VersionId сменился на versionId созданной деплой версии вложенного типа"
    )
    @allure.title(
        "В информации о деплой версии диаграммы, проверить, что в переменной диаграммы ссылка на деплой "
        "версию пользовательского типа"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_cmplx_type", varType="in", isComplex=True),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.save_diagram(True)
    def test_submit_diagram_ctype_vers_changed_in_node(
        self, super_user, diagram_constructor
    ):
        parameter_version_is_deploy_type_version = False
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_constructor["diagram_id"]
            complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]
        with allure.step("Отправка диаграммы на деплой"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Получение списка версий диаграммы"):
            diagram_deploy_version = None
            versions_response = get_diagram_versions(super_user, diagram_id)
            diagram_versions: [DiagramShortInfoVersionsView] = versions_response.body
            for version in diagram_versions:
                if version["versionType"] == "DEPLOYED":
                    diagram_deploy_version = version["versionId"]
        with allure.step("Получение списка версий комплекс типа"):
            ctype_deploy_version_id = None
            versions_body = list_complex_type_versions(
                super_user, complex_type.typeId
            ).body
            type_versions: [ComplexTypeGetFullVersionView] = []
            for version in versions_body:
                type_versions.append(ComplexTypeGetFullVersionView.construct(**version))
            for version in type_versions:
                if version.versionType == VersionType.DEPLOYED:
                    ctype_deploy_version_id = version.versionId
        with allure.step("Получение информации о деплой версии диаграммы"):
            deploy_diag_info = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, diagram_deploy_version).body
            )
            params = get_diagram_parameters(super_user, diagram_deploy_version).body
            for param in params["inOutParameters"]:
                if param["parameterType"] == "IN" and param["complexFlag"]:
                    if param["typeId"] == ctype_deploy_version_id:
                        parameter_version_is_deploy_type_version = True
        with allure.step(
            "Проверка, что идентификатор переменной деплой версии диаграммы - деплой версия типа"
        ):
            assert parameter_version_is_deploy_type_version

    # def test_invalid_diagram_not_in_deploy_list(self):
