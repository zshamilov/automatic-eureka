from sdk.user.interface.api.request import ApiRequest


class DecisionDeploy:
    @staticmethod
    def get_deploy(query) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/deploy',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_deploy_config(deploy_ids: list[str]) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/deploy/configuration',
            query={"deployIds": deploy_ids},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_deploy_delete(ids: list[str]) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/deploy/delete',
            query={"ids": ids},
            body={},
            headers={'Content-Type': 'application/json'}
        )

