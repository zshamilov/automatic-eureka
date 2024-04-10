from sdk.user.interface.api.request import ApiRequest


class DecisionOfferStorageApi:

    @staticmethod
    def get_client_id_types() -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/offer-storage/clientIdTypes',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )