from sdk.Admin.scheme.admin_scheme import Adminapi
from sdk.user import User


def create_group(user: User, body: dict):
    return user.with_api.send(Adminapi.create_group(body=body))


def create_realm_user(user: User, email: str = "", groups=None, name: str = None):
    if groups is None:
        groups = []

    body = {
        "enabled": "true",
        "attributes": {},
        "groups": groups,
        "emailVerified": "true",
        "username": email
    }

    if name is not None:
        body["firstName"] = name
        body["lastName"] = name

    response = user.with_api.send(Adminapi.create_realm_user(body=body))
    return response.body


def delete_group(user: User, group_id):
    return user.with_api.send(Adminapi.delete_group(group_id=group_id))


def delete_realm_user(user: User, user_id):
    response_delete = user.with_api.send(Adminapi.delete_realm_user(user_id=user_id))
    return response_delete


def update_group(user: User, group_id: str, body: dict):
    return user.with_api.send(Adminapi.put_group(body=body, group_id=group_id))


def search_group(user: User, query: dict):
    return user.with_api.send(Adminapi.search_group(query=query))


def search_user(user: User, email):
    query = {
        'briefRepresentation': True,
        'first': 0,
        'max': 20,
        'search': email
    }
    response = user.with_api.send(Adminapi.search_user(query=query))
    return response.body


def get_users(user: User):
    query = {
        'briefRepresentation': True,
        # 'first': 0,
        # 'max': 1000
    }
    response = user.with_api.send(Adminapi.search_user(query=query))
    return response.body


def get_client(user: User, client_id: str):
    client_uuid = None
    query = {
        'search': True,
        # 'first': 0,
        'max': 20
    }
    client_list = user.with_api.send(Adminapi.get_realm_clients(query=query)).body
    for client in client_list:
        if client["clientId"] == client_id:
            client_uuid = client["id"]
            break
    return client_uuid


def get_client_role(user: User, user_id: str, client_uuid: str, role_name: str):
    wanted_role = None
    role_list = user.with_api.send(Adminapi.get_client_available_roles(
        user_id=user_id, client_uuid=client_uuid)).body
    for role in role_list:
        if role["name"] == role_name:
            wanted_role = role
            break
    return wanted_role


def get_group_available_role(user: User, group_id: str, query: dict):
    return user.with_api.send(Adminapi.get_group_available_roles(group_id=group_id, query=query))


def reset_password(user: User, user_id):
    body = {
        "type": "password",
        "value": "password",
        "temporary": False
    }
    response = user.with_api.send(Adminapi.reset_user_password(body=body, user_id=user_id))
    return response


def add_role_to_group(user: User, group_id, client_uuid, body: list):
    return user.with_api.send(Adminapi.post_role_mappings_to_group(group_id=group_id,
                                                                   client_uuid=client_uuid,
                                                                   body=body))


def add_role_to_user(user: User, user_id, client_uuid, body: list):
    return user.with_api.send(Adminapi.post_role_mappings(user_id=user_id,
                                                          client_uuid=client_uuid,
                                                          body=body))
