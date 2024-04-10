from products.Decision.framework.scheme.decision_policy_api import DecisionPolicyApi
from sdk.user import User


def get_policy_attributes(user: User):
    return user.with_api.send(DecisionPolicyApi.get_attributes())