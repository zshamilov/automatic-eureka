import base64
from typing import Literal

from products.Decision.framework.model import ResponseDto, LockingDtoShortView
from products.Decision.framework.scheme.decision_scheme_locking import DecisionLock
from sdk.user import User


def delete_locking(user: User, object_id,
                   object_type: Literal["DEPLOY", "DIAGRAM", "AGGREGATE", "CUSTOM_CODE", "COMPLEX_TYPE", "SERVICE",
                                        "DATA_PROVIDER", "CUSTOM_ATTRIBUTE_DICTIONARY", "COMMUNICATION_CHANNEL",
                                        "OFFER", "USER_FUNCTION", "DATA_PROVIDER_RELATION", "CATALOG", "KAFKA",
                                        "PYTHON_ENVIRONMENT", "DIAGRAM_RELATION",
                                        "CUSTOM_ATTRIBUTE_DICTIONARY_RELATIONS",
                                        "OFFER_RELATION", "SERVICE_RELATION", "CUSTOM_CODE_RELATION",
                                        "COMMUNICATION_RELATION", "AGGREGATE_RELATION", "MESSAGE_BROKER"] = "DIAGRAM",
                   unlock_type: Literal["SOFT", "HARD"] = "HARD", unlock_dt: str = None) -> ResponseDto:
    query = {"unlockType": unlock_type}
    if unlock_dt is not None:
        query["unlockDt"] = unlock_dt
    return ResponseDto.construct(**user.with_api.send(DecisionLock.delete_locking(object_type, object_id, query)).body)


def locking_list(user: User, diagram_name=None):
    str_query = '{"filters":[],"sorts":[],"searchBy":"","page":1,"size":20}'
    if diagram_name is not None:
        str_query = f'{{"filters":[],"sorts":[],"searchBy":"{diagram_name}","page":1,"size":20}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    response = user.with_api.send(DecisionLock.get_locking(query))
    if response.status != 204:
        raw_list = response.body["content"]
        lock_list = []
        for lock in raw_list:
            lock_list.append(LockingDtoShortView.construct(**lock))
        return lock_list
    else:
        return []
