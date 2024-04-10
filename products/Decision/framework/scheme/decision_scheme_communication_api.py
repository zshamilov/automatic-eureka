from products.Decision.framework.model import CommunicationChannelCreateDto, CommunicationChannelCreateUserVersionDto, \
    CommunicationChannelUpdateDto
from sdk.user.interface.api.request import ApiRequest


class DecisionCommunication:

    @staticmethod
    def post_communication(body: CommunicationChannelCreateDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/communication',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_communication(version_id: str) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/communication/{version_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_communication(version_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/communication/{version_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_communication_versions(communication_channel_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/communication/{communication_channel_id}/versions',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_communication_variables(version_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/communication/{version_id}/variables',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_communications(query) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/communication',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_communications_catalog(query) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/communication/catalog',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_communication_user_vers(version_id: str,
                                     body: CommunicationChannelCreateUserVersionDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/communication/{version_id}/create/userVersion',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_communication(version_id: str,
                          body: CommunicationChannelUpdateDto) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/communication/{version_id}',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )
