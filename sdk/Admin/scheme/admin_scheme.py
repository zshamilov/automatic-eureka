from sdk.user.interface.api.request import ApiRequest
import os
basic_headers = {'Content-Type': 'application/json'}


class Adminapi:
    @staticmethod
    def create_group(*, body: dict) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/admin/realms/{os.getenv("AUTH_REALM")}/groups',
            query={},
            body=body,
            headers=basic_headers,
        )

    @staticmethod
    def create_realm_user(*, body: dict) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/admin/realms/{os.getenv("AUTH_REALM")}/users',
            query={},
            body=body,
            headers=basic_headers,
        )

    @staticmethod
    def delete_group(*, group_id: str) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/admin/realms/{os.getenv("AUTH_REALM")}/groups/{group_id}',
            query={},
            body={},
            headers=basic_headers,
        )

    @staticmethod
    def delete_realm_user(*, user_id: str) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/admin/realms/{os.getenv("AUTH_REALM")}/users/{user_id}',
            query={},
            body={},
            headers=basic_headers,
        )

    @staticmethod
    def put_group(*, group_id: str, body: dict) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/admin/realms/{os.getenv("AUTH_REALM")}/groups/{group_id}',
            query={},
            body=body,
            headers=basic_headers,
        )

    @staticmethod
    def search_group(*, query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/admin/realms/{os.getenv("AUTH_REALM")}/groups',
            query=query,
            body={},
            headers=basic_headers,
        )

    @staticmethod
    def search_user(*, query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/admin/realms/{os.getenv("AUTH_REALM")}/users',
            query=query,
            body={},
            headers=basic_headers,
        )

    @staticmethod
    def reset_user_password(*, body: dict, user_id: str) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/admin/realms/{os.getenv("AUTH_REALM")}/users/{user_id}/reset-password',
            query={},
            body=body,
            headers=basic_headers,
        )

    @staticmethod
    def get_realm_clients(*, query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/admin/realms/{os.getenv("AUTH_REALM")}/clients',
            query=query,
            body={},
            headers=basic_headers,
        )

    @staticmethod
    def get_client_available_roles(*, user_id: str, client_uuid: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/admin/realms/{os.getenv("AUTH_REALM")}/users/{user_id}/role-mappings/clients/{client_uuid}/available',
            query={},
            body={},
            headers=basic_headers,
        )

    @staticmethod
    def get_group_available_roles(*, group_id: str, query: {}) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/admin/realms/{os.getenv("AUTH_REALM")}/ui-ext/available-roles/groups/{group_id}',
            query=query,
            body={},
            headers=basic_headers,
        )

    @staticmethod
    def post_role_mappings(*, user_id: str, client_uuid: str, body) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/admin/realms/{os.getenv("AUTH_REALM")}/users/{user_id}/role-mappings/clients/{client_uuid}',
            query={},
            body=body,
            headers=basic_headers,
        )

    @staticmethod
    def post_role_mappings_to_group(*, group_id: str, client_uuid: str, body: list) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/admin/realms/{os.getenv("AUTH_REALM")}/groups/{group_id}/role-mappings/clients/{client_uuid}',
            query={},
            body=body,
            headers=basic_headers,
        )
