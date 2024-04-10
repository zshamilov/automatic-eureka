import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import ResponseDto, ScriptFullView, VariableType1, ScriptUpdateUserVersion, \
    ScriptFullVersionView
from products.Decision.framework.steps.decision_steps_script_api import get_groovy_script_by_id, update_groovy_script, \
    update_python_script, get_python_script_by_id, update_user_version, get_script_versions_by_id
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description
from products.Decision.utilities.custom_code_constructors import code_update_construct, script_vars_construct


@allure.epic("Кастомные коды")
@allure.feature("Обновление кастомного кода")
@pytest.mark.scenario("DEV-15466")
class TestCustomCodesUpdate:

    @allure.story("Возможно обновить Groovy скрипт(имя, описание, текст скрипта)")
    @allure.title("Обновить поля name, decription, text groovy скрипта")
    @pytest.mark.smoke
    def test_update_groovy_script_name_desc_text(self, super_user, create_groovy_code_int_vars):
        groovy_code_create_result: ScriptFullView = create_groovy_code_int_vars["code_create_result"]
        inp_var = create_groovy_code_int_vars["inp_var"]
        out_var = create_groovy_code_int_vars["out_var"]
        script_view_old = ScriptFullView.construct(
            **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body)
        updated_text = "output_int = input_int + 4"
        updated_name = "updated_groovy_script_ag_" + generate_diagram_name_description(6, 1)["rand_name"]
        script_update = code_update_construct(script_id=script_view_old.scriptId,
                                              version_id=script_view_old.versionId,
                                              script_type="groovy",
                                              script_name=updated_name,
                                              script_text=updated_text,
                                              variables=[inp_var, out_var],
                                              description="this_script_was_updated")
        script_version_id = groovy_code_create_result.versionId
        groovy_code_update_result: ScriptFullView = update_groovy_script(super_user,
                                                                         script_update)
        script_view = ScriptFullView.construct(
            **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body)

        assert script_view.scriptText == updated_text \
               and script_view.objectName == updated_name \
               and script_view.description == "this_script_was_updated"

    @allure.story("Невозможно обновить Groovy скрипт с именем, которое уже есть в списке.")
    @allure.title("Обновить поле name groovy скрипта на уже существующее")
    @allure.issue("DEV-2929")
    def test_update_groovy_script_name_not_unique(self, super_user, create_code_gen):
        with allure.step("Создание первого скрипта"):
            inp_var1 = script_vars_construct(var_name="input_int",
                                             var_type=VariableType1.IN,
                                             is_array=False, primitive_id="1")
            out_var1 = script_vars_construct(var_name="output_int",
                                             var_type=VariableType1.OUT,
                                             is_array=False, primitive_id="1")
            script_text1 = "output_int = input_int + 2"
            script_name1 = "test_groovy_script_" + generate_diagram_name_description(6, 1)["rand_name"]
            groovy_code_create_result1: ScriptFullView = \
                create_code_gen.create_groovy_code(script_text1, script_name1, inp_var1, out_var1)["code_create_result"]
        with allure.step("Создание второго скрипта"):
            script_text2 = "output_int = input_int + 2"
            script_name2 = "test_groovy_script_" + generate_diagram_name_description(6, 1)["rand_name"]
            groovy_code_create_result2: ScriptFullView = \
                create_code_gen.create_groovy_code(script_text2, script_name2, inp_var1, out_var1)["code_create_result"]
            script_view_old = ScriptFullView.construct(
                **get_groovy_script_by_id(super_user, groovy_code_create_result2.versionId).body)
        with allure.step("Обновление имени второго скрипта на имя первого скрипта"):
            updated_name = script_name1
            script_version_id = groovy_code_create_result2.versionId
            script_update = code_update_construct(script_id=script_view_old.scriptId,
                                                  version_id=script_version_id,
                                                  script_type="groovy",
                                                  script_name=updated_name,
                                                  script_text=script_text2,
                                                  variables=[inp_var1, out_var1],
                                                  description="this_script_was_updated")
        with allure.step("Проверка, что клиенту запрещено обновлять скрипт на уже существующее имя"):
            with pytest.raises(HTTPError, match="400"):
                assert update_groovy_script(super_user, script_update)

    @allure.story("Возможно обновить Python скрипт(имя, описание, текст скрипта)")
    @allure.title("Обновить поля name, decription, text python скрипта")
    @allure.issue("DEV-15688")
    @pytest.mark.smoke
    def test_update_python_script_name_desc_text(self, super_user, create_python_code_int_vars):
        python_code_create_result: ScriptFullView = create_python_code_int_vars["code_create_result"]
        inp_var = create_python_code_int_vars["inp_var"]
        script_view_old = ScriptFullView.construct(
            **get_python_script_by_id(super_user, python_code_create_result.versionId).body)
        out_var = create_python_code_int_vars["out_var"]
        updated_text = "output_int = input_int + 4"
        updated_name = "updated_python_script_ag_" + generate_diagram_name_description(6, 1)["rand_name"]
        script_version_id = python_code_create_result.versionId
        script_update = code_update_construct(script_id=script_view_old.scriptId,
                                              version_id=script_version_id,
                                              script_type="python",
                                              script_name=updated_name,
                                              script_text=updated_text,
                                              variables=[inp_var, out_var],
                                              description="this_script_was_updated")
        python_code_update_result: ScriptFullView = update_python_script(super_user,
                                                                         script_update)
        script_view = ScriptFullView.construct(
            **get_python_script_by_id(super_user, python_code_create_result.versionId).body)

        assert script_view.scriptText == updated_text \
               and script_view.objectName == updated_name \
               and script_view.description == "this_script_was_updated"

    @allure.story("Невозможно обновить Python скрипт с именем, которое уже есть в списке.")
    @allure.title("Обновить поле name python скрипта на уже существующее")
    @allure.issue("DEV-2929")
    def test_update_python_script_name_not_unique(self, super_user, create_code_gen):
        with allure.step("Создание первого скрипта"):
            inp_var1 = script_vars_construct(var_name="input_int",
                                             var_type=VariableType1.IN,
                                             is_array=False, primitive_id="1")
            out_var1 = script_vars_construct(var_name="output_int",
                                             var_type=VariableType1.OUT,
                                             is_array=False, primitive_id="1")
            script_text1 = "output_int = input_int + 2"
            script_name1 = "test_python_script_" + generate_diagram_name_description(6, 1)["rand_name"]
            python_code_create_result1: ScriptFullView = \
                create_code_gen.create_python_code(script_text1, script_name1, inp_var1, out_var1)["code_create_result"]
        with allure.step("Создание второго скрипта"):
            script_text2 = "output_int = input_int + 2"
            script_name2 = "test_python_script_" + generate_diagram_name_description(6, 1)["rand_name"]
            python_code_create_result2: ScriptFullView = \
                create_code_gen.create_python_code(script_text2, script_name2, inp_var1, out_var1)["code_create_result"]
            script_view_old = ScriptFullView.construct(
                **get_python_script_by_id(super_user, python_code_create_result2.versionId).body)
        with allure.step("Обновление имени второго скрипта на имя первого скрипта"):
            updated_name = script_name1
            script_version_id = python_code_create_result2.versionId
            script_update = code_update_construct(script_id=script_view_old.scriptId,
                                                  version_id=script_version_id,
                                                  script_type="python",
                                                  script_name=updated_name,
                                                  script_text=script_text2,
                                                  variables=[inp_var1, out_var1],
                                                  description="this_script_was_updated")
        with allure.step("Проверка, что клиенту запрещено обновлять скрипт на уже существующее имя"):
            with pytest.raises(HTTPError, match="400"):
                assert update_python_script(super_user, script_update)

    @allure.story("Невозможно обновить Groovy скрипт без кода scriptText:"", scriptText:null")
    @allure.title("при обновлении groovy скрипта в поле text не ввести ничего")
    def test_update_groovy_script_without_text(self, super_user, create_groovy_code_int_vars):
        groovy_code_create_result: ScriptFullView = create_groovy_code_int_vars["code_create_result"]
        inp_var = create_groovy_code_int_vars["inp_var"]
        script_view_old = ScriptFullView.construct(
            **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body)
        out_var = create_groovy_code_int_vars["out_var"]
        updated_text = None
        updated_name = "updated_groovy_script_ag_" + generate_diagram_name_description(6, 1)["rand_name"]
        script_version_id = groovy_code_create_result.versionId
        script_update = code_update_construct(script_id=script_view_old.scriptId,
                                              version_id=script_version_id,
                                              script_type="groovy",
                                              script_name=updated_name,
                                              script_text=updated_text,
                                              variables=[inp_var, out_var],
                                              description="this_script_was_updated")
        with pytest.raises(HTTPError, match="400"):
            assert update_python_script(super_user, script_update)

    @allure.story("Невозможно обновить Python скрипт без кода scriptText:"", scriptText:null")
    @allure.title("при обновлении python скрипта в поле text не ввести ничего")
    def test_update_python_script_without_text(self, super_user, create_python_code_int_vars):
        python_code_create_result: ScriptFullView = create_python_code_int_vars["code_create_result"]
        inp_var = create_python_code_int_vars["inp_var"]
        script_view_old = ScriptFullView.construct(
            **get_python_script_by_id(super_user, python_code_create_result.versionId).body)
        out_var = create_python_code_int_vars["out_var"]
        updated_text = None
        updated_name = "updated_python_script_ag_" + generate_diagram_name_description(6, 1)["rand_name"]
        script_version_id = python_code_create_result.versionId
        script_update = code_update_construct(script_id=script_view_old.scriptId,
                                              version_id=script_version_id,
                                              script_type="python",
                                              script_name=updated_name,
                                              script_text=updated_text,
                                              variables=[inp_var, out_var],
                                              description="this_script_was_updated")
        with pytest.raises(HTTPError, match="400"):
            assert update_python_script(super_user, script_update)

    @allure.story("Возможно обновить Groovy скрипт(разные атрибуты)")
    @allure.title("Обновить атрибуты groovy скрипта")
    @pytest.mark.smoke
    def test_update_groovy_script_attrs(self, super_user, create_groovy_code_int_vars):
        in_var_updated = False
        out_var_updated = False
        groovy_code_create_result: ScriptFullView = create_groovy_code_int_vars["code_create_result"]
        script_view_old = ScriptFullView.construct(
            **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body)
        script_name = create_groovy_code_int_vars["script_name"]
        script_text = create_groovy_code_int_vars["script_text"]
        inp_var_up = script_vars_construct(var_name="input_float",
                                           var_type=VariableType1.IN.value,
                                           is_array=False, primitive_id="0")
        out_var_up = script_vars_construct(var_name="output_float",
                                           var_type=VariableType1.OUT.value,
                                           is_array=False, primitive_id="0")
        script_version_id = groovy_code_create_result.versionId
        script_update = code_update_construct(script_id=script_view_old.scriptId,
                                              version_id=script_version_id,
                                              script_type="groovy",
                                              script_name=script_name,
                                              script_text=script_text,
                                              variables=[inp_var_up, out_var_up],
                                              description="this_script_was_updated")
        groovy_code_update_result: ScriptFullView = update_groovy_script(super_user,
                                                                         script_update)
        script_view = ScriptFullView.construct(
            **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body)

        for variable in script_view.variables:
            if variable["variableName"] == "input_float" and variable["primitiveTypeId"] == "0":
                in_var_updated = True
            if variable["variableName"] == "output_float" and variable["primitiveTypeId"] == "0":
                out_var_updated = True

        assert in_var_updated and out_var_updated

    @allure.story("Возможно обновить Python скрипт(разные атрибуты)")
    @allure.title("Обновить атрибуты python скрипта")
    @pytest.mark.smoke
    def test_update_python_script_attrs(self, super_user, create_python_code_int_vars):
        in_var_updated = False
        out_var_updated = False
        python_code_create_result: ScriptFullView = create_python_code_int_vars["code_create_result"]
        script_view_old = ScriptFullView.construct(
            **get_python_script_by_id(super_user, python_code_create_result.versionId).body)
        script_name = create_python_code_int_vars["script_name"]

        script_text = create_python_code_int_vars["script_text"]
        inp_var_up = script_vars_construct(var_name="input_float",
                                           var_type=VariableType1.IN.value,
                                           is_array=False, primitive_id="0")
        out_var_up = script_vars_construct(var_name="output_float",
                                           var_type=VariableType1.OUT.value,
                                           is_array=False, primitive_id="0")
        script_version_id = python_code_create_result.versionId
        script_update = code_update_construct(script_id=script_view_old.scriptId,
                                              version_id=script_version_id,
                                              script_type="python",
                                              script_name=script_name,
                                              script_text=script_text,
                                              variables=[inp_var_up, out_var_up],
                                              description="this_script_was_updated")
        python_code_update_result: ScriptFullView = update_python_script(super_user,
                                                                         script_update)
        script_view = ScriptFullView.construct(
            **get_python_script_by_id(super_user, python_code_create_result.versionId).body)
        for variable in script_view.variables:
            if variable["variableName"] == "input_float" and variable["primitiveTypeId"] == "0":
                in_var_updated = True
            if variable["variableName"] == "output_float" and variable["primitiveTypeId"] == "0":
                out_var_updated = True

        assert in_var_updated and out_var_updated

    @allure.story("Возможно обновить пользовательскую версию существующего скрипта")
    @allure.title("Обновить имя и описание юзер-версии скрипта")
    @pytest.mark.smoke
    def test_update_user_version(self, super_user, create_groovy_code_int_vars_user_version):
        version_found = False
        version_updated_correct = False
        user_version_id = create_groovy_code_int_vars_user_version["user_version_id"]
        script_id = create_groovy_code_int_vars_user_version["script_id"]
        new_vers_name = "new_updated_version"
        new_vers_description = "description_was_also_updated"
        update_body = ScriptUpdateUserVersion(versionName=new_vers_name,
                                              versionDescription=new_vers_description)
        create_vers_result: ResponseDto = ResponseDto.construct(**
                                                                update_user_version(super_user, user_version_id,
                                                                                    update_body).body)
        versions_body = get_script_versions_by_id(super_user, script_id).body
        versions: [ScriptFullVersionView] = []
        for version in versions_body:
            versions.append(ScriptFullVersionView.construct(**version))
        for version in versions:
            if version.versionId == user_version_id:
                version_found = True
                if version.versionDescription == new_vers_description and version.versionName == new_vers_name:
                    version_updated_correct = True
        assert version_found and version_updated_correct
