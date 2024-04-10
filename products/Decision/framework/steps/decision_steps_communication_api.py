import base64

from products.Decision.framework.model import CommunicationChannelCatalogShortInfoDto
from products.Decision.framework.scheme.decision_scheme_communication_api import DecisionCommunication
from sdk.user import User


def create_communication(user: User, body):
    return user.with_api.send(DecisionCommunication.post_communication(body=body))


def create_channel_user_version(user: User, version_id, body):
    return user.with_api.send(DecisionCommunication.post_communication_user_vers(
        version_id=version_id, body=body))


def update_channel(user: User, version_id, body):
    return user.with_api.send(DecisionCommunication.put_communication(
        version_id=version_id, body=body))


def delete_communication(user: User, version_id):
    return user.with_api.send(DecisionCommunication.delete_communication(version_id=version_id))


def get_communication_channel(user: User, version_id):
    return user.with_api.send(DecisionCommunication.get_communication(version_id=version_id))


def get_channel_variables(user: User, version_id):
    return user.with_api.send(DecisionCommunication.get_communication_variables(version_id=version_id))


def get_channel_versions(user: User, communication_channel_id):
    return user.with_api.send(DecisionCommunication.get_communication_versions(
        communication_channel_id=communication_channel_id))


def get_channel_list(user: User, query=None):
    if query is None:
        query = {
            "searchRequest": "eyJmaWx0ZXJzIjpbXSwic29ydHMiOltdLCJzZWFyY2hCeSI6IiIsInBhZ2UiOjEsInNpemUiOjEwMDAwMH0="}
    return user.with_api.send(DecisionCommunication.get_communications(query=query))


def get_channel_list_content(user: User, query=None):
    if query is None:
        query = {
            "searchRequest": "eyJmaWx0ZXJzIjpbXSwic29ydHMiOltdLCJzZWFyY2hCeSI6IiIsInBhZ2UiOjEsInNpemUiOjEwMDAwMH0="}
    response = user.with_api.send(DecisionCommunication.get_communications(query=query))
    if response.status != 204:
        return response.body["content"]
    else:
        return []


def get_channel_list_catalog_content(user: User, query=None, filtered_name=None):
    if query is None:
        query = {
            "searchRequest": "eyJmaWx0ZXJzIjpbXSwic29ydHMiOltdLCJzZWFyY2hCeSI6IiIsInBhZ2UiOjEsInNpemUiOjEwMDAwMH0="}
    if filtered_name is not None:
        filt = f'{{"filters":[],"sorts":[],"searchBy":"{filtered_name}","page":1,"size":20}}'
        q_enc = base64.b64encode(bytes(filt, 'utf-8'))
        query = {"searchRequest": q_enc.decode("utf-8")}
    response = user.with_api.send(DecisionCommunication.get_communications_catalog(query=query))
    if response.status != 204:
        objects_list = []
        for el in response.body["content"]:
            objects_list.append(CommunicationChannelCatalogShortInfoDto.construct(**el))
        return objects_list
    else:
        return []


def find_channel_in_channel_catalogs(user: User, channel_version_id, catalog_id=None, channel_name=None) \
        -> CommunicationChannelCatalogShortInfoDto:
    str_query = '{"filters":[],"sorts":[],"page":1,"size":20}'
    if catalog_id is not None:
        str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":"{catalog_id}"}}]' \
                    f',"sorts":[],"page":1,"size":20,"currentCatalogId":"{catalog_id}"}}'
    if channel_name is not None:
        str_query = f'{{"filters":[],"sorts":[],"searchBy":"{channel_name}","page":1,"size":20}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    resp = user.with_api.send(DecisionCommunication.get_communications_catalog(query=query))
    channel = None
    if resp.status != 204:
        for el in resp.body["content"]:
            if el["versionId"] == channel_version_id:
                channel = CommunicationChannelCatalogShortInfoDto.construct(**el)
                break
    return channel


def get_channel_catalog_content_by_id(user: User, catalog_id):
    str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":"{catalog_id}"}}]' \
                f',"sorts":[],"page":1,"size":20,"currentCatalogId":"{catalog_id}"}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    return user.with_api.send(DecisionCommunication.get_communications_catalog(query=query))
