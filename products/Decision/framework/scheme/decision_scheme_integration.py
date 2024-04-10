from sdk.user.interface.api.request import ApiRequest


class DecisionIntegration:

    @staticmethod
    def post_integration(call_uri: str, body: dict) -> ApiRequest:
        return ApiRequest(
            method="POST",
            path=f"/decision/{call_uri}",
            query={},
            body=body,
            headers={"Content-Type": "application/json"},
        )