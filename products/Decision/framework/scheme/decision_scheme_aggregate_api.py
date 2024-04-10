from products.Decision.framework.model import AggregateCreate, AggregateUpdate
from sdk.user.interface.api.request import ApiRequest


class DecisionAggregate:

    @staticmethod
    def post_aggregates(*, body: AggregateCreate) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/aggregates',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_aggregate(*, aggregate_id) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/aggregates/{aggregate_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_aggregate(*, aggregate_id) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/aggregates/{aggregate_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_aggregates(query) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/aggregates',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_aggregate(*, aggregate_id, body: AggregateUpdate) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/aggregates/{aggregate_id}',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_aggregate_versions(*, aggregate_id) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/aggregates/{aggregate_id}/versions',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_aggregate_grouping_elements() -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/aggregates/groupingElements',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )