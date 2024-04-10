from products.Decision.framework.model import EnvironmentCreateDto, EnvironmentUpdateDto
from sdk.user.interface.api.request import ApiRequest


class DecisionEnvironmentsApi:

    @staticmethod
    def post_environments(*, body: EnvironmentCreateDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/environments',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_environment(*, environment_id) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/environments/{environment_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_environment(*, environment_id, body: EnvironmentUpdateDto) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/environments/{environment_id}',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_environment(*, environment_id) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/environments/{environment_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_environments() -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/environments',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )
