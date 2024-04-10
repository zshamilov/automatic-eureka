import glamor as allure
from requests import HTTPError

from products.Decision.framework.model import (
    ResponseDto,
    ScriptFullVersionView, ComplexTypeGetFullView,
)
from products.Decision.framework.steps.decision_steps_complex_type import get_custom_type
from products.Decision.framework.steps.decision_steps_script_api import (
    get_script_versions_by_id,
)
from products.Decision.runtime_tests.runtime_fixtures.custom_code_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, IntValueType
from products.Decision.utilities.custom_type_constructors import generate_attr_type_name, attribute_construct


@allure.epic("Кастомные коды")
@allure.feature("Добавление кастомного кода")
class TestCustomCodesAdd:
    @allure.story("Возможно добавить кастомный код Python")
    @allure.title("создать python код, проверить. что создан")
    @pytest.mark.scenario("DEV-15466")
    @pytest.mark.smoke
    def test_create_python_custom_code(self, super_user, create_code_gen):
        inp_var = script_vars_construct(
            var_name="input_int",
            var_type=VariableType1.IN,
            is_array=False,
            primitive_id="1",
        )
        out_var = script_vars_construct(
            var_name="output_int",
            var_type=VariableType1.OUT,
            is_array=False,
            primitive_id="1",
        )
        script_text = "output_int = input_int + 2"
        script_name = (
                "test_python_script_" + generate_string()
        )
        python_code_create_result: ScriptFullView = create_code_gen.create_python_code(
            script_text, script_name, inp_var, out_var
        )["code_create_result"]
        script_view = ScriptFullView.construct(
            **get_python_script_by_id(super_user, python_code_create_result.versionId).body
        )
        assert (
                script_view.scriptText == script_text
                and script_view.objectName == script_name
        )

    @allure.story("Возможно добавить кастомный код Python с переменной complex type")
    @allure.title("создать python код с атрибутом комплекс типа, проверить, что создан")
    @pytest.mark.scenario("DEV-15466")
    @pytest.mark.smoke
    def test_create_python_custom_code_ctype(self, super_user,
                                             create_custom_types_gen,
                                             create_code_gen):
        with allure.step("Создание кастом типа"):
            type_name = generate_attr_type_name(True, False, True, "")
            create_result: ResponseDto = create_custom_types_gen.create_type(
                type_name, [attribute_construct()]
            )
            custom_type_version_id = create_result.uuid
        with allure.step("Поиск созданного типа"):
            complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_custom_type(super_user, custom_type_version_id).body
            )
        inp_var = script_vars_construct(
            var_name="input_int",
            var_type=VariableType1.IN,
            is_array=False,
            primitive_id="1",
        )
        out_var = script_vars_construct(
            var_name="output_var",
            var_type=VariableType1.OUT,
            is_array=False,
            complex_vers_id=complex_type.versionId,
        )
        script_text = "{}"
        script_name = (
                "test_python_script_" + generate_string()
        )
        python_code_create_result: ScriptFullView = create_code_gen.create_python_code(
            script_text, script_name, inp_var, out_var
        )["code_create_result"]
        script_view = ScriptFullView.construct(
            **get_python_script_by_id(super_user, python_code_create_result.versionId).body
        )
        assert (
                script_view.scriptText == script_text
                and script_view.objectName == script_name
        )

    @allure.story(
        "Невозможно создать скрипт Python с именем, которое уже есть в списке"
    )
    @allure.title("создать python код с неуникальным именем, проверить. что запрещено")
    @pytest.mark.scenario("DEV-15466")
    @allure.issue("DEV-2929")
    def test_create_python_custom_code_non_unique(self, super_user, create_code_gen):
        inp_var = script_vars_construct(
            var_name="input_int",
            var_type=VariableType1.IN,
            is_array=False,
            primitive_id="1",
        )
        out_var = script_vars_construct(
            var_name="output_int",
            var_type=VariableType1.OUT,
            is_array=False,
            primitive_id="1",
        )
        script_text = "output_int = input_int + 2"
        script_name = (
                "test_python_script_" + generate_string()
        )
        with pytest.raises(HTTPError, match="400"):
            assert create_code_gen.try_create_python(
                script_text, script_name, inp_var, out_var
            )["code_create_response"]

    @allure.story("Возможно добавить кастомный код Groovy")
    @allure.title("создать groovy код, проверить. что создан")
    @pytest.mark.scenario("DEV-15466")
    @pytest.mark.smoke
    def test_create_groovy_custom_code(self, super_user, create_code_gen):
        inp_var = script_vars_construct(
            var_name="input_int",
            var_type=VariableType1.IN,
            is_array=False,
            primitive_id="1",
        )
        out_var = script_vars_construct(
            var_name="output_int",
            var_type=VariableType1.OUT,
            is_array=False,
            primitive_id="1",
        )
        script_text = "output_int = input_int + 2"
        script_name = (
                "test_groovy_script_" + generate_string()
        )
        groovy_code_create_result: ScriptFullView = create_code_gen.create_groovy_code(
            script_text, script_name, inp_var, out_var
        )["code_create_result"]
        script_view = ScriptFullView.construct(
            **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body
        )
        assert (
                script_view.scriptText == script_text
                and script_view.objectName == script_name
        )

    @allure.story(
        "Невозможно создать скрипт Groovy с именем, которое уже есть в списке"
    )
    @allure.title("создать groovy код с неуникальным именем, проверить. что запрещено")
    @pytest.mark.scenario("DEV-15466")
    @allure.issue("DEV-2929")
    def test_create_groovy_custom_code_non_unique(self, super_user, create_code_gen):
        inp_var = script_vars_construct(
            var_name="input_int",
            var_type=VariableType1.IN,
            is_array=False,
            primitive_id="1",
        )
        out_var = script_vars_construct(
            var_name="output_int",
            var_type=VariableType1.OUT,
            is_array=False,
            primitive_id="1",
        )
        script_text = "output_int = input_int + 2"
        script_name = (
                "test_groovy_script_" + generate_string()
        )
        groovy_code_create_result: ScriptFullView = create_code_gen.create_groovy_code(
            script_text, script_name, inp_var, out_var
        )["code_create_result"]
        with pytest.raises(HTTPError, match="400"):
            assert create_code_gen.try_create_groovy(
                script_text, script_name, inp_var, out_var)["code_create_response"]

    @allure.story(
        "Невозможно создать Python скрипт без кода scriptText:" ", scriptText:null"
    )
    @allure.title("невозможность создания скрипта без текста скрипта")
    @pytest.mark.scenario("DEV-15466")
    def test_create_bad_custom_code(self, super_user, create_code_gen):
        inp_var = script_vars_construct(
            var_name="input_int",
            var_type=VariableType1.IN,
            is_array=False,
            primitive_id="1",
        )
        out_var = script_vars_construct(
            var_name="output_int",
            var_type=VariableType1.OUT,
            is_array=False,
            primitive_id="1",
        )
        script_name = (
                "test_groovy_script_" + generate_string()
        )
        with pytest.raises(HTTPError, match="400"):
            assert create_code_gen.try_create_groovy(
                    None, script_name, inp_var, out_var
                    )["code_create_response"]

    @allure.story(
        "Возможно создать пользовательскую версию существующего Python скрипта"
    )
    @allure.title("создать юзер-версию python скрипта, проверить параметры")
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_create_python_code_user_version(
            self, super_user, create_python_code_int_vars, create_code_gen
    ):
        version_found = False
        version_correct = False
        python_code: ScriptFullView = create_python_code_int_vars["code_view"]
        script_name = create_python_code_int_vars["script_name"]
        script_text = create_python_code_int_vars["script_text"]
        inp_var = create_python_code_int_vars["inp_var"]
        out_var = create_python_code_int_vars["out_var"]
        script_id = python_code.scriptId
        vers_name = "user_version_" + script_name
        create_vers_result: ResponseDto = (
            create_code_gen.create_python_code_user_version(
                script_id, script_text, script_name, vers_name, inp_var, out_var
            )["vers_create_result"]
        )
        versions_body = get_script_versions_by_id(super_user, script_id).body
        versions: [ScriptFullVersionView] = []
        for version in versions_body:
            versions.append(ScriptFullVersionView.construct(**version))
        for version in versions:
            if version.versionId == create_vers_result.uuid:
                version_found = True
                if (
                        version.versionDescription == "different name"
                        and version.versionName == vers_name
                ):
                    version_correct = True
        assert version_found and version_correct

    @allure.story(
        "Возможно создать пользовательскую версию существующего Groovy скрипта"
    )
    @allure.title("создать юзер-версию groovy скрипта, проверить параметры")
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_create_groovy_code_user_version(
            self, super_user, create_groovy_code_int_vars, create_code_gen
    ):
        version_found = False
        version_correct = False
        groovy_code: ScriptFullView = create_groovy_code_int_vars["code_view"]
        script_name = create_groovy_code_int_vars["script_name"]
        script_text = create_groovy_code_int_vars["script_text"]
        inp_var = create_groovy_code_int_vars["inp_var"]
        out_var = create_groovy_code_int_vars["out_var"]
        script_id = groovy_code.scriptId
        vers_name = "user_version_" + script_name
        create_vers_result: ResponseDto = (
            create_code_gen.create_groovy_code_user_version(
                script_id, script_text, script_name, vers_name, inp_var, out_var
            )["vers_create_result"]
        )
        versions_body = get_script_versions_by_id(super_user, script_id).body
        versions: [ScriptFullVersionView] = []
        for version in versions_body:
            versions.append(ScriptFullVersionView.construct(**version))
        for version in versions:
            if version.versionId == create_vers_result.uuid:
                version_found = True
                if (
                        version.versionDescription == "different name"
                        and version.versionName == vers_name
                ):
                    version_correct = True
        assert version_found and version_correct

    @allure.story(
        "При создании глобальной версии диаграммы со скриптом, создаётся и глобальная версия скрипта"
    )
    @allure.title("создать глобал-версию диаграммы со скриптом,"
                  " проверить что у скрипта появилась глобал_версия")
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["кастомный код"])
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_create_global_version(self, super_user, diagram_custom_code_python_2, save_diagrams_gen):
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
        with allure.step("Поиск в списке версий скриптов глобальной версии скрипта"):
            get_script_versions_by_id(super_user, script_view.scriptId)
            vers_list = []
            for vers in get_script_versions_by_id(super_user, script_view.scriptId).body:
                vers_list.append(ScriptFullVersionView.construct(**vers))
            assert any(vers.versionType == "USER_GLOBAL" for vers in vers_list)
