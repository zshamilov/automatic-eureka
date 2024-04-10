from products.Decision.framework.scheme.decision_scheme_environments import DecisionEnvironment
from sdk.user import User


def environments_list(user: User):
    return user.with_api.send(DecisionEnvironment.get_environments())


def env_id_by_name(user: User, env_name: str):
    env_list = user.with_api.send(DecisionEnvironment.get_environments()).body
    for env in env_list:
        if env["environmentName"] == env_name:
            return env["environmentId"]
