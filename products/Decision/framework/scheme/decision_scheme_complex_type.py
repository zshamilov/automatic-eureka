from products.Decision.framework.model import ComplexTypeCreate, ComplexTypeUpdate, AttributeUpdate, AttributeCreate
from sdk.user.interface.api.request import ApiRequest


class DecisionComplexType:

    @staticmethod
    def get_complex_types(query) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/complextype',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_complex_type(*, type_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/complextype/{type_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_complex_type(*, body: ComplexTypeCreate) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path='/complextype',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_complex_type(*, type_id, body: ComplexTypeUpdate) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/complextype/{type_id}',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_complex_type(*, version_id: str) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/complextype/{version_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_complex_type_attributes(*, type_id, body: AttributeUpdate) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/complextype/{type_id}/attributes',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_complex_type_attributes(*, type_id, body: AttributeCreate) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/complextype/{type_id}/attributes',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_complex_type_attributes(*, type_id, attribute_id) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/complextype/{type_id}/attributes/{attribute_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_complex_type_attributes(*, type_id) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/complextype/{type_id}/attributes',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_complex_type_versions(*, type_id) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/complextype/{type_id}/versions',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_complex_type_map(*, type_id) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/complextype/{type_id}/map',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_complex_type_tree(*, version_id) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/complextype/{version_id}/tree',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )