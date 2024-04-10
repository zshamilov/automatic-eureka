from products.Decision.framework.model import PythonEnvironmentUpdateDto, PythonEnvironmentCreateDto
from sdk.user.interface.api.request import ApiRequest


class PythonEnvironmentApi:

    @staticmethod
    def get_python_environments_version(*, version_id) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/script/python/environment/{version_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_python_environments(*, version_id, body: PythonEnvironmentUpdateDto) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/script/python/environment/{version_id}',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_python_environments(*, body: PythonEnvironmentCreateDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/script/python/environment',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_python_environments_txt(*, query: dict) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/script/python/environment/requirementsTxt',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_python_environments(*, version_id) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/script/python/environment/{version_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_python_environments(*, query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/script/python/environment',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_python_environment_versions(*, version_id) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/script/python/environment/{version_id}/versions',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )
