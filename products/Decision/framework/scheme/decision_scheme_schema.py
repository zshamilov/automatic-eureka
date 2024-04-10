from sdk.user.interface.api.request import ApiRequest


class DecisionSchema:

    @staticmethod
    def post_schema(body) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/diagrams/schemas',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_schema(shema_id) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/diagrams/schemas/{shema_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_schema(shema_id) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/diagrams/schemas/{shema_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_schemas() -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/diagrams/schemas',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )