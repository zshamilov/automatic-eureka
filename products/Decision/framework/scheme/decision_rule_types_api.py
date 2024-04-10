from products.Decision.framework.model import RuleTypeCreateDto, RuleTypeUpdateDto
from sdk.user.interface.api.request import ApiRequest


class DecisionRuleTypes:

    @staticmethod
    def post_ruletype(*, body: RuleTypeCreateDto) -> ApiRequest:
        return ApiRequest(
            method='POST',
            path=f'/ruletype',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def put_ruletype(*, body: RuleTypeUpdateDto, rule_type_id: str) -> ApiRequest:
        return ApiRequest(
            method='PUT',
            path=f'/ruletype/{rule_type_id}',
            query={},
            body=body.dict(),
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_ruletypes() -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/ruletype',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def delete_ruletype(rule_type_id: str) -> ApiRequest:
        return ApiRequest(
            method='DELETE',
            path=f'/ruletype/{rule_type_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )

    @staticmethod
    def get_ruletype(rule_type_id: str) -> ApiRequest:
        return ApiRequest(
            method='GET',
            path=f'/ruletype/{rule_type_id}',
            query={},
            body={},
            headers={'Content-Type': 'application/json'}
        )