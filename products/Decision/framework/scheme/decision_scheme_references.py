from sdk.user.interface.api.request import ApiRequest


class DecisionReferences:

    @staticmethod
    def get_function_list() -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/references/functions',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_data_type_list() -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/references/datatype',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )