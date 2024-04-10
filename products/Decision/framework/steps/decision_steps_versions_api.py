from products.Decision.framework.scheme.decision_scheme_versions_api import DecisionVersions
from sdk.user import User


def get_app_versions(user: User):
    return user.with_api.send(DecisionVersions.get_versions())