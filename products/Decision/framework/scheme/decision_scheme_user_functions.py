from sdk.user.interface.api.request import ApiRequest


class DecisionUserFunctionApi:
    @staticmethod
    def post_user_function(jar_id: str, body, query) -> ApiRequest:
        return ApiRequest(
            method="POST",
            path=f"/user-function/{jar_id}",
            query=query,
            body=body,
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def get_user_function(jar_id: str) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/user-function/{jar_id}",
            query={},
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def get_user_functions(query) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/user-function",
            query=query,
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def delete_user_function(query) -> ApiRequest:
        return ApiRequest(
            method="DELETE",
            path=f"/user-function/delete",
            query=query,
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def put_user_function(function_id: str, body) -> ApiRequest:
        return ApiRequest(
            method="PUT",
            path=f"/user-function/{function_id}",
            query={},
            body=body.dict(),
            headers={"Content-Type": "application/json"},
        )
