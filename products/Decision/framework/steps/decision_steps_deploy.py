import base64

from products.Decision.framework.model import DeployViewDto
from products.Decision.framework.scheme.decision_scheme_deploy import DecisionDeploy
from sdk.user import User
from sdk.user.interface.api.response import ApiResponse


def deploy_list(user: User, query=None):
    if query is None:
        query = {
            "searchRequest": "eyJmaWx0ZXJzIjpbXSwic29ydHMiOltdLCJzZWFyY2hCeSI6IiIsInBhZ2UiOjEsInNpemUiOjEwMDAwMH0="}
    return user.with_api.send(DecisionDeploy.get_deploy(query=query))


def deploy_list_by_name_resp(user: User, diagram_name) -> ApiResponse:
    filt = f'{{"filters":[],"sorts":[],"searchBy":"{diagram_name}","page":1,"size":20}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    return user.with_api.send(DecisionDeploy.get_deploy(query={"searchRequest": list_query.decode(
        "utf-8")}))


def deploy_list_by_name(user: User, diagram_name):
    model_l = []
    filt = f'{{"filters":[],"sorts":[],"searchBy":"{diagram_name}","page":1,"size":20}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    deploy_resp = user.with_api.send(DecisionDeploy.get_deploy(query={"searchRequest": list_query.decode(
        "utf-8")}))
    if deploy_resp.status != 204:
        deploy_l = deploy_resp.body["content"]
        for deploy in deploy_l:
            model_l.append(DeployViewDto.construct(**deploy))

    return model_l


def deploy_list_by_status(user: User, deploy_status: str):
    filt = f'{{"filters":[{{"columnName":"deployStatus","operator":"IN","values":["{deploy_status}"]}}],"sorts":[{{' \
           f'"direction":"DESC","columnName":"changeDt"}}],"page":1,"size":20}} '
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    response = user.with_api.send(DecisionDeploy.get_deploy(query={"searchRequest": list_query.decode(
        "utf-8")}))
    if response.status == 204:
        return []
    else:
        deploys = response.body["content"]
        return deploys


def deploy_list_by_username(user: User, username: str):
    filt = '{"filters":[],"sorts":[{"direction":"DESC","columnName":"changeDt"}],"page":1,"size":200}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    response = user.with_api.send(DecisionDeploy.get_deploy(query={"searchRequest": list_query.decode("utf-8")}))
    deploys_unfiltered = (response.body.get("content") or [])
    deploys = list(filter(lambda deploy: deploy["createUser"] == username, deploys_unfiltered))
    return deploys


def check_deploy_status(user: User, diagram_name, diagram_id, status: str):
    status_expected = False
    filt = f'{{"filters":[],"sorts":[],"searchBy":"{diagram_name}","page":1,"size":20}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    deploys = user.with_api.send(DecisionDeploy.get_deploy(query={"searchRequest": list_query.decode(
        "utf-8")})).body["content"]
    for deploy in deploys:
        if (
                deploy["diagram"]["diagramId"] == diagram_id
                and deploy["deployStatus"] == status
        ):
            status_expected = True
            break
    return status_expected


def find_deploy_id(user: User, diagram_name, diagram_id, sorting=False):
    deploy_id = None
    if sorting:
        filt = f'{{"filters":[],"sorts":[{{"direction":"DESC","columnName":"changeDt"}}],"searchBy":"{diagram_name}",' \
               f'"page":1,"size":20}}'
    else:
        filt = f'{{"filters":[],"sorts":[],"searchBy":"{diagram_name}","page":1,"size":20}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    deploys = user.with_api.send(DecisionDeploy.get_deploy(query={"searchRequest": list_query.decode(
        "utf-8")})).body["content"]
    for deploy in deploys:
        if deploy["diagram"]["diagramId"] == diagram_id and deploy["deployStatus"] == "READY_FOR_DEPLOY":
            deploy_id = deploy["deployId"]
            break
    return deploy_id


def deploy_config(user: User, deploy_version_id: str):
    return user.with_api.send(DecisionDeploy.get_deploy_config(deploy_ids=[deploy_version_id])).body[0]


def deploy_configs(user: User, deploy_ids: list[str]):
    return user.with_api.send(DecisionDeploy.get_deploy_config(deploy_ids=deploy_ids)).body


def find_deploy_with_children(user: User, diagram_name, diagram_id):
    deploy_id = None
    child_deploys = []
    filt = f'{{"filters":[],"sorts":[],"searchBy":"{diagram_name}","page":1,"size":20}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    deploys = user.with_api.send(DecisionDeploy.get_deploy(query={"searchRequest": list_query.decode(
        "utf-8")})).body["content"]
    for deploy in deploys:
        if deploy["diagram"]["diagramId"] == diagram_id and deploy["deployStatus"] == "READY_FOR_DEPLOY":
            deploy_id = deploy["deployId"]
            for children in deploy["childDeploys"]:
                child_deploys.append(children["deployId"])
            break
    return {"deploy_id": deploy_id, "child_deploys": child_deploys}


def deploy_delete(user: User, ids: list[str]):
    return user.with_api.send(DecisionDeploy.delete_deploy_delete(ids=ids)).body
