from products.Decision.framework.model import SqlValidationApiDto, JsonGenerationValidationDto
from sdk.user.interface.api.request import ApiRequest


class DecisionValidate:

    @staticmethod
    def post_validate_sql(*, body: [SqlValidationApiDto]) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/validate/sql',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def post_validate_expression(*, body: JsonGenerationValidationDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/validate/calculate/expression',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )