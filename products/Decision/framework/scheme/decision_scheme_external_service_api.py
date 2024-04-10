from products.Decision.framework.model import ExternalServiceCreateDto, ExternalServiceUpdateDto, \
    ExternalServiceCreateUserVersionDto, ExternalServiceUpdateUserVersionDto
from sdk.user.interface.api.request import ApiRequest


class DecisionExternalServiceApi:

    @staticmethod
    def post_services(*, body: ExternalServiceCreateDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/services',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_services(*, service_id: str, body: ExternalServiceUpdateDto) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/services/{service_id}',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_services_user_version(*, service_id: str, body: ExternalServiceCreateUserVersionDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/services/{service_id}/create/userVersion',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_services_user_version(*, version_id: str, body: ExternalServiceUpdateUserVersionDto) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/services/{version_id}/updateUserVersion',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_external_service(service_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/services/{service_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_external_service(service_id: str) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/services/{service_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_services(query) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/services',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_external_service_versions(service_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/services/{service_id}/versions',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_tech_service(query) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/services/techService',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_external_service_variables(service_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/services/{service_id}/variables',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )