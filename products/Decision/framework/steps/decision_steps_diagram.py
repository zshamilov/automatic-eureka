import base64
import time
from typing import Literal

from products.Decision.framework.model import DiagramInOutParameterFullViewDto, DeployViewDto, DeployStatus, \
    DeployConfigurationFullDto, DiagramParameterDto, ParameterType
from products.Decision.framework.scheme.decision_scheme_deploy import DecisionDeploy
from products.Decision.framework.scheme.decision_scheme_diagram import DecisionDiagram
from products.Decision.framework.steps.decision_steps_locking import locking_list, delete_locking
from sdk.user import User


def diagrams_list(user: User, query=None):
    filt = '{"filters":[],"sorts":[],"searchBy":"","page":1,"size":30}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    if query is None:
        query = {
            "searchRequest": list_query.decode("utf-8")}
    return user.with_api.send(DecisionDiagram.get_diagrams(query=query))


def diagram_list_by_name(user: User, name: str):
    filt = f'{{"filters":[],"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"searchBy":"{name}","page":1,"size":999}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    response = user.with_api.send(DecisionDiagram.get_diagrams(query={"searchRequest": list_query.decode(
        "utf-8")}))
    if response.status == 204:
        return []
    else:
        diagrams = response.body["content"]
        return diagrams


def create_template(user: User, catalog_id=None):
    if catalog_id is not None:
        query = {"catalogId": catalog_id}
    else:
        query = {}
    return user.with_api.send(DecisionDiagram.create_diagram_template(query=query))


def create_as_new(user: User, body):
    return user.with_api.send(DecisionDiagram.create_diagram_as_new(body=body))


def create_user_version(user: User, body):
    return user.with_api.send(DecisionDiagram.post_diagrams_user_version(body=body))


def create_template_from_latest(user: User, version_id):
    return user.with_api.send(DecisionDiagram.create_template_from_latest(version_id=version_id))


def rename_diagram(user: User, version_id, body):
    return user.with_api.send(DecisionDiagram.rename_diagram_by_id(version_id=version_id, body=body))


def save_diagram(user: User, body):
    return user.with_api.send(DecisionDiagram.post_diagrams(body=body))


def get_diagram_by_version(user: User, key: str, mode: Literal["READ", "WRITE"] = "READ"):
    query = {"mode": mode}
    return user.with_api.send(DecisionDiagram.get_diagram_by_id(version_id=key, query=query))


def update_diagram_parameters(user: User, version_id: str, in_out_params: [DiagramInOutParameterFullViewDto],
                              inner_vars=None):
    # if inner_vars is None:
    #     inner_vars = []
    body = DiagramParameterDto.construct(inOutParameters=in_out_params,
                                         innerVariables=inner_vars)
    return user.with_api.send(DecisionDiagram.put_diagram_parameters(version_id=version_id,
                                                                     body=body))


def get_diagram_parameters(user: User, version_id: str):
    return user.with_api.send(DecisionDiagram.get_diagram_parameters(version_id=version_id))


def get_filtered_variables(user: User, diagram_version_id,
                           variable_type: Literal[
                               "внешние", "внутренние", "входные", "выходные", "сквозные"] = "внешние"):
    variables: DiagramParameterDto = DiagramParameterDto.construct(**get_diagram_parameters(user,
                                                                                            diagram_version_id).body)
    filtered_variables = []
    if variable_type == "внешние":
        filtered_variables = variables.inOutParameters
    elif variable_type == "внутренние":
        filtered_variables = variables.innerVariables
    elif variable_type == "входные":
        filtered_variables = list(filter(lambda var: var["parameterType"] == ParameterType.IN.value,
                                         variables.inOutParameters))
    elif variable_type == "выходные":
        filtered_variables = list(filter(lambda var: var["parameterType"] == ParameterType.OUT.value,
                                         variables.inOutParameters))
    elif variable_type == "сквозные":
        filtered_variables = list(filter(lambda var: var["parameterType"] == ParameterType.IN_OUT.value,
                                         variables.inOutParameters))

    return filtered_variables


def delete_diagram(user: User, key: str):
    time.sleep(2)
    return user.with_api.send(DecisionDiagram.delete_diagram_by_id(diagram_id=key))


def delete_diagram_check_locking(user: User, key: str):
    vers_id = key
    diagram_data = get_diagram_by_version(user, vers_id).body
    diagram_name = diagram_data["objectName"]
    lock_list = locking_list(user, diagram_name=diagram_name)
    for lock in lock_list:
        if lock.objectName == diagram_name and str(lock.objectId) == diagram_data["diagramId"]:
            delete_locking(user, object_id=lock.objectId)
    time.sleep(2)
    return user.with_api.send(DecisionDiagram.delete_diagram_by_id(diagram_id=key))


def put_diagram_submit(user: User, diagram_id, deploy_type=None):
    if deploy_type is None:
        deploy_type = "REALTIME"
    return user.with_api.send(DecisionDiagram.put_diagram_submit(diagram_id=diagram_id, deploy_type=deploy_type))


def delete_diagram_template(user: User, diagram_id: str):
    return user.with_api.send(DecisionDiagram.delete_diagram_template(diagram_id=diagram_id))


def get_diagram_versions(user: User, diagram_id: str):
    return user.with_api.send(DecisionDiagram.get_diagram_versions_by_id(diagram_id=diagram_id))


def start_deploy_async(user: User, deploy_id, environment_id, body: list[DeployConfigurationFullDto]):
    filt = f'{{"filters":[],"sorts":[],"searchBy":"{deploy_id}","page":1,"size":20}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    deploy: DeployViewDto = DeployViewDto.construct(**user.with_api.send(
        DecisionDeploy.get_deploy(query={"searchRequest": list_query.decode(
            "utf-8")})).body["content"][0])
    deploy_resp = user.with_api.send(DecisionDiagram.post_deploy(environment_id=environment_id, body=body))
    if deploy_resp.status == 201:
        for i in range(60):
            deploy = DeployViewDto.construct(**user.with_api.send(
                DecisionDeploy.get_deploy(query={"searchRequest": list_query.decode(
                    "utf-8")})).body["content"][0])
            if deploy.deployStatus == DeployStatus.DEPLOYED or deploy.deployStatus == DeployStatus.ERROR:
                break
            else:
                time.sleep(5)
    return deploy


def stop_deploy(user: User, deploy_id):
    return user.with_api.send(DecisionDiagram.post_undeploy(deploy_id=deploy_id))


def get_diagrams_related_to_object(user: User, object_type, object_id):
    return user.with_api.send(
        DecisionDiagram.get_related_diagram_with_obj(object_type=object_type, object_id=object_id))


def validate_diagram(user: User, version_id):
    return user.with_api.send(DecisionDiagram.post_diagram_validate(version_id=version_id))


def start_multiple_diagram_deploy(user: User, deploy_ids, environment_id, body: list[DeployConfigurationFullDto]):
    list_queries = []
    deploys = []
    for deploy_id in deploy_ids:
        list_queries.append(base64.b64encode(bytes(
            f'{{"filters":[],"sorts":[],"searchBy":"{deploy_id}","page":1,"size":20}}'
            , 'utf-8')))
    deploy_resp = user.with_api.send(DecisionDiagram.post_deploy(environment_id=environment_id, body=body))
    if deploy_resp.status == 201:
        for i in range(60):
            for list_query in list_queries:
                deploys.append(DeployViewDto.construct(**user.with_api.send(
                    DecisionDeploy.get_deploy(query={"searchRequest": list_query.decode(
                        "utf-8")})).body["content"][0]))
            if all(deploy.deployStatus == DeployStatus.ERROR or
                   deploy.deployStatus == DeployStatus.DEPLOYED
                   for deploy in deploys
                   ):
                break
            else:
                time.sleep(5)
    return deploys
