from typing import Literal

from products.Decision.framework.model import DataProviderCreateDto, TestConnectionRequestDto, DataProviderUpdateDto, \
    AvailableTypesRequestDto
from sdk.user.interface.api.request import ApiRequest


class DecisionDataProviderApi:

    @staticmethod
    def post_dataprovider(*, body: DataProviderCreateDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/dataprovider',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_dataprovider(*, source_id: str, body: DataProviderUpdateDto) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/dataprovider/{source_id}',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_dataproviders(query) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/dataprovider',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_dataprovider(source_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/dataprovider/{source_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_dataprovider(source_id: str) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/dataprovider/{source_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_dataprovider_test_connection(*, body: TestConnectionRequestDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/dataprovider/testConnection',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_dataprovider_tables(source_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/dataprovider/{source_id}/tables',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_dataprovider_tables_table(source_id: str, table_name: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/dataprovider/{source_id}/tables/{table_name}/columns',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_dataprovider_table_index(source_id: str, table_name: str,
                                     index_type) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/dataprovider/{source_id}/tables/{table_name}/indices/{index_type}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_dataprovider_function(source_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/dataprovider/{source_id}/functions',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_dataprovider_decision_types_by_column(body: AvailableTypesRequestDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/dataprovider/decisionTypesByColumn',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )
