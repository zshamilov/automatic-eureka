from products.Decision.framework.model import SchemaSaveDto
from products.Decision.framework.scheme.decision_scheme_schema import DecisionSchema
from sdk.user import User


def create_schema(user: User, body: SchemaSaveDto):
    return user.with_api.send(DecisionSchema.post_schema(body))


def find_schema_by_id(user: User, shema_id):
    return user.with_api.send(DecisionSchema.get_schema(shema_id))


def delete_schema(user: User, shema_id):
    return user.with_api.send(DecisionSchema.delete_schema(shema_id))


def get_schema_list(user: User):
    return user.with_api.send(DecisionSchema.get_schemas())
