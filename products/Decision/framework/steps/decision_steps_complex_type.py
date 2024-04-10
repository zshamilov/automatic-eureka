import base64

from products.Decision.framework.model import ComplexTypeGetTreeView
from products.Decision.framework.scheme.decision_scheme_complex_type import DecisionComplexType
from sdk.user import User


def complex_type_list(user: User, query=None):
    if query is None:
        query = {
            "searchRequest": "eyJmaWx0ZXJzIjpbXSwic29ydHMiOltdLCJzZWFyY2hCeSI6IiIsInBhZ2UiOjEsInNpemUiOjEwMDAwMH0="}
    return user.with_api.send(DecisionComplexType.get_complex_types(query=query))


def type_list_by_name(user: User, name: str):
    filt = f'{{"filters":[],"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"searchBy":"{name}","page":1,"size":999}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    response = user.with_api.send(DecisionComplexType.get_complex_types(query={"searchRequest": list_query.decode(
        "utf-8")}))
    if response.status == 204:
        return []
    else:
        types = response.body["content"]
        return types


def create_custom_type(user: User, body):
    return user.with_api.send(DecisionComplexType.post_complex_type(body=body))


def update_custom_type(user: User, type_id, body):
    return user.with_api.send(DecisionComplexType.put_complex_type(type_id=type_id, body=body))


def update_custom_type_attributes(user: User, type_id, body):
    return user.with_api.send(DecisionComplexType.put_complex_type_attributes(type_id=type_id, body=body))


def create_custom_type_attributes(user: User, type_id, body):
    return user.with_api.send(DecisionComplexType.post_complex_type_attributes(type_id=type_id, body=body))


def delete_custom_type_attributes(user: User, type_id, attribute_id):
    return user.with_api.send(DecisionComplexType.delete_complex_type_attributes(type_id=type_id,
                                                                                 attribute_id=attribute_id))


def get_custom_type_attributes(user: User, type_id):
    return user.with_api.send(DecisionComplexType.get_complex_type_attributes(type_id=type_id))


def get_custom_type(user: User, type_id):
    return user.with_api.send(DecisionComplexType.get_complex_type(type_id=type_id))


def get_complex_type_map(user: User, type_id):
    return user.with_api.send(DecisionComplexType.get_complex_type_map(type_id=type_id))


def list_complex_type_versions(user: User, type_id):
    return user.with_api.send(DecisionComplexType.get_complex_type_versions(type_id=type_id))


def delete_custom_type(user: User, version_id: str):
    return user.with_api.send(DecisionComplexType.delete_complex_type(version_id=version_id))


def get_complex_type_tree(user: User, version_id):
    response = user.with_api.send(DecisionComplexType.get_complex_type_tree(version_id=version_id))
    if response.status != 204:
        return ComplexTypeGetTreeView(**response.body)
    else:
        return None
