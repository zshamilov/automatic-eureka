from products.Decision.framework.model import CustomAttributeDictionaryCreate, CustomAttributeDictionaryUpdate
from sdk.user.interface.api.request import ApiRequest


class DecisionCustomAttrDictApi:

    @staticmethod
    def post_custom_attribute(*, body: CustomAttributeDictionaryCreate) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/custom-attribute-dict',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_custom_attribute(*, dict_id: str, body: CustomAttributeDictionaryUpdate) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/custom-attribute-dict/{dict_id}',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_custom_attributes(query=None) -> ApiRequest:
        if query is None:
            query = {}
        return ApiRequest(
            method='GET',
            path=f'/custom-attribute-dict',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_custom_attribute(*, dict_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/custom-attribute-dict/{dict_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_custom_attribute(*, dict_id: str) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/custom-attribute-dict/{dict_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_custom_attribute_diagrams(*, dict_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/custom-attribute-dict/{dict_id}/diagrams',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_custom_attribute_values(*, dict_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/custom-attribute-dict/{dict_id}/values',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_custom_attributes_by_types(*, dict_value_type_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/custom-attribute-dict/{dict_value_type_id}/dictByValueType',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )