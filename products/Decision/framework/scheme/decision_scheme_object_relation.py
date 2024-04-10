from sdk.user.interface.api.request import ApiRequest
from products.Decision.framework.model import ObjectType


class DecisionObjectRelation:
    @staticmethod
    def get_object_relation(object_type: str, query) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/object-relation/{object_type}',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )