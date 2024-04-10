from products.Decision.framework.model import (
    GenerateConfirmExportDtoRequest,
    ExportStatusDto,
    SelectedImportDto,
)
from sdk.user.interface.api.request import ApiRequest


class DecisionMigration:
    @staticmethod
    def post_generate_export_objects(
        *, body: GenerateConfirmExportDtoRequest
    ) -> ApiRequest:
        return ApiRequest(
            method="POST",
            path=f"/migration/generateExportObjects",
            query={},
            body=body.dict(),
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def post_export(*, body: ExportStatusDto) -> ApiRequest:
        return ApiRequest(
            method="POST",
            path=f"/migration/export",
            query={},
            body=body.dict(),
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def get_download_export_file(*, file_name: str) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/migration/downloadExportFile/{file_name}",
            query={},
            body={},
            headers={"accept": "application/octet-stream"},
        )

    @staticmethod
    def post_upload_import_file(*, file: str) -> ApiRequest:
        return ApiRequest(
            method="POST",
            path=f"/migration/uploadImportFile",
            query={},
            body={},
            files=[file],
            headers={"Content-Type": "multipart/form-data"},
        )

    @staticmethod
    def post_import(*, body: SelectedImportDto) -> ApiRequest:
        return ApiRequest(
            method="POST",
            path=f"/migration/import",
            query={},
            body=body.dict(),
            headers={"Content-Type": "application/json"},
        )
