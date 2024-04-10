from products.Decision.framework.model import PythonVersionFullViewDto
from sdk.user.interface.api.request import ApiRequest


class PythonVersionApi:

    @staticmethod
    def get_python_version() -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/script/python/version',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_python_version_id(*, id) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/script/python/version/{id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_python_version(*, body: [PythonVersionFullViewDto]) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/script/python/version',
            query={},
            body=body,
            headers={'Content-Type': 'application/json'}
        )
