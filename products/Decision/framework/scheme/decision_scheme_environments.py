from sdk.user.interface.api.request import ApiRequest


class DecisionEnvironment:

    @staticmethod
    def get_environments() -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/environments',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )