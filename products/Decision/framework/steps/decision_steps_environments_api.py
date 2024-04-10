from products.Decision.framework.scheme.decision_scheme_environments_api import DecisionEnvironmentsApi
from sdk.user import User


def create_environment(user: User, body):
    return user.with_api.send(DecisionEnvironmentsApi.post_environments(body=body))


def get_environment_by_id(user: User, environment_id):
    return user.with_api.send(DecisionEnvironmentsApi.get_environment(environment_id=environment_id))


def update_environment(user: User, environment_id, body):
    return user.with_api.send(DecisionEnvironmentsApi.put_environment(environment_id=environment_id,
                                                                      body=body))


def delete_environment_by_id(user: User, environment_id):
    return user.with_api.send(DecisionEnvironmentsApi.delete_environment(environment_id=environment_id))


def get_environments_list(user: User):
    return user.with_api.send(DecisionEnvironmentsApi.get_environments())
