from products.Decision.framework.model import DiagramCreateNewVersion, DiagramCreateUserVersion, DiagramCreateAsNew, \
    DiagramRename, DiagramParameterDto
from sdk.user.interface.api.request import ApiRequest


class DecisionDiagram:

    @staticmethod
    def get_diagrams(query) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/diagrams',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_diagram_by_id(*, version_id: str, query: dict) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/diagrams/{version_id}',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def rename_diagram_by_id(*, version_id: str, body: DiagramRename) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/diagrams/{version_id}/rename',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_diagram_versions_by_id(*, diagram_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/diagrams/{diagram_id}/versions',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def create_template_from_latest(*, version_id: str) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/diagrams/{version_id}/createTemplateFromLatest',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def create_diagram(*, body: DiagramCreateNewVersion) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path='/diagrams',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def create_diagram_template(query) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path='/diagrams/createTemplate',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def create_diagram_as_new(*, body: DiagramCreateAsNew) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path='/diagrams/createAsNew',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_diagrams(*, body: DiagramCreateNewVersion) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path='/diagrams',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_diagram_by_id(*, diagram_id: str) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/diagrams/{diagram_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_diagram_template(*, diagram_id: str) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/diagrams/{diagram_id}/removeTemplate',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_diagram_parameters(*, version_id: str, body: DiagramParameterDto) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/diagrams/{version_id}/parameters',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_diagram_parameters(version_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/diagrams/{version_id}/parameters',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_diagram_submit(*, diagram_id: str, deploy_type) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/diagrams/{diagram_id}/{deploy_type}/submit',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_deploy(environment_id: str, body) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/diagrams/{environment_id}/deploy',
            query={},
            body=body,
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_undeploy(*, deploy_id: str) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/diagrams/{deploy_id}/undeploy',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_related_diagram_with_obj(*, object_type: str, object_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/diagrams/getRelatedDiagramsWithObject/{object_type}/{object_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_diagram_validate(*, version_id: str) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/diagrams/{version_id}/validate',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_diagrams_user_version(*, body: DiagramCreateUserVersion) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path='/diagrams/create/userVersion',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )
