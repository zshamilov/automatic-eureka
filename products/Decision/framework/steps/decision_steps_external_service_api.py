from typing import Literal

from products.Decision.framework.model import ExternalServiceFullViewDto, ExternalServiceVariableFullViewDto
from products.Decision.framework.scheme.decision_scheme_external_service_api import DecisionExternalServiceApi
from sdk.user import User


def create_service(user: User, body):
    return user.with_api.send(DecisionExternalServiceApi.post_services(body=body))


def update_service(user: User, service_id, body):
    return user.with_api.send(DecisionExternalServiceApi.put_services(service_id=service_id, body=body))


def create_service_user_version(user: User, service_id, body):
    return user.with_api.send(DecisionExternalServiceApi.post_services_user_version(service_id=service_id, body=body))


def update_service_user_version(user: User, version_id, body):
    return user.with_api.send(DecisionExternalServiceApi.put_services_user_version(version_id=version_id, body=body))


def find_service_by_id(user: User, service_id):
    return user.with_api.send(DecisionExternalServiceApi.get_external_service(service_id=service_id))


def get_tech_service(user: User, node_type: Literal["OFFER_STORAGE_WRITE", "COMMUNICATION_HUB",
                                                    "COMMUNICATION_HUB_READ", "OFFER_STORAGE_READ_BY_CLIENT_ID",
                                                    "OFFER_STORAGE_READ_BY_OFFER_ID", "POLICY_READ"]):
    query = {"techTypes": node_type}
    return user.with_api.send(DecisionExternalServiceApi.get_tech_service(query=query))


def find_service_var_by_type(user: User, service_id, var_type) -> ExternalServiceVariableFullViewDto:
    service: ExternalServiceFullViewDto = ExternalServiceFullViewDto.construct(
        **user.with_api.send(DecisionExternalServiceApi.get_external_service(service_id=service_id)).body)
    var = None
    for variable in service.variables:
        if variable["variableType"] == var_type:
            var = ExternalServiceVariableFullViewDto.construct(**variable)
    return var


def delete_service(user: User, service_id):
    return user.with_api.send(DecisionExternalServiceApi.delete_external_service(service_id=service_id))


def services_list(user: User, query=None):
    if query is None:
        query = {
            "searchRequest": "eyJmaWx0ZXJzIjpbXSwic29ydHMiOltdLCJzZWFyY2hCeSI6IiIsInBhZ2UiOjEsInNpemUiOjEwMDAwMH0="}
    return user.with_api.send(DecisionExternalServiceApi.get_services(query=query))


def service_versions_list(user: User, service_id):
    return user.with_api.send(DecisionExternalServiceApi.get_external_service_versions(service_id=service_id))


def service_variables_list(user: User, service_id):
    return user.with_api.send(DecisionExternalServiceApi.get_external_service_variables(service_id=service_id))
