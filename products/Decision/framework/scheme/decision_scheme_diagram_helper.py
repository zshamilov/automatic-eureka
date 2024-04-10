from products.Decision.framework.model import JsonGenerationDto
from sdk.user.interface.api.request import ApiRequest


class DecisionDiagramHelper:

    @staticmethod
    def post_scorecard_file(file: str) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/diagram-helper/upload-scorecard-file',
            query={},
            body={},
            files=[(file, open(file, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')],
            headers={"Content-Type": "multipart/form-data"},
        )

    @staticmethod
    def post_generate_json(*, body: JsonGenerationDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/diagram-helper/generateJson',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )