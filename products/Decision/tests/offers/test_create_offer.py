import allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import ResponseDto, ComplexTypeGetFullView, VariableType1, ScriptFullView, \
    DataSourceType, OfferFullViewDto, OfferShortInfoDto, OfferShortInfoVersionDto, VersionType
from products.Decision.framework.steps.decision_steps_complex_type import get_custom_type
from products.Decision.framework.steps.decision_steps_diagram import get_diagram_by_version
from products.Decision.framework.steps.decision_steps_offer_api import get_offer_info, get_offer_list, \
    get_offer_versions
from products.Decision.framework.steps.decision_steps_script_api import get_python_script_by_id
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description
from products.Decision.utilities.custom_code_constructors import script_vars_construct
from products.Decision.utilities.custom_type_constructors import generate_attr_type_name, attribute_construct
from products.Decision.utilities.offer_constructors import offer_variable_construct, offer_construct


@allure.epic("Шаблоны предложений")
@allure.feature("Добавление шаблона предложения")
@pytest.mark.scenario("DEV-15467")
class TestOffersCreate:

    @allure.story("Есть возможность создать новый шаблон предложения")
    @allure.title("Создать шаблон предложения, найти в системе")
    @allure.link("DEV-3379")
    @pytest.mark.smoke
    def test_create_offer(self, super_user,
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
        with allure.step("Assert offer found"):
            assert search_response.objectName == offer_name and \
                   search_response.scriptName == script_name

    @allure.story("Созданный шаблон предложения появляется в списке шаблонов")
    @allure.title("Создать шаблон предложения, найти в списке шаблонов предложения")
    @allure.link("DEV-3379")
    @pytest.mark.smoke
    def test_create_offer_found_in_list(self, super_user,
                                        create_custom_types_gen,
                                        create_code_gen,
                                        create_offer_gen):
        offer_found = False
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
        with allure.step("Get offer list"):
            offer_list = []
            for template in get_offer_list(super_user).body["content"]:
                offer_list.append(OfferShortInfoDto.construct(**template))
            for template in offer_list:
                if template.versionId == create_response.uuid:
                    offer_found = True
        with allure.step("Assert offer found in offer list"):
            assert offer_found

    @allure.story("Шаблон предложения имеет уникальный id")
    @allure.title("Создать два шаблона предложения, сравнить id")
    @allure.issue("DEV-8174")
    def test_create_offer_unique_id(self, super_user,
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
            offer_new = offer_construct(offer_name=offer_name + "new",
                                        script_version_id=script_view.versionId,
                                        script_id=script_view.scriptId,
                                        script_name=script_view.objectName,
                                        offer_complex_type_version_id=complex_type.versionId,
                                        offer_variables=[offer_variable])
        with allure.step("Create offer"):
            create_response: ResponseDto = create_offer_gen.create_offer(offer=offer)
        with allure.step("Create another offer"):
            create_response_new: ResponseDto = create_offer_gen.create_offer(offer=offer_new)
        with allure.step("Search offer"):
            offer_info: OfferFullViewDto = OfferFullViewDto.construct(
                **get_offer_info(super_user, create_response.uuid).body)
            offer_id = offer_info.id
            offer_new_info: OfferFullViewDto = OfferFullViewDto.construct(
                **get_offer_info(super_user, create_response_new.uuid).body)
            offer_id_new = offer_new_info.id
        with allure.step("Assert offer found in offer list"):
            assert offer_id_new != offer_id

    @allure.story("В названии предложения можно использовать любые буквы кириллицы и латинского алфавита, "
                  "а также цифры, символы пробела, нижнего подчеркивания и точки.")
    @allure.title("Создать шаблон предложения с именем с буквами латиницы, кириллицы, цифрами, пробелами, символами и "
                  "точками")
    def test_create_offer_name_valid(self, super_user,
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
        with allure.step("Construct an offer with valid name"):
            offer_name = "test_ag_offer_ ! 123.тест на имя" + generate_diagram_name_description(6, 1)["rand_name"]
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
        with allure.step("Assert offer found and name same as was set"):
            assert search_response.objectName == offer_name

    @allure.story("Название предложения не может быть более 100 знаков")
    @allure.title("Создать шаблон предложения с именами различной длины, проверить возможность")
    @pytest.mark.parametrize(
        "name,status",
        [
            (generate_diagram_name_description(99, 1)["rand_name"], 201),
            (generate_diagram_name_description(100, 1)["rand_name"], 201),
        ],
    )
    def test_create_offer_name_length(self, super_user,
                                      create_custom_types_gen,
                                      create_code_gen,
                                      create_offer_gen,
                                      name,
                                      status):
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
        with allure.step("Construct an offer with name of different length"):
            offer = offer_construct(offer_name=name,
                                    script_version_id=script_view.versionId,
                                    script_id=script_view.scriptId,
                                    script_name=script_view.objectName,
                                    offer_complex_type_version_id=complex_type.versionId,
                                    offer_variables=[offer_variable])
        with allure.step("Create offer"):
            create_response = create_offer_gen.try_create_offer(offer=offer)
        with allure.step("Assert offer found and name same as was set"):
            assert create_response.status == status

    @allure.story("Название предложения не может быть более 100 знаков")
    @allure.title("Создать шаблон предложения с именами различной длины, проверить возможность")
    @pytest.mark.parametrize(
        "name,status",
        [
            (generate_diagram_name_description(101, 1)["rand_name"], 400),
        ],
    )
    def test_create_offer_name_length_neg(self, super_user,
                                          create_custom_types_gen,
                                          create_code_gen,
                                          create_offer_gen,
                                          name,
                                          status):
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
        with allure.step("Construct an offer with name of different length"):
            offer = offer_construct(offer_name=name,
                                    script_version_id=script_view.versionId,
                                    script_id=script_view.scriptId,
                                    script_name=script_view.objectName,
                                    offer_complex_type_version_id=complex_type.versionId,
                                    offer_variables=[offer_variable])
        with allure.step("Name length must be less than 100"):
            with pytest.raises(HTTPError):
                assert create_offer_gen.try_create_offer(offer=offer).status == status

    @allure.story("Название предложения должно начинаться с буквы")
    @allure.title("Создать шаблон предложения с недопустимыми символами вначале")
    @allure.issue("DEV-8122")
    @pytest.mark.parametrize(
        "name,status",
        [
            ("!" + generate_diagram_name_description(8, 1)["rand_name"], 400),
            ("1" + generate_diagram_name_description(8, 1)["rand_name"], 400),
            (" " + generate_diagram_name_description(8, 1)["rand_name"], 400),
        ],
    )
    def test_create_offer_name_starts_with_letter(self, super_user,
                                                  create_custom_types_gen,
                                                  create_code_gen,
                                                  create_offer_gen,
                                                  name,
                                                  status):
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
        with allure.step("Construct an offer with name of different length"):
            offer = offer_construct(offer_name=name,
                                    script_version_id=script_view.versionId,
                                    script_id=script_view.scriptId,
                                    script_name=script_view.objectName,
                                    offer_complex_type_version_id=complex_type.versionId,
                                    offer_variables=[offer_variable])
        with allure.step("You can't create offer with restricted symbols at the start of the name"):
            assert create_offer_gen.try_create_offer(offer=offer).status == status

    @allure.story("Название предложения должно быть уникально")
    @allure.title("Создать второй шаблон с именем, как у первого, проверить, что недопустимо")
    @allure.issue("DEV-8292")
    def test_create_offer_unique_name(self, super_user,
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
        with allure.step("Construct offers"):
            offer_name = "test_ag_offer_" + generate_diagram_name_description(6, 1)["rand_name"]
            offer = offer_construct(offer_name=offer_name,
                                    script_version_id=script_view.versionId,
                                    script_id=script_view.scriptId,
                                    script_name=script_view.objectName,
                                    offer_complex_type_version_id=complex_type.versionId,
                                    offer_variables=[offer_variable])
        with allure.step("Create offer"):
            create_response: ResponseDto = create_offer_gen.create_offer(offer=offer)
        with allure.step("Assert you can't create offer with not unique name"):
            with pytest.raises(HTTPError):
                assert create_offer_gen.try_create_offer(offer=offer).status == 400

    @allure.story("Созданная пользовательская версия шаблона предложения отображается в списке версий шаблона")
    @allure.title("Создать пользовательскую версию, проверить, что появилась в версиях")
    @allure.link("DEV-3379")
    @pytest.mark.smoke
    def test_create_offer_user_version(self, super_user,
                                       create_custom_types_gen,
                                       create_code_gen,
                                       create_offer_gen):
        version_found = False
        version_correct = False
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
        with allure.step("Get offer versions"):
            versions_list = []
            for version in get_offer_versions(super_user, search_response.id).body:
                versions_list.append(OfferShortInfoVersionDto.construct(**version))
            for version in versions_list:
                if version.versionType == VersionType.USER_LOCAL and \
                        version.versionId == uv_id:
                    version_found = True
                    if version.versionName == version_name and \
                            version.versionDescription == version_desc:
                        version_correct = True
        with allure.step("Assert that version found and correct"):
            assert version_found
            assert version_correct

    @allure.title("Создать оффер с 2 переменными с неуникальными именами")
    @allure.story("Переменные шаблона предложения должны быть с уникальными именами")
    @allure.issue("DEV-8316")
    # создать тип, создать код,создать 2 одинаковые переменные и передать в оффер и посмотреть, что не создался(запросим инфу по офферу)
    def test_create_offer_attribute_not_unique_name(self, super_user,
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
        with allure.step("Создать оффер с неуникальными именами переменных"):
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
            offer_variable2 = offer_variable_construct(variable_name="test_var",
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
                                    offer_variables=[offer_variable, offer_variable2])
        with allure.step("Проверить, что нельзя создать оффер с неуникальными переменными"):
            with pytest.raises(HTTPError):
                assert create_offer_gen.try_create_offer(offer=offer).status == 400

    @allure.story("При создании глобальной версии диаграммы с оффером, создаётся и глобальная версия оффера")
    @allure.issue("DEV-12324")
    @allure.title(
        "Создать глобальную версию диаграммы с предложением, найти глобальную версию предложения в списке версий")
    @pytest.mark.smoke
    def test_create_offer_global_version(self, super_user,
                                         diagram_offer_save, save_diagrams_gen):
        saved_version_id = diagram_offer_save["saved_version_id"]
        diagram_id = diagram_offer_save["diagram_id"]
        new_diagram_name = diagram_offer_save["diagram_name"]
        offer = diagram_offer_save["offer"]
        with allure.step("Создание глобальной версии диаграммы"):
            gv_create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram_user_vers(
                    diagram_id=diagram_id,
                    saved_version_id=saved_version_id,
                    version_name="diagram_user_global",
                    diagram_name=new_diagram_name,
                    global_flag=True,
                ).body
            )
            with allure.step("Поиск в списке версий предложений глобальной версии"):
                get_offer_versions(super_user, offer.id)
                vers_list = []
                for vers in get_offer_versions(super_user, offer.id).body:
                    vers_list.append(OfferShortInfoVersionDto.construct(**vers))
                assert any(vers.versionType == "USER_GLOBAL" for vers in vers_list)
