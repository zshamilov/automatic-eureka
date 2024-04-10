from products.Decision.framework.scheme.decision_scheme_references import DecisionReferences
from sdk.user import User
from sdk.user.interface.api.response import ApiResponse


def get_function_list(user: User) -> ApiResponse:
    return user.with_api.send(DecisionReferences.get_function_list())


def get_data_type_list(user: User) -> ApiResponse:
    return user.with_api.send(DecisionReferences.get_data_type_list())
