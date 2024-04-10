import uuid

import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import OfferShortInfoDto, ResponseDto, ComplexTypeGetFullView, VariableType1, \
    ScriptFullView, DataSourceType, OfferFullViewDto, OfferShortInfoVersionDto, ObjectType, DiagramCreateNewVersion, \
    DiagramInOutParameterFullViewDto, NodeViewShortInfo
from products.Decision.framework.steps.decision_steps_complex_type import get_custom_type
from products.Decision.framework.steps.decision_steps_diagram import delete_diagram, save_diagram
from products.Decision.framework.steps.decision_steps_nodes import delete_node_by_id, update_node
from products.Decision.framework.steps.decision_steps_object_relation import get_objects_relation_by_object_id
from products.Decision.framework.steps.decision_steps_offer_api import get_offer_list, get_offer_info, \
    get_offer_versions
from products.Decision.framework.steps.decision_steps_script_api import get_python_script_by_id
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description
from products.Decision.utilities.custom_code_constructors import script_vars_construct
from products.Decision.utilities.custom_models import VariableParams
from products.Decision.utilities.custom_type_constructors import generate_attr_type_name, attribute_construct
from products.Decision.utilities.node_cunstructors import offer_variable, variables_for_node, offer_properties, \
    offer_node_construct
from products.Decision.utilities.offer_constructors import offer_variable_construct, offer_construct


@allure.epic("Шаблоны предложений")
@allure.feature("Информация о шаблоне предложения")
class TestOffersInfo:

    @allure.story("В списке шаблонов предложений у каждого шаблона содержится информация:"
                  " id, versionId, createDt, changeDt, offerName")
    @allure.title("Создать шаблон предложения, найти в списке шаблонов предложения")
    @pytest.mark.scenario("DEV-15467")
    @allure.link("DEV-3379")
    @pytest.mark.smoke
    def test_offer_list(self, super_user):
        with allure.step("Get offer list"):
            offer_list = []
            for template in get_offer_list(super_user).body["content"]:
                offer_list.append(OfferShortInfoDto.construct(**template))
        with allure.step("Проверка, что в списке содержатся необходимые поля"):
            offers_contain_req_fields = next((offer for offer in offer_list if offer.id is not None
                                              and offer.versionId is not None
                                              and offer.lastChangeByUser is not None
                                              and offer.changeDt is not None
                                              and offer.objectName is not None), True)

            assert len(offer_list) != 0 and offers_contain_req_fields

    @allure.story("Созданный шаблон можно найти в списке шаблонов")
    @allure.title("Создать шаблон предложения, найти в списке шаблонов предложения")
    @pytest.mark.scenario("DEV-15467")
    @allure.link("DEV-3379")
    @pytest.mark.smoke
    def test_offer_versions(self, super_user,
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
        with allure.step("Get offer versions"):
            versions_list = []
            for version in get_offer_versions(super_user, search_response.id).body:
                versions_list.append(OfferShortInfoVersionDto.construct(**version))
        assert versions_list[0].versionId == create_response.uuid and \
               versions_list[0].versionType == "LATEST" and \
               versions_list[0].versionName is not None and \
               versions_list[0].id is not None

    @allure.story(
        "Связь предложения с диаграммой появляется при сохранении диаграммы с 1 блоком предложения"
    )
    @allure.title(
        "Сохранить диаграмму с предложением и проверить наличие диаграммы в related objects"
    )
    @pytest.mark.scenario("DEV-8572")
    @allure.link("DEV-8572")
    @pytest.mark.smoke
    def test_check_offer_diagram_in_relation(self,
                                             super_user,
                                             diagram_offer_for_runtime
                                             ):
        with allure.step("Получение информации об объектах"):
            offer_id = diagram_offer_for_runtime["offer"].id
            diagram_latest_id = diagram_offer_for_runtime["create_result"].uuid
        with allure.step("Получение информации связях"):
            object_type = ObjectType.OFFER_RELATION.value
            related_objects_response = get_objects_relation_by_object_id(
                super_user, object_type, offer_id
            ).body["content"]
        assert (
                related_objects_response[0]["objectToVersionId"] == diagram_latest_id
                and len(related_objects_response) == 1
        )

    @allure.story(
        "Связь удаляется для LATEST версии диаграммы после удаления диаграммы"
    )
    @allure.title(
        "Удалить сохраненную диаграмму с предложением, проверить, что список объектов пустой"
    )
    @pytest.mark.scenario("DEV-8572")
    @allure.link("DEV-8572")
    @pytest.mark.smoke
    def test_check_offer_deleted_diagram_not_in_relation(self,
                                                         super_user,
                                                         diagram_offer_for_runtime,
                                                         ):
        with allure.step("Получение информации об объектах"):
            offer_id = diagram_offer_for_runtime["offer"].id
            diagram_latest_id = diagram_offer_for_runtime["create_result"].uuid
        with allure.step("Удаление диаграммы"):
            delete_diagram(super_user, str(diagram_latest_id))
        with allure.step("Получение информации связях"):
            object_type = ObjectType.OFFER_RELATION.value
            related_objects_response_body = get_objects_relation_by_object_id(
                super_user, object_type, offer_id
            ).body
            related_objects_response_status = get_objects_relation_by_object_id(
                super_user, object_type, offer_id
            ).status
        assert (
                not related_objects_response_body
                and related_objects_response_status == 204
        )

    @allure.story(
        "Связь удаляется после удаления узла из диаграммы")
    @allure.title(
        "Удалить узел в диаграмме с предложением, проверить, что список объектов пустой")
    @pytest.mark.scenario("DEV-8572")
    @allure.link("DEV-8572")
    @pytest.mark.smoke
    def test_check_offer_deleted_node_not_in_relation(self,
                                                      super_user,
                                                      diagram_offer_for_runtime,
                                                      ):
        with allure.step("Получение информации об объектах"):
            offer_id = diagram_offer_for_runtime["offer"].id
            temp_version_id = diagram_offer_for_runtime["template"]["versionId"]
            temp_offer_node_id = diagram_offer_for_runtime["node_offer"].uuid
            diagram_id = diagram_offer_for_runtime["diagram_id"]
            diagram_name = diagram_offer_for_runtime["diagram_name"]
        with allure.step("Удаление узла и сохранение диаграммы"):
            delete_node_by_id(super_user, temp_offer_node_id)
            diagram_data = DiagramCreateNewVersion(diagramId=diagram_id,
                                                   versionId=temp_version_id,
                                                   errorResponseFlag=False,
                                                   objectName=diagram_name,
                                                   diagramDescription="diagram created in test")
            save_diagram(super_user, body=diagram_data)
        with allure.step("Получение информации связях"):
            object_type = ObjectType.OFFER_RELATION.value
            related_objects_response_body = get_objects_relation_by_object_id(
                super_user, object_type, offer_id
            ).body
            related_objects_response_status = get_objects_relation_by_object_id(
                super_user, object_type, offer_id
            ).status
        assert (
                not related_objects_response_body
                and related_objects_response_status == 204
        )

    @allure.story(
        "2 связи с диаграммой появляются при сохранении диаграммы с 2 узлами предложения"
    )
    @allure.title(
        "Сохранить диаграмму с двумя узлами предложения и проверить наличие диаграммы в related objects"
    )
    @pytest.mark.scenario("DEV-8572")
    @pytest.mark.variable_data([VariableParams(varName="in_int", varType="in", varDataType=1),
                                VariableParams(varName="out_cmplx", varType="out", isComplex=True, isArray=True,
                                               isConst=False, varValue="offer_complex_type")])
    @pytest.mark.nodes(["предложение_1", "предложение_2"])
    def test_check_offer_2_diagram_in_relation(self,
                                               super_user,
                                               save_diagrams_gen,
                                               diagram_constructor,
                                               ):
        with allure.step("Получение информации об объектах"):
            node_offer1: NodeViewShortInfo = diagram_constructor["nodes"]["предложение_1"]
            node_offer2: NodeViewShortInfo = diagram_constructor["nodes"]["предложение_2"]
            diagram_param_in: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int"]
            diagram_param_out: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_cmplx"]
            temp_version_id = diagram_constructor["temp_version_id"]
            diagram_id = diagram_constructor["diagram_id"]
            complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]
            script_inp_var = diagram_constructor["script_inp_var"]
            offer: OfferFullViewDto = diagram_constructor["offer"]
        with allure.step("Заполнение двух узлов предложения"):
            offer_var = offer_variable(var_id=offer.offerVariables[0]["id"], value=5)
            node_var_mapping = variables_for_node(node_type="offer_mapping",
                                                  is_arr=False,
                                                  is_compl=False,
                                                  is_dict=False,
                                                  type_id="1",
                                                  node_variable=script_inp_var.variableName,
                                                  name=diagram_param_in.parameterName,
                                                  param_id=diagram_param_in.parameterId)
            output_var_mapping = variables_for_node(node_type="offer_output",
                                                    is_arr=True,
                                                    is_compl=True,
                                                    is_dict=False,
                                                    type_id=complex_type.versionId,
                                                    node_variable=diagram_param_out.parameterName,
                                                    name=diagram_param_out.parameterName,
                                                    param_id=diagram_param_out.parameterId)
            node_offer_properties = offer_properties(offer_id=offer.id,
                                                     offer_version_id=offer.versionId,
                                                     offer_variables=[offer_var],
                                                     node_variables_mapping=[node_var_mapping],
                                                     output_variable_mapping=output_var_mapping)
            update_body_offer1 = offer_node_construct(x=700, y=202.22915649414062,
                                                      node_id=str(node_offer1.nodeId),
                                                      temp_version_id=temp_version_id,
                                                      properties=node_offer_properties,
                                                      operation="update")
            update_node(super_user, node_id=node_offer1.nodeId, body=update_body_offer1)
            update_body_offer2 = offer_node_construct(x=700, y=202.22915649414062,
                                                      node_id=str(node_offer2.nodeId),
                                                      temp_version_id=temp_version_id,
                                                      properties=node_offer_properties,
                                                      operation="update")
            update_node(super_user, node_id=node_offer2.nodeId, body=update_body_offer2)
        with allure.step("Сохранение диаграммы"):
            create_result: ResponseDto = ResponseDto.construct(**save_diagrams_gen.save_diagram(
                diagram_id, temp_version_id, "diagram" + "_" + generate_string(), 'diagram created in test'
            ).body)
        with allure.step("Получение информации связях"):
            object_type = ObjectType.OFFER_RELATION.value
            related_objects_response = get_objects_relation_by_object_id(
                super_user, object_type, offer.id
            ).body["content"]
        assert (
                related_objects_response[0]["objectToVersionId"] == create_result.uuid
                and related_objects_response[1]["objectToVersionId"] == create_result.uuid
                and len(related_objects_response) == 2
        )
