import base64

from products.Decision.framework.scheme.decision_scheme_custom_attr_dict import DecisionCustomAttrDictApi
from sdk.user import User


def create_custom_attribute(user: User, body):
    return user.with_api.send(DecisionCustomAttrDictApi.post_custom_attribute(body=body))


def update_custom_attribute(user: User, dict_id, body):
    return user.with_api.send(DecisionCustomAttrDictApi.put_custom_attribute(dict_id=dict_id, body=body))


def custom_attributes_list(user: User):

    filt = f'{{"filters":[],"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"page":1,"size":999}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    return user.with_api.send(DecisionCustomAttrDictApi.get_custom_attributes(
        query={"searchRequest": list_query.decode("utf-8")}))


def get_custom_attribute(user: User, dict_id):
    return user.with_api.send(DecisionCustomAttrDictApi.get_custom_attribute(dict_id=dict_id))


def dict_list_by_name(user: User, name: str):
    filt = f'{{"filters":[],"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"searchBy":"{name}","page":1,"size":999}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    response = user.with_api.send(DecisionCustomAttrDictApi.get_custom_attributes(
        query={"searchRequest": list_query.decode("utf-8")}))
    if response.status == 204:
        return []
    else:
        dicts = response.body["content"]
        return dicts


def delete_custom_attribute(user: User, dict_id):
    return user.with_api.send(DecisionCustomAttrDictApi.delete_custom_attribute(dict_id=dict_id))


def get_custom_attribute_diagrams(user: User, dict_id):
    return user.with_api.send(DecisionCustomAttrDictApi.get_custom_attribute_diagrams(dict_id=dict_id))


def get_custom_attribute_values(user: User, dict_id):
    return user.with_api.send(DecisionCustomAttrDictApi.get_custom_attribute_values(dict_id=dict_id))


def get_custom_attributes_by_types(user: User, dict_value_type_id):
    return user.with_api.send(DecisionCustomAttrDictApi.get_custom_attributes_by_types(
        dict_value_type_id=dict_value_type_id))
