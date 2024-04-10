from products.Decision.framework.scheme.decision_rule_types_api import DecisionRuleTypes
from sdk.user import User


def create_ruletype(user: User, body):
    return user.with_api.send(DecisionRuleTypes.post_ruletype(body=body))


def update_ruletype(user: User, rule_type_id, body):
    return user.with_api.send(DecisionRuleTypes.put_ruletype(rule_type_id=rule_type_id, body=body))


def ruletype_list(user: User):
    return user.with_api.send(DecisionRuleTypes.get_ruletypes())


def delete_ruletype_by_id(user: User, rule_type_id):
    return user.with_api.send(DecisionRuleTypes.delete_ruletype(rule_type_id=rule_type_id))


def get_ruletype_by_id(user: User, rule_type_id):
    return user.with_api.send(DecisionRuleTypes.get_ruletype(rule_type_id=rule_type_id))
