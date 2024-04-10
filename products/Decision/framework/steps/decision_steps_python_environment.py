import base64

from products.Decision.framework.model import PythonEnvironmentCreateDto, PythonEnvironmentUpdateDto, \
    PythonEnvironmentShortInfoDto
from products.Decision.framework.scheme.decision_schema_python_environment import PythonEnvironmentApi
from sdk.user import User


def create_python_environment(user: User, body: PythonEnvironmentCreateDto):
    return user.with_api.send(PythonEnvironmentApi.post_python_environments(body=body))


def update_python_environment(user: User, version_id, body: PythonEnvironmentUpdateDto):
    return user.with_api.send(PythonEnvironmentApi.put_python_environments(version_id=version_id, body=body))


def delete_python_environment(user: User, version_id):
    return user.with_api.send(PythonEnvironmentApi.delete_python_environments(version_id=version_id))


def get_environment_versions_by_version_id(user: User, version_id):
    return user.with_api.send(PythonEnvironmentApi.get_python_environment_versions(version_id=version_id))


def get_environment_python_version(user: User, version_id):
    return user.with_api.send(PythonEnvironmentApi.get_python_environments_version(version_id=version_id))


def get_environments_python_list(user: User, name=None):
    envs = []
    query = None
    if name is None:
        str_query = '{"filters":[],"sorts":[],"page":1,"size":999}'
        q_enc = base64.b64encode(bytes(str_query, "utf-8"))
        query = {"searchRequest": q_enc.decode("utf-8")}
    else:
        str_query = f'{{"filters":[],"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"searchBy":"{name}","page":1,"size":20}}'
        q_enc = base64.b64encode(bytes(str_query, "utf-8"))
        query = {"searchRequest": q_enc.decode("utf-8")}
    response = user.with_api.send(PythonEnvironmentApi.get_python_environments(query=query))
    if response.status != 204:
        for env in response.body["content"]:
            envs.append(PythonEnvironmentShortInfoDto.construct(**env))

    return envs
