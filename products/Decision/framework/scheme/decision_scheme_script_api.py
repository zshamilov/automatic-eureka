from products.Decision.framework.model import PythonCreate, GroovyCreate, PythonUpdate, GroovyUpdate, \
    PythonCreateUserVersion, GroovyCreateUserVersion, ScriptUpdateUserVersion
from sdk.user.interface.api.request import ApiRequest


class DecisionScripts:

    @staticmethod
    def post_python_script(*, body: PythonCreate) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/scripts/python',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_python_script_user_version(body: PythonCreateUserVersion) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/scripts/python/create/userVersion',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_groovy_script(*, body: GroovyCreate) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/scripts/groovy',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_groovy_script_user_version(body: GroovyCreateUserVersion) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/scripts/groovy/create/userVersion',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_python_script(body: PythonUpdate) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/scripts/python',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_groovy_script(body: GroovyUpdate) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/scripts/groovy',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_python_script(script_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/scripts/python/{script_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_groovy_script(script_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/scripts/groovy/{script_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_scripts_versions(script_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/scripts/{script_id}/versions',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_scripts_variables(script_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/scripts/{script_id}/variables',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_script(script_id: str) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/scripts/{script_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_user_version(script_id: str, body: ScriptUpdateUserVersion) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/scripts/{script_id}/updateUserVersion',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_scripts(query) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/scripts',
            query=query,
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_script_type() -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/scripts/types',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )