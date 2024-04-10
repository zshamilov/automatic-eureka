from products.Decision.framework.model import EmptyTestCreate, TestCreate
from sdk.user.interface.api.request import ApiRequest


class DecisionTestingApi:
    @staticmethod
    def get_test_list(query: dict) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/test",
            query=query,
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def post_test_next(body: EmptyTestCreate) -> ApiRequest:
        return ApiRequest(
            method="POST",
            path=f"/test/next",
            query={},
            body=body.dict(),
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def delete_test(test_id: str) -> ApiRequest:
        return ApiRequest(
            method="DELETE",
            path=f"/test/{test_id}",
            query={},
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def get_test(test_id: str) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/test/{test_id}",
            query={},
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def get_test_results(test_id: str) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/test/{test_id}/test_results",
            query={},
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def get_test_case(test_case_id: str) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/test/case/{test_case_id}",
            query={},
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def put_test(test_id: str, body: TestCreate) -> ApiRequest:
        return ApiRequest(
            method="PUT",
            path=f"/test/{test_id}",
            query={},
            body=body.dict(),
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def post_testing_file(*, test_id: str, file: str) -> ApiRequest:
        return ApiRequest(
            method="POST",
            path=f"/test/upload/file/{test_id}",
            query={},
            body={},
            files=[(file, open(file, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')],
            headers={"Content-Type": "multipart/form-data"},
        )

    @staticmethod
    def post_start_testing(*, diagram_version_id: str, body) -> ApiRequest:
        return ApiRequest(
            method="POST",
            path=f"/test/start/{diagram_version_id}",
            query={},
            body=body,
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def get_testing_file_gen(*, diagram_version_id: str) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/test/generate/{diagram_version_id}",
            query={},
            body={},
            headers={"accept": "*/*"},
        )

    @staticmethod
    def get_testing_file(*, test_id: str) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/test/{test_id}/download-testfile",
            query={},
            body={},
            headers={"accept": "application/octet-stream"},
        )

    @staticmethod
    def get_testing_report(*, test_id: str) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/test/{test_id}/download-report",
            query={},
            body={},
            headers={"accept": "application/octet-stream"},
        )

    @staticmethod
    def get_test_debug(*, test_case_id: str) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/test/case/{test_case_id}/debug",
            query={},
            body={},
            headers={"accept": "application/json"},
        )

    @staticmethod
    def get_case_result(*, test_case_id: str) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/test/case/{test_case_id}",
            query={},
            body={},
            headers={"accept": "application/json"},
        )
