from sdk.Admin.steps.admin_steps import (
    create_realm_user,
    search_user,
    reset_password,
    delete_realm_user,
    get_users,
    get_client,
    get_client_role,
    add_role_to_user,
)
from sdk.clients.api import ApiClient
from sdk.user import User
from common.generators import generate_username
import pytest


@pytest.fixture(scope="session")
def rbac_user(endpoint, keycloak_client, admin, email, auth, request):
    response = create_realm_user(admin, email)
    user_id = search_user(admin, email)
    client_uuid = get_client(admin, client_id=keycloak_client)
    role = get_client_role(
        admin,
        user_id=user_id[0]["id"],
        client_uuid=client_uuid,
        role_name=request.param,
    )
    add_role_to_user(
        admin, user_id=user_id[0]["id"], client_uuid=client_uuid, body=[role]
    )
    set_password = reset_password(admin, user_id[0]["id"])
    user = User(username=email, password="password")
    user.add_api_client(client=ApiClient(host=auth))
    user.with_api.authorize()
    user.with_api.client._host = endpoint

    yield user

    delete_realm_user(admin, user_id[0]["id"])
