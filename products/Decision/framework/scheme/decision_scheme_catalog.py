from products.Decision.framework.model import CatalogCreate, CatalogUpdate, CatalogMove
from sdk.user.interface.api.request import ApiRequest


class DecisionCatalog:

    @staticmethod
    def post_catalog(body: CatalogCreate) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/catalog',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_catalog(query: dict) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/catalog/delete',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_catalog(body: CatalogUpdate) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/catalog',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_catalogs(query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/catalog',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_catalog_move(body: CatalogMove) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/catalog/move',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_types_catalogs(query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/complextype/catalog',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_user_funcs_catalogs(query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/user-function/catalog',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_diagrams_catalogs(query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/diagrams/catalog',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_scripts_catalogs(query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/scripts/catalog',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_services_catalogs(query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/services/catalog',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_aggregate_catalogs(query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/aggregates/catalog',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_offer_catalogs(query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/offer/catalog',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )