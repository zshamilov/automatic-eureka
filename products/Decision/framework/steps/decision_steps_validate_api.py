from products.Decision.framework.model import JsonGenerationValidationDto, SqlValidationApiDto
from products.Decision.framework.scheme.decision_scheme_validate_api import DecisionValidate
from sdk.user import User
from typing import List


def get_ee_calc_result(user: User, body: JsonGenerationValidationDto):
    return user.with_api.send(DecisionValidate.post_validate_expression(body=body))


def sql_validation_query(user: User, body: SqlValidationApiDto):
    return user.with_api.send(DecisionValidate.post_validate_sql(body=body))
