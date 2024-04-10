import base64
from typing import Literal

from products.Decision.framework.scheme.decision_scheme_data_provider_api import DecisionDataProviderApi
from sdk.user import User


def create_data_provider(user: User, body):
    return user.with_api.send(DecisionDataProviderApi.post_dataprovider(body=body))


def update_data_provider(user: User, source_id, body):
    return user.with_api.send(DecisionDataProviderApi.put_dataprovider(source_id=source_id, body=body))


def providers_list(user: User, query=None):
    if query is None:
        query = {}
    return user.with_api.send(DecisionDataProviderApi.get_dataproviders(query))


def provider_list_by_name(user: User, name: str):
    filt = f'{{"filters":[],"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"searchBy":"{name}","page":1,"size":999}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    response = user.with_api.send(DecisionDataProviderApi.get_dataproviders(query={"searchRequest": list_query.decode(
        "utf-8")}))
    if response.status == 204:
        return []
    else:
        providers = response.body["content"]
        return providers


def get_data_provider(user: User, source_id):
    return user.with_api.send(DecisionDataProviderApi.get_dataprovider(source_id=source_id))


def delete_data_provider(user: User, source_id):
    return user.with_api.send(DecisionDataProviderApi.delete_dataprovider(source_id=source_id))


def make_test_connection(user: User, body):
    return user.with_api.send(DecisionDataProviderApi.post_dataprovider_test_connection(body=body))


def get_data_provider_tables(user: User, source_id):
    return user.with_api.send(DecisionDataProviderApi.get_dataprovider_tables(source_id=source_id))


def get_data_provider_table(user: User, source_id, table_name):
    return user.with_api.send(DecisionDataProviderApi.get_dataprovider_tables_table(
        source_id=source_id, table_name=table_name))


def get_data_provider_table_indexes(user: User, source_id, table_name,
                                    index_type: Literal["ALL", "PRIMARY", "UNIQUE"] = "UNIQUE"):
    return user.with_api.send(DecisionDataProviderApi.get_dataprovider_table_index(
        source_id=source_id, table_name=table_name, index_type=index_type))


def get_data_provider_functions(user: User, source_id):
    return user.with_api.send(DecisionDataProviderApi.get_dataprovider_function(
        source_id=source_id))


def post_data_provider_types_by_column(user: User, body):
    return user.with_api.send(DecisionDataProviderApi.post_dataprovider_decision_types_by_column(body=body))
