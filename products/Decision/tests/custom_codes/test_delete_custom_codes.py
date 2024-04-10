import glamor as allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import (
    ResponseDto,
    ScriptFullView,
    ScriptFullVersionView,
)
from products.Decision.framework.steps.decision_steps_script_api import (
    get_python_script_by_id,
    delete_script_by_id,
    get_script_versions_by_id,
)
from products.Decision.runtime_tests.runtime_fixtures.custom_code_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, IntValueType


@allure.epic("Кастомные коды")
@allure.feature("Удаление кастомного кода")
class TestCustomCodesDelete:
    @allure.story("Скрипт успешно удаляется по идентификатору")
    @allure.title("Удалить скрипт, проверить, что не найден")
    @pytest.mark.scenario("DEV-15466")
    @pytest.mark.smoke
    def test_delete_python_custom_code(self, super_user, create_python_code_int_vars):
        python_code_create_result: ScriptFullView = create_python_code_int_vars[
            "code_create_result"
        ]
        delete_script_by_id(super_user, python_code_create_result.versionId)
        with pytest.raises(HTTPError, match="404"):
            assert get_python_script_by_id(
                    super_user, python_code_create_result.versionId
                    )

    @allure.story(
        "Удалённая user local версия python скрипта пропадает из списка версий этого скрипта"
    )
    @allure.title("Удалить юзер-версию python скрипта, проверить что пропала из списка")
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_delete_python_code_user_version(
        self, super_user, create_python_code_int_vars, create_code_gen
    ):
        version_found = False
        with allure.step("Создание python скрипта"):
            python_code: ScriptFullView = create_python_code_int_vars["code_view"]
            script_name = create_python_code_int_vars["script_name"]
            script_text = create_python_code_int_vars["script_text"]
            inp_var = create_python_code_int_vars["inp_var"]
            out_var = create_python_code_int_vars["out_var"]
            script_id = python_code.scriptId
        with allure.step("Создание юзер-версии python скрипта из latest версии"):
            vers_name = "user_version_" + script_name
            create_vers_result: ResponseDto = (
                create_code_gen.create_python_code_user_version(
                    script_id, script_text, script_name, vers_name, inp_var, out_var
                )["vers_create_result"]
            )
        with allure.step("Удаление юзер-версии python скрипта"):
            delete_script_by_id(super_user, create_vers_result.uuid)
        with allure.step("Получение списка версий скрипта"):
            versions_body = get_script_versions_by_id(super_user, script_id).body
            versions: [ScriptFullVersionView] = []
            for version in versions_body:
                versions.append(ScriptFullVersionView.construct(**version))
            for version in versions:
                if version.versionId == create_vers_result.uuid:
                    version_found = True
        with allure.step("Проверка, что удалённая юзер-версия не найдена"):
            assert not version_found

    @allure.story(
        "Удалённая user local версия groovy скрипта пропадает из списка версий этого скрипта"
    )
    @allure.title("Удалить юзер-версию groovy скрипта, проверить что пропала из списка")
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_delete_groovy_code_user_version(
        self, super_user, create_groovy_code_int_vars, create_code_gen
    ):
        version_found = False
        with allure.step("Создание groovy скрипта"):
            groovy_code: ScriptFullView = create_groovy_code_int_vars["code_view"]
            script_name = create_groovy_code_int_vars["script_name"]
            script_text = create_groovy_code_int_vars["script_text"]
            inp_var = create_groovy_code_int_vars["inp_var"]
            out_var = create_groovy_code_int_vars["out_var"]
            script_id = groovy_code.scriptId
        with allure.step("Создание юзер-версии groovy скрипта из latest версии"):
            vers_name = "user_version_" + script_name
            create_vers_result: ResponseDto = (
                create_code_gen.create_groovy_code_user_version(
                    script_id, script_text, script_name, vers_name, inp_var, out_var
                )["vers_create_result"]
            )
        with allure.step("Удаление юзер-версии groovy скрипта"):
            delete_script_by_id(super_user, create_vers_result.uuid)
        with allure.step("Получение списка версий скрипта"):
            versions_body = get_script_versions_by_id(super_user, script_id).body
            versions: [ScriptFullVersionView] = []
            for version in versions_body:
                versions.append(ScriptFullVersionView.construct(**version))
            for version in versions:
                if version.versionId == create_vers_result.uuid:
                    version_found = True
        with allure.step("Проверка, что удалённая юзер-версия не найдена"):
            assert not version_found

    @allure.story(
        "Нельзя удалить глобал-версию скрипта"
    )
    @allure.issue("DEV-12199")
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["кастомный код"])
    @allure.title("создать глобал-версию диаграммы со скриптом, "
                  "удалить глобальную версию, проверить что нельзя удалить")
    def test_delete_global_version(self, super_user, diagram_custom_code_python_2, save_diagrams_gen):
        script_view = diagram_custom_code_python_2["script_view"]
        diagram_id = diagram_custom_code_python_2["diagram_id"]
        saved_version_id = diagram_custom_code_python_2["saved_version_id"]
        new_diagram_name = diagram_custom_code_python_2["diagram_name"]
        with allure.step("Создание глобальной версии диаграммы"):
            gv_create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram_user_vers(
                    diagram_id=diagram_id,
                    saved_version_id=saved_version_id,
                    version_name="diagram_user_version",
                    diagram_name=new_diagram_name,
                    global_flag=True,
                ).body
            )
        with allure.step("Получить список версий"):
            vers_list = []
            for vers in get_script_versions_by_id(super_user, script_view.scriptId).body:
                vers_list.append(ScriptFullVersionView.construct(**vers))
            for vers in vers_list:
                if vers.versionType == "USER_GLOBAL":
                    version_id = vers.versionId

            with allure.step("Нельзя удалять глобальные версии скриптов"):
                with pytest.raises(HTTPError, match="400"):
                    assert delete_script_by_id(super_user, version_id)
