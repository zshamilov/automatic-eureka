import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import ResponseDto, ComplexTypeGetFullView, VariableType1, ScriptFullView, \
    DataSourceType, OfferFullViewDto
from products.Decision.framework.steps.decision_steps_complex_type import get_custom_type
from products.Decision.framework.steps.decision_steps_offer_api import get_offer_info, update_offer
from products.Decision.framework.steps.decision_steps_script_api import get_python_script_by_id
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description
from products.Decision.utilities.custom_code_constructors import script_vars_construct
from products.Decision.utilities.custom_type_constructors import generate_attr_type_name, attribute_construct
from products.Decision.utilities.offer_constructors import offer_variable_construct, offer_construct


@allure.epic("Шаблоны предложений")
@allure.feature("Изменение шаблона предложения")
@pytest.mark.scenario("DEV-15467")
class TestOffersUpdate:

    @allure.story("Есть возможность создать новый шаблон предложения")
    @allure.title("Создать шаблон предложения, найти в системе")
    @allure.link("DEV-3379")
    @pytest.mark.smoke
    def test_update_offer_name(self, super_user,
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
            offer_name = "test_ag_offer_" + generate_diagram_name_description(6, 1)["rand_name"]
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
            variable_id = search_response.offerVariables[0]["id"]
        with allure.step("Construct an offer variable for update"):
            offer_variable_up = offer_variable_construct(variable_name="test_var",
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
                                                         dynamic_list_type=None,
                                                         variable_id=str(variable_id),
                                                         op="update")
        with allure.step("Construct an offer for update"):
            offer_name_up = "test_ag_offer_up_" + generate_diagram_name_description(6, 1)["rand_name"]
            offer_up = offer_construct(offer_name=offer_name_up,
                                       script_version_id=str(script_view.versionId),
                                       script_id=script_view.scriptId,
                                       script_name=script_view.objectName,
                                       offer_complex_type_version_id=complex_type.versionId,
                                       offer_variables=[offer_variable_up],
                                       op="update",
                                       offer_vers_id=search_response.versionId)
        with allure.step("Update offer name"):
            update_offer(super_user,
                         version_id=str(search_response.versionId),
                         body=offer_up)
        with allure.step("Search updated offer"):
            search_response_up: OfferFullViewDto = OfferFullViewDto.construct(
                **get_offer_info(super_user, create_response.uuid).body)
            assert search_response_up.objectName == offer_name_up and \
                   search_response_up.id == search_response.id

    @allure.issue("DEV-8174")
    @allure.title("Создание двух офферов и изменение имени второго на имя первого")
    @allure.story("Невозможно изменить имя оффера на уже существующее")
    def test_update_not_unique_name(self, super_user,
                                    create_custom_types_gen,
                                    create_code_gen,
                                    create_offer_gen):
        with allure.step("Создать пользовательский тип"):
            type_name = generate_attr_type_name(True, False, True, "")
            create_result: ResponseDto = create_custom_types_gen.create_type(
                type_name, [attribute_construct()]
            )
            custom_type_version_id = create_result.uuid
            complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_custom_type(super_user, custom_type_version_id).body
            )

        with allure.step("Создать скрипт"):
            inp_var = script_vars_construct(
                var_name="input_int",
                var_type=VariableType1.IN,
                is_array=False,
                primitive_id="1",
            )
            out_var = script_vars_construct(
                var_name="output_var",
                var_type=VariableType1.OUT,
                is_array=True,
                complex_vers_id=complex_type.versionId,
            )
            script_text = "{}"
            script_name = (
                    "test_python_script_" + generate_diagram_name_description(6, 1)["rand_name"]
            )
            python_code_create_result: ScriptFullView = create_code_gen.create_python_code(
                script_text, script_name, inp_var, out_var
            )["code_create_result"]
            script_view = ScriptFullView.construct(
                **get_python_script_by_id(super_user, python_code_create_result.versionId).body
            )
        with allure.step("Создать первый оффер"):
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
            offer_name = "test_ag_offer_" + generate_diagram_name_description(6, 1)["rand_name"]
            offer = offer_construct(offer_name=offer_name,
                                    script_version_id=script_view.versionId,
                                    script_id=script_view.scriptId,
                                    script_name=script_view.objectName,
                                    offer_complex_type_version_id=complex_type.versionId,
                                    offer_variables=[offer_variable])
            create_response: ResponseDto = create_offer_gen.create_offer(offer=offer)
            search_response: OfferFullViewDto = OfferFullViewDto.construct(
                **get_offer_info(super_user, create_response.uuid).body)

        with allure.step("Создать второй оффер с уникальным именем"):
            offer_name2 = "test_ag_offer2_" + generate_diagram_name_description(6, 1)["rand_name"]
            offer2 = offer_construct(offer_name=offer_name2,
                                     script_version_id=script_view.versionId,
                                     script_id=script_view.scriptId,
                                     script_name=script_view.objectName,
                                     offer_complex_type_version_id=complex_type.versionId,
                                     offer_variables=[offer_variable])
            create_response2: ResponseDto = create_offer_gen.create_offer(offer=offer2)
            search_response2: OfferFullViewDto = OfferFullViewDto.construct(
                **get_offer_info(super_user, create_response2.uuid).body)
            variable_id2 = search_response2.offerVariables[0]["id"]
        with allure.step("Изменить имя второго оффера на имя первого офера"):
            offer_variable_up = offer_variable_construct(variable_name="test_var",
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
                                                         dynamic_list_type=None,
                                                         variable_id=str(variable_id2),
                                                         op="update")
            offer_up = offer_construct(offer_name=offer_name,
                                       script_version_id=str(script_view.versionId),
                                       script_id=script_view.scriptId,
                                       script_name=script_view.objectName,
                                       offer_complex_type_version_id=complex_type.versionId,
                                       offer_variables=[offer_variable_up],
                                       op="update",
                                       offer_vers_id=search_response2.versionId)
        with allure.step("Проверить, что обновление на существующее имя запрещено"):
            with pytest.raises(HTTPError, match="400"):
                assert update_offer(super_user,
                                    version_id=str(search_response2.versionId),
                                    body=offer_up).body["message"] == "Предложение с таким именем уже существует; "
