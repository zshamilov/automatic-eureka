from sdk.user.interface.api.request import ApiRequest


class DecisionPolicyApi:

    @staticmethod
    def get_attributes() -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/policy/attributes',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )