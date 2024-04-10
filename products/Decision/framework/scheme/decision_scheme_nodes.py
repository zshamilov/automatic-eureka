from products.Decision.framework.model import NodeCreateDto, LinkCreateDto, NodeUpdateDto, NodeValidateDto, \
    NodeRemapDto, NodesCopyDto, NodesPasteRequestDto, NodeMetaInfo, NodeAutoMappingDto
from sdk.user.interface.api.request import ApiRequest


class DecisionNodes:

    @staticmethod
    def create_node(*, body: NodeCreateDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/diagrams/nodes',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def create_link(*, body: LinkCreateDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/diagrams/links',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_node(*, node_id) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/diagrams/nodes/{node_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_node(*, node_id) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/diagrams/nodes/{node_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_link(*, link_id) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/diagrams/links/{link_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_update_node(*, node_id: str, body: NodeUpdateDto) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/diagrams/nodes/{node_id}',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_node_validate(node_id, body: NodeValidateDto) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/diagrams/nodes/{node_id}/validate',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_previous_nodes(*, node_id, query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/diagrams/nodes/{node_id}/prevNodes',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_possible_nodes(*, node_id, query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/diagrams/nodes/{node_id}/possible',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_remap_node(*, node_id: str, body: NodeRemapDto) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/diagrams/nodes/{node_id}/remap',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    # TODO Написать тесты с использованием put_relocate_node, добавить шаг перемещения start_node
    #  в diagam_constructor для более красивых диаграмм
    def put_relocate_node(*, node_id: str, body: NodeMetaInfo) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/diagrams/nodes/{node_id}/metainfo',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_copy_nodes(*, body: NodesCopyDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/diagrams/nodes/copy',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_paste_nodes(*, body: NodesPasteRequestDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/diagrams/nodes/paste',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_revalidate_nodes(*, diagram_version_id: str) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/diagrams/nodes/{diagram_version_id}/reValidate',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_automap_node(*, node_id: str, body: NodeAutoMappingDto) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/diagrams/nodes/{node_id}/autoMap',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )
