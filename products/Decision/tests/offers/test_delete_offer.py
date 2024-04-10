import allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import VariableType1, ComplexTypeGetFullView, ResponseDto, ScriptFullView, \
    DataSourceType, OfferShortInfoVersionDto, VersionType, OfferFullViewDto
from products.Decision.framework.steps.decision_steps_complex_type import get_custom_type
from products.Decision.framework.steps.decision_steps_offer_api import create_offer, delete_offer, get_offer_info, \
    get_offer_versions
from products.Decision.framework.steps.decision_steps_script_api import get_python_script_by_id
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description
from products.Decision.utilities.custom_code_constructors import script_vars_construct
from products.Decision.utilities.custom_type_constructors import attribute_construct, generate_attr_type_name
from products.Decision.utilities.offer_constructors import offer_variable_construct, offer_construct


@allure.epic("Шаблоны предложений")
@allure.feature("Удаление шаблона предложения")
class TestOffersDelete:

    @allure.story("Шаблон предложения удаляется")
    @allure.title("Удалить созданный шаблон предложения")
    @pytest.mark.scenario("DEV-15467")
    @allure.link("DEV-3379")
    @pytest.mark.smoke
    def test_delete_offer(self, super_user,
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
        with allure.step("Construct input variable"):
            inp_var = script_vars_construct(
                var_name="input_int",
                var_type=VariableType1.IN,
                is_array=False,
                primitive_id="1",
            )
        with allure.step("Construct output variable"):
            out_var = script_vars_construct(
                var_name="output_var",
                var_type=VariableType1.OUT,
                is_array=True,
                complex_vers_id=complex_type.versionId,
            )
        with allure.step("Create python script"):
            script_text = "{}"
            script_name = (
                    "test_python_script_" + generate_diagram_name_description(6, 1)["rand_name"]
            )
            python_code_create_result: ScriptFullView = create_code_gen.create_python_code(
                script_text, script_name, inp_var, out_var
            )["code_create_result"]
        with allure.step("Get a script info"):
            script_view = ScriptFullView.construct(
                **get_python_script_by_id(super_user, python_code_create_result.versionId).body
            )
        with allure.step("Construct an offer variable"):
            offer_variable = offer_variable_construct(variable_name="test_var",
                                                      script_variable_name=inp_var.variableName,
                                                      array_flag=False,
                                                      data_source_type=DataSourceType.USER_INPUT,
                                                      mandatory_flag=False,
                                                      primitive_type_id="1",
                                                      complex_type_version_id=None,
                                                      min_value="3",
                                                      max_value="10",
                                                      max_size=None,
                                                      dictionary_id=None,
                                                      dynamic_list_type=None)
        with allure.step("Construct an offer"):
            offer_name = "test_ag_offer_" + generate_string()
            offer = offer_construct(offer_name=offer_name,
                                    script_version_id=script_view.versionId,
                                    script_id=script_view.scriptId,
                                    script_name=script_view.objectName,
                                    offer_complex_type_version_id=complex_type.versionId,
                                    offer_variables=[offer_variable])
        with allure.step("Create offer"):
            create_response: ResponseDto = ResponseDto.construct(
                **create_offer(super_user, body=offer).body)
        with allure.step("Delete offer"):
            delete_offer(super_user, create_response.uuid)
        with allure.step("Assert deleted not found"):
            with pytest.raises(HTTPError, match="404"):
                assert get_offer_info(super_user, create_response.uuid).status == 404

    @allure.story("Можно удалить пользовательскую версию")
    @allure.title("Удалить пользовательскую версию, проверить, что пропала из списков версий")
    @pytest.mark.scenario("DEV-727")
    @allure.link("DEV-3379")
    @pytest.mark.smoke
    def test_delete_user_version(self, super_user,
                                 create_custom_types_gen,
                                 create_code_gen,
                                 create_offer_gen):
        version_found = False
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
        with allure.step("Construct input variable"):
            inp_var = script_vars_construct(
                var_name="input_int",
                var_type=VariableType1.IN,
                is_array=False,
                primitive_id="1",
            )
        with allure.step("Construct output variable"):
            out_var = script_vars_construct(
                var_name="output_var",
                var_type=VariableType1.OUT,
                is_array=True,
                complex_vers_id=complex_type.versionId,
            )
        with allure.step("Create python script"):
            script_text = "{}"
            script_name = (
                    "test_python_script_" + generate_diagram_name_description(6, 1)["rand_name"]
            )
            python_code_create_result: ScriptFullView = create_code_gen.create_python_code(
                script_text, script_name, inp_var, out_var
            )["code_create_result"]
        with allure.step("Get a script info"):
            script_view = ScriptFullView.construct(
                **get_python_script_by_id(super_user, python_code_create_result.versionId).body
            )
        with allure.step("Construct an offer variable"):
            offer_variable = offer_variable_construct(variable_name="test_var",
                                                      script_variable_name=inp_var.variableName,
                                                      array_flag=False,
                                                      data_source_type=DataSourceType.USER_INPUT,
                                                      mandatory_flag=False,
                                                      primitive_type_id="1",
                                                      complex_type_version_id=None,
                                                      min_value="3",
                                                      max_value="10",
                                                      max_size=None,
                                                      dictionary_id=None,
                                                      dynamic_list_type=None)
        with allure.step("Construct an offer"):
            offer_name = "test_ag_offer_" + generate_string()
            offer = offer_construct(offer_name=offer_name,
                                    script_version_id=script_view.versionId,
                                    script_id=script_view.scriptId,
                                    script_name=script_view.objectName,
                                    offer_complex_type_version_id=complex_type.versionId,
                                    offer_variables=[offer_variable])
        with allure.step("Create offer"):
            create_response: ResponseDto = create_offer_gen.create_offer(offer=offer)
        with allure.step("Search offer"):
            search_response: OfferFullViewDto = OfferFullViewDto.construct(
                **get_offer_info(super_user, create_response.uuid).body)
        with allure.step("Construct an offer user version"):
            version_name = "user_version_ag_offer_" + generate_diagram_name_description(6, 1)["rand_name"]
            version_desc = "made_in_test"
            offer_user_version = offer_construct(offer_name=offer_name,
                                                 script_version_id=script_view.versionId,
                                                 script_id=script_view.scriptId,
                                                 script_name=script_view.objectName,
                                                 offer_complex_type_version_id=complex_type.versionId,
                                                 offer_variables=[offer_variable],
                                                 op="create_user_version",
                                                 version_name=version_name,
                                                 version_description=version_desc,
                                                 offer_id=search_response.id)
        with allure.step("Create an offer user version"):
            uv_create_response: ResponseDto = create_offer_gen.create_offer_user_version(
                offer_user_version=offer_user_version,
                offer_id=search_response.id)
            uv_id = uv_create_response.uuid
        with allure.step("Delete offer"):
            delete_offer(super_user, uv_id)
        with allure.step("Get offer versions"):
            versions_list = []
            for version in get_offer_versions(super_user, search_response.id).body:
                versions_list.append(OfferShortInfoVersionDto.construct(**version))
            for version in versions_list:
                if version.versionType == VersionType.USER_LOCAL and \
                        version.versionId == uv_id:
                    version_found = True
        with allure.step("Assert that version found and correct"):
            assert not version_found

    @allure.story("При удалении latest версии удаляются все версии")
    @allure.title("Создать пользовательскую версию, удалить latest, проверить, что список версий пуст")
    @pytest.mark.scenario("DEV-727")
    @allure.link("DEV-3379")
    @pytest.mark.smoke
    def test_delete_latest_uv_deleted(self, super_user,
                                      create_custom_types_gen,
                                      create_code_gen,
                                      create_offer_gen):
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
        with allure.step("Construct input variable"):
            inp_var = script_vars_construct(
                var_name="input_int",
                var_type=VariableType1.IN,
                is_array=False,
                primitive_id="1",
            )
        with allure.step("Construct output variable"):
            out_var = script_vars_construct(
                var_name="output_var",
                var_type=VariableType1.OUT,
                is_array=True,
                complex_vers_id=complex_type.versionId,
            )
        with allure.step("Create python script"):
            script_text = "{}"
            script_name = (
                    "test_python_script_" + generate_diagram_name_description(6, 1)["rand_name"]
            )
            python_code_create_result: ScriptFullView = create_code_gen.create_python_code(
                script_text, script_name, inp_var, out_var
            )["code_create_result"]
        with allure.step("Get a script info"):
            script_view = ScriptFullView.construct(
                **get_python_script_by_id(super_user, python_code_create_result.versionId).body
            )
        with allure.step("Construct an offer variable"):
            offer_variable = offer_variable_construct(variable_name="test_var",
                                                      script_variable_name=inp_var.variableName,
                                                      array_flag=False,
                                                      data_source_type=DataSourceType.USER_INPUT,
                                                      mandatory_flag=False,
                                                      primitive_type_id="1",
                                                      complex_type_version_id=None,
                                                      min_value="3",
                                                      max_value="10",
                                                      max_size=None,
                                                      dictionary_id=None,
                                                      dynamic_list_type=None)
        with allure.step("Construct an offer"):
            offer_name = "test_ag_offer_" + generate_string()
            offer = offer_construct(offer_name=offer_name,
                                    script_version_id=script_view.versionId,
                                    script_id=script_view.scriptId,
                                    script_name=script_view.objectName,
                                    offer_complex_type_version_id=complex_type.versionId,
                                    offer_variables=[offer_variable])
        with allure.step("Create offer"):
            create_response: ResponseDto = create_offer_gen.create_offer(offer=offer)
        with allure.step("Search offer"):
            search_response: OfferFullViewDto = OfferFullViewDto.construct(
                **get_offer_info(super_user, create_response.uuid).body)
        with allure.step("Construct an offer user version"):
            version_name = "user_version_ag_offer_" + generate_diagram_name_description(6, 1)["rand_name"]
            version_desc = "made_in_test"
            offer_user_version = offer_construct(offer_name=offer_name,
                                                 script_version_id=script_view.versionId,
                                                 script_id=script_view.scriptId,
                                                 script_name=script_view.objectName,
                                                 offer_complex_type_version_id=complex_type.versionId,
                                                 offer_variables=[offer_variable],
                                                 op="create_user_version",
                                                 version_name=version_name,
                                                 version_description=version_desc,
                                                 offer_id=search_response.id)
        with allure.step("Create an offer user version"):
            create_offer_gen.create_offer_user_version(
                offer_user_version=offer_user_version,
                offer_id=search_response.id)
        with allure.step("Delete offer latest version"):
            delete_offer(super_user, search_response.versionId)
        with allure.step("Get offer versions"):
            versions_response = get_offer_versions(super_user, search_response.id)
        with allure.step("Assert that after deleting latest version, all versions are deleted"):
            assert len(versions_response.body) == 0
