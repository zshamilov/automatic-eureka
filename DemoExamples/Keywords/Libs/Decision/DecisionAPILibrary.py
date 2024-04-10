import os

import requests
#from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
from contextlib import contextmanager
from robot.api.logger import info, debug, trace, console
from products.Decision.framework.steps.decision_steps_diagram import *
from products.Decision.framework.steps.decision_steps_deploy import *
from products.Decision.framework.steps.decision_steps_environments_api import get_environments_list
from products.Decision.modelv2 import *
from sdk.clients.api import ApiClient
from sdk.user import User
import allure
import json
from sdk.user.interface.api.request import ApiRequest


class DecisionAPILibrary:
    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self, tc_session_reset=False) -> None:
        '''When option for resetting the user session each test (`tc_session_reset`)
        is set to `True` a `Login User` has to be called each test.
        Otherwise, the library keeps the session for the whole robot framework suite.'''
        self.ROBOT_LIBRARY_SCOPE = 'TEST' if tc_session_reset else 'SUITE'
        console(f'Library Scope is {self.ROBOT_LIBRARY_SCOPE}')
        self._session = None
        self.endpoint = ''
        self.auth = ''
        self.realm = ''
        self._token = ''
        self._connection = None
        self._callUri = None

    @allure.step('Get Deploys')
    def get_deploys(self):
        response = deploy_list(self.session)
        return response.body

    @allure.step('Get Nodes')
    def get_nodes(self, id):
        response = get_diagram_by_version(self.session, id, "READ")
        return response.body

    @property
    def session(self):
        if self._session is None:
            raise PermissionError('No valid user session. Authenticate first!')
        return self._session

    @property
    def callUri(self):
        if self._callUri is None:
            raise PermissionError('No valid user session. Authenticate first!')
        return self._callUri

    @allure.step("Get Token")
    def get_token(self):
        if self._token is None:
            raise PermissionError('No valid user session. Authenticate first!')
        return self._token

    # @allure.step("Set Login Name")
    # def set_login_name(self, login):
    #     '''Sets the users login name and stores it for authentication.'''
    #     self.login = login
    #     info(f'User login set to: {login}')

    @allure.step("Set User")
    def set_user(self, login, password):
        '''Sets the user with login and passwords'''
        self._connection = User(username=login, password=password)
        info(f'User set with credentials: {login} ')

    # @allure.step("Set Password")
    # def set_password(self, password):
    #     '''Sets the users login name and stores it for authentication.'''
    #     self.password = password
    #     info(f'Password set.')

    @allure.step("Set Endpoint")
    def set_endpoint(self, endpoint):
        '''Sets the users login name and stores it for authentication.'''
        self.endpoint = endpoint
        info(f'Endpoint set.')

    @allure.step("Set Auth")
    def set_auth(self, auth, realm):
        '''Sets the keycloak auth endpoint and realm '''
        self.auth = auth
        self.realm = realm
        info(f'Auth and Realm set')

    @allure.step("Add API client")
    def add_api_client(self, client_id, client_secret):
        '''add client keycloak credentials.'''
        self._connection.add_api_client(client=ApiClient(host=self.endpoint),
                            client_id=client_id,
                            client_secret=client_secret)

        info(f'api client ready.')

    @allure.step("Login User")
    def login_user(self) -> None:
        '''`Login User` authenticates a user to the backend.

        The session will be stored during this test suite.'''
        self._connection.with_api.client._host = self.auth
        os.environ["AUTH_REALM"] = self.realm
        self._token = self._connection.with_api.authorize()
        self._connection.with_api.client._host = self.endpoint
        self._session = self._connection

    def input_message_uri(self, uri, message, int_endpoint):
        self._session.with_api.client._host = int_endpoint

        response = self._session.with_api.send(ApiRequest(
            method='POST',
            path=f'/camel/decision/{uri}',
            query={},
            body=message,
            headers={'Content-Type': 'application/json'}
        ))
        return response.raw
        #return json.dumps(response.body, indent=4)

    def deploy_diagram(self, diagram_id):

        if self._callUri is None:
            info("# Останавливаем запущенные деплои")
            deploy_list = deploy_list_by_status(self._session, deploy_status="DEPLOYED")
            for deploy in deploy_list:
                deploy_id = deploy["deployId"]
                stop_deploy(self._session, deploy["deployId"])
            info("# Сабмитим диаграмму")
            put_diagram_submit(self._session, diagram_id)
            env_id = None
            info("# Находим DEPLOYED версию диаграммы")
            version_list = []
            for vers in get_diagram_versions(self._session, diagram_id).body:
                version_list.append(DiagramShortInfoVersionsView.construct(**vers))
            time_arr = []
            for vers in version_list:
                if vers.versionType == VersionType.DEPLOYED:
                    time_arr.append(vers.changeDt)
            latest_deploy_vers = list(filter(lambda v: v.changeDt == max(time_arr), version_list))[0]
            info("# Находим деплой айди")
            filt = f'{{"filters":[],"sorts":[],"searchBy":"{latest_deploy_vers.versionName}","page":1,"size":20}}'
            list_query = base64.b64encode(bytes(filt, 'utf-8'))
            deploy_id = self._session.with_api.send(DecisionDeploy.get_deploy(query={"searchRequest": list_query.decode(
                "utf-8")})).body["content"][0]["deployId"]
            info("# Находим айди дефолтного окружения")
            env_list = []
            for environment in get_environments_list(self._session).body:
                env_list.append(EnvironmentShortInfoDto.construct(**environment))
            for env in env_list:
                if env.environmentName == "default_dev":
                    env_id = env.environmentId

            config: DeployConfigurationFullDto = DeployConfigurationFullDto.construct(
                **deploy_config(self._session, env_id, deploy_version_id=deploy_id))
            config.taskManagerCpuLimit = 0.8
            config.jobManagerCpuLimit = 0.8
            config.taskManagerMemory = 1524
            config.jobManagerMemory = 1524
            config.timeout = 50
            if config.subDiagramConfigurations is not None:
                if len(config.subDiagramConfigurations) != 0:
                    for sub_config in config.subDiagramConfigurations:
                        sub_config["taskManagerCpuLimit"] = 0.7
                        sub_config["jobManagerCpuLimit"] = 0.7
                        sub_config["taskManagerMemory"] = 1024
                        sub_config["jobManagerMemory"] = 1024
                        sub_config["timeout"] = 50
            response: DeployViewDto = start_deploy_async(self._session, deploy_id, env_id,
                                                         body=[config])
            #return {"deploy_reponse": response, "config": config, "call_uri": config.callUri}
            self._callUri = config.callUri
            return config.callUri
        else:
            return self._callUri
