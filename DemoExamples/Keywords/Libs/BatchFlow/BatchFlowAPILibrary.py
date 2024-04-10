import os

import requests
from pydantic import ValidationError
from robot.libraries.BuiltIn import BuiltIn
from contextlib import contextmanager
from robot.api.logger import info, debug, trace, console
from products.Batch_Flow.framework.steps.bf_steps import *
from products.Batch_Flow.framework.scheme.bf_scheme import BatchFlow
from sdk.clients.api import ApiClient
from sdk.user import User
import allure
import json
from sdk.user.interface.api.request import ApiRequest
from robotlibcore import DynamicCore, HybridCore
from robot.api.deco import keyword, library
from faker import Faker
from config import settings
#from products.Axiom.framework.axiommodelv2 import *
from pytest_in_robotframework import pytest_execute
#from products.Batch_Flow.tests.diagrams.conftest import node
from products.Batch_Flow.framework.model import *

faker = Faker()



@library
class BatchFlowAPILibrary:
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

    # @pytest_execute
    # def test_node(self, node):
    #     return node()
    @property
    def session(self):
        if self._session is None:
            raise PermissionError('No valid user session. Authenticate first!')
        return self._session


    @allure.step("Get Token")
    def get_token(self):
        if self._token is None:
            raise PermissionError('No valid user session. Authenticate first!')
        return self._token


    @allure.step("Set User")
    def set_user(self, login, password):
        '''Sets the user with login and passwords'''
        self._connection = User(username=login, password=password)
        info(f'User set with credentials: {login} ')


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

    @keyword("Создать Диаграмму")
    def create_diagram(self, name):
        """
        Create a diagram with the given name and set its state to 'locked'.

        :param name: The name of the diagram to be created.
        :return: None
        """

        response = create_diagram(
            self._session, body=DiagramCreate(name=name, comment="As a fixture")
        )
        put_diagram_state(
            self._session, uuid=response.body["uuid"], query={"value": "locked"}
        )



    @keyword("Разблокировать Диаграмму")
    def unlock_diagram(self, name):
        pass

    @keyword("Запустить Диаграмму")
    def start_diagram(self, name):
        pass

    @keyword("Запланировать Диаграмму")
    def schedule_diagram(self, name):
        pass

    @keyword('Добавить Узел ${node_type} в Диаграмму')
    def add_node_to_diagram(self, diagram_name, node_type):
        node_factory = self.test_node()
        node_factory.create_node(self._session, node_type)
        pass

    @keyword("Настроить Узел на Диаграмме")
    def configure_node_on_diagram(self, diagram_name, node_type, configuration_details):
        pass

    @keyword("Связать Узлы на Диаграмме")
    def link_nodes_on_diagram(self, diagram_name, node_type1, node_type2):
        pass

    @keyword("Добавить и Настроить Узлы на Диаграмме")
    def add_and_configure_nodes_on_diagram(self, diagram_name, node_types, configuration_details):
        pass

    @keyword("Запустить Цепочку Диаграмм")
    def run_diagram_chain(self, *diagram_names):
        pass

    @keyword("Загрузить Сущность")
    def load_entity(self, entity_type, entity_name):
        pass

    @keyword("Загрузить Сущности с Связью")
    def load_entities_with_relation(self, entity1, relation_type, entity2):
        pass

    @keyword("Загрузить Сущность с Характеристиками")
    def load_entity_with_features(self, entity_type, entity_name, features_list):
        pass

    @keyword("Выполнить Пользовательский SQL")
    def execute_custom_sql(self, sql_code):
        pass

    @keyword("Определить Характеристику Сущности")
    def define_entity_feature(self, entity_name, feature_name):
        pass

    @keyword("Агрегировать Характеристики Сущности")
    def aggregate_entity_features(self, entity_type, entity_name, features_list):
        pass

    @keyword("Настроить Узел Фильтр")
    def set_node_filter(self, diagram_name, entity_name):
        pass

    @keyword("Настроить Узел Коммуникации")
    def set_node_communication(self, diagram_name, node_configuration):
        pass

    @keyword("Настроить Узел Объединения")
    def set_node_union(self, diagram_name, node_configuration):
        pass

    @keyword("Связать Узел")
    def link_node(self, node_name, target_node_name):
        pass

    @keyword("Настроить Узлы с Сущностью")
    def configure_nodes_with_entity(self, diagram_name, node_type, entity_name):
        pass

    @keyword("Настроить и Связать Узлы")
    def configure_and_link_nodes(self, diagram_name, configuration_details, link_details):
        pass

    @keyword("Создать Пользовательский Код")
    def create_custom_code(self, code_details):
        pass

    @keyword("Создать Форму для Узла")
    def create_node_form(self, node_name, field_type, field_requirement):
        pass

    @keyword("Создать Кампанию")
    def create_campaign(self, campaign_details):
        pass

    @keyword("Создать Формулу")
    def create_formula(self, formula_details):
        pass

    @keyword("Создать Агрегат с Сущностью")
    def create_entity_aggregate(self, entity_type, entity_name):
        pass


####### Variant #2 ###########
    @keyword
    def create_cform(self, body_as_string: str):
        # Convert the string representation of 'body' back to a Cform object
        body = self._string_to_object(body_as_string, Cform)
        result = create_cform(self._session, body)
        # Handle the result as needed for Robot Framework
        return result

    @keyword
    def create_cscript(self, body_as_string: str):
        body = self._string_to_object(body_as_string, Cscript)
        result = create_cscript(self._session, body)
        # Handle the result as needed for Robot Framework
        return result


    @keyword(name="Create Data Item")
    def create_data_item(self, uuid_as_string: str, body_as_string: str):

        body = self._string_to_object(body_as_string, DataItem)
        result =  create_data_item(self._session, uuid=uuid_as_string, body=body)
        return result

    @keyword(name="Create Data Item And Validate")
    def create_data_item_and_validate(self, uuid_as_string: str, body_as_string: str):

        body = self._string_to_object(body_as_string, DataItem())
        result =  create_data_item_and_validate(self._session, uuid=uuid_as_string, body=body)
        return result

    @keyword(name="Create Diagram")
    def create_diagram(self, body_as_string: str, query_as_string: str):
        body = self._string_to_object(body_as_string, DiagramCreate)
        #query = self._string_to_object(query_as_string, dict)
        result = create_diagram(self._session, body)
        return result

    @keyword(name="Create Folder")
    def create_folder(self, body_as_string: str, query_as_string: str):
        body = self._string_to_object(body_as_string, dict)
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.new_folder(body=body, query=query))

    @keyword(name="Create Import")
    def create_import(self, body_as_string: str, package_uuid_as_string: str):
        body = self._string_to_object(body_as_string, dict)
        package_uuid = self._string_to_object(package_uuid_as_string, Union[str, UUID])
        return self._session.with_api.send(BatchFlow.new_import(body=body, package_uuid=package_uuid))

    @keyword(name="Create Package")
    def create_package(self, file_content_as_string: str):
        file_content = self._string_to_object(file_content_as_string, dict)
        return self._session.with_api.send(BatchFlow.new_package(file_content=file_content))

    @keyword(name="Create Package From File")
    def create_package_from_file(self, file_as_string: str):
        file = self._string_to_object(file_as_string, str)
        return self._session.with_api.send(BatchFlow.new_package_from_file(file=file))

    @keyword(name="Create Schedule")
    def create_schedule(self, body_as_string: str):
        body = self._string_to_object(body_as_string, Schedule)
        return self._session.with_api.send(BatchFlow.new_schedule(body=body))


    @keyword(name="Delete Cform")
    def delete_cform(self, uuid_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        return self._session.with_api.send(BatchFlow.delete_cform(uuid=uuid))


    @keyword(name="Delete Cscript")
    def delete_cscript(self, uuid_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        return self._session.with_api.send(BatchFlow.delete_cscript(uuid=uuid))


    @keyword(name="Delete Data Item")
    def delete_data_item(self, uuid_as_string: str, data_item_name_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        data_item_name = self._string_to_object(data_item_name_as_string, str)
        return self._session.with_api.send(BatchFlow.delete_data_item(uuid=uuid, data_item_name=data_item_name))


    @keyword(name="Delete Diagram")
    def delete_diagram(self, diagram_uuid_as_string: str):
        diagram_uuid = self._string_to_object(diagram_uuid_as_string, str)
        return self._session.with_api.send(BatchFlow.delete_diagram(uuid=diagram_uuid))


    @keyword(name="Delete Diagram Version")
    def delete_diagram_version(self, diagram_uuid_as_string: str, version_as_string: str):
        diagram_uuid = self._string_to_object(diagram_uuid_as_string, str)
        version = self._string_to_object(version_as_string, str)
        return self._session.with_api.send(BatchFlow.delete_diagram_version(uuid=diagram_uuid, version=version))


    @keyword(name="Delete Folder")
    def delete_folder(self, folder_uuid_as_string: str, query_as_string: str):
        folder_uuid = self._string_to_object(folder_uuid_as_string, str)
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.delete_folder(folder_uuid=folder_uuid, query=query))


    @keyword(name="Delete Schedule")
    def delete_schedule(self, uuid_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        return self._session.with_api.send(BatchFlow.delete_schedule(uuid=uuid))

    @keyword(name="Get All Cforms")
    def get_all_cforms(self, query_as_string: str):
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.get_all_cforms(query=query))

    @keyword(name="Get All Cscripts")
    def get_all_cscripts(self, query_as_string: str):
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.get_all_cscripts(query=query))

    @keyword(name="Get All Data Entities")
    def get_all_data_entities(self, query_as_string: str):
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.get_data_entities(query=query))

    @keyword(name="Get All Data Items")
    def get_all_data_items(self, query_as_string: str):
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.get_all_data_items(query=query))

    @keyword(name="Get All Diagrams")
    def get_all_diagrams(self, query_as_string: str):
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.get_all_diagrams(query=query))

    @keyword(name="Get All Entities")
    def get_all_entities(self, uuid_as_string: str, query_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.get_diagram_data_items(uuid=uuid, query=query, version="1"))

    @keyword(name="Get All Folders")
    def get_all_folders(self, query_as_string: str):
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.get_folders(query=query))

    @keyword(name="Get All Runs")
    def get_all_runs(self, uuid_as_string: str, version_as_string: str, status_as_string: str, query_as_string: str):
        uuid = self._string_to_object(uuid_as_string, UUID)
        version = self._string_to_object(version_as_string, int)
        status = self._string_to_object(status_as_string, str)
        query = self._string_to_object(query_as_string, dict)
        query.update(diagramUuid=uuid, diagramVersion=version, status=status)
        return self._session.with_api.send(BatchFlow.get_all_runs(query=query))

    @keyword(name="Get All Schedules")
    def get_all_schedules(self, query_as_string: str = "{}"):
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.get_all_schedules(query=query))

    @keyword(name="Get Cform")
    def get_cform(self, uuid_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        return self._session.with_api.send(BatchFlow.get_cform(uuid=uuid))

    @keyword(name="Get Cengines")
    def get_cengines(self, query_as_string: str):
        query = dict(query_as_string)
        return self._session.with_api.send(BatchFlow.get_cengines(query=query))

    @keyword(name="Get Cscript")
    def get_cscript(self, uuid_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        return self._session.with_api.send(BatchFlow.get_cscript(uuid=uuid))

    @keyword(name="Get Diagram Info")
    def get_diagram_info(self, uuid_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        return self._session.with_api.send(BatchFlow.get_diagram_info(uuid=uuid))

    @keyword(name="Get Diagram Data Item")
    def get_diagram_data_item(self, uuid_as_string: str, version_as_string: str, query_as_string: str,
                              data_item_name_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        version = self._string_to_object(version_as_string, str)
        query = self._string_to_object(query_as_string, dict)
        data_item_name = self._string_to_object(data_item_name_as_string, str)
        return self._session.with_api.send(
            BatchFlow.get_diagram_data_item(uuid=uuid, version=version, query=query, data_item_name=data_item_name))

    @keyword(name="Get Diagram Data Entities")
    def get_diagram_data_entitites(self, uuid_as_string: str, version_as_string: str, query_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        version = self._string_to_object(version_as_string, str)
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(
            BatchFlow.get_diagram_data_entitites(uuid=uuid, version=version, query=query))

    @keyword(name="Get Diagram Nodes")
    def get_diagram_nodes(self, uuid_as_string: str, version_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        version = self._string_to_object(version_as_string, str)
        return self._session.with_api.send(BatchFlow.get_diagram_nodes(uuid=uuid, version=version))

    @keyword(name="Get Folder Members")
    def get_folder_members(self, folder_uuid_as_string: str, query_as_string: str = "{}"):
        folder_uuid = self._string_to_object(folder_uuid_as_string, str)
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.get_folders_members_info(folder_uuid, query))

    @keyword(name="Get Import")
    def get_import(self, uuid_as_string: str):
        uuid = self._string_to_object(uuid_as_string, Union[str, UUID])
        return self._session.with_api.send(BatchFlow.get_import(uuid=uuid))

    @keyword(name="Get Package")
    def get_package(self, uuid_as_string: str, parts_as_string: str):
        uuid = self._string_to_object(uuid_as_string, Union[str, UUID])
        parts = self._string_to_object(parts_as_string, str)
        return self._session.with_api.send(BatchFlow.get_package(uuid=uuid, parts=parts))

    @keyword(name="Get Results")
    def get_results(self, query_as_string: str):
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.get_results(query=query, uuid=query["diagramUuid"]))

    @keyword(name="Get Run")
    def get_run(self, run_uuid_as_string: str):
        run_uuid = self._string_to_object(run_uuid_as_string, str)
        return self._session.with_api.send(BatchFlow.get_run(uuid=run_uuid))

    @keyword(name="Get Run Results")
    def get_run_results(self, run_uuid_as_string: str):
        run_uuid = self._string_to_object(run_uuid_as_string, str)
        return self._session.with_api.send(BatchFlow.get_run_results(uuid=run_uuid))

    @keyword(name="Get Schedule")
    def get_schedule(self, schedule_uuid_as_string: str):
        schedule_uuid = self._string_to_object(schedule_uuid_as_string, str)
        return self._session.with_api.send(BatchFlow.get_schedule(uuid=schedule_uuid))

    @keyword(name="Get Segment")
    def get_segment(self, segment_name_as_string: str, query_as_string: str):
        segment_name = self._string_to_object(segment_name_as_string, str)
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.get_segment(segment_name, query=query))

    @keyword(name="Get User Info")
    def get_user_info(self):
        return self._session.with_api.send(BatchFlow.get_user_info())

    @keyword(name="Head Diagram")
    def head_diagram(self, uuid_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        return self._session.with_api.send(BatchFlow.head_diagram(uuid=uuid))

    @keyword(name="Patch Data Items")
    def patch_data_items(self, body_as_string: str):
        body = self._string_to_object(body_as_string, list)
        return self._session.with_api.send(BatchFlow.patch_data_items(body=body))

    @keyword(name="Patch Folder Members")
    def patch_folder_members(self, body_as_string: str, source_folder_uuid_as_string: str, member_uuid_as_string: str):
        body = self._string_to_object(body_as_string, dict)
        source_folder_uuid = self._string_to_object(source_folder_uuid_as_string, str)
        member_uuid = self._string_to_object(member_uuid_as_string, str)
        return self._session.with_api.send(BatchFlow.patch_folder_members(body, source_folder_uuid, member_uuid))

    @keyword(name="Put Cform")
    def put_cform(self, uuid_as_string: str, body_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        body = self._string_to_object(body_as_string, Cform)
        return self._session.with_api.send(BatchFlow.put_cform(uuid=uuid, body=body))

    @keyword(name="Put Cscript")
    def put_cscript(self, uuid_as_string: str, body_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        body = self._string_to_object(body_as_string, Cscript)
        return self._session.with_api.send(BatchFlow.put_cscript(uuid=uuid, body=body))

    @keyword(name="Put Data Item")
    def put_data_item(self, uuid_as_string: str, data_item_name_as_string: str, body_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        data_item_name = self._string_to_object(data_item_name_as_string, str)
        body = self._string_to_object(body_as_string, DataItemUpdate)
        return self._session.with_api.send(BatchFlow.put_data_item(uuid=uuid, data_item_name=data_item_name, body=body))


    @keyword(name="Put Diagram Nodes")
    def put_diagram_nodes(self, body_as_string: str):
        body = self._string_to_object(body_as_string, DiagramUpdate)
        return self._session.with_api.send(BatchFlow.put_diagram_nodes(body=body, uuid=body.uuid))

    @keyword(name="Put Run Status")
    def put_run_status(self, run_uuid_as_string: str, query_as_string: str):
        run_uuid = self._string_to_object(run_uuid_as_string, str)
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.put_run_status(uuid=run_uuid, query=query))

    @keyword(name="Put Schedule")
    def put_schedule(self, body_as_string: str, uuid_as_string: str):
        body = self._string_to_object(body_as_string, Schedule)
        uuid = self._string_to_object(uuid_as_string, str)
        return self._session.with_api.send(BatchFlow.put_schedule(body=body, uuid=uuid))

    @keyword(name="Put Diagram State")
    def put_diagram_state(self, uuid_as_string: str, query_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.put_diagram_state(uuid=uuid, query=query))

    @keyword(name="Put Schedule State")
    def put_schedule_state(self, uuid_as_string: str, query_as_string: str):
        uuid = self._string_to_object(uuid_as_string, str)
        query = self._string_to_object(query_as_string, dict)
        return self._session.with_api.send(BatchFlow.put_schedule_state(uuid=uuid, query=query))

    @keyword(name="Refresh Token")
    def refresh_token(self):
        return self._session.with_api.authorize()

    @keyword(name="Run Diagram")
    def run_diagram(self, body_as_string: str):
        body = self._string_to_object(body_as_string, Run)
        return self._session.with_api.send(BatchFlow.run_diagram(body=body))
    def _string_to_object(self, string_representation: str, object_type: Model) -> Model:
        """
           Converts a JSON-like string to a specified Pydantic model type.

           Parameters:
           - string_representation: JSON-like string to convert.
           - object_type: Pydantic model class to convert the string to.

           Returns:
           - An instance of the specified Pydantic model if conversion is successful.

           Throws:
           - ValidationError if the string_data does not conform to the model's schema.
           - JSONDecodeError if the string_data is not a valid JSON.
           """
        try:
            return object_type.model_validate(string_representation)
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Invalid JSON format: {e}")
            raise


    def _deserialize(self, json_str: str, target_class):
        # Implement deserialization of JSON string to target_class instance
        pass