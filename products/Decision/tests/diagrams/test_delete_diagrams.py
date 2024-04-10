import glamor as allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import DiagramViewDto, ResponseDto, DiagramShortInfoView, \
    DiagramShortInfoVersionsView, DiagramCreateUserVersion
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version, delete_diagram, \
    diagrams_list, delete_diagram_template, put_diagram_submit, \
    get_diagram_versions, create_user_version
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description


@allure.epic("Диаграммы")
@allure.feature("Удаление диаграммы")
class TestDiagramsDelete:
    @allure.story("Удалённая диаграмма не должна отображаться в списке")
    @allure.title("Создать диаграмму, сохранить, удалить, проверить, что не появляется в списке")
    @pytest.mark.scenario("DEV-5853")
    @pytest.mark.smoke
    def test_delete_diagram(self, super_user, create_and_save_empty_diagram):
        diagram_found = False
        # Range
        with allure.step("Создание и сохранение диаграммы"):
            diagram = create_and_save_empty_diagram
            saved_version_id = diagram["versionId"]
            diagram_name = diagram["objectName"]
        # Act
        with allure.step("Запрос на удаление диаграммы по diagramId"):
            delete_result = delete_diagram(super_user, saved_version_id)

        with allure.step("Запрос на получение списка диаграмм"):
            result = diagrams_list(super_user)
            diagram_list: [DiagramShortInfoView] = result.body["content"]

        with allure.step("проверка по всему списку диаграмм, что удалённая диаграмма не найдена"):
            for diagram in diagram_list:
                if diagram["objectName"] == diagram_name:
                    diagram_found = True

            assert diagram_found == False and delete_result.status == 200

    @allure.story("Удалить можно только временную версию для removeTemplate")
    @allure.title("Создать постоянную версию диаграммы, удалить как временную, убедиться, что запрещено")
    @pytest.mark.scenario("DEV-5853")
    def test_delete_diagram_template_only_template(self, super_user, create_and_save_empty_diagram):
        # Range
        with allure.step("Создание постоянной версии диаграммы"):
            diagram = create_and_save_empty_diagram
            diagram_id = diagram["diagramId"]
            version_id = diagram["versionId"]
            diagram_name = diagram["objectName"]

        # Act
        with allure.step("Запрос на удаление временной версии диаграммы по versionId сохранённой диаграммы запрещён"):
            with pytest.raises(HTTPError):
                assert delete_diagram_template(super_user, version_id).status == 400

    @allure.story("Можно удалить временную версию диаграммы")
    @allure.title("Создать временную версию диаграммы, удалить, проверить, что не найдена")
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_delete_diagram_template(self, super_user, create_temp_diagram):
        with allure.step("Создание временной версии диаграммы"):
            template = create_temp_diagram
            temp_version_id = template["versionId"]
        with allure.step("Запрос на удаление временной версии диаграммы по versionId"):
            delete_diagram_template(super_user, temp_version_id)
        with allure.step("Проверка на то, что временная версия не найдена после удаления"):
            with pytest.raises(HTTPError):
                assert get_diagram_by_version(super_user, temp_version_id).status == 404

    @allure.story("Версию типа DEPLOYED и TEST_DEPLOYED удалить нельзя")
    @allure.issue("DEV-4990")
    # @pytest.xfail("DEV-4990")
    @allure.title("Проверить, что клиенту запрещено удалять задеплоенную версию")
    @pytest.mark.scenario("DEV-727")
    def test_delete_diagram_ready_for_deploy(self, super_user, create_temp_diagram,
                                             simple_diagram):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            create_and_save_result = simple_diagram
            diagram_id = create_and_save_result["template"]["diagramId"]
            version_id = create_and_save_result["create_result"]["uuid"]
            get_diagram_versions(super_user, diagram_id)
        with allure.step("Отправка диаграммы на деплой"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Запрос на получение версий диаграмм"):
            versions_response = get_diagram_versions(super_user, diagram_id)
            list_versions: [DiagramShortInfoVersionsView] = versions_response.body
        with allure.step("Проверка, что нельзя удалить деплой версию"):
            for version in list_versions:
                if version["versionType"] == "DEPLOYED":
                    with pytest.raises(HTTPError):
                        assert delete_diagram(super_user, version["versionId"]).status == 400

    @allure.story("Возможно удалить пользовательскую версию диаграммы")
    @allure.title("Удалить user local версию, проверить, что не найдена")
    @pytest.mark.scenario("DEV-727")
    @allure.issue("DEV-6950")
    @pytest.mark.smoke
    def test_delete_diagram_user_version(self, super_user, create_temp_diagram, save_diagrams_gen):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Генерация информации о диаграмме"):
            new_diagram_name = "diagram" + "_" + generate_diagram_name_description(16, 1)["rand_name"]
            diagram_description = 'diagram created in test'
        with allure.step("Сохранение диаграммы"):
            create_result = save_diagrams_gen.save_diagram(diagram_id, temp_version_id, new_diagram_name,
                                                           diagram_description).body
            saved_version_id = create_result["uuid"]
        with allure.step("Создание пользовательской версии диаграммы"):
            uv_create_result: ResponseDto = ResponseDto.construct(**
                                                                  create_user_version(super_user,
                                                                                      body=DiagramCreateUserVersion(
                                                                                          diagramId=diagram_id,
                                                                                          versionId=saved_version_id,
                                                                                          versionDescription="diagram_user_version",
                                                                                          versionName="diagram_user_version",
                                                                                          objectName=new_diagram_name,
                                                                                          globalFlag=False,
                                                                                          errorResponseFlag=False)).body)
            user_version_id = uv_create_result.uuid
        with allure.step("Удаление пользовательской версии диаграммы"):
            delete_diagram(super_user, user_version_id)
        with allure.step(
                "Проверка, что удалённая версия не найдена"):
            with pytest.raises(HTTPError):
                assert get_diagram_by_version(super_user, str(user_version_id)).status == 404

    @allure.story("Возможно удалить пользовательскую версию диаграммы")
    @allure.title("удалить пользовательскую версию, проверить, что не найдена в списке версий")
    @pytest.mark.scenario("DEV-727")
    @allure.issue("DEV-6950")
    def test_user_version_delete_from_vers_list(self, super_user, create_temp_diagram, save_diagrams_gen):
        version_found_in_vers_list = False
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Генерация информации о диаграмме"):
            new_diagram_name = "diagram" + "_" + generate_diagram_name_description(16, 1)["rand_name"]
            diagram_description = 'diagram created in test'
        with allure.step("Сохранение диаграммы"):
            create_result = save_diagrams_gen.save_diagram(diagram_id, temp_version_id, new_diagram_name,
                                                           diagram_description).body
            saved_version_id = create_result["uuid"]
        with allure.step("Создание пользовательской версии диаграммы"):
            uv_create_result: ResponseDto = ResponseDto.construct(**
                                                                  create_user_version(super_user,
                                                                                      body=DiagramCreateUserVersion(
                                                                                          diagramId=diagram_id,
                                                                                          versionId=saved_version_id,
                                                                                          versionDescription="diagram_user_version",
                                                                                          versionName="diagram_user_version",
                                                                                          objectName=new_diagram_name,
                                                                                          globalFlag=False,
                                                                                          errorResponseFlag=False)).body)
            user_version_id = uv_create_result.uuid
            delete_diagram(super_user, user_version_id)
        with allure.step("Загрузка списка версий"):
            version_list = []
            for vers in get_diagram_versions(super_user, diagram_id).body:
                version_list.append(DiagramShortInfoVersionsView.construct(**vers))
            for vers in version_list:
                if vers.versionId == user_version_id:
                    version_found_in_vers_list = True
            assert not version_found_in_vers_list

    @allure.story("Возможно удалить user global версию диаграммы")
    @allure.title("Удалить user global версию, проверить, что не найдена")
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_delete_diagram_global_version(self, super_user, create_temp_diagram, save_diagrams_gen):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Генерация информации о диаграмме"):
            new_diagram_name = "diagram" + "_" + generate_diagram_name_description(16, 1)["rand_name"]
            diagram_description = 'diagram created in test'
        with allure.step("Сохранение диаграммы"):
            create_result = save_diagrams_gen.save_diagram(diagram_id, temp_version_id, new_diagram_name,
                                                           diagram_description).body
            saved_version_id = create_result["uuid"]
        with allure.step("Создание глобальной версии диаграммы"):
            gv_create_result: ResponseDto = ResponseDto.construct(**
                                                                  create_user_version(super_user,
                                                                                      body=DiagramCreateUserVersion(
                                                                                          diagramId=diagram_id,
                                                                                          versionId=saved_version_id,
                                                                                          versionDescription="diagram_user_version",
                                                                                          versionName="diagram_user_version",
                                                                                          objectName=new_diagram_name,
                                                                                          globalFlag=True,
                                                                                          errorResponseFlag=False)).body)
            global_version_id = gv_create_result.uuid
            delete_diagram(super_user, global_version_id)
        with allure.step(
                "Проверка, что версия удалена и не находится"):
            with pytest.raises(HTTPError):
                assert get_diagram_by_version(super_user, str(global_version_id)).status == 404

    @allure.story("При удалении  user global версию диаграммы она пропадает из списка версий диаграмм")
    @allure.title("Удалить user global версию, проверить, что не найдена в списке версий")
    @pytest.mark.scenario("DEV-727")
    def test_delete_diagram_global_version_from_vers_list(self, super_user, create_temp_diagram, save_diagrams_gen):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Генерация информации о диаграмме"):
            new_diagram_name = "diagram" + "_" + generate_diagram_name_description(16, 1)["rand_name"]
            diagram_description = 'diagram created in test'
        with allure.step("Сохранение диаграммы"):
            create_result = save_diagrams_gen.save_diagram(diagram_id, temp_version_id, new_diagram_name,
                                                           diagram_description).body
            saved_version_id = create_result["uuid"]
        with allure.step("Создание глобальной версии диаграммы"):
            gv_create_result: ResponseDto = ResponseDto.construct(**
                                                                  create_user_version(super_user,
                                                                                      body=DiagramCreateUserVersion(
                                                                                          diagramId=diagram_id,
                                                                                          versionId=saved_version_id,
                                                                                          versionDescription="diagram_user_version",
                                                                                          versionName="diagram_user_version",
                                                                                          objectName=new_diagram_name,
                                                                                          globalFlag=True,
                                                                                          errorResponseFlag=False)).body)
            global_version_id = gv_create_result.uuid
            delete_diagram(super_user, global_version_id)
            version_response: DiagramShortInfoVersionsView.construct(**get_diagram_versions(super_user, diagram_id).body)
        with allure.step("Проверка, что версия удалена и не находится в списке версий"):
            vers_list = []
            for vers in get_diagram_versions(super_user, diagram_id).body:
                vers_list.append(DiagramShortInfoVersionsView.construct(**vers))
            assert not any(vers.versionType == "USER_GLOBAL" for vers in vers_list)




