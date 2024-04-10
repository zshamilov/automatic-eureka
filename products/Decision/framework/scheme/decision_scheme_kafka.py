from sdk.user.interface.api.request import ApiRequest


class DecisionKafka:

    @staticmethod
    def post_kafka(body) -> ApiRequest:
        return ApiRequest(
            method="POST",
            path=f"/kafka",
            query={},
            body=body.dict(),
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def get_kafka(kafka_id) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/kafka/{kafka_id}",
            query={},
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def get_kafkas(query) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/kafka",
            query=query,
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def delete_kafka(kafka_id) -> ApiRequest:
        return ApiRequest(
            method="DELETE",
            path=f"/kafka/{kafka_id}",
            query={},
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def put_kafka(kafka_id, body) -> ApiRequest:
        return ApiRequest(
            method="PUT",
            path=f"/kafka/{kafka_id}",
            query={},
            body=body.dict(),
            headers={"Content-Type": "application/json"},
        )