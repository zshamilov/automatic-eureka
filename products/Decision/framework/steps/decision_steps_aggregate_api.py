import base64

from products.Decision.framework.scheme.decision_scheme_aggregate_api import DecisionAggregate
from sdk.user import User


def create_aggregate(user: User, body):
    return user.with_api.send(DecisionAggregate.post_aggregates(body=body))


def update_aggregate(user: User, aggregate_id, body):
    return user.with_api.send(DecisionAggregate.put_aggregate(aggregate_id=aggregate_id, body=body))


def delete_aggregate(user: User, aggregate_id):
    return user.with_api.send(DecisionAggregate.delete_aggregate(aggregate_id=aggregate_id))


def get_aggregate(user: User, aggregate_id):
    return user.with_api.send(DecisionAggregate.get_aggregate(aggregate_id=aggregate_id))


def aggregate_list(user: User, query=None, agr_name=None):
    filt = '{"filters":[],"sorts":[],"searchBy":"","page":1,"size":30}'
    if agr_name is not None:
        filt = f'{{"filters":[],"sorts":[],"searchBy":"{agr_name}","page":1,"size":20}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    if query is None:
        query = {
            "searchRequest": list_query.decode("utf-8")}
    return user.with_api.send(DecisionAggregate.get_aggregates(query=query))


def aggregate_list_content(user: User, query=None):
    if query is None:
        query = {
            "searchRequest": "eyJmaWx0ZXJzIjpbXSwic29ydHMiOltdLCJzZWFyY2hCeSI6IiIsInBhZ2UiOjEsInNpemUiOjEwMDAwMH0="}
    response = user.with_api.send(DecisionAggregate.get_aggregates(query=query))
    if response.status != 204:
        return response.body["content"]
    else:
        return []


def aggregate_versions(user: User, aggregate_id):
    return user.with_api.send(DecisionAggregate.get_aggregate_versions(aggregate_id=aggregate_id))


def get_grouping_elements_list(user: User):
    return user.with_api.send(DecisionAggregate.get_aggregate_grouping_elements())


def aggregate_list_by_name(user: User, name: str):
    filt = f'{{"filters":[],"sorts":[],"searchBy":"{name}","page":1,"size":999}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    response = user.with_api.send(
        DecisionAggregate.get_aggregates(query={"searchRequest": list_query.decode("utf-8")}))
    aggregates = response.body.get("content") or []
    return aggregates
