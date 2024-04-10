from sdk.user.interface.api.request import ApiRequest


class DecisionUserJarApi:
    @staticmethod
    def post_user_jar(file: str) -> ApiRequest:
        return ApiRequest(
            method="POST",
            path=f"/user-jar",
            query={},
            body={},
            files=[{'jarFile': ('user_funcs_testing.jar', open(file, 'rb'), 'application/java-archive')}],
            headers={"Content-Type": "multipart/form-data"},
        )

    @staticmethod
    def get_user_jar() -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/user-jar",
            query={},
            body={},
            headers={'Content-Type': 'application/json'},
        )

    @staticmethod
    def delete_user_jar(jar_id: str) -> ApiRequest:
        return ApiRequest(
            method="DELETE",
            path=f"/user-jar/{jar_id}",
            query={},
            body={},
            headers={'Content-Type': 'application/json'},
        )