import uuid

import glamor as allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import (
    ResponseDto,
    DiagramViewDto,
    NodeViewShortInfo,
    ScriptFullView,
    NodeViewWithVariablesDto,
    ScriptType2,
    VariableType1, ScriptVariableFullView, NodeValidateDto, DiagramInOutParameterFullViewDto, ComplexTypeGetFullView,
    AttributeShortView,
)
from products.Decision.framework.steps.decision_steps_diagram import (
    get_diagram_by_version, update_diagram_parameters,
)
from products.Decision.framework.steps.decision_steps_nodes import (
    create_node,
    update_node,
    get_node_by_id, validate_node, remap_node,
)
from products.Decision.framework.steps.decision_steps_script_api import (
    get_python_script_by_id,
    get_groovy_script_by_id,
)
from products.Decision.utilities.custom_code_constructors import script_vars_construct
from products.Decision.utilities.custom_models import VariableParams
from products.Decision.utilities.node_cunstructors import (
    node_construct,
    variables_for_node,
    node_update_construct, node_remap_construct,
)
from products.Decision.utilities.variable_constructors import variable_construct


@allure.epic("Диаграммы")
@allure.feature("Узел пользовательский код")
class TestCustomCodeNode:
    @allure.title(
        "Создать диаграмму с узлом кастомного кода без параметров, увидеть, что создался"
    )
    @allure.story("Возможно создать узел кастомного кода")
    @pytest.mark.scenario("DEV-15463")
    @pytest.mark.smoke
    def test_create_node_script(self, super_user, create_temp_diagram):
        template = create_temp_diagram
        temp_version_id = template["versionId"]
        diagram_id = template["diagramId"]
        node_script = node_construct(
            700, 202.22915649414062, "custom_code", template["versionId"]
        )
        node_script_response: ResponseDto = ResponseDto.construct(
            **create_node(super_user, node_script).body
        )
        node_script_id = node_script_response.uuid
        diagram = DiagramViewDto.construct(
            **get_diagram_by_version(super_user, temp_version_id).body
        )
        for key, value in diagram.nodes.items():
            diagram.nodes[key] = NodeViewShortInfo.construct(**diagram.nodes[key])
        assert diagram.nodes[str(node_script_id)].nodeTypeId == 1

    @allure.title(
        "Создать диаграмму с узлом кастомного кода и добавить к нему кастом код"
    )
    @allure.story(
        "В узел кастомного кода возможно добавить кастомный код из существующих"
    )
    @pytest.mark.scenario("DEV-15463")
    @pytest.mark.smoke
    def test_create_node_script_with_script(
            self,
            super_user,
            create_python_code_int_vars,
            crete_temp_diagram_with_custom_code_node,
    ):
        script_view: ScriptFullView = create_python_code_int_vars["code_view"]
        script_id = script_view.scriptId
        script_version_id = script_view.versionId
        script_input_var: ScriptVariableFullView = (
            create_python_code_int_vars["inp_var"]
        )
        script_output_var: ScriptVariableFullView = (
            create_python_code_int_vars["out_var"]
        )
        template = crete_temp_diagram_with_custom_code_node["template"]
        temp_version_id = template["versionId"]
        diagram_id = template["diagramId"]
        node_script_response: ResponseDto = crete_temp_diagram_with_custom_code_node[
            "node_script_resp"
        ]
        node_script_id = node_script_response.uuid
        out_var_map = variables_for_node(
            node_type="custom_code",
            is_arr=False,
            is_compl=False,
            name="",
            node_variable=script_output_var.variableName,
            type_id=script_output_var.primitiveTypeId,
            outer_variable_id=script_output_var.variableId
        )
        inp_var_map = variables_for_node(
            node_type="custom_code",
            is_arr=False,
            is_compl=False,
            name="",
            node_variable=script_input_var.variableName,
            type_id=script_input_var.primitiveTypeId,
            outer_variable_id=script_input_var.variableId
        )
        node_script_upd = node_update_construct(
            x=700,
            y=202.22915649414062,
            node_type="custom_code",
            temp_version_id=temp_version_id,
            script_id=script_id,
            script_version_id=script_version_id,
            script_type=ScriptType2.PYTHON,
            inp_custom_code_vars=[inp_var_map],
            out_custom_code_vars=[out_var_map],
        )
        update_node(super_user, node_id=node_script_id, body=node_script_upd,
                    validate_body=NodeValidateDto.construct(
                        nodeTypeId=node_script_upd.nodeTypeId,
                        properties=node_script_upd.properties))
        node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_script_id).body
        )

        assert (
                node_view.properties["customCodeId"] == script_id
                and node_view.properties["versionId"] == script_version_id
                and node_view.properties["inputVariablesMapping"] is not None
                and node_view.properties["outputVariablesMapping"] is not None
        )

    @allure.title("Сослаться на несуществующие аттрибуты скрипта в узле кастом код")
    @allure.issue("DEV-6841")
    @allure.story(
        "Перечень атрибутов inputVariablesMapping при несоответствии актуальному перечню соответствующих "
        "входных атрибутов скрипта, на который ссылается узел; узел невалидный"
    )
    @pytest.mark.scenario("DEV-6398")
    def test_valid_attr(
            self,
            super_user,
            create_python_code_int_vars,
            crete_temp_diagram_with_custom_code_node,
    ):
        script_view: ScriptFullView = create_python_code_int_vars["code_view"]
        script_id = script_view.scriptId
        script_version_id = script_view.versionId
        script_input_var: ScriptVariableFullView = (
            create_python_code_int_vars["inp_var"]
        )
        script_output_var: ScriptVariableFullView = (
            create_python_code_int_vars["out_var"]
        )
        template = crete_temp_diagram_with_custom_code_node["template"]
        temp_version_id = template["versionId"]
        diagram_id = template["diagramId"]
        node_script_response: ResponseDto = crete_temp_diagram_with_custom_code_node[
            "node_script_resp"
        ]
        node_script_id = node_script_response.uuid
        out_var_map = variables_for_node(
            node_type="custom_code",
            is_arr=False,
            is_compl=False,
            name="",
            node_variable="papa",
            type_id=script_output_var.primitiveTypeId,
            outer_variable_id=script_input_var.variableId
        )
        inp_var_map = variables_for_node(
            node_type="custom_code",
            is_arr=False,
            is_compl=False,
            name="",
            node_variable="mama",
            type_id=script_input_var.primitiveTypeId,
            outer_variable_id=script_input_var.variableId
        )
        node_script_upd = node_update_construct(
            x=700,
            y=202.22915649414062,
            node_type="custom_code",
            temp_version_id=temp_version_id,
            script_id=script_id,
            script_version_id=script_version_id,
            script_type=ScriptType2.PYTHON,
            inp_custom_code_vars=[inp_var_map],
            out_custom_code_vars=[out_var_map]
        )
        update_node(super_user, node_id=node_script_id, body=node_script_upd,
                    validate_body=NodeValidateDto.construct(
                        nodeTypeId=node_script_upd.nodeTypeId,
                        properties=node_script_upd.properties))
        node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_script_id).body
        )
        assert node_view.validFlag == False

    @allure.title("Сослаться на несуществующий скрипт в узле кастом код")
    @allure.issue("DEV-6841")
    @allure.story(
        "customCodeId - при указании на несуществующий script_id - узел невалидный"
    )
    @pytest.mark.scenario("DEV-6398")
    def test_valid_script_id(
            self,
            super_user,
            create_python_code_int_vars,
            crete_temp_diagram_with_custom_code_node,
    ):
        script_view: ScriptFullView = create_python_code_int_vars["code_view"]
        script_id = script_view.scriptId
        script_version_id = script_view.versionId
        script_input_var: ScriptVariableFullView = (
            create_python_code_int_vars["inp_var"]
        )
        script_output_var: ScriptVariableFullView = (
            create_python_code_int_vars["out_var"]
        )
        template = crete_temp_diagram_with_custom_code_node["template"]
        temp_version_id = template["versionId"]
        diagram_id = template["diagramId"]
        node_script_response: ResponseDto = crete_temp_diagram_with_custom_code_node[
            "node_script_resp"
        ]
        node_script_id = node_script_response.uuid
        out_var_map = variables_for_node(
            node_type="custom_code",
            is_arr=False,
            is_compl=False,
            name="",
            node_variable=script_output_var.variableName,
            type_id=script_output_var.primitiveTypeId,
            outer_variable_id=script_input_var.variableId
        )
        inp_var_map = variables_for_node(
            node_type="custom_code",
            is_arr=False,
            is_compl=False,
            name="",
            node_variable=script_input_var.variableName,
            type_id=script_input_var.primitiveTypeId,
            outer_variable_id=script_input_var.variableId
        )
        node_script_upd = node_update_construct(
            x=700,
            y=202.22915649414062,
            node_type="custom_code",
            temp_version_id=temp_version_id,
            script_id=str(uuid.uuid4()),
            script_version_id=script_version_id,
            script_type=ScriptType2.PYTHON,
            inp_custom_code_vars=[inp_var_map],
            out_custom_code_vars=[out_var_map],
        )
        update_node(super_user, node_id=node_script_id, body=node_script_upd,
                    validate_body=NodeValidateDto.construct(
                        nodeTypeId=node_script_upd.nodeTypeId,
                        properties=node_script_upd.properties))
        node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_script_id).body
        )
        assert node_view.validFlag == False

    @allure.title("Сослаться на несуществующую версию скрипта в узле кастом код")
    @allure.issue("DEV-6841")
    @allure.story(
        "versionId - при указании на несуществующий script_version_id - узел невалидный"
    )
    @pytest.mark.scenario("DEV-6398")
    def test_valid_script_version_id(
            self,
            super_user,
            create_temp_diagram,
            create_python_code_int_vars,
            crete_temp_diagram_with_custom_code_node,
    ):
        script_view: ScriptFullView = create_python_code_int_vars["code_view"]
        script_id = script_view.scriptId
        script_version_id = script_view.versionId
        script_input_var: ScriptVariableFullView = (
            create_python_code_int_vars["inp_var"]
        )
        script_output_var: ScriptVariableFullView = (
            create_python_code_int_vars["out_var"]
        )
        template = crete_temp_diagram_with_custom_code_node["template"]
        temp_version_id = template["versionId"]
        diagram_id = template["diagramId"]
        node_script_response: ResponseDto = crete_temp_diagram_with_custom_code_node[
            "node_script_resp"
        ]
        node_script_id = node_script_response.uuid
        out_var_map = variables_for_node(
            node_type="custom_code",
            is_arr=False,
            is_compl=False,
            name="",
            node_variable=script_output_var.variableName,
            type_id=script_output_var.primitiveTypeId,
            outer_variable_id=script_input_var.variableId
        )
        inp_var_map = variables_for_node(
            node_type="custom_code",
            is_arr=False,
            is_compl=False,
            name="",
            node_variable=script_input_var.variableName,
            type_id=script_input_var.primitiveTypeId,
            outer_variable_id=script_input_var.variableId
        )
        node_script_upd = node_update_construct(
            x=700,
            y=202.22915649414062,
            node_type="custom_code",
            temp_version_id=temp_version_id,
            script_id=script_id,
            script_version_id=str(uuid.uuid4()),
            script_type=ScriptType2.PYTHON,
            inp_custom_code_vars=[inp_var_map],
            out_custom_code_vars=[out_var_map],
        )
        update_node(super_user, node_id=node_script_id, body=node_script_upd,
                    validate_body=NodeValidateDto.construct(
                        nodeTypeId=node_script_upd.nodeTypeId,
                        properties=node_script_upd.properties))
        node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_script_id).body
        )
        assert node_view.validFlag == False

    @allure.title("Сослаться на несуществующий scriptType в узле кастом кода")
    @allure.issue("DEV-6841")
    @allure.story(
        "scriptType - при указании на несуществующий тип скрипта из GET /scripts/types - узел невалидный"
    )
    @pytest.mark.scenario("DEV-6398")
    def test_valid_script_type(
            self,
            super_user,
            create_temp_diagram,
            create_python_code_int_vars,
            crete_temp_diagram_with_custom_code_node,
    ):
        script_view: ScriptFullView = create_python_code_int_vars["code_view"]
        script_id = script_view.scriptId
        script_version_id = script_view.versionId
        script_input_var: ScriptVariableFullView = (
            create_python_code_int_vars["inp_var"]
        )
        script_output_var: ScriptVariableFullView = (
            create_python_code_int_vars["out_var"]
        )
        template = crete_temp_diagram_with_custom_code_node["template"]
        temp_version_id = template["versionId"]
        diagram_id = template["diagramId"]
        node_script_response: ResponseDto = crete_temp_diagram_with_custom_code_node[
            "node_script_resp"
        ]
        node_script_id = node_script_response.uuid
        out_var_map = variables_for_node(
            node_type="custom_code",
            is_arr=False,
            is_compl=False,
            name="",
            node_variable=script_output_var.variableName,
            type_id=script_output_var.primitiveTypeId,
            outer_variable_id=script_input_var.variableId
        )
        inp_var_map = variables_for_node(
            node_type="custom_code",
            is_arr=False,
            is_compl=False,
            name="",
            node_variable=script_input_var.variableName,
            type_id=script_input_var.primitiveTypeId,
            outer_variable_id=script_input_var.variableId
        )
        node_script_upd = node_update_construct(
            x=700,
            y=202.22915649414062,
            node_type="custom_code",
            temp_version_id=temp_version_id,
            script_id=script_id,
            script_version_id=script_version_id,
            script_type="JAVA",
            inp_custom_code_vars=[inp_var_map],
            out_custom_code_vars=[out_var_map],
        )
        with pytest.raises(HTTPError, match="400"):
            assert validate_node(
                super_user, node_id=node_script_id, body=NodeValidateDto.construct(
                    nodeTypeId=node_script_upd.nodeTypeId,
                    properties=node_script_upd.properties)
            )

    @allure.title("Добавить в узел кастом кода python скрипт с синтаксической ошибкой")
    @allure.issue("DEV-6841")
    @allure.story("синтаксические ошибки в скрипте PYTHON")
    @pytest.mark.scenario("DEV-6398")
    def test_valid_script_valid_python_code_text(
            self, super_user, create_code_gen, crete_temp_diagram_with_custom_code_node
    ):
        inp_var = script_vars_construct(
            var_name="input_int",
            var_type=VariableType1.IN,
            is_array=False,
            primitive_id="1"
        )
        out_var = script_vars_construct(
            var_name="output_int",
            var_type=VariableType1.OUT,
            is_array=False,
            primitive_id="1",
        )
        script_text = "it is a syntax error in python code"
        script_name = "test_python_script_bad_syntax" + generate_string(8)
        create_result = create_code_gen.create_python_code(
            script_text, script_name, inp_var, out_var
        )
        python_code_create_result: ScriptFullView = create_result["code_create_result"]
        input_var: ScriptVariableFullView = create_result["inp_var"]
        output_var: ScriptVariableFullView = create_result["out_var"]
        script_view = ScriptFullView.construct(
            **get_python_script_by_id(super_user, python_code_create_result.versionId).body
        )
        template = crete_temp_diagram_with_custom_code_node["template"]
        temp_version_id = template["versionId"]
        diagram_id = template["diagramId"]
        node_script_response: ResponseDto = crete_temp_diagram_with_custom_code_node[
            "node_script_resp"
        ]
        node_script_id = node_script_response.uuid
        out_var_map = variables_for_node(
            node_type="custom_code",
            is_arr=False,
            is_compl=False,
            name="",
            node_variable=output_var.variableName,
            type_id=output_var.primitiveTypeId,
            outer_variable_id=input_var.variableId
        )
        inp_var_map = variables_for_node(
            node_type="custom_code",
            is_arr=False,
            is_compl=False,
            name="",
            node_variable=input_var.variableName,
            type_id=input_var.primitiveTypeId,
            outer_variable_id=input_var.variableId
        )
        node_script_upd = node_update_construct(
            x=700,
            y=202.22915649414062,
            node_type="custom_code",
            temp_version_id=temp_version_id,
            script_id=script_view.scriptId,
            script_version_id=script_view.versionId,
            script_type=ScriptType2.PYTHON,
            inp_custom_code_vars=[inp_var_map],
            out_custom_code_vars=[out_var_map],
        )
        update_node(super_user, node_id=node_script_id, body=node_script_upd,
                    validate_body=NodeValidateDto.construct(
                        nodeTypeId=node_script_upd.nodeTypeId,
                        properties=node_script_upd.properties))
        node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_script_id).body
        )
        assert node_view.validFlag == False

    @allure.title("Добавить в узел кастом кода groovy скрипт с синтаксической ошибкой")
    @allure.issue("DEV-6841")
    @allure.story("синтаксические ошибки в скрипте GROOVY")
    @pytest.mark.scenario("DEV-6398")
    def test_valid_script_valid_groovy_code_text(
            self, super_user, create_code_gen, crete_temp_diagram_with_custom_code_node
    ):
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
        script_text = "it is a syntax error in groovy code"
        script_name = "test_groovy_script_bad_syntax" + generate_string()
        create_result = create_code_gen.create_groovy_code(
            script_text, script_name, inp_var, out_var
        )
        groovy_code_create_result: ScriptFullView = create_result["code_create_result"]
        input_var: ScriptVariableFullView = create_result["inp_var"]
        output_var: ScriptVariableFullView = create_result["out_var"]
        script_view = ScriptFullView.construct(
            **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body
        )
        template = crete_temp_diagram_with_custom_code_node["template"]
        temp_version_id = template["versionId"]
        diagram_id = template["diagramId"]
        node_script_response: ResponseDto = crete_temp_diagram_with_custom_code_node[
            "node_script_resp"
        ]
        node_script_id = node_script_response.uuid
        out_var_map = variables_for_node(
            node_type="custom_code",
            is_arr=False,
            is_compl=False,
            name="",
            node_variable=output_var.variableName,
            type_id=output_var.primitiveTypeId,
            outer_variable_id=output_var.variableId
        )
        inp_var_map = variables_for_node(
            node_type="custom_code",
            is_arr=False,
            is_compl=False,
            name="",
            node_variable=input_var.variableName,
            type_id=input_var.primitiveTypeId,
            outer_variable_id=input_var.variableId
        )
        node_script_upd = node_update_construct(
            x=700,
            y=202.22915649414062,
            node_type="custom_code",
            temp_version_id=temp_version_id,
            script_id=script_view.scriptId,
            script_version_id=script_view.versionId,
            script_type=ScriptType2.GROOVY,
            inp_custom_code_vars=[inp_var_map],
            out_custom_code_vars=[out_var_map],
        )
        update_node(super_user, node_id=node_script_id, body=node_script_upd,
                    validate_body=NodeValidateDto.construct(
                        nodeTypeId=node_script_upd.nodeTypeId,
                        properties=node_script_upd.properties))
        node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_script_id).body
        )
        assert node_view.validFlag == False

    @allure.title("Создать валидный узел кастомного кода, провалидировать его")
    @allure.story("При корректном заполнении узла кастомного кода не происходит ошибки валидации")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.nodes(["кастомный код"])
    @pytest.mark.smoke
    def test_valid_node(
            self,
            super_user,
            create_python_code_int_vars,
            diagram_constructor):
        temp_version_id = diagram_constructor["diagram_info"].versionId
        diagram_inp_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int_v"]
        script_output_var: ScriptVariableFullView = create_python_code_int_vars["out_var"]
        script: ScriptFullView = create_python_code_int_vars["code_view"]
        script_input_var: ScriptVariableFullView = create_python_code_int_vars["inp_var"]
        script_id = script.scriptId
        script_version_id = script.versionId
        node_script_id = diagram_constructor["nodes"]["кастомный код"].nodeId

        with allure.step("Обновление узла Кастомного кода"):
            out_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False, is_compl=False,
                                             name=diagram_inp_var.parameterName,
                                             node_variable=script_output_var.variableName,
                                             type_id=script_output_var.primitiveTypeId,
                                             outer_variable_id=script_output_var.variableId,
                                             param_id=diagram_inp_var.parameterId)
            inp_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False, is_compl=False,
                                             name=diagram_inp_var.parameterName,
                                             node_variable=script_input_var.variableName,
                                             type_id=script_input_var.primitiveTypeId,
                                             outer_variable_id=script_input_var.variableId,
                                             param_id=diagram_inp_var.parameterId)
            node_script_upd = node_update_construct(x=700, y=202.22915649414062, node_type="custom_code",
                                                    temp_version_id=temp_version_id,
                                                    script_id=script_id, script_version_id=script_version_id,
                                                    script_type=ScriptType2.PYTHON,
                                                    inp_custom_code_vars=[inp_var_map],
                                                    out_custom_code_vars=[out_var_map])
            update_node(super_user, node_id=node_script_id, body=node_script_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_script_upd.nodeTypeId,
                            properties=node_script_upd.properties))
        with allure.step("Валидация узла кастомного кода"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_script_id).body
            )
            assert node_view.validFlag

    @allure.story("Происходит корректный маппинг переменной комплексного типа на входную переменную"
                  " узла кастомного кода")
    @allure.title("Cоздание диаграммы с целочисленным атрибутом переменной комплексного типа на вход и "
                  "целочисленной переменной на выход")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.variable_data([VariableParams(varName="in_cmplx",
                                               varType="in", isComplex=True, isArray=False),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.nodes(["кастомный код"])
    @pytest.mark.smoke
    def test_node_script_inp_complex(self,
                                     super_user,
                                     create_python_code_int_vars,
                                     diagram_constructor):
        with allure.step("Создание диаграммы с узлами начало, кастом код, завершение где на "
                         "вход подается переменная компл типа с интовым атрибутом и интовой переменной на выход"):
            diagram_inp_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_cmplx"]
            diagram_out_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_int"]
            complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]
            attr: AttributeShortView = AttributeShortView.construct(**complex_type.attributes[0])
            temp_version_id = diagram_constructor["diagram_info"].versionId
            script_output_var: ScriptVariableFullView = create_python_code_int_vars["out_var"]
            script: ScriptFullView = create_python_code_int_vars["code_view"]
            script_input_var: ScriptVariableFullView = create_python_code_int_vars["inp_var"]
            script_id = script.scriptId
            script_version_id = script.versionId
            node_script_id = diagram_constructor["nodes"]["кастомный код"].nodeId
        with allure.step("Добавляю атрибут комплексного типа на вход"):
            out_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False,
                                             is_compl=False,
                                             name=diagram_out_var.parameterName,
                                             node_variable=script_output_var.variableName,
                                             type_id=script_output_var.primitiveTypeId,
                                             outer_variable_id=script_output_var.variableId,
                                             param_id=diagram_out_var.parameterId)
            inp_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False,
                                             is_compl=False,
                                             name=attr.attributeName,
                                             type_id=script_input_var.primitiveTypeId,
                                             outer_variable_id=script_input_var.variableId,
                                             var_path=diagram_inp_var.parameterName,
                                             var_root_id=complex_type.versionId,
                                             param_id=diagram_inp_var.parameterId
                                             )
            node_script_upd = node_update_construct(x=700, y=202.22915649414062, node_type="custom_code",
                                                    temp_version_id=temp_version_id,
                                                    script_id=script_id,
                                                    script_version_id=script_version_id,
                                                    script_type=ScriptType2.PYTHON,
                                                    inp_custom_code_vars=[inp_var_map],
                                                    out_custom_code_vars=[out_var_map])
            update_node(super_user, node_id=node_script_id, body=node_script_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_script_upd.nodeTypeId,
                            properties=node_script_upd.properties))

        with allure.step("Валидация узла кастомного кода"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_script_id).body
            )
            assert node_view.validFlag

    @allure.story("Происходит корректный маппинг переменной комплексного типа на выходную переменную"
                  " узла кастомного кода")
    @allure.title("Cоздание диаграммы с целочисленным атрибутом переменной комплексного типа на выход и "
                  "целочисленной переменной на вход")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.variable_data([VariableParams(varName="in_int", varType="in", varDataType=1),
                                VariableParams(varName="out_cmplx",
                                               varType="out", isComplex=True, isArray=False)])
    @pytest.mark.nodes(["кастомный код"])
    @pytest.mark.smoke
    def test_node_script_out_complex(self,
                                     super_user,
                                     create_python_code_int_vars,
                                     diagram_constructor):
        with allure.step("Создание диаграммы с узлами начало, кастом код, завершение где на "
                         "выход подается переменная компл типа с интовым атрибутом и интовой переменной на вход"):
            diagram_inp_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int"]
            diagram_out_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_cmplx"]
            complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]
            attr: AttributeShortView = AttributeShortView.construct(**complex_type.attributes[0])
            temp_version_id = diagram_constructor["diagram_info"].versionId
            script_output_var: ScriptVariableFullView = create_python_code_int_vars["out_var"]
            script: ScriptFullView = create_python_code_int_vars["code_view"]
            script_input_var: ScriptVariableFullView = create_python_code_int_vars["inp_var"]
            script_id = script.scriptId
            script_version_id = script.versionId
            node_script_id = diagram_constructor["nodes"]["кастомный код"].nodeId
        with allure.step("Добавляю атрибут комплексного типа на вход"):
            out_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False,
                                             is_compl=False,
                                             name=attr.attributeName,
                                             var_path=diagram_out_var.parameterName,
                                             var_root_id=complex_type.versionId,
                                             type_id=script_output_var.primitiveTypeId,
                                             outer_variable_id=script_output_var.variableId)
            inp_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False,
                                             is_compl=False,
                                             name=diagram_inp_var.parameterName,
                                             type_id=script_input_var.primitiveTypeId,
                                             outer_variable_id=script_input_var.variableId,
                                             node_variable=script_output_var.variableName,
                                             param_id=diagram_inp_var.parameterId
                                             )
            node_script_upd = node_update_construct(x=700, y=202.22915649414062, node_type="custom_code",
                                                    temp_version_id=temp_version_id,
                                                    script_id=script_id,
                                                    script_version_id=script_version_id,
                                                    script_type=ScriptType2.PYTHON,
                                                    inp_custom_code_vars=[inp_var_map],
                                                    out_custom_code_vars=[out_var_map])
            update_node(super_user, node_id=node_script_id, body=node_script_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_script_upd.nodeTypeId,
                            properties=node_script_upd.properties))

        with allure.step("Валидация узла кастомного кода"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_script_id).body
            )
            assert node_view.validFlag

    @allure.story("Происходит корректный маппинг переменной комплексного типа на выходную переменную"
                  " узла кастомного кода")
    # "Пока отключена валидация"
    @allure.title("Cоздание диаграммы с целочисленным атрибутом переменной комплексного типа на выход и "
                  "целочисленной переменной на вход, с последующим изменение имени намапленной переменной")
    @pytest.mark.scenario("DEV-6398")
    @pytest.mark.variable_data([VariableParams(varName="in_int", varType="in", varDataType=1),
                                VariableParams(varName="out_cmplx",
                                               varType="out", isComplex=True, isArray=False)])
    @pytest.mark.nodes(["кастомный код"])
    @pytest.mark.smoke
    def test_node_script_change_name(self,
                                     super_user,
                                     create_python_code_int_vars,
                                     diagram_constructor):
        with allure.step("Создание диаграммы с узлами начало, кастом код, завершение где на "
                         "выход подается переменная компл типа с интовым атрибутом и интовой переменной на вход"):
            diagram_inp_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int"]
            diagram_out_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_cmplx"]
            complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]
            attr: AttributeShortView = AttributeShortView.construct(**complex_type.attributes[0])
            temp_version_id = diagram_constructor["diagram_info"].versionId
            script_output_var: ScriptVariableFullView = create_python_code_int_vars["out_var"]
            script: ScriptFullView = create_python_code_int_vars["code_view"]
            script_input_var: ScriptVariableFullView = create_python_code_int_vars["inp_var"]
            script_id = script.scriptId
            script_version_id = script.versionId
            node_script_id = diagram_constructor["nodes"]["кастомный код"].nodeId
        with allure.step("Добавление атрибута комплексного типа на выход"):
            out_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False,
                                             is_compl=False,
                                             name=attr.attributeName,
                                             var_path=diagram_out_var.parameterName,
                                             var_root_id=complex_type.versionId,
                                             type_id=script_output_var.primitiveTypeId,
                                             outer_variable_id=script_output_var.variableId)
            inp_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False,
                                             is_compl=False,
                                             name=diagram_inp_var.parameterName,
                                             type_id=script_input_var.primitiveTypeId,
                                             outer_variable_id=script_input_var.variableId,
                                             node_variable=script_output_var.variableName,
                                             param_id=diagram_inp_var.parameterId
                                             )
            node_script_upd = node_update_construct(x=700, y=202.22915649414062, node_type="custom_code",
                                                    temp_version_id=temp_version_id,
                                                    script_id=script_id,
                                                    script_version_id=script_version_id,
                                                    script_type=ScriptType2.PYTHON,
                                                    inp_custom_code_vars=[inp_var_map],
                                                    out_custom_code_vars=[out_var_map])
            update_node(super_user, node_id=node_script_id, body=node_script_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_script_upd.nodeTypeId,
                            properties=node_script_upd.properties))
        with allure.step("замена переменной диаграммы на вход"):
            update_diagram = update_diagram_parameters(
                super_user, str(temp_version_id), [variable_construct(),
                                                   variable_construct(array_flag=False,
                                                                      complex_flag=False,
                                                                      is_execute_status=None,
                                                                      order_num=0,
                                                                      param_name="var_name_change",
                                                                      parameter_type="in",
                                                                      parameter_version_id=str(
                                                                          diagram_inp_var.parameterId),
                                                                      type_id=1,
                                                                      parameter_id=str(diagram_inp_var.parameterId))])
        with allure.step("Валидация узла кастомного кода"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_script_id).body
            )
            assert node_view.validFlag == False

    @allure.story("Замена кастомного кода Groovy на Python в узле кастомного кода диаграммы")
    @allure.title("создать диаграмму с узлом кастомного кода, изменить в узле кастомный код")
    @pytest.mark.scenario("DEV-11978")
    @pytest.mark.variable_data([VariableParams(varName="in_int", varType="in", varDataType=1),
                                VariableParams(varName="out_cmplx",
                                               varType="out", isComplex=True, isArray=False)])
    @pytest.mark.nodes(["кастомный код"])
    @pytest.mark.smoke
    def test_node_script_remap(self,
                               super_user,
                               create_python_code_int_vars,
                               create_groovy_code_int_vars,
                               diagram_constructor):
        with allure.step("Создание диаграммы с узлами начало, кастом код, завершение где на "
                         "выход подается переменная компл типа с интовым атрибутом и интовой переменной на вход"):
            diagram_inp_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int"]
            diagram_out_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_cmplx"]
            complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]
            attr: AttributeShortView = AttributeShortView.construct(**complex_type.attributes[0])
            temp_version_id = diagram_constructor["diagram_info"].versionId
            script_output_var: ScriptVariableFullView = create_groovy_code_int_vars["out_var"]
            script: ScriptFullView = create_groovy_code_int_vars["code_view"]
            script_input_var: ScriptVariableFullView = create_groovy_code_int_vars["inp_var"]
            script_id = script.scriptId
            script_version_id = script.versionId
            script_output_var2: ScriptVariableFullView = create_python_code_int_vars["out_var"]
            script2: ScriptFullView = create_python_code_int_vars["code_view"]
            script_input_var2: ScriptVariableFullView = create_python_code_int_vars["inp_var"]
            script_id2 = script2.scriptId
            script_version_id2 = script2.versionId
            node_script_id = diagram_constructor["nodes"]["кастомный код"].nodeId
        with allure.step("Добавляю атрибут комплексного типа на выход"):
            out_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False,
                                             is_compl=False,
                                             name=attr.attributeName,
                                             var_path=diagram_out_var.parameterName,
                                             var_root_id=complex_type.versionId,
                                             type_id=script_output_var.primitiveTypeId,
                                             outer_variable_id=script_output_var.variableId)
            inp_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False,
                                             is_compl=False,
                                             name=diagram_inp_var.parameterName,
                                             type_id=script_input_var.primitiveTypeId,
                                             outer_variable_id=script_input_var.variableId,
                                             node_variable=script_output_var.variableName,
                                             param_id=diagram_inp_var.parameterId
                                             )
            node_script_upd = node_update_construct(x=700, y=202.22915649414062, node_type="custom_code",
                                                    temp_version_id=temp_version_id,
                                                    script_id=script_id,
                                                    script_version_id=script_version_id,
                                                    script_type=ScriptType2.PYTHON,
                                                    inp_custom_code_vars=[inp_var_map],
                                                    out_custom_code_vars=[out_var_map])
            update_node(super_user, node_id=node_script_id, body=node_script_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_script_upd.nodeTypeId,
                            properties=node_script_upd.properties))

        with allure.step("Изменить кастомный код"):
            out_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False,
                                             is_compl=False,
                                             name=attr.attributeName,
                                             var_path=diagram_out_var.parameterName,
                                             var_root_id=complex_type.versionId,
                                             type_id=script_output_var2.primitiveTypeId,
                                             outer_variable_id=script_output_var2.variableId)
            inp_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False,
                                             is_compl=False,
                                             name=diagram_inp_var.parameterName,
                                             type_id=script_input_var2.primitiveTypeId,
                                             outer_variable_id=script_input_var2.variableId,
                                             node_variable=script_output_var2.variableName,
                                             param_id=diagram_inp_var.parameterId
                                             )
            remap_properties = node_script_upd.properties
            remap_properties.inputVariablesMapping = [inp_var_map]
            remap_properties.outputVariablesMapping = [out_var_map]
            remap_properties.scriptType = "PYTHON"
            remap_properties.customCodeId = script_id
            remap_properties.versionId = script_version_id
            node_remap_body = node_remap_construct(int_node_type=1,
                                                   object_id=script_id2,
                                                   object_version_id=script_version_id2,
                                                   properties=remap_properties)
            remap = remap_node(super_user, node_script_id, body=node_remap_body)

            with allure.step("намапить переменные, обновить узел"):
                out_var_map2 = variables_for_node(node_type="custom_code",
                                                  is_arr=False,
                                                  is_compl=False,
                                                  name=attr.attributeName,
                                                  var_path=diagram_out_var.parameterName,
                                                  var_root_id=complex_type.versionId,
                                                  type_id=script_output_var2.primitiveTypeId,
                                                  outer_variable_id=script_output_var2.variableId)
                inp_var_map2 = variables_for_node(node_type="custom_code",
                                                  is_arr=False,
                                                  is_compl=False,
                                                  name=diagram_inp_var.parameterName,
                                                  type_id=script_input_var2.primitiveTypeId,
                                                  outer_variable_id=script_input_var2.variableId,
                                                  node_variable=script_output_var2.variableName,
                                                  param_id=diagram_inp_var.parameterId
                                                  )
                node_script_upd_new = node_update_construct(x=700, y=202.22915649414062, node_type="custom_code",
                                                            temp_version_id=temp_version_id,
                                                            script_id=script_id2,
                                                            script_version_id=script_version_id2,
                                                            script_type=ScriptType2.PYTHON,
                                                            inp_custom_code_vars=[inp_var_map2],
                                                            out_custom_code_vars=[out_var_map2])
                update_node(super_user, node_id=node_script_id, body=node_script_upd_new,
                            validate_body=NodeValidateDto.construct(
                                nodeTypeId=node_script_upd_new.nodeTypeId,
                                properties=node_script_upd_new.properties))

            with allure.step("Валидация узла кастомного кода"):
                node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                    **get_node_by_id(super_user, node_script_id).body
                )
                assert node_view.validFlag and node_view.properties["customCodeId"] == script_id2 \
                       and node_view.properties["versionId"] == script_version_id2 \
                       and node_view.properties["scriptType"] == "PYTHON"

    @allure.story("Замена кастомного кода Python на Groovy в узле кастомного кода диаграммы,"
                  " с последующим сохранением узла и настройкой мапинга")
    @allure.issue("DEV-14186")
    @allure.title("создать диаграмму с узлом кастомного кода, изменить в узле кастомный код, "
                  "произвести мапинг и сохранить узел")
    @pytest.mark.scenario("DEV-11978")
    @pytest.mark.variable_data([VariableParams(varName="in_int", varType="in", varDataType=1),
                                VariableParams(varName="out_cmplx",
                                               varType="out", isComplex=True, isArray=False)])
    @pytest.mark.nodes(["кастомный код"])
    @pytest.mark.smoke
    def test_node_script_remap_validate(self,
                                        super_user,
                                        create_python_code_int_vars,
                                        create_groovy_code_int_vars,
                                        diagram_constructor):
        with allure.step("Создание диаграммы с узлами начало, кастом код, завершение где на "
                         "выход подается переменная компл типа с интовым атрибутом и интовой переменной на вход"):
            diagram_inp_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["in_int"]
            diagram_out_var: DiagramInOutParameterFullViewDto = diagram_constructor["variables"]["out_cmplx"]
            complex_type: ComplexTypeGetFullView = diagram_constructor["complex_type"]
            attr: AttributeShortView = AttributeShortView.construct(**complex_type.attributes[0])
            temp_version_id = diagram_constructor["diagram_info"].versionId
            script_output_var: ScriptVariableFullView = create_python_code_int_vars["out_var"]
            script: ScriptFullView = create_python_code_int_vars["code_view"]
            script_input_var: ScriptVariableFullView = create_python_code_int_vars["inp_var"]
            script_id = script.scriptId
            script_version_id = script.versionId
            script_output_var2: ScriptVariableFullView = create_groovy_code_int_vars["out_var"]
            script2: ScriptFullView = create_groovy_code_int_vars["code_view"]
            script_input_var2: ScriptVariableFullView = create_groovy_code_int_vars["inp_var"]
            script_id2 = script2.scriptId
            script_version_id2 = script2.versionId
            node_script_id = diagram_constructor["nodes"]["кастомный код"].nodeId
        with allure.step("Добавляю атрибут комплексного типа на выход"):
            out_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False,
                                             is_compl=False,
                                             name=attr.attributeName,
                                             var_path=diagram_out_var.parameterName,
                                             var_root_id=complex_type.versionId,
                                             type_id=script_output_var.primitiveTypeId,
                                             outer_variable_id=script_output_var.variableId)
            inp_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False,
                                             is_compl=False,
                                             name=diagram_inp_var.parameterName,
                                             type_id=script_input_var.primitiveTypeId,
                                             outer_variable_id=script_input_var.variableId,
                                             node_variable=script_output_var.variableName,
                                             param_id=diagram_inp_var.parameterId
                                             )
            node_script_upd = node_update_construct(x=700, y=202.22915649414062, node_type="custom_code",
                                                    temp_version_id=temp_version_id,
                                                    script_id=script_id,
                                                    script_version_id=script_version_id,
                                                    script_type=ScriptType2.PYTHON,
                                                    inp_custom_code_vars=[inp_var_map],
                                                    out_custom_code_vars=[out_var_map])
            update_node(super_user, node_id=node_script_id, body=node_script_upd,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_script_upd.nodeTypeId,
                            properties=node_script_upd.properties))

        with allure.step("Изменить кастомный код"):
            out_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False,
                                             is_compl=False,
                                             name=attr.attributeName,
                                             var_path=diagram_out_var.parameterName,
                                             var_root_id=complex_type.versionId,
                                             type_id=script_output_var2.primitiveTypeId,
                                             outer_variable_id=script_output_var2.variableId)
            inp_var_map = variables_for_node(node_type="custom_code",
                                             is_arr=False,
                                             is_compl=False,
                                             name=diagram_inp_var.parameterName,
                                             type_id=script_input_var2.primitiveTypeId,
                                             outer_variable_id=script_input_var2.variableId,
                                             node_variable=script_output_var2.variableName,
                                             param_id=diagram_inp_var.parameterId
                                             )
            remap_properties = node_script_upd.properties
            remap_properties.inputVariablesMapping = [inp_var_map]
            remap_properties.outputVariablesMapping = [out_var_map]
            remap_properties.scriptType = "PYTHON"
            remap_properties.customCodeId = script_id
            remap_properties.versionId = script_version_id
            node_remap_body = node_remap_construct(int_node_type=1,
                                                   object_id=script_id2,
                                                   object_version_id=script_version_id2,
                                                   properties=remap_properties)
            remap = remap_node(super_user, node_script_id, body=node_remap_body)

        with allure.step("намапить переменные, обновить узел"):
            out_var_map2 = variables_for_node(node_type="custom_code",
                                              is_arr=False,
                                              is_compl=False,
                                              name=attr.attributeName,
                                              var_path=diagram_out_var.parameterName,
                                              var_root_id=complex_type.versionId,
                                              type_id=script_output_var2.primitiveTypeId,
                                              outer_variable_id=script_output_var2.variableId)
            inp_var_map2 = variables_for_node(node_type="custom_code",
                                              is_arr=False,
                                              is_compl=False,
                                              name=diagram_inp_var.parameterName,
                                              type_id=script_input_var2.primitiveTypeId,
                                              outer_variable_id=script_input_var2.variableId,
                                              node_variable=script_output_var2.variableName,
                                              param_id=diagram_inp_var.parameterId
                                              )
            node_script_upd_new = node_update_construct(x=700, y=202.22915649414062, node_type="custom_code",
                                                        temp_version_id=temp_version_id,
                                                        script_id=script_id2,
                                                        script_version_id=script_version_id2,
                                                        script_type=ScriptType2.GROOVY,
                                                        inp_custom_code_vars=[inp_var_map2],
                                                        out_custom_code_vars=[out_var_map2])
            update_node(super_user, node_id=node_script_id, body=node_script_upd_new,
                        validate_body=NodeValidateDto.construct(
                            nodeTypeId=node_script_upd_new.nodeTypeId,
                            properties=node_script_upd_new.properties))

        with allure.step("Валидация узла кастомного кода"):
            node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
                **get_node_by_id(super_user, node_script_id).body
            )
            assert node_view.validFlag and node_view.properties["customCodeId"] == script_id2 \
                   and node_view.properties["versionId"] == script_version_id2 \
                   and node_view.properties["scriptType"] == "GROOVY"
