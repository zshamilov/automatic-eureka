import base64

from products.Decision.framework.scheme.decision_scheme_script_api import DecisionScripts
from sdk.user import User


def create_python_script(user: User, body):
    return user.with_api.send(DecisionScripts.post_python_script(body=body))


def create_python_script_user_version(user: User, body):
    return user.with_api.send(DecisionScripts.post_python_script_user_version(body=body))


def update_python_script(user: User, body):
    return user.with_api.send(DecisionScripts.put_python_script(body=body))


def get_python_script_by_id(user: User, script_id):
    return user.with_api.send(DecisionScripts.get_python_script(script_id=script_id))


def create_groovy_script(user: User, body):
    return user.with_api.send(DecisionScripts.post_groovy_script(body=body))


def create_groovy_script_user_version(user: User, body):
    return user.with_api.send(DecisionScripts.post_groovy_script_user_version(body=body))


def update_groovy_script(user: User, body):
    return user.with_api.send(DecisionScripts.put_groovy_script(body=body))


def get_groovy_script_by_id(user: User, script_id):
    return user.with_api.send(DecisionScripts.get_groovy_script(script_id=script_id))


def delete_script_by_id(user: User, script_id):
    return user.with_api.send(DecisionScripts.delete_script(script_id=script_id))


def update_user_version(user: User, script_id, body):
    return user.with_api.send(DecisionScripts.put_user_version(script_id=script_id, body=body))


def get_script_versions_by_id(user: User, script_id):
    return user.with_api.send(DecisionScripts.get_scripts_versions(script_id=script_id))


def get_script_vars_by_id(user: User, script_id):
    return user.with_api.send(DecisionScripts.get_scripts_variables(script_id=script_id))


def get_script_list(user: User, query=None):
    if query is None:
        query = {
            "searchRequest": "eyJmaWx0ZXJzIjpbXSwic29ydHMiOltdLCJzZWFyY2hCeSI6IiIsInBhZ2UiOjEsInNpemUiOjEwMDAwMH0="}
    return user.with_api.send(DecisionScripts.get_scripts(query=query))


def script_list_by_name(user: User, name: str):
    filt = f'{{"filters":[],"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"searchBy":"{name}","page":1,"size":999}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    response = user.with_api.send(DecisionScripts.get_scripts(query={"searchRequest": list_query.decode(
        "utf-8")}))
    if response.status == 204:
        return []
    else:
        scripts = response.body["content"]
        return scripts


def get_scripts_types(user: User):
    return user.with_api.send(DecisionScripts.get_script_type())
