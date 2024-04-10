from typing import Literal

from sdk.user.interface.api.request import ApiRequest


class DecisionLock:

    @staticmethod
    def delete_locking(object_type: Literal["DEPLOY", "DIAGRAM", "AGGREGATE", "CUSTOM_CODE", "COMPLEX_TYPE", "SERVICE",
                                            "DATA_PROVIDER", "CUSTOM_ATTRIBUTE_DICTIONARY", "COMMUNICATION_CHANNEL",
                                            "OFFER", "USER_FUNCTION", "DATA_PROVIDER_RELATION", "CATALOG", "KAFKA",
                                            "PYTHON_ENVIRONMENT", "DIAGRAM_RELATION",
                                            "CUSTOM_ATTRIBUTE_DICTIONARY_RELATIONS",
                                            "OFFER_RELATION", "SERVICE_RELATION", "CUSTOM_CODE_RELATION",
                                            "COMMUNICATION_RELATION", "AGGREGATE_RELATION", "MESSAGE_BROKER"],
                       object_id, query) -> ApiRequest:
        return ApiRequest(
            method="DELETE",
            path=f"/locking/{object_type}/{object_id}",
            query=query,
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def get_locking(query) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/locking",
            query=query,
            body={},
            headers={"Content-Type": "application/json"},
        )