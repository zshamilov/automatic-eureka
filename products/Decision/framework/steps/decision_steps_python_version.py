from products.Decision.framework.model import PythonVersionFullViewDto
from products.Decision.framework.scheme.decision_scheme_python_version import PythonVersionApi
from sdk.user import User


def create_python_version(user: User, body: [PythonVersionFullViewDto]):
    return user.with_api.send(PythonVersionApi.post_python_version(body=body))


def get_python_version_id(user: User, id):
    return user.with_api.send(PythonVersionApi.get_python_version_id(id=id))


def get_python_version_list(user: User):
    version_list = []
    response = user.with_api.send(PythonVersionApi.get_python_version())
    if response.status != 204:
        for version in response.body:
            version_list.append(PythonVersionFullViewDto.construct(**version))
    return version_list



