from sdk.user import User
from sdk.user.interface.api.request import ApiRequest
from products.Decision.framework.model import ObjectRelationPage, ObjectType
import base64
from products.Decision.framework.scheme.decision_scheme_object_relation import DecisionObjectRelation


def get_objects_relation_by_object_id(user: User, object_type: str, object_id: str):
    str_query = f'{{"filters":[{{"columnName":"fromId","operator":"EQUAL","value":"{object_id}"}}]' \
                ',"sorts":[],"page":1,"size":20}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    return user.with_api.send(DecisionObjectRelation.get_object_relation(query=query, object_type=object_type))