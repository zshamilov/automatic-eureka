import json
import os
import random
import string
import time
import uuid

import pytest
from typing import List

from common.generators import generate_string
from products.Decision.framework.model import DiagramViewDto, DiagramCreateNewVersion, ResponseDto, LinkCreateDto, \
    EnvironmentShortInfoDto, \
    ComplexTypeGetFullView, VariableType1, \
    ScriptFullView, ScriptVariableViewWithoutVersionIdDto, ImportResponseDto, RuleTypeCreateDto, \
    DiagramInOutParametersViewDto, EmptyTestCreate, Locale, EmptyTestDto, TestInfo, Status3, \
    DiagramInOutParameterFullViewDto, ConfirmExportDto, ExportResponseDto, ObjectsType, NodeValidateDto, \
    AggregateFunction1, \
    AggregateGetFullView, RetentionType, RetentionTimeUnit, DataSourceType, OfferFullViewDto, DataSourceType1, \
    CommunicationChannelFullViewDto, CustomAttributeDictionaryFullView, ExportStatusDto
from products.Decision.framework.steps.decision_steps_aggregate_api import get_aggregate
from products.Decision.framework.steps.decision_steps_communication_api import delete_communication, \
    get_communication_channel
from products.Decision.framework.steps.decision_steps_complex_type import delete_custom_type, \
    get_custom_type
from products.Decision.framework.steps.decision_steps_custom_attr_dict import create_custom_attribute, \
    delete_custom_attribute, get_custom_attribute
from products.Decision.framework.steps.decision_steps_data_provider_api import delete_data_provider
from products.Decision.framework.steps.decision_steps_deploy import find_deploy_id, deploy_delete
from products.Decision.framework.steps.decision_steps_diagram import create_template, save_diagram, \
    get_diagram_by_version, delete_diagram, update_diagram_parameters, delete_diagram_template, put_diagram_submit, \
    get_diagram_parameters, get_filtered_variables
from products.Decision.framework.steps.decision_steps_environments import environments_list
from products.Decision.framework.steps.decision_steps_external_service_api import delete_service
from products.Decision.framework.steps.decision_steps_migration import download_export_file, confirm_import, \
    generate_export_objects, set_export
from products.Decision.framework.steps.decision_steps_nodes import create_node, create_link, update_node
from products.Decision.framework.steps.decision_steps_offer_api import delete_offer, get_offer_info
from products.Decision.framework.steps.decision_steps_rule_types_api import create_ruletype, delete_ruletype_by_id
from products.Decision.framework.steps.decision_steps_script_api import get_python_script_by_id, delete_script_by_id
from products.Decision.framework.steps.decision_steps_testing_api import download_test_file_gen, download_test_file, \
    create_empty_test, send_testing_file, start_testing, find_test, download_test_report
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description
from products.Decision.utilities.aggregate_constructors import aggregate_json_construct, aggregate_construct
from products.Decision.utilities.communication_constructors import communication_var_construct, communication_construct
from products.Decision.utilities.custom_code_constructors import script_vars_construct
from products.Decision.utilities.custom_type_constructors import generate_attr_type_name, \
    attribute_construct
from products.Decision.utilities.dict_constructors import dict_value_construct, dict_construct
from products.Decision.utilities.export_import_constructors import generate_export_objects_construct
from products.Decision.utilities.file_utils import file_testing_generate_test_cases
from products.Decision.utilities.node_cunstructors import variables_for_node, node_construct, link_construct, \
    node_update_construct, aggregate_compute_node_construct, \
    aggregate_properties, aggregate_compute_out_var, grouping_element_map, aggregate_compute_properties, \
    offer_node_construct, offer_properties, offer_variable
from products.Decision.utilities.offer_constructors import offer_variable_construct, offer_construct
from products.Decision.utilities.variable_constructors import variable_construct


# Fixtures for diagrams Range


@pytest.fixture()
def create_and_save_empty_diagram(super_user):
    response_create_template = create_template(super_user)
    diagram_template: DiagramViewDto = response_create_template.body
    diagram_id = diagram_template["diagramId"]
    temp_version_id = diagram_template["versionId"]
    letters = string.ascii_lowercase
    rand_string_diagram_name = ''.join(random.choice(letters) for i in range(16))
    new_diagram_name = "diagram" + "_" + rand_string_diagram_name
    diagram_description = 'diagram created in test'
    response_save = save_diagram(super_user, body=DiagramCreateNewVersion(diagramId=uuid.UUID(diagram_id),
                                                                          versionId=temp_version_id,
                                                                          errorResponseFlag=False,
                                                                          objectName=new_diagram_name,
                                                                          diagramDescription=diagram_description))
    create_result: ResponseDto = response_save.body
    version_id = create_result["uuid"]
    get_diagram_by_version_response = get_diagram_by_version(super_user, version_id)
    diagram: DiagramViewDto = get_diagram_by_version_response.body
    saved_version_id = diagram["versionId"]
    yield diagram


@pytest.fixture()
def create_and_save_empty_diagram_without_info(super_user):
    response_create_template = create_template(super_user)
    diagram_template: DiagramViewDto = response_create_template.body
    diagram_id = diagram_template["diagramId"]
    temp_version_id = diagram_template["versionId"]
    letters = string.ascii_lowercase
    rand_string_diagram_name = ''.join(random.choice(letters) for i in range(16))
    new_diagram_name = "diagram" + "_" + rand_string_diagram_name
    diagram_description = 'diagram created in test'
    response_save = save_diagram(super_user, body=DiagramCreateNewVersion(diagramId=uuid.UUID(diagram_id),
                                                                          versionId=temp_version_id,
                                                                          errorResponseFlag=False,
                                                                          objectName=new_diagram_name,
                                                                          diagramDescription=diagram_description))
    create_result: ResponseDto = response_save.body
    saved_version_id = create_result["uuid"]
    yield create_result

    delete_diagram(super_user, saved_version_id)


@pytest.fixture()
def crete_temp_diagram_with_custom_code_node(super_user, create_temp_diagram_gen):
    template = dict(create_temp_diagram_gen.create_template())
    temp_version_id = template["versionId"]
    node_script = node_construct(700, 202.22915649414062, "custom_code", temp_version_id)
    node_script_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_script).body)
    node_script_id = node_script_response.uuid

    return {"template": template, "node_script_resp": node_script_response}


@pytest.fixture()
def create_two_temp_diagram(super_user):
    response_create_template = create_template(super_user)
    diagram_template: DiagramViewDto = response_create_template.body
    response_create_template2 = create_template(super_user)
    diagram_template2: DiagramViewDto = response_create_template2.body
    yield {"first_template": diagram_template, "second_template": diagram_template2}

    delete_diagram_template(super_user, diagram_template["versionId"])
    delete_diagram_template(super_user, diagram_template2["versionId"])


@pytest.fixture()
def simple_diagram_dict_attr(super_user, create_temp_diagram_gen, create_dict_gen):
    dict_name = "ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"]
    value = dict_value_construct(dict_value="15",
                                 dict_value_display_name="age")
    custom_attr = dict_construct(
        dict_name=dict_name,
        dict_value_type_id="1",
        values=[value])
    dict_create_result: ResponseDto = create_dict_gen.create_dict(dict_body=custom_attr)
    diagram_template = dict(create_temp_diagram_gen.create_template())
    diagram_id = diagram_template["diagramId"]
    temp_version_id = diagram_template["versionId"]
    letters = string.ascii_lowercase
    rand_string_param_name = ''.join(random.choice(letters) for i in range(8))
    parameter_version_id2 = str(uuid.uuid4())
    diagram_param = variable_construct(array_flag=False,
                                       complex_flag=False,
                                       default_value=None,
                                       is_execute_status=None,
                                       order_num=0,
                                       param_name=rand_string_param_name,
                                       parameter_type="in_out",
                                       parameter_version_id=parameter_version_id2,
                                       type_id=1,
                                       dict_flag=True,
                                       dict_id=dict_create_result.uuid,
                                       dict_name=dict_name,
                                       parameter_id=parameter_version_id2
                                       )

    params_response = update_diagram_parameters(super_user,
                                                temp_version_id,
                                                [variable_construct(),
                                                 diagram_param])

    update_response: ResponseDto = params_response.body

    start_variables = variables_for_node(node_type="start", is_arr=False,
                                         is_compl=False, name=rand_string_param_name,
                                         type_id=1, vers_id=parameter_version_id2,
                                         is_dict=True, dict_id=dict_create_result.uuid)
    finish_variables = variables_for_node(node_type="finish", is_arr=False,
                                          is_compl=False, name=rand_string_param_name,
                                          type_id=1, vers_id=parameter_version_id2,
                                          is_dict=True, dict_id=dict_create_result.uuid)
    node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id, [start_variables])
    node_finish_raw = node_construct(714, 202.22915649414062, "finish", temp_version_id, None)
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = node_start_response.body
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = node_end_response.body

    link_create_response = create_link(super_user, body=LinkCreateDto(diagramVersionId=temp_version_id,
                                                                      prevNodeId=node_start["uuid"],
                                                                      nextNodeId=node_end["uuid"]))
    update_node_response = update_node(super_user,
                                       node_id=node_end["uuid"],
                                       body=node_update_construct(714, 202.22915649414062, "finish", temp_version_id,
                                                                  [finish_variables]))

    rand_string_diagram_name = ''.join(random.choice(letters) for i in range(16))
    new_diagram_name = "diagram" + "_" + rand_string_diagram_name
    diagram_description = 'diagram created in test'

    response_save = save_diagram(super_user, body=DiagramCreateNewVersion(diagramId=uuid.UUID(diagram_id),
                                                                          versionId=temp_version_id,
                                                                          errorResponseFlag=False,
                                                                          objectName=new_diagram_name,
                                                                          diagramDescription=diagram_description))

    create_result: ResponseDto = response_save.body

    saved_version_id = create_result["uuid"]

    yield {"template": diagram_template, "create_result": create_result,
           "diagram_param": diagram_param, "dict_id": dict_create_result.uuid,
           "saved_version_id": saved_version_id}

    delete_diagram(super_user, saved_version_id)


@pytest.fixture(scope="class")
def diagram_start_finish_test_results(super_user, generate_test_file_gen):
    response_create_template = create_template(super_user)
    diagram_template: DiagramInOutParametersViewDto = response_create_template.body
    exec_var: DiagramInOutParameterFullViewDto = diagram_template["inOutParameters"][0]
    diagram_id = diagram_template["diagramId"]
    temp_version_id = diagram_template["versionId"]
    letters = string.ascii_lowercase
    parameter_version_id1 = str(uuid.uuid4())
    parameter_version_id2 = str(uuid.uuid4())
    diagram_param_in = variable_construct(array_flag=False,
                                          complex_flag=False,
                                          default_value=None,
                                          is_execute_status=None,
                                          order_num=0,
                                          param_name="input_var",
                                          parameter_type="in",
                                          parameter_version_id=parameter_version_id1,
                                          parameter_id=parameter_version_id1,
                                          type_id=1
                                          )

    diagram_param_out = variable_construct(array_flag=False,
                                           complex_flag=False,
                                           default_value=None,
                                           is_execute_status=None,
                                           order_num=0,
                                           param_name="out_var",
                                           parameter_type="out",
                                           parameter_version_id=parameter_version_id2,
                                           parameter_id=parameter_version_id2,
                                           type_id=1
                                           )

    params_response = update_diagram_parameters(super_user,
                                                temp_version_id,
                                                [exec_var,
                                                 diagram_param_in,
                                                 diagram_param_out])

    update_response: ResponseDto = params_response.body

    start_variables = variables_for_node(node_type="start", is_arr=False, is_compl=False,
                                         name="input_var", type_id=1, vers_id=parameter_version_id1)
    finish_variables = variables_for_node(node_type="finish_out", is_arr=False, is_compl=False,
                                          name="input_var", type_id=1, vers_id=parameter_version_id2,
                                          param_name="out_var")
    node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id, [start_variables])
    node_finish_raw = node_construct(714, 202.22915649414062, "finish", temp_version_id, [finish_variables])
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = node_start_response.body
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = node_end_response.body

    link_create_response = create_link(super_user, body=LinkCreateDto(diagramVersionId=temp_version_id,
                                                                      prevNodeId=node_start["uuid"],
                                                                      nextNodeId=node_end["uuid"]))
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variables])
    update_node(super_user, node_id=node_end["uuid"], body=finish_up_body)

    rand_string_diagram_name = ''.join(random.choice(letters) for i in range(8))
    new_diagram_name = "diagram" + "_" + rand_string_diagram_name
    diagram_description = 'diagram created in test'
    body = DiagramCreateNewVersion(diagramId=uuid.UUID(diagram_id),
                                   versionId=temp_version_id,
                                   errorResponseFlag=False,
                                   objectName=new_diagram_name,
                                   diagramDescription=diagram_description)

    response_save = save_diagram(super_user, body=body)

    create_result: ResponseDto = response_save.body

    saved_version_id = create_result["uuid"]

    diagram_vars: List[DiagramInOutParameterFullViewDto] = \
        [DiagramInOutParameterFullViewDto.construct(**var) for var in
         get_filtered_variables(super_user,
                                saved_version_id, )]
    file_path = generate_test_file_gen.generate_and_load_testing_file(
        diagram_version_id=saved_version_id
    )
    testfile_fill_result = file_testing_generate_test_cases(file_path, diagram_vars)
    empty_test = EmptyTestCreate(locale=Locale.ru, diagramId=diagram_id)
    test_create_result = EmptyTestDto(
        **create_empty_test(super_user, body=empty_test).body
    )
    test_set_id = test_create_result.testId
    send_testing_file(
        super_user,
        test_set_id,
        file=file_path,
    )
    start_testing(super_user, saved_version_id, body=[str(test_create_result.testId)])
    test_status = None
    for i in range(300):
        test_info = TestInfo.construct(
            **find_test(super_user, test_create_result.testId).body
        )
        if (
                test_info.status == Status3.EMERGENCY_STOP
                or test_info.status == Status3.FAIL
                or test_info.status == Status3.SUCCESS
        ):
            test_status = test_info.status
            break
        time.sleep(1)

    yield {"template": diagram_template, "create_result": create_result,
           "diagram_param_in": diagram_param_in,
           "diagram_param_out": diagram_param_out, "diagram_data": body,
           "test_id": test_create_result.testId, "test_status": test_status}

    delete_diagram(super_user, saved_version_id)


# @pytest.fixture()
# def diagram_deployed(super_user,
#                      create_and_save_diagram_int_var_start_finish_nodes_ready_for_deploy,
#                      deploy_diagrams_gen):
#     create_and_save_result = create_and_save_diagram_int_var_start_finish_nodes_ready_for_deploy
#     diagram_id = create_and_save_result["template"]["diagramId"]
#     version_id = create_and_save_result["create_result"]["uuid"]
#     diagram_name = create_and_save_result["diagram_name"]
#     put_diagram_submit(super_user, diagram_id)
#     deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
#     env_list: [EnvironmentShortInfoDto] = environments_list(super_user).body
#     env_id = ""
#     for env in env_list:
#         if env["environmentName"] == "default_dev":
#             env_id = env["environmentId"]
#             break
#
#     deploy_configuration = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["config"]
#
#     return {"diagram_id": diagram_id, "version_id": version_id, "env_id": env_id,
#             "deploy_id": deploy_id, "diagram_name": diagram_name,
#             "deploy_configuration": deploy_configuration
#             }


@pytest.fixture(scope='class')
def generate_test_report_gen(super_user):
    class GenerateReport:
        file_paths = []

        @staticmethod
        def download_testing_report(test_id):
            file_path = f"products/Decision/resources/test_report{len(GenerateReport.file_paths)}.xlsx"
            if os.path.isfile(file_path):
                os.remove(file_path)
            download_test_report(user=super_user, test_id=test_id, file_path=file_path)
            GenerateReport.file_paths.append(file_path)
            return file_path

    yield GenerateReport

    for f_path in GenerateReport.file_paths:
        if os.path.isfile(f_path):
            os.remove(f_path)
            print("success")
        else:
            print("File doesn't exists!")


@pytest.fixture(scope='class')
def generate_test_file_gen(super_user):
    class GenerateFile:
        file_paths = []

        @staticmethod
        def generate_and_load_testing_file(diagram_version_id):
            file_path = f"products/Decision/resources/test{len(GenerateFile.file_paths)}.xlsx"
            download_test_file_gen(super_user, diagram_version_id, file_path=file_path)
            GenerateFile.file_paths.append(file_path)
            return file_path

        @staticmethod
        def download_testing_file(test_id):
            file_path = f"products/Decision/resources/test_data{len(GenerateFile.file_paths)}.xlsx"
            download_test_file(user=super_user, test_id=test_id, file_path=file_path)
            GenerateFile.file_paths.append(file_path)
            return file_path

    yield GenerateFile

    for f_path in GenerateFile.file_paths:
        if os.path.isfile(f_path):
            os.remove(f_path)
            print("success")
        else:
            print("File doesn't exists!")


@pytest.fixture()
def create_groovy_code_int_vars_user_version(super_user, create_groovy_code_int_vars, create_code_gen):
    groovy_code: ScriptFullView = create_groovy_code_int_vars["code_view"]
    script_name = create_groovy_code_int_vars["script_name"]
    script_text = create_groovy_code_int_vars["script_text"]
    inp_var = create_groovy_code_int_vars["inp_var"]
    out_var = create_groovy_code_int_vars["out_var"]
    script_id = groovy_code.scriptId
    vers_name = "user_version_" + script_name
    create_vers_result: ResponseDto = create_code_gen.create_groovy_code_user_version(script_id, script_text,
                                                                                      script_name, vers_name,
                                                                                      inp_var, out_var)[
        "vers_create_result"]

    yield {"user_version_id": create_vers_result.uuid, "script_id": script_id}

    delete_script_by_id(super_user, create_vers_result.uuid)


@pytest.fixture(scope='class')
def export_import_file(super_user):
    class ExportImportFile:
        file_paths = []

        @staticmethod
        def download_export_file(file_name):
            file_path = f"products/Decision/resources/{file_name}"
            download_export_file(super_user, file_name=file_name, file_path=file_path)
            ExportImportFile.file_paths.append(file_path)
            return file_path

        @staticmethod
        def try_download_export_file(file_name, path=True):
            if path:
                file_path = f"products/Decision/resources/{file_name}"
                resp = download_export_file(super_user, file_name=file_name, file_path=file_path)
                if resp.status == 200:
                    ExportImportFile.file_paths.append(file_path)
            else:
                resp = download_export_file(super_user, file_name=file_name)
            return resp

        @staticmethod
        def export_objects_file_with_all_dependencies(object_ids: list,
                                                      include_all_versions=True,
                                                      object_type: ObjectsType = ObjectsType.DIAGRAM):
            gen_export_body = generate_export_objects_construct(objects_type=object_type,
                                                                object_ids=object_ids,
                                                                is_include_all_versions=include_all_versions
                                                                )
            gen_export_objects = generate_export_objects(super_user, body=gen_export_body).body

            for key in gen_export_objects:
                for element in gen_export_objects[key]:
                    element["isSelected"] = True
            export_body = ExportStatusDto.construct(**gen_export_objects)
            export_resp: ExportResponseDto = ExportResponseDto.construct(
                **set_export(super_user, body=export_body).body
            )
            file_name = export_resp.fileName
            file_path = f"products/Decision/resources/{file_name}"
            download_export_file(super_user, file_name=file_name, file_path=file_path)
            ExportImportFile.file_paths.append(file_path)
            return file_path

    yield ExportImportFile

    for f_path in ExportImportFile.file_paths:
        if os.path.isfile(f_path):
            os.remove(f_path)
            print("success")
        else:
            print("File doesn't exists!")


@pytest.fixture(scope='function')
def import_file(super_user):
    class ImportFile:
        vers_ids = []
        ctypes_vers_ids = []
        script_vers_ids = []
        offer_vers_ids = []

        @staticmethod
        def confirm_import_gen(body):
            import_response = ImportResponseDto.construct(**confirm_import(super_user, body).body)
            if import_response.importStatus["objectsInfo"]:
                if "diagrams" in import_response.importStatus["objectsInfo"]:
                    if import_response.importStatus["objectsInfo"]["diagrams"]:
                        for diagram in import_response.importStatus["objectsInfo"]["diagrams"]:
                            if diagram["status"] != "CANCELED" and diagram["objectVersionType"] != "DEPLOYED":
                                ImportFile.vers_ids.append(
                                    diagram["objectVersionId"])
                if "complexTypes" in import_response.importStatus["objectsInfo"]:
                    if import_response.importStatus["objectsInfo"]["complexTypes"]:
                        for ctype in import_response.importStatus["objectsInfo"]["complexTypes"]:
                            if ctype["status"] != "CANCELED":
                                ImportFile.ctypes_vers_ids.append(
                                    ctype["objectVersionId"])
                if "scripts" in import_response.importStatus["objectsInfo"]:
                    if import_response.importStatus["objectsInfo"]["scripts"]:
                        for script in import_response.importStatus["objectsInfo"]["scripts"]:
                            if script["status"] != "CANCELED":
                                ImportFile.script_vers_ids.append(
                                    script["objectVersionId"])
                if "offers" in import_response.importStatus["objectsInfo"]:
                    if import_response.importStatus["objectsInfo"]["diagrams"]:
                        for offer in import_response.importStatus["objectsInfo"]["offers"]:
                            if offer["status"] != "CANCELED" and offer["objectVersionType"] != "DEPLOYED":
                                ImportFile.offer_vers_ids.append(
                                    offer["objectVersionId"])
            return import_response

    yield ImportFile

    for version_id in ImportFile.vers_ids:
        try:
            delete_diagram(super_user, version_id)
        except:
            print("can't delete diagram")
    for offer_version_id in ImportFile.offer_vers_ids:
        try:
            delete_offer(super_user, offer_version_id)
        except:
            print("can't delete offer")
    for script_version_id in ImportFile.script_vers_ids:
        try:
            delete_script_by_id(super_user, script_version_id)
        except:
            print("can't delete script")
    for c_type_version_id in ImportFile.ctypes_vers_ids:
        try:
            delete_custom_type(super_user, c_type_version_id)
        except:
            print("can't delete ctype")


@pytest.fixture(scope='class')
def create_rule_gen(super_user):
    class CreateRule:
        rule_ids = []

        @staticmethod
        def create_rule(type_name, display_name):
            create_response: ResponseDto = ResponseDto.construct(
                **create_ruletype(super_user, body=RuleTypeCreateDto(typeName=type_name,
                                                                     displayName=display_name)).body)
            rule_id = create_response.uuid
            CreateRule.rule_ids.append(rule_id)
            return create_response

        @staticmethod
        def try_create_rule(type_name, display_name):
            create_response = create_ruletype(super_user, body=RuleTypeCreateDto(typeName=type_name,
                                                                                 displayName=display_name))
            if create_response.status == 201:
                CreateRule.rule_ids.append(create_response.body["uuid"])
            return create_response

    yield CreateRule

    for type_id in CreateRule.rule_ids:
        delete_ruletype_by_id(super_user, type_id)


@pytest.fixture()
def diagram_aggregate_compute_save(super_user, create_aggregate_gen, create_temp_diagram_gen,
                                   save_diagrams_gen, aggregate_function=None):
    aggr_name = "auto_test_aggregate_" + generate_string()
    grouping_element = "client_id"
    aggr_function = AggregateFunction1.AggCount
    aggr_json = aggregate_json_construct(
        aggregate_name=aggr_name,
        aggregate_variable_type="1",
        aggregate_function=aggr_function,
        aggregate_description="created in test",
        grouping_element=f"{grouping_element}",
    )
    print(json.dumps(dict(aggr_json)))
    aggr_body = aggregate_construct(
        aggregate_name=aggr_name,
        aggregate_json=json.dumps(dict(aggr_json)),
        aggregate_description="created in test",
    )
    create_resp: ResponseDto = create_aggregate_gen.create_aggr(
        aggr_body=aggr_body
    )
    aggregate: AggregateGetFullView = AggregateGetFullView.construct(
        **get_aggregate(super_user, create_resp.uuid).body)

    diagram_template = dict(create_temp_diagram_gen.create_template())
    temp_version_id = diagram_template["versionId"]
    diagram_id = diagram_template["diagramId"]
    letters = string.ascii_lowercase
    in_param_name = "input_var"
    in_aggr_param_name = "aggregate_var"
    out_param_name = "output_var"
    in_param_version_id = str(uuid.uuid4())
    in_aggr_param_version_id = str(uuid.uuid4())
    out_param_version_id = str(uuid.uuid4())
    in_param = variable_construct(array_flag=False,
                                  complex_flag=False,
                                  default_value=None,
                                  is_execute_status=None,
                                  order_num=0,
                                  param_name=in_param_name,
                                  parameter_type="in",
                                  parameter_version_id=in_param_version_id,
                                  type_id=1,
                                  parameter_id=in_param_version_id)
    out_param = variable_construct(array_flag=False,
                                   complex_flag=False,
                                   default_value=None,
                                   is_execute_status=None,
                                   order_num=0,
                                   param_name=out_param_name,
                                   parameter_type="out",
                                   parameter_version_id=out_param_version_id,
                                   type_id=1,
                                   parameter_id=out_param_version_id)
    in_aggr_param = variable_construct(array_flag=False,
                                       complex_flag=False,
                                       default_value=None,
                                       is_execute_status=None,
                                       order_num=0,
                                       param_name=in_aggr_param_name,
                                       parameter_type="in",
                                       parameter_version_id=in_aggr_param_version_id,
                                       type_id=1,
                                       parameter_id=in_aggr_param_version_id)
    params_response = update_diagram_parameters(
        super_user, temp_version_id, [variable_construct(),
                                      in_param,
                                      in_aggr_param,
                                      out_param])
    update_response: ResponseDto = params_response.body

    start_variable1 = variables_for_node("start", False, False, in_param_name, "1",
                                         str(in_param_version_id))
    start_variable2 = variables_for_node("start", False, False, in_aggr_param_name, "1",
                                         str(in_aggr_param_version_id))
    finish_variable = variables_for_node("finish", False, False, out_param_name, "1",
                                         str(out_param_version_id), None, None, None, None)
    node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id,
                                    [start_variable1, start_variable2])
    node_finish_raw = node_construct(1400, 202.22915649414062, "finish", temp_version_id,
                                     [finish_variable])
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)
    node_aggr_compute = aggregate_compute_node_construct(
        x=700, y=202.22915649414062, temp_version_id=temp_version_id
    )
    node_aggr_compute_response: ResponseDto = ResponseDto.construct(
        **create_node(super_user, node_aggr_compute).body
    )
    node_aggr_compute_id = node_aggr_compute_response.uuid
    link_s_a = link_construct(temp_version_id, node_start.uuid, node_aggr_compute_id)
    link_s_a_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_a).body)
    link_s_a_id = link_s_a_create_response.uuid
    link_a_f = link_construct(temp_version_id, node_aggr_compute_id, node_end.uuid)
    link_a_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_a_f).body)
    link_a_f_id = link_a_f_create_response.uuid
    aggr_for_node = aggregate_properties(aggregate_id=aggregate.aggregateId,
                                         aggregate_version_id=aggregate.versionId,
                                         diagram_aggregate_element=in_param.parameterName,
                                         is_used_in_diagram=True,
                                         aggregate_element_type_id="1",
                                         aggregate_function=aggregate_function)
    output_var_mapping = aggregate_compute_out_var(is_arr=False,
                                                   is_compl=False,
                                                   aggregate=aggr_for_node,
                                                   is_dict=False,
                                                   var_name=out_param.parameterName,
                                                   type_id="1")
    gr_element = grouping_element_map(aggregate_element=grouping_element,
                                      diagram_element=in_aggr_param.parameterName,
                                      full_path_value=grouping_element,
                                      simple_name_value=grouping_element,
                                      column=grouping_element)
    node_aggr_properties = aggregate_compute_properties(output_vars=[output_var_mapping],
                                                        retention_type=RetentionType.process,
                                                        retention_time_value=28,
                                                        retention_time_unit=RetentionTimeUnit.d,
                                                        grouping_elements=[gr_element])
    update_body = aggregate_compute_node_construct(x=700, y=202.22915649414062,
                                                   temp_version_id=temp_version_id,
                                                   properties=node_aggr_properties,
                                                   operation="update")
    update_node(super_user, node_id=node_aggr_compute_id, body=update_body,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=update_body.nodeTypeId,
                    properties=update_body.properties))
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variable])
    update_node(super_user, node_id=node_end.uuid, body=finish_up_body)
    diagram_name = "ag_diagram_aggregate_comp" + "_" + generate_string()
    diagram_description = 'diagram created in test'
    response_save: ResponseDto = ResponseDto.construct(
        **save_diagrams_gen.save_diagram(diagram_id=diagram_id,
                                         temp_version_id=temp_version_id,
                                         new_diagram_name=diagram_name,
                                         diagram_description=diagram_description).body)
    saved_version_id = response_save.uuid
    return {"node_start": node_start, "node_end": node_end,
            "node_aggr_compute": node_aggr_compute_response,
            "in_param": in_param, "in_aggr_param": in_aggr_param,
            "out_param": out_param, "template": diagram_template,
            "aggregate": aggregate, "grouping_element": grouping_element,
            "aggregate_function": aggr_function, "diagram_name": diagram_name,
            "saved_version_id": saved_version_id, "diagram_id": diagram_id}


@pytest.fixture()
def diagram_offer_save(super_user,
                       create_custom_types_gen,
                       create_code_gen,
                       create_offer_gen,
                       create_temp_diagram_gen):
    type_name = generate_attr_type_name(True, False, True, "")
    create_result: ResponseDto = create_custom_types_gen.create_type(
        type_name, [attribute_construct()]
    )
    custom_type_version_id = create_result.uuid
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
    offer_var = offer_variable_construct(variable_name=inp_var.variableName,
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
                            offer_variables=[offer_var])
    create_response: ResponseDto = create_offer_gen.create_offer(offer=offer)
    search_response: OfferFullViewDto = OfferFullViewDto.construct(
        **get_offer_info(super_user, create_response.uuid).body)

    diagram_template = dict(create_temp_diagram_gen.create_template())
    temp_version_id = diagram_template["versionId"]
    diagram_id = diagram_template["diagramId"]
    parameter_in_version_id = str(uuid.uuid4())
    parameter_out_version_id = str(uuid.uuid4())
    new_var_in = variable_construct(array_flag=False,
                                    complex_flag=False,
                                    default_value=None,
                                    is_execute_status=None,
                                    order_num=1,
                                    param_name="in_int_variable",
                                    parameter_type="in",
                                    parameter_version_id=parameter_in_version_id,
                                    type_id="1",
                                    parameter_id=parameter_in_version_id)
    new_var_out = variable_construct(array_flag=True,
                                     complex_flag=True,
                                     default_value=None,
                                     is_execute_status=None,
                                     order_num=2,
                                     param_name="out_cmplx_var",
                                     parameter_type="out",
                                     parameter_version_id=parameter_out_version_id,
                                     type_id=custom_type_version_id,
                                     parameter_id=parameter_out_version_id)
    params_response = update_diagram_parameters(super_user,
                                                temp_version_id,
                                                [variable_construct(),
                                                 new_var_in,
                                                 new_var_out])
    update_response: ResponseDto = params_response.body

    start_variables = variables_for_node("start", False, False, new_var_in.parameterName, new_var_in.typeId,
                                         parameter_in_version_id, None, None, None, None)
    finish_variables = variables_for_node("finish", True, True, new_var_out.parameterName, new_var_out.typeId,
                                          parameter_out_version_id, None, None, None, None)
    node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id, [start_variables])
    node_offer_raw = offer_node_construct(x=700, y=202.22915649414062, temp_version_id=temp_version_id)
    node_finish_raw = node_construct(1400, 202.22915649414062, "finish", temp_version_id, [finish_variables])
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)
    node_offer: ResponseDto = ResponseDto.construct(**create_node(super_user, node_offer_raw).body)
    link_s_o = link_construct(temp_version_id, node_start.uuid, node_offer.uuid)
    link_s_o_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_o).body)
    link_s_o_id = link_s_o_create_response.uuid
    link_o_f = link_construct(temp_version_id, node_offer.uuid, node_end.uuid)
    link_o_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_o_f).body)
    link_o_f_id = link_o_f_create_response.uuid
    offer_var = offer_variable(var_id=search_response.offerVariables[0]["id"],
                               value=5)
    output_var_mapping = variables_for_node(node_type="offer_output",
                                            is_arr=True,
                                            is_compl=True,
                                            is_dict=False,
                                            type_id=complex_type.versionId,
                                            node_variable=out_var.variableName,
                                            name=new_var_out.parameterName)
    node_var_mapping = variables_for_node(node_type="offer_mapping",
                                          is_arr=False,
                                          is_compl=False,
                                          is_dict=False,
                                          type_id="1",
                                          node_variable=inp_var.variableName,
                                          name=new_var_in.parameterName)
    node_offer_properties = offer_properties(offer_id=search_response.id,
                                             offer_version_id=search_response.versionId,
                                             offer_variables=[offer_var],
                                             node_variables_mapping=[node_var_mapping],
                                             output_variable_mapping=output_var_mapping)
    update_body = offer_node_construct(x=700, y=202.22915649414062,
                                       node_id=str(node_offer.uuid),
                                       temp_version_id=temp_version_id,
                                       properties=node_offer_properties,
                                       operation="update")
    update_node(super_user, node_id=node_offer.uuid, body=update_body,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=update_body.nodeTypeId,
                    properties=update_body.properties))
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variables])
    update_node(super_user, node_id=node_end.uuid, body=finish_up_body)

    new_diagram_name = "diagram" + "_" + generate_diagram_name_description(8, 1)["rand_name"]
    diagram_description = 'diagram created in test'
    diagram_data = DiagramCreateNewVersion(diagramId=uuid.UUID(diagram_id),
                                           versionId=temp_version_id,
                                           errorResponseFlag=False,
                                           objectName=new_diagram_name,
                                           diagramDescription=diagram_description)
    response_save = save_diagram(super_user, body=diagram_data)
    create_result: ResponseDto = ResponseDto.construct(**response_save.body)
    saved_version_id = create_result.uuid

    yield {"node_start": node_start, "node_end": node_end, "node_offer": node_offer,
           "param_in": new_var_in, "param_out": new_var_out, "template": diagram_template,
           "create_result": create_result, "diagram_data": diagram_data,
           "complex_type": complex_type, "script": script_view, "offer": search_response,
           "script_inp_var": inp_var, "script_out_var": out_var, "diagram_name": new_diagram_name,
           "saved_version_id": saved_version_id, "diagram_id": diagram_id}


@pytest.fixture()
def create_standart_communication_channel(super_user,
                                          create_python_code_int_vars,
                                          create_communication_gen):
    script_view: ScriptFullView = create_python_code_int_vars["code_view"]
    inp_var: ScriptVariableViewWithoutVersionIdDto = create_python_code_int_vars["inp_var"]
    channel_name = "channel_" + generate_string()
    var = communication_var_construct(variable_name="comm_v",
                                      script_var_name=inp_var.variableName,
                                      primitive_type_id=inp_var.primitiveTypeId,
                                      data_source_type=DataSourceType1.USER_INPUT)
    comm = communication_construct(communication_channel_name=channel_name,
                                   script_version_id=script_view.versionId,
                                   communication_variables=[var],
                                   description="made_in_test")
    create_response: ResponseDto = create_communication_gen.create_communication_channel(
        communication_channel_body=comm)
    communication_view = CommunicationChannelFullViewDto.construct(
        **get_communication_channel(super_user, create_response.uuid).body)

    yield {"communication": communication_view, "script": script_view}

    try:
        delete_communication(super_user, communication_view.versionId)
    except:
        print("запрос на удаление коммуникации не исполнен")


@pytest.fixture()
def all_primitive_types_basic_value():
    return {"0": 1.1,
            "1": 1,
            "2": 'hello world',
            "3": 1641934800,
            "4": True,
            "5": 1641979545050,
            "6": 14584,
            "7": 11111111111111111}


@pytest.fixture()
def create_custom_custom_attributes(super_user, all_primitive_types_basic_value, request):
    """
    Фикстура для создания n-кол-ва справочников, принимает аргументы через
    @pytest.mark.create_custom_custom_attributes_data()
    принимает числовые аргументы в соответствии с примитивными типами и специальный аргумент(для создания всех типов
    сразу)
    """
    type_marker = request.node.get_closest_marker("dict_types")
    dicts: dict[str, CustomAttributeDictionaryFullView] = {}
    if type_marker is not None:
        marker_value: list[str] = type_marker.args[0]
        if marker_value[0] == "all_types":
            # добавить справочники всех типов, ключи - типы данных
            dict_types = (0, 1, 2, 3, 4, 5, 6, 7)
            for d_type in dict_types:
                value = dict_value_construct(dict_value=f"{all_primitive_types_basic_value[str(d_type)]}",
                                             dict_value_display_name="")
                custom_attr = dict_construct(
                    dict_name="ag_test_dict_" + generate_string(),
                    dict_value_type_id=str(d_type),
                    values=[value])
                create_result: ResponseDto = ResponseDto.construct(
                    **create_custom_attribute(super_user, body=custom_attr).body)
                dict_info: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
                    **get_custom_attribute(super_user, dict_id=create_result.uuid).body)
                dicts[f"{d_type}"] = dict_info
        else:
            for m_value in marker_value:
                d_type = m_value[-1]
                value = dict_value_construct(dict_value=f"{all_primitive_types_basic_value[d_type]}",
                                             dict_value_display_name="")
                custom_attr = dict_construct(
                    dict_name="ag_test_dict_" + generate_string(),
                    dict_value_type_id=d_type,
                    values=[value])
                create_result: ResponseDto = ResponseDto.construct(
                    **create_custom_attribute(super_user, body=custom_attr).body)
                dict_info: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
                    **get_custom_attribute(super_user, dict_id=create_result.uuid).body)
                dicts[m_value] = dict_info
    else:
        # добавить дефолтный справочник int_dict
        d_type = "1"
        value = dict_value_construct(dict_value="1",
                                     dict_value_display_name="")
        custom_attr = dict_construct(
            dict_name="ag_test_dict_" + generate_string(),
            dict_value_type_id=d_type,
            values=[value])
        create_result: ResponseDto = ResponseDto.construct(
            **create_custom_attribute(super_user, body=custom_attr).body)
        dict_info: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
            **get_custom_attribute(super_user, dict_id=create_result.uuid).body)
        dicts["int_dict"] = dict_info

    yield dicts

    for d in dicts.values():
        d_id = d.id
        try:
            delete_custom_attribute(super_user, dict_id=d_id)
        except:
            print("can't delete dict")
