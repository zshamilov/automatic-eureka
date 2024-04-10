import base64

import allure

from products.Decision.framework.model import UserFunctionShortInfo
from products.Decision.framework.scheme.decision_scheme_user_functions import DecisionUserFunctionApi
from products.Decision.framework.scheme.decision_scheme_user_jar import DecisionUserJarApi
from sdk.user import User


def upload_jar_file(user: User, file):
    return user.with_api.send(DecisionUserJarApi.post_user_jar(file=file))


def delete_jar_file(user: User, jar_id: str):
    return user.with_api.send(DecisionUserJarApi.delete_user_jar(jar_id=jar_id))


def get_jar_files_list(user: User):
    return user.with_api.send(DecisionUserJarApi.get_user_jar())


def create_user_function(user: User, jar_id: str, body, catalog_id=None):
    query = {}
    if catalog_id is not None:
        query = {"catalogId": catalog_id}
    return user.with_api.send(DecisionUserFunctionApi.post_user_function(jar_id, body, query))


def get_functions_list(user: User, query=None):
    if query is None:
        query = {"searchRequest": "eyJmaWx0ZXJzIjpbXSwic29ydHMiOltdLCJzZWFyY2hCeSI6IiIsInBhZ2UiOjEsInNpemUiOjk5OX0="}
    return user.with_api.send(DecisionUserFunctionApi.get_user_functions(query))


def get_functions_list_filter_date(user: User, date_from: str, date_to: str):
    start_date = date_from
    # "2023-03-10 00:00:00.000", "%Y-%m-%d %H:%M:%S.%f"
    finish_date = date_to
    # "2023-03-20 00:00:00.000", "%Y-%m-%d %H:%M:%S.%f"
    list_query_str = f'{{"filters":[{{"columnName":"changeDt","operator":"BETWEEN","value":"{start_date}","valueTo":"{finish_date}"}}],"sorts":[],"searchBy":"","page":1,"size":20}}'
    list_query = base64.b64encode(bytes(list_query_str, "utf-8"))
    print(list_query.decode("utf-8"))
    query = {"searchRequest": list_query}
    func_list = []
    for f in user.with_api.send(DecisionUserFunctionApi.get_user_functions(query)).body["content"]:
        func_list.append(UserFunctionShortInfo.construct(**f))
    return func_list


def get_functions_list_sort(user: User, sort: str, column: str):
    df = sort
    # ASC or DESC
    tp = column
    # lastChangeDt or resultType or functionName
    list_query_str = f'{{"filters":[],"sorts":[{{"columnName":"{tp}","direction":"{df}"}}],"searchBy":"","page":1,"size":20}}'
    list_query = base64.b64encode(bytes(list_query_str, "utf-8"))
    print(list_query.decode("utf-8"))
    query = {"searchRequest": list_query}
    func_list = []
    for f in user.with_api.send(DecisionUserFunctionApi.get_user_functions(query)).body["content"]:
        func_list.append(UserFunctionShortInfo.construct(**f))
    return func_list


def delete_user_functions(user: User, func_ids: list[str]):
    query = {"ids": func_ids}
    return user.with_api.send(DecisionUserFunctionApi.delete_user_function(query=query))


def update_user_function(user: User, function_id, body):
    return user.with_api.send(DecisionUserFunctionApi.put_user_function(function_id, body))
