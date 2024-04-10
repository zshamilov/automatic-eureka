from sdk.user.interface.api.request import ApiRequest


class DecisionVersions:

    @staticmethod
    def get_versions() -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/versions',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )