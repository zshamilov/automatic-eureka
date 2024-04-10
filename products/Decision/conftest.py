import base64
import json
import string
import uuid

import allure
import pytest
import sqlalchemy

import products.Decision.framework.db_framework.db_model as model
from common.generators import generate_username, generate_string
from config import settings
from products.Decision.framework.db_framework.db_steps.db_steps_test_tables import insert_values
from products.Decision.framework.db_framework.db_steps.db_teardown_steps import delete_constraint, delete_from_table, \
    return_constraint
from products.Decision.framework.model import ResponseDto, DiagramCreateNewVersion, DiagramInOutParametersViewDto, \
    EnvironmentShortInfoDto, DeployConfigurationFullDto, ColumnsDto, DataProviderGetFullView, SourceType, \
    DiagramCreateAsNew, DiagramCreateUserVersion, AggregateGetFullView, \
    ComplexTypeGetFullView, OfferFullViewDto, DataSourceType, ComplexTypeCreate, \
    RetentionType, RetentionTimeUnit, VariableType1, ScriptFullView, DiagramViewDto, \
    NodeViewWithVariablesDto, \
    JoinConditionType, VariableType2, Protocol, SyncType, FileFormat, Method, \
    ExternalServiceFullViewDto, ExternalServiceGetIdWithVariables, ServiceType, ScriptVariableFullView, \
    UserJarFunctionsDto, UserFunctionUploadView, UserFunctionShortView, \
    UserFunctionShortInfo, ConnectionType, NodeValidateDto, CatalogCreate, DeployViewDto, AttributeShortView, \
    NodeViewShortInfo, LinkViewDto, IndexDto, ObjectType, FunctionsDto, DataTypeGetFullView, KafkaCreateDto, \
    KafkaSettingsWithoutIdDto, \
    KafkaAdditionalSettingsWithoutIdDto, KafkaGetFullViewDto, SchemaIdDto, SchemaFullDto, \
    ExternalServiceHeaderViewWithoutIdDto, DiagramInOutParameterFullViewDto, TablesDto, \
    CommunicationChannelFullViewDto, ExternalService
from products.Decision.framework.steps.decision_steps_aggregate_api import get_aggregate, create_aggregate, \
    delete_aggregate, get_grouping_elements_list, aggregate_list_by_name
from products.Decision.framework.steps.decision_steps_catalog import create_catalog, delete_catalogs, \
    get_objects_by_query
from products.Decision.framework.steps.decision_steps_communication_api import create_channel_user_version, \
    create_communication, delete_communication, get_communication_channel
from products.Decision.framework.steps.decision_steps_complex_type import get_custom_type, create_custom_type, \
    delete_custom_type, type_list_by_name
from products.Decision.framework.steps.decision_steps_custom_attr_dict import create_custom_attribute, \
    delete_custom_attribute, dict_list_by_name
from products.Decision.framework.steps.decision_steps_data_provider_api import get_data_provider_table, \
    get_data_provider, create_data_provider, delete_data_provider, get_data_provider_table_indexes, \
    get_data_provider_functions, providers_list, get_data_provider_tables
from products.Decision.framework.steps.decision_steps_deploy import find_deploy_id, \
    find_deploy_with_children, deploy_config, deploy_configs, deploy_list_by_username, deploy_delete
from products.Decision.framework.steps.decision_steps_diagram import delete_diagram, save_diagram, \
    update_diagram_parameters, delete_diagram_template, create_template, start_deploy_async, stop_deploy, \
    put_diagram_submit, \
    create_as_new, create_user_version, create_template_from_latest, get_diagram_by_version, diagram_list_by_name, \
    get_diagram_parameters, start_multiple_diagram_deploy, delete_diagram_check_locking
from products.Decision.framework.steps.decision_steps_environments import env_id_by_name
from products.Decision.framework.steps.decision_steps_environments_api import get_environments_list
from products.Decision.framework.steps.decision_steps_external_service_api import find_service_by_id, \
    service_variables_list, delete_service, create_service, create_service_user_version
from products.Decision.framework.steps.decision_steps_kafka import create_kafka, get_kafka_info
from products.Decision.framework.steps.decision_steps_nodes import create_link, create_node, update_node, \
    get_node_by_id, remap_external_service_node
from products.Decision.framework.steps.decision_steps_offer_api import get_offer_info, create_offer, \
    create_offer_user_version, delete_offer, offer_list_by_name
from products.Decision.framework.steps.decision_steps_python_environment import get_environments_python_list, \
    delete_python_environment
from products.Decision.framework.steps.decision_steps_python_version import get_python_version_list, \
    create_python_version
from products.Decision.framework.steps.decision_steps_references import get_data_type_list
from products.Decision.framework.steps.decision_steps_schema import create_schema, find_schema_by_id
from products.Decision.framework.steps.decision_steps_script_api import delete_script_by_id, create_python_script, \
    get_python_script_by_id, create_groovy_script, get_groovy_script_by_id, create_python_script_user_version, \
    create_groovy_script_user_version, script_list_by_name
from products.Decision.framework.steps.decision_steps_user_functions import upload_jar_file, delete_jar_file, \
    create_user_function, get_functions_list, get_jar_files_list
from products.Decision.utilities.aggregate_constructors import aggregate_construct, aggregate_json_construct
from products.Decision.utilities.communication_constructors import communication_var_construct, communication_construct
from products.Decision.utilities.custom_code_constructors import script_vars_construct, code_construct, \
    code_user_version_construct
from products.Decision.utilities.custom_models import VariableParams, NodeFullInfo, IntNodeType, SourceSettings, \
    TargetSettings, BasicPrimitiveValues
from products.Decision.utilities.custom_type_constructors import attribute_construct, type_create_construct
from products.Decision.utilities.data_provider_constructors import data_provider_construct, provider_setting_construct
from products.Decision.utilities.external_service_constructors import service_setting_construct, service_var_construct, \
    service_construct, service_header_construct
from products.Decision.utilities.node_cunstructors import node_update_construct, link_construct, node_construct, \
    variables_for_node, aggregate_compute_node_construct, \
    offer_node_construct, offer_properties, aggregate_properties, aggregate_compute_out_var, \
    grouping_element_map, aggregate_compute_properties, \
    default_branch, fork_node_construct, join_node_construct, \
    join_branch, external_service_node_construct, \
    ext_serv_var, external_service_properties, empty_node_construct
from products.Decision.utilities.offer_constructors import offer_variable_construct, offer_construct
from products.Decision.utilities.schema_constructors import schema_construct
from products.Decision.utilities.sdi_source_node_constructors import kafka_source_construct, kafka_target_construct
from products.Decision.utilities.variable_constructors import variable_construct
from sdk.Admin.steps.admin_steps import (
    create_realm_user,
    search_user,
    reset_password,
    delete_realm_user,
)
from sdk.clients.api import ApiClient
from sdk.user import User


@pytest.fixture(scope="class")
def credentials():
    return {
        "username": "writer",
        "password": "writer",
    }


@pytest.fixture(scope='session')
def db_credentials() -> dict:
    return {
        'username': settings["DB_POSTGRESQL_USERNAME"],
        'password': settings["DB_POSTGRESQL_PASSWORD"],
        'host': settings["DB_POSTGRESQL_HOST"],
        'port': settings["DB_POSTGRESQL_PORT"],
        'db_name': settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]
    }


@pytest.fixture(scope='session')
def product_db_credentials() -> dict:
    return {
        'username': settings["DB_POSTGRESQL_USERNAME"],
        'password': settings["DB_POSTGRESQL_PASSWORD"],
        'host': settings["DB_POSTGRESQL_HOST"],
        'port': settings["DB_POSTGRESQL_PORT"],
        'db_name': settings["PRODUCT_DB_NAME"]
    }


@pytest.fixture(scope="class")
def admin(endpoint, auth, credentials):
    user = User(**credentials)
    user.add_api_client(client=ApiClient(host=auth))
    user.with_api.authorize()
    # user.with_api.client._host = endpoint
    return user


@pytest.fixture(scope="class")
def email():
    # Foobar
    email = generate_username()
    return email


@pytest.fixture(scope="class")
def super_user(endpoint, admin, email, auth):
    response = create_realm_user(admin, email, ["/DECISION_ROOT"], "autotest_user")
    user_id = search_user(admin, email)
    set_password = reset_password(admin, user_id[0]["id"])
    user = User(username=email, password="password")
    user.add_api_client(client=ApiClient(host=auth),
                        client_id="decision.frontend",
                        client_secret="")
    user.with_api.authorize()
    user.with_api.client._host = endpoint

    yield user

    delete_realm_user(admin, user_id[0]["id"])


@pytest.fixture(scope="class")
def user_gen(endpoint, admin, auth):
    class DecisionUser:
        user_ids = []

        @staticmethod
        def create_user():
            email = generate_username()
            response = create_realm_user(admin, email, ["/DECISION_ROOT"])
            user_id = search_user(admin, email)
            set_password = reset_password(admin, user_id[0]["id"])
            user = User(username=email, password="password")
            user.add_api_client(client=ApiClient(host=auth),
                                client_id="decision.frontend",
                                client_secret="")
            user.with_api.authorize()
            user.with_api.client._host = endpoint
            DecisionUser.user_ids.append(user_id[0]["id"])

            return user

    yield DecisionUser

    for u_id in DecisionUser.user_ids:
        delete_realm_user(admin, u_id)


@pytest.fixture(scope='session')
def db_user(db_credentials) -> User:
    user = User()
    user.add_db_client(**db_credentials, echo=True)
    return user


@pytest.fixture(scope='session')
def product_db_user(product_db_credentials) -> User:
    user = User()
    user.add_db_client(**product_db_credentials, echo=True)
    return user


@pytest.fixture(scope="class")
def integration_user(endpoint, realm, admin, auth):
    email = generate_username()
    response = create_realm_user(admin, email, ["/DECISION_INTEGRATOR"])
    user_id = search_user(admin, email)
    set_password = reset_password(admin, user_id[0]["id"])
    user = User(username=email, password="password")
    user.add_api_client(client=ApiClient(host=auth))
    user.with_api.authorize()
    new_endpoint = endpoint
    new_endpoint = new_endpoint.replace("decision", "decision-integration")
    new_endpoint = new_endpoint.replace("/api", "/camel")
    user.with_api.client._host = new_endpoint

    yield user

    delete_realm_user(admin, user_id[0]["id"])


@pytest.fixture(scope="class")
def commhub_user(realm, admin, auth):
    user = User(username="decision_cli_admin",
                password="decision_cli_admin")
    user.add_api_client(client=ApiClient(host=auth),
                        client_id="decision.frontend",
                        client_secret="")
    user.with_api.authorize()
    user.with_api.client._host = (
        f"https://communication-{realm}.k8s.datasapience.ru/api"
    )

    yield user


@pytest.fixture(scope="session")
def create_db_all_tables_and_scheme(db_user):
    schema_name = model.new_schema
    engine = db_user.with_db.engine
    with engine.connect() as conn:
        if not conn.dialect.has_schema(conn, schema_name):
            conn.execute(sqlalchemy.schema.CreateSchema(schema_name))
            conn.commit()

    metadata_public = model.metadata_obj
    metadata_new_schema = model.metadata_with_scheme

    metadata_public.create_all(engine)
    metadata_new_schema.create_all(engine)
    read_table = model.read_node_table
    values_in_read = {read_table.c.double_val: BasicPrimitiveValues.floatBasic.value,
                      read_table.c.int_val: BasicPrimitiveValues.intBasic.value,
                      read_table.c.str_val: BasicPrimitiveValues.strBasic.value,
                      read_table.c.date_val: BasicPrimitiveValues.dateBasic.value,
                      read_table.c.bool_val: BasicPrimitiveValues.boolBasic.value,
                      read_table.c.date_time_val: BasicPrimitiveValues.dateTimeBasic.value,
                      read_table.c.time_val: BasicPrimitiveValues.timeBasic.value,
                      read_table.c.long_val: BasicPrimitiveValues.longBasic.value
                      }

    insertion_into_read_node_table = insert_values(db_user, model.read_node_table,
                                                   values_in_read)

    yield {"read_node_table": model.read_node_table, "insert_node_table": model.insert_node_table,
           "table_in_schema": model.table_in_schema, "schema_name": schema_name, "default_pk_autoincrement_table": model.default_pk_autoincrement_table}

    metadata_public.drop_all(engine)
    metadata_new_schema.drop_all(engine)
    with engine.connect() as conn:
        if conn.dialect.has_schema(conn, schema_name):
            conn.execute(sqlalchemy.schema.DropSchema(schema_name, cascade=True))
            conn.commit()


@pytest.fixture()
def create_temp_with_in_out_v(super_user):
    response_create_template = create_template(super_user)
    diagram_template: DiagramInOutParametersViewDto = \
        DiagramInOutParametersViewDto.construct(**response_create_template.body)
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template.inOutParameters[0])
    param_name = "output_var"
    parameter_version_id = str(uuid.uuid4())
    diagram_param = variable_construct(array_flag=False,
                                       complex_flag=False,
                                       default_value=None,
                                       is_execute_status=None,
                                       order_num=0,
                                       param_name=param_name,
                                       parameter_type="in_out",
                                       parameter_version_id=parameter_version_id,
                                       parameter_id=parameter_version_id,
                                       type_id=1
                                       )

    params_response = update_diagram_parameters(super_user,
                                                diagram_template.versionId,
                                                [diagram_exec_var,
                                                 diagram_param])
    yield {"template": diagram_template, "diagram_param": diagram_param}

    delete_diagram_template(super_user, diagram_template.versionId)


@pytest.fixture()
def create_temp_diagram(super_user):
    response_create_template = create_template(super_user)
    diagram_template: DiagramInOutParametersViewDto = response_create_template.body
    yield diagram_template

    try:
        delete_diagram_template(super_user, diagram_template["versionId"])
    except:
        print("can't delete template")


@pytest.fixture()
def create_temp_diagram_gen(super_user):
    class CreateTemp:
        diagram_ids = []

        @staticmethod
        def create_template(catalog_id=None):
            response_create_template = create_template(super_user, catalog_id=catalog_id)
            diagram_template: DiagramInOutParametersViewDto = DiagramInOutParametersViewDto.construct(
                **response_create_template.body)
            CreateTemp.diagram_ids.append(diagram_template.versionId)
            return diagram_template

        @staticmethod
        def create_temp_from_latest(version_id):
            response_create_template = create_template_from_latest(super_user, version_id)
            diagram_template: DiagramViewDto = DiagramViewDto.construct(
                **response_create_template.body)
            CreateTemp.diagram_ids.append(diagram_template.versionId)
            return diagram_template

    yield CreateTemp

    for diagram_id in CreateTemp.diagram_ids:
        try:
            delete_diagram_template(super_user, diagram_id)
        except:
            print("can't delete template")


@pytest.fixture(scope='class')
def save_diagrams_gen(super_user):
    class SaveDiagrams:
        version_ids = []

        @staticmethod
        def save_diagram(diagram_id=None, temp_version_id=None, new_diagram_name=None,
                         diagram_description="made_in_test"):
            response_save = save_diagram(super_user, body=DiagramCreateNewVersion(diagramId=uuid.UUID(diagram_id),
                                                                                  versionId=temp_version_id,
                                                                                  errorResponseFlag=False,
                                                                                  objectName=new_diagram_name,
                                                                                  diagramDescription=diagram_description))
            if response_save.status == 201:
                SaveDiagrams.version_ids.append(response_save.body["uuid"])
            return response_save

        @staticmethod
        def save_diagram_as_new(diagram_id=None, temp_version_id=None, new_diagram_name=None, diagram_description=None):
            response_create_as_new = create_as_new(super_user,
                                                   body=DiagramCreateAsNew(diagramId=uuid.UUID(diagram_id),
                                                                           versionId=temp_version_id,
                                                                           errorResponseFlag=False,
                                                                           objectName=new_diagram_name,
                                                                           diagramDescription=diagram_description))
            if response_create_as_new.status == 201:
                SaveDiagrams.version_ids.append(response_create_as_new.body["uuid"])
            return response_create_as_new

        @staticmethod
        def save_diagram_user_vers(diagram_id, saved_version_id, version_name,
                                   global_flag, diagram_name=None, error_response_flag=False, version_description=None):
            response_save = create_user_version(super_user,
                                                body=DiagramCreateUserVersion(diagramId=diagram_id,
                                                                              versionId=saved_version_id,
                                                                              versionDescription=version_description,
                                                                              versionName=version_name,
                                                                              globalFlag=global_flag,
                                                                              errorResponseFlag=error_response_flag))
            if response_save.status == 201:
                SaveDiagrams.version_ids.append(response_save.body["uuid"])
            return response_save

        @staticmethod
        def save_empty_diagram_in_catalog(catalog_id):
            template: DiagramInOutParametersViewDto = DiagramInOutParametersViewDto.construct(
                **create_template(super_user, catalog_id=catalog_id).body)
            saved_diagram_name = "ag_diag_for_cat_" + generate_string()
            diagram_description = "diagram created in test"
            response_save = save_diagram(super_user,
                                         body=DiagramCreateNewVersion(
                                             diagramId=uuid.UUID(template.diagramId),
                                             versionId=template.versionId,
                                             errorResponseFlag=False,
                                             objectName=saved_diagram_name,
                                             diagramDescription=diagram_description))
            get_diagram_by_version_response = get_diagram_by_version(
                super_user, response_save.body["uuid"]
            )
            diagram: DiagramViewDto = DiagramViewDto(**get_diagram_by_version_response.body)
            if response_save.status == 201:
                SaveDiagrams.version_ids.append(response_save.body["uuid"])
            return diagram

    yield SaveDiagrams

    # for version_id in SaveDiagrams.version_ids:
    #     try:
    #         delete_diagram(super_user, version_id)
    #     except:
    #         print("can't delete diagram")


@pytest.fixture()
def ctype_prim_attr(super_user):
    type_name = "test_type_" + generate_string()
    create_response = create_custom_type(super_user,
                                         body=type_create_construct(type_name,
                                                                    [attribute_construct()]))
    create_result: ResponseDto = ResponseDto.construct(**create_response.body)
    custom_type_version_id = create_result.uuid
    complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
        **get_custom_type(super_user, custom_type_version_id).body)
    attributes = []
    for attr in complex_type.attributes:
        attributes.append(AttributeShortView.construct(**attr))
    complex_type.attributes = attributes
    yield complex_type
    # delete_custom_type(super_user, str(custom_type_version_id))


@pytest.fixture()
def created_catalog_id(super_user):
    catalog_name = "ag_test_catalog_" + generate_string()
    create_resp: ResponseDto = ResponseDto(
        **create_catalog(super_user, CatalogCreate(
            catalogName=catalog_name)).body)
    catalog_id = create_resp.uuid

    yield str(catalog_id)

    delete_catalogs(super_user, catalog_ids=[catalog_id])


@pytest.fixture()
def created_two_catalogs(super_user):
    catalog_name1 = "ag_test_catalog1_" + generate_string()
    create_resp1: ResponseDto = ResponseDto(
        **create_catalog(super_user, CatalogCreate(
            catalogName=catalog_name1)).body)
    catalog_name2 = "ag_test_catalog2_" + generate_string()
    create_resp2: ResponseDto = ResponseDto(
        **create_catalog(super_user, CatalogCreate(
            catalogName=catalog_name2)).body)
    catalog_id1 = create_resp1.uuid
    catalog_id2 = create_resp2.uuid

    yield {"catalog_id1": catalog_id1,
           "catalog_id2": catalog_id2}

    delete_catalogs(super_user, catalog_ids=[catalog_id1, catalog_id2])


@pytest.fixture()
def create_catalogs_gen(super_user):
    class Catalogs:
        catalog_ids = []

        @staticmethod
        def create_catalog(catalog_name: str, parent_catalog_id=None):
            create_resp: ResponseDto = ResponseDto(
                **create_catalog(super_user, CatalogCreate(
                    catalogName=catalog_name,
                    parentCatalogId=parent_catalog_id)).body)
            catalog_id = create_resp.uuid
            Catalogs.catalog_ids.append(catalog_id)
            return str(catalog_id)

        @staticmethod
        def try_create_catalog(catalog_name: str, parent_catalog_id=None):
            create_resp = create_catalog(super_user, CatalogCreate.construct(
                catalogName=catalog_name,
                parentCatalogId=parent_catalog_id))
            if create_resp.status == 201:
                catalog_id = create_resp.body["uuid"]
                Catalogs.catalog_ids.append(catalog_id)
            return create_resp

    yield Catalogs

    try:
        delete_catalogs(super_user, catalog_ids=Catalogs.catalog_ids)
    except:
        print("can't delete catalog")


@pytest.fixture()
def upload_funcs_gen(super_user):
    class UserFuncs:
        jar_ids = []
        func_ids = []

        @staticmethod
        def upload_jar_file(file: str):
            for jfile in get_jar_files_list(super_user).body:
                if jfile["jarName"] == "user_funcs_testing.jar":
                    delete_jar_file(super_user, jfile["id"])
            upload_resp: UserJarFunctionsDto = UserJarFunctionsDto(
                **upload_jar_file(super_user, file).body)
            UserFuncs.jar_ids.append(upload_resp.jarId)
            return upload_resp

        @staticmethod
        def add_user_func(jar_file_id: str, functions_body):
            create_response: ResponseDto = ResponseDto.construct(
                **create_user_function(super_user, jar_file_id, body=functions_body).body)
            function_list = []
            for f in get_functions_list(super_user).body["content"]:
                function_list.append(UserFunctionShortInfo.construct(**f))
            user_function = None
            for f in function_list:
                if "made_in_test" in f.description:
                    UserFuncs.func_ids.append(f.id)
                    user_function = f
            return user_function

        @staticmethod
        def try_add_user_func(jar_file_id: str, functions_body):
            create_response = create_user_function(super_user, jar_file_id, body=functions_body)
            if create_response.status == 201:
                function_list = []
                for f in get_functions_list(super_user).body["content"]:
                    function_list.append(UserFunctionShortInfo.construct(**f))
                for f in function_list:
                    if "made_in_test" in f.description:
                        UserFuncs.func_ids.append(f.id)
            return create_response

        @staticmethod
        def add_user_func_from_file(file: str, func_name: str, func_result_type: str,
                                    catalog_id=None):
            for jfile in get_jar_files_list(super_user).body:
                if jfile["jarName"] == "user_funcs_testing.jar":
                    delete_jar_file(super_user, jfile["id"])
            upload_response = upload_jar_file(super_user, file)
            upload_resp: UserJarFunctionsDto = UserJarFunctionsDto(
                **upload_response.body)
            UserFuncs.jar_ids.append(upload_resp.jarId)
            functions = upload_resp.functions
            file_func: UserFunctionShortView = UserFunctionShortView.construct()
            for f in functions:
                if f.objectName == func_name:
                    file_func = f
            func_description = "made_in_test_" + generate_string()
            func_body = UserFunctionUploadView(objectName=file_func.objectName,
                                               jarFunctionName=file_func.jarFunctionName,
                                               functionClass=file_func.functionClass,
                                               resultType=func_result_type,
                                               description=func_description)
            create_response: ResponseDto = ResponseDto.construct(
                **create_user_function(super_user, upload_resp.jarId, body=[func_body],
                                       catalog_id=catalog_id).body)
            function_list = []
            for f in get_functions_list(super_user).body["content"]:
                function_list.append(UserFunctionShortInfo.construct(**f))
            user_function = None
            for f in function_list:
                if "made_in_test" in f.description:
                    UserFuncs.func_ids.append(f.id)
                    user_function = f
            return user_function

    yield UserFuncs

    # delete_user_functions(super_user, func_ids=UserFuncs.func_ids)
    for jar_id in UserFuncs.jar_ids:
        delete_jar_file(super_user, jar_id)


@pytest.fixture()
def get_env(super_user):
    class Env:
        @staticmethod
        def get_env_id(environment_name="default_dev"):
            env_list = []
            env_id = None
            for environment in get_environments_list(super_user).body:
                env_list.append(EnvironmentShortInfoDto.construct(**environment))
            for env in env_list:
                if env.environmentName == environment_name:
                    env_id = env.environmentId
            return env_id

    yield Env


@pytest.fixture(scope='class')
def create_data_provider_gen(super_user):
    class CreateProviders:
        provider_ids = []

        @staticmethod
        def create_provider(data_provider):
            create_response: ResponseDto = ResponseDto.construct(
                **create_data_provider(super_user, body=data_provider).body)
            CreateProviders.provider_ids.append(create_response.uuid)

            return create_response

        @staticmethod
        def create_postgress_provider():
            provider_name = "data_provider_" + generate_string()
            env_id = "a0bb1b74-bb05-42a4-9d7d-15b3ae172180"
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                port=settings["DB_POSTGRESQL_PORT"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="made in test",
                settings=[setting],
            )
            create_response: ResponseDto = ResponseDto.construct(
                **create_data_provider(super_user, body=data_provider).body)
            provider_info: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
            CreateProviders.provider_ids.append(create_response.uuid)

            return provider_info

        @staticmethod
        def try_create_provider(data_provider):
            create_resp = create_data_provider(super_user, body=data_provider)
            if create_resp.status == 201:
                version_id = ResponseDto.construct(**create_resp.body).uuid
                CreateProviders.provider_ids.append(version_id)

            return create_resp

    yield CreateProviders

    # for provider_id in CreateProviders.provider_ids:
    #     delete_data_provider(super_user, provider_id)


@pytest.fixture()
def provider_constructor(super_user, get_env, create_data_provider_gen, request):
    provider_type_marker = request.node.get_closest_marker("provider_type")
    print(provider_type_marker)
    table_name_marker = request.node.get_closest_marker("table_name")
    index_marker = request.node.get_closest_marker("index_type")
    search_type_marker = request.node.get_closest_marker("search_type")
    provider_name = "data_provider_" + generate_string()
    index = None
    columns = None
    provider_info = None
    functions = []
    table_name = None
    env_id = get_env.get_env_id("default_dev")
    if provider_type_marker is None:
        provider_type_marker = "postgres"
        provider_name = "data_provider_" + generate_string()
        env_id = get_env.get_env_id("default_dev")
        setting = provider_setting_construct(
            environment_settings_id=env_id,
            server_name=settings["DB_POSTGRESQL_HOST"],
            port=settings["DB_POSTGRESQL_PORT"],
            username=settings["DB_POSTGRESQL_USERNAME"],
            password=settings["DB_POSTGRESQL_PASSWORD"],
            additional_properties="",
            database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]
        )
        data_provider = data_provider_construct(
            source_name=provider_name,
            source_type=SourceType.POSTGRES,
            connection_type=ConnectionType.JDBC,
            description="made in test",
            settings=[setting],
        )
        create_source_response: ResponseDto = create_data_provider_gen.create_provider(
            data_provider
        )
        provider_info: DataProviderGetFullView = DataProviderGetFullView.construct(
            **get_data_provider(super_user, create_source_response.uuid).body
        )
    elif provider_type_marker is not None:
        provider_type_marker = request.node.get_closest_marker("provider_type").args[0]
        setting = provider_setting_construct(environment_settings_id=env_id)
        data_provider = data_provider_construct(
            source_name=provider_name,
            description="made in test"
        )
        if provider_type_marker == "tdg":
            setting.serverName = "10.35.0.20"
            setting.port = 3304
            setting.username = "tdg_service_user"
            setting.password = ""
            setting.additionalProperties = ""
            data_provider.settings = [setting]
            data_provider.sourceType = SourceType.TARANTOOL_DATAGRID_CLUSTER
            data_provider.connectionType = ConnectionType.NO_SQL
        if provider_type_marker == "tarantool_cluster":
            setting.serverName = "ds-tarantool-1.ru-central1.internal"
            setting.port = 3301
            setting.username = ""
            setting.password = ""
            setting.additionalProperties = ""
            data_provider.settings = [setting]
            data_provider.sourceType = SourceType.TARANTOOL_CARTRIDGE_CLUSTER
            data_provider.connectionType = ConnectionType.NO_SQL
        if provider_type_marker == "tarantool_instance":
            setting.serverName = "ds-tarantool-1.ru-central1.internal"
            setting.port = 3301
            setting.username = ""
            setting.password = ""
            setting.additionalProperties = ""
            data_provider.settings = [setting]
            data_provider.sourceType = SourceType.TARANTOOL
            data_provider.connectionType = ConnectionType.NO_SQL
        if provider_type_marker == "postgres":
            setting.serverName = "decision-postgresql"
            setting.port = 5432
            setting.username = "postgres"
            setting.password = "postgres"
            setting.additionalProperties = "/test"
            data_provider.settings = [setting]
            data_provider.sourceType = SourceType.POSTGRES
            data_provider.connectionType = ConnectionType.JDBC

        create_source_response: ResponseDto = create_data_provider_gen.create_provider(
            data_provider
        )
        provider_info: DataProviderGetFullView = DataProviderGetFullView.construct(
            **get_data_provider(super_user, create_source_response.uuid).body
        )
        if search_type_marker is not None:
            search_type = search_type_marker.args[0]
            if search_type == "LUA_FUNCTION_SEARCH":
                functions = [FunctionsDto(**function) for function in
                             get_data_provider_functions(super_user,
                                                         source_id=provider_info.sourceId).body]
    if table_name_marker is not None:
        table_name = table_name_marker.args[0]
        table_list = []
        for table in get_data_provider_tables(
                super_user, provider_info.sourceId
        ).body:
            table_list.append(TablesDto(**table))
        columns = [ColumnsDto(**column) for column in get_data_provider_table(
            super_user, source_id=provider_info.sourceId, table_name=table_name).body]
        if index_marker is not None:
            index_type = index_marker.args[0]
            if index_type == "ALL":
                index = [IndexDto(**index) for index in
                         get_data_provider_table_indexes(super_user,
                                                         source_id=provider_info.sourceId,
                                                         table_name=table_name, index_type=index_type).body]
            else:
                index = IndexDto(**get_data_provider_table_indexes(super_user,
                                                                   source_id=provider_info.sourceId,
                                                                   table_name=table_name,
                                                                   index_type=index_type).body[0])
    schema_name = ""
    if provider_info.sourceType == "POSTGRES":
        schemas = get_data_provider_tables(super_user, source_id=provider_info.sourceId).body
        schema_name = list(filter(lambda schema: schema["tableName"] == table_name, schemas)).pop()["schemaName"]
    return {"provider_info": provider_info, "columns": columns, "index": index, "functions": functions,
            "table_name": table_name, "env_id": env_id, "schema_name": schema_name}


@pytest.fixture(scope='class')
def create_service_gen(super_user):
    class CreateService:
        service_vers_ids = []

        @staticmethod
        def create_service_user_vers(serv_id, service):
            create_service_resp: ResponseDto = ResponseDto.construct(
                **create_service_user_version(super_user, service_id=serv_id, body=service).body)
            service_vers_id = create_service_resp.uuid
            CreateService.service_vers_ids.append(service_vers_id)
            return create_service_resp

        @staticmethod
        def create_service(service):
            create_service_resp: ResponseDto = ResponseDto.construct(**create_service(super_user, body=service).body)
            service_vers_id = create_service_resp.uuid
            CreateService.service_vers_ids.append(service_vers_id)
            return create_service_resp

        @staticmethod
        def try_create_service(service):
            create_service_resp = create_service(super_user, body=service)
            if create_service_resp.status == 201:
                CreateService.service_vers_ids.append(create_service_resp.body["uuid"])
            return create_service_resp

        @staticmethod
        def create_fake_valid_service(env_id="a0bb1b74-bb05-42a4-9d7d-15b3ae172180",
                                      catalog_id=None):
            setting = service_setting_construct(environment_settings_id=env_id,
                                                host="some_host",
                                                service_type=ServiceType.HTTPS,
                                                endpoint="/endpoint",
                                                port=11,
                                                second_attempts_cnt=4,
                                                transactions_per_second=3,
                                                interval=3,
                                                timeout=2)

            header = service_header_construct(header_name="test", header_value="\"test\"")

            var_in = service_var_construct(variable_name="var_in",
                                           variable_type=VariableType2.IN,
                                           array_flag=False,
                                           primitive_type_id="1",
                                           complex_type_version_id=None,
                                           source_path="/",
                                           expression=None)

            var_out = service_var_construct(variable_name="var_out",
                                            variable_type=VariableType2.OUT,
                                            array_flag=False,
                                            primitive_type_id="1",
                                            complex_type_version_id=None,
                                            source_path="/path_to_service",
                                            expression=None)

            var_calc = service_var_construct(variable_name="var_calc",
                                             variable_type=VariableType2.CALCULATED,
                                             array_flag=False,
                                             primitive_type_id="1",
                                             complex_type_version_id=None,
                                             source_path="/",
                                             expression="1+1")

            service = service_construct(protocol=Protocol.REST,
                                        sync_type=SyncType.ASYNC,
                                        service_name="service_" + generate_string(),
                                        batch_flag=True,
                                        description=None,
                                        file_format=FileFormat.JSON,
                                        method=Method.POST,
                                        body="{\"param\":${var_in}\n}",
                                        service_settings=[setting],
                                        headers=[header],
                                        variables=[var_in, var_out, var_calc],
                                        catalog_id=catalog_id)
            create_service_resp: ResponseDto = ResponseDto.construct(**create_service(super_user, body=service).body)
            service_vers_id = create_service_resp.uuid
            CreateService.service_vers_ids.append(service_vers_id)
            return create_service_resp

    yield CreateService

    # for service_version_id in CreateService.service_vers_ids:
    #     delete_service(super_user, service_version_id)
    # for i in range(len(CreateService.service_vers_ids) - 1, -1, -1):
    #     delete_service(super_user, CreateService.service_vers_ids[i])


@pytest.fixture(scope='class')
def create_aggregate_gen(super_user):
    class CreateAggr:
        aggregate_ids = []

        @staticmethod
        def create_aggr(aggr_body):
            create_resp: ResponseDto = ResponseDto.construct(
                **create_aggregate(super_user, body=aggr_body).body)
            CreateAggr.aggregate_ids.append(create_resp.uuid)

            return create_resp

        @staticmethod
        def create_aggr_in_catalog(catalog_id):
            grouping_elements = get_grouping_elements_list(super_user).body
            grouping_element = grouping_elements[0]
            aggr_name = "auto_test_aggregate_" + generate_string()
            aggr_json = aggregate_json_construct(
                aggregate_name=aggr_name,
                aggregate_variable_type="1",
                aggregate_function=AggregateFunction1.AggCount,
                aggregate_description="created in test",
                grouping_element=f"{grouping_element}",
            )
            aggr_body = aggregate_construct(
                aggregate_name=aggr_name,
                aggregate_json=json.dumps(dict(aggr_json)),
                aggregate_description="created in test",
                catalog_id=catalog_id
            )
            create_resp: ResponseDto = ResponseDto.construct(
                **create_aggregate(super_user, body=aggr_body).body)
            CreateAggr.aggregate_ids.append(create_resp.uuid)
            search_result = AggregateGetFullView.construct(
                **get_aggregate(super_user, create_resp.uuid).body)

            return search_result

        @staticmethod
        def try_create_aggr(aggr_body):
            create_resp = create_aggregate(super_user, body=aggr_body)
            if create_resp.status == 201:
                version_id = ResponseDto.construct(**create_resp.body).uuid
                CreateAggr.aggregate_ids.append(version_id)

            return create_resp

    yield CreateAggr

    # for aggregate_id in CreateAggr.aggregate_ids:
    #     delete_aggregate(super_user, aggregate_id)


@pytest.fixture()
def simple_diagram(super_user, create_temp_diagram_gen):
    diagram_template = dict(create_temp_diagram_gen.create_template())
    diagram_id = diagram_template["diagramId"]
    temp_version_id = diagram_template["versionId"]
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template["inOutParameters"][0])
    rand_string_param_name = "in_out_var_name"
    parameter_version_id2 = str(uuid.uuid4())
    diagram_param = variable_construct(array_flag=False,
                                       complex_flag=False,
                                       default_value=None,
                                       is_execute_status=None,
                                       order_num=0,
                                       param_name=rand_string_param_name,
                                       parameter_type="in_out",
                                       parameter_version_id=parameter_version_id2,
                                       parameter_id=parameter_version_id2,
                                       type_id=1
                                       )

    params_response = update_diagram_parameters(super_user,
                                                temp_version_id,
                                                [diagram_exec_var,
                                                 diagram_param])

    update_response: ResponseDto = params_response.body

    start_variables = variables_for_node("start", False, False, rand_string_param_name, 1,
                                         parameter_version_id2)
    finish_variables = variables_for_node("finish", False, False, rand_string_param_name, 1,
                                          parameter_version_id2)
    node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id, [start_variables])
    node_finish_raw = node_construct(714, 202.22915649414062, "finish", temp_version_id, [finish_variables])
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = node_start_response.body
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = node_end_response.body

    link_s_f = link_construct(temp_version_id, node_start["uuid"], node_end["uuid"])
    link_s_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_f).body)
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variables])
    update_node(super_user, node_id=node_end["uuid"], body=finish_up_body)
    new_diagram_name = "diagram" + "_simple" + generate_string(8)
    diagram_description = 'diagram created in test'

    response_save = save_diagram(super_user, body=DiagramCreateNewVersion(diagramId=uuid.UUID(diagram_id),
                                                                          versionId=temp_version_id,
                                                                          errorResponseFlag=False,
                                                                          objectName=new_diagram_name,
                                                                          diagramDescription=diagram_description))

    create_result: ResponseDto = response_save.body

    saved_version_id = create_result["uuid"]

    subdiagram_info_resp = get_diagram_by_version(
        super_user, saved_version_id
    )
    subdiagram_info: DiagramViewDto = DiagramViewDto.construct(**subdiagram_info_resp.body)
    inner_diagram_exec_var = None
    subdiagram_var = None
    params = get_diagram_parameters(super_user, saved_version_id).body
    for var in params["inOutParameters"]:
        if var["parameterName"] == diagram_exec_var.parameterName:
            inner_diagram_exec_var = DiagramInOutParameterFullViewDto.construct(**var)
        if var["parameterName"] == diagram_param.parameterName:
            subdiagram_var = DiagramInOutParameterFullViewDto.construct(**var)

    yield {"template": diagram_template, "create_result": create_result,
           "diagram_param": subdiagram_var,
           "diagram_name": new_diagram_name,
           "inner_diagram_execute_var": inner_diagram_exec_var}

    # delete_diagram(super_user, saved_version_id)


@pytest.fixture()
def diagram_deployed(super_user, simple_diagram, get_env, deploy_diagrams_gen):
    diagram_id = simple_diagram["template"]["diagramId"]
    version_id = simple_diagram["create_result"]["uuid"]
    diagram_name = simple_diagram["diagram_name"]
    put_diagram_submit(super_user, diagram_id)
    deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
    env_id = get_env.get_env_id("default_dev")
    deploy_configuration = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["config"]

    return {"diagram_id": diagram_id, "version_id": version_id, "env_id": env_id,
            "deploy_id": deploy_id, "diagram_name": diagram_name,
            "deploy_configuration": deploy_configuration
            }


@pytest.fixture()
def create_temp_start_finish_sub_int_var_linked(super_user,
                                                create_temp_diagram_gen):
    diagram_template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
    diagram_id = diagram_template.diagramId
    temp_version_id = diagram_template.versionId
    param_name = "diagram_variable"
    parameter_version_id2 = str(uuid.uuid4())
    exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template.inOutParameters[0])
    new_var = variable_construct(array_flag=False,
                                 complex_flag=False,
                                 default_value=None,
                                 is_execute_status=None,
                                 order_num=0,
                                 param_name=param_name,
                                 parameter_type="in_out",
                                 parameter_version_id=parameter_version_id2,
                                 type_id=1,
                                 parameter_id=parameter_version_id2)
    params_response = update_diagram_parameters(super_user, temp_version_id,
                                                [exec_var, new_var])
    update_response: ResponseDto = params_response.body
    start_variables = variables_for_node("start", False, False,
                                         param_name, 1, parameter_version_id2)
    finish_variables = variables_for_node("finish", False, False,
                                          param_name, 1, parameter_version_id2)
    node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id,
                                    [start_variables])
    node_finish_raw = node_construct(1400, 202.22915649414062, "finish", temp_version_id,
                                     [finish_variables])
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)
    node_sub = node_construct(700, 202.22915649414062, "subdiagram", temp_version_id, None)
    node_sub_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_sub).body)
    node_sub_id = node_sub_response.uuid
    link_s_c = link_construct(temp_version_id, node_start.uuid, node_sub_id)
    link_s_c_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_c).body)
    link_s_c_id = link_s_c_create_response.uuid
    link_c_f = link_construct(temp_version_id, node_sub_id, node_end.uuid)
    link_c_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_c_f).body)
    link_c_f_id = link_c_f_create_response.uuid
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variables])
    update_node(super_user, node_id=node_end.uuid, body=finish_up_body)

    return {"diagram_template": diagram_template, "node_sub_id": node_sub_id,
            "diagram_variable": new_var, "node_end": node_end,
            "diagram_execute_status": exec_var}


@pytest.fixture()
def diagram_aggregate_calculation(super_user, create_aggregate_gen, create_temp_diagram_gen):
    aggr_name = "auto_test_aggregate_" + generate_string()
    grouping_element = "client_id"
    aggr_function = AggregateFunction1.AggCount
    aggr_json = aggregate_json_construct(
        aggregate_name=aggr_name,
        aggregate_variable_type="1",
        aggregate_function=aggr_function,
        aggregate_description="created in test",
        grouping_element=f"{grouping_element}",
    )
    aggr_body = aggregate_construct(
        aggregate_name=aggr_name,
        aggregate_json=json.dumps(dict(aggr_json)),
        aggregate_description="created in test",
    )
    create_resp: ResponseDto = create_aggregate_gen.create_aggr(
        aggr_body=aggr_body
    )
    aggregate: AggregateGetFullView = AggregateGetFullView.construct(
        **get_aggregate(super_user, create_resp.uuid).body)

    diagram_template = dict(create_temp_diagram_gen.create_template())
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template["inOutParameters"][0])
    temp_version_id = diagram_template["versionId"]
    diagram_id = diagram_template["diagramId"]
    letters = string.ascii_lowercase
    in_param_name = "input_var"
    in_aggr_param_name = "aggregate_var"
    out_param_name = "output_var"
    in_param_version_id = str(uuid.uuid4())
    in_aggr_param_version_id = str(uuid.uuid4())
    out_param_version_id = str(uuid.uuid4())
    in_param = variable_construct(array_flag=False,
                                  complex_flag=False,
                                  default_value=None,
                                  is_execute_status=None,
                                  order_num=0,
                                  param_name=in_param_name,
                                  parameter_type="in",
                                  parameter_version_id=in_param_version_id,
                                  type_id=1,
                                  parameter_id=in_param_version_id)
    out_param = variable_construct(array_flag=False,
                                   complex_flag=False,
                                   default_value=None,
                                   is_execute_status=None,
                                   order_num=0,
                                   param_name=out_param_name,
                                   parameter_type="out",
                                   parameter_version_id=out_param_version_id,
                                   type_id=1,
                                   parameter_id=out_param_version_id)
    in_aggr_param = variable_construct(array_flag=False,
                                       complex_flag=False,
                                       default_value=None,
                                       is_execute_status=None,
                                       order_num=0,
                                       param_name=in_aggr_param_name,
                                       parameter_type="in",
                                       parameter_version_id=in_aggr_param_version_id,
                                       type_id=1,
                                       parameter_id=in_aggr_param_version_id)
    params_response = update_diagram_parameters(
        super_user, temp_version_id, [diagram_exec_var,
                                      in_param,
                                      in_aggr_param,
                                      out_param])
    update_response: ResponseDto = params_response.body

    start_variable1 = variables_for_node("start", False, False, in_param_name, "1",
                                         str(in_param_version_id))
    start_variable2 = variables_for_node("start", False, False, in_aggr_param_name, "1",
                                         str(in_aggr_param_version_id))
    finish_variable = variables_for_node("finish", False, False, out_param_name, "1",
                                         str(out_param_version_id), None, None, None, None)
    node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id,
                                    [start_variable1, start_variable2])
    node_finish_raw = node_construct(1400, 202.22915649414062, "finish", temp_version_id,
                                     [finish_variable])
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)
    node_aggr_compute = aggregate_compute_node_construct(
        x=700, y=202.22915649414062, temp_version_id=temp_version_id
    )
    node_aggr_compute_response: ResponseDto = ResponseDto.construct(
        **create_node(super_user, node_aggr_compute).body
    )
    node_aggr_compute_id = node_aggr_compute_response.uuid
    link_s_a = link_construct(temp_version_id, node_start.uuid, node_aggr_compute_id)
    link_s_a_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_a).body)
    link_s_a_id = link_s_a_create_response.uuid
    link_a_f = link_construct(temp_version_id, node_aggr_compute_id, node_end.uuid)
    link_a_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_a_f).body)
    link_a_f_id = link_a_f_create_response.uuid

    yield {"node_start": node_start, "node_end": node_end,
           "node_aggr_compute": node_aggr_compute_response,
           "in_param": in_param, "in_aggr_param": in_aggr_param,
           "out_param": out_param, "template": diagram_template,
           "aggregate": aggregate, "grouping_element": grouping_element,
           "aggregate_function": aggr_function, "finish_var": finish_variable}


@pytest.fixture()
def diagram_aggr_comp_submit(super_user, diagram_aggregate_calculation,
                             get_env, save_diagrams_gen):
    node_aggr_comp: ResponseDto = diagram_aggregate_calculation["node_aggr_compute"]
    in_param: DiagramInOutParameterFullViewDto = diagram_aggregate_calculation["in_param"]
    in_aggr_param: DiagramInOutParameterFullViewDto = diagram_aggregate_calculation["in_aggr_param"]
    out_param: DiagramInOutParameterFullViewDto = diagram_aggregate_calculation["out_param"]
    # diagram_version_id = diagram_offer["create_result"].uuid
    temp_version_id = diagram_aggregate_calculation["template"]["versionId"]
    diagram_id = diagram_aggregate_calculation["template"]["diagramId"]
    aggregate: AggregateGetFullView = diagram_aggregate_calculation["aggregate"]
    grouping_element = diagram_aggregate_calculation["grouping_element"]
    aggregate_function = diagram_aggregate_calculation["aggregate_function"]
    finish_variable = diagram_aggregate_calculation["finish_var"]
    node_end = diagram_aggregate_calculation["node_end"]
    aggr_for_node = aggregate_properties(aggregate_id=aggregate.aggregateId,
                                         aggregate_version_id=aggregate.versionId,
                                         diagram_aggregate_element=in_param.parameterName,
                                         is_used_in_diagram=True,
                                         aggregate_element_type_id="1",
                                         aggregate_function=aggregate_function)
    output_var_mapping = aggregate_compute_out_var(is_arr=False,
                                                   is_compl=False,
                                                   aggregate=aggr_for_node,
                                                   is_dict=False,
                                                   var_name=out_param.parameterName,
                                                   type_id="1")
    gr_element = grouping_element_map(aggregate_element=grouping_element,
                                      diagram_element=in_aggr_param.parameterName,
                                      full_path_value=grouping_element,
                                      simple_name_value=grouping_element,
                                      column=grouping_element)
    node_aggr_properties = aggregate_compute_properties(output_vars=[output_var_mapping],
                                                        retention_type=RetentionType.process,
                                                        retention_time_value=28,
                                                        retention_time_unit=RetentionTimeUnit.d,
                                                        grouping_elements=[gr_element])
    update_body = aggregate_compute_node_construct(x=700, y=202.22915649414062,
                                                   temp_version_id=temp_version_id,
                                                   properties=node_aggr_properties,
                                                   operation="update")
    update_node(super_user, node_id=node_aggr_comp.uuid, body=update_body,
                validate_body=NodeValidateDto.construct(
                    nodeTypeId=update_body.nodeTypeId,
                    properties=update_body.properties))
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variable])
    update_node(super_user, node_id=node_end.uuid, body=finish_up_body)
    diagram_name = "ag_diagram_aggregate_comp" + "_" + generate_string()
    diagram_description = 'diagram created in test'
    response_save: ResponseDto = save_diagrams_gen.save_diagram(diagram_id=diagram_id,
                                                                temp_version_id=temp_version_id,
                                                                new_diagram_name=diagram_name,
                                                                diagram_description=diagram_description)
    submit_response = put_diagram_submit(super_user, diagram_id)
    env_id = get_env.get_env_id("default_dev")
    deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
    return {"deploy_id": deploy_id, "env_id": env_id, "in_param": in_param,
            "in_aggr_param": in_aggr_param, "out_param": out_param,
            "diagram_id": diagram_id, "diagram_name": diagram_name}


@pytest.fixture()
def diagram_subdiagram_working(super_user, simple_diagram, create_temp_diagram_gen):
    subdiagram_version_id = simple_diagram["create_result"]["uuid"]
    subdiagram_id = simple_diagram["template"]["diagramId"]
    subdiagram_name = simple_diagram["diagram_name"]
    subdiagram_var: DiagramInOutParameterFullViewDto = simple_diagram["diagram_param"]
    out_subdiagram_var = 'inner_out_subd_par'
    # diagram_template: DiagramViewDto = create_temp_start_finish_sub_int_var_linked["diagram_template"]
    # node_sub_id = create_temp_start_finish_sub_int_var_linked["node_sub_id"]
    # diagram_var: InOutParameterFullViewDto = create_temp_start_finish_sub_int_var_linked["diagram_variable"]
    inner_diagram_exec_var: DiagramInOutParameterFullViewDto = simple_diagram["inner_diagram_execute_var"]
    diagram_template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template.inOutParameters[0])
    diagram_id = diagram_template.diagramId
    temp_version_id = diagram_template.versionId
    param_name = "diagram_variable"
    parameter_version_id2 = str(uuid.uuid4())
    diagram_var = variable_construct(array_flag=False,
                                     complex_flag=False,
                                     default_value=None,
                                     is_execute_status=None,
                                     order_num=0,
                                     param_name=param_name,
                                     parameter_type="in_out",
                                     parameter_version_id=parameter_version_id2,
                                     parameter_id=parameter_version_id2,
                                     type_id=1)
    params_response = update_diagram_parameters(super_user, temp_version_id,
                                                [diagram_exec_var, diagram_var])
    update_response: ResponseDto = params_response.body
    start_variables = variables_for_node("start", False, False,
                                         param_name, 1, parameter_version_id2)
    finish_variables = variables_for_node("finish", False, False,
                                          param_name, 1, parameter_version_id2)
    node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id,
                                    [start_variables])
    node_finish_raw = node_construct(1400, 202.22915649414062, "finish", temp_version_id,
                                     [finish_variables])
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)
    node_sub = node_construct(700, 202.22915649414062, "subdiagram", temp_version_id, None)
    node_sub_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_sub).body)
    node_sub_id = node_sub_response.uuid
    link_s_c = link_construct(temp_version_id, node_start.uuid, node_sub_id)
    link_s_c_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_c).body)
    link_s_c_id = link_s_c_create_response.uuid
    link_c_f = link_construct(temp_version_id, node_sub_id, node_end.uuid)
    link_c_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_c_f).body)
    link_c_f_id = link_c_f_create_response.uuid

    inp_diagram_vars = variables_for_node(node_type="subdiagram_input",
                                          is_arr=False, is_compl=False, name=diagram_var.parameterName,
                                          type_id="1",
                                          outer_variable_id=subdiagram_var.parameterVersionId,
                                          param_id=diagram_var.parameterId)
    out_diagram_var1 = variables_for_node(node_type="subdiagram_output",
                                          is_arr=False, is_compl=False, name=diagram_var.parameterName,
                                          type_id="1",
                                          outer_variable_id=subdiagram_var.parameterVersionId,
                                          param_id=diagram_var.parameterId)
    out_diagram_var2 = variables_for_node(node_type="subdiagram_output",
                                          is_arr=False, is_compl=False,
                                          name="diagram_execute_status", type_id="2",
                                          outer_variable_id=inner_diagram_exec_var.parameterVersionId,
                                          is_hide=True)
    node_sub_upd = node_update_construct(x=700, y=202, node_type="subdiagram",
                                         temp_version_id=diagram_template.versionId,
                                         diagram_id=subdiagram_id,
                                         diagram_version_id=subdiagram_version_id,
                                         inp_subdiagram_vars=[inp_diagram_vars],
                                         out_subdiagram_vars=[out_diagram_var1, out_diagram_var2])
    update_node_response = update_node(super_user,
                                       node_id=node_sub_id,
                                       body=node_sub_upd)
    node_view: NodeViewWithVariablesDto = NodeViewWithVariablesDto.construct(
        **get_node_by_id(super_user, node_sub_id).body)

    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variables])
    update_node(super_user, node_id=node_end.uuid, body=finish_up_body)

    new_diagram_name = "diagram" + "_" + generate_string()
    diagram_description = 'diagram created in test'

    response_save = save_diagram(super_user, body=DiagramCreateNewVersion(diagramId=diagram_template.diagramId,
                                                                          versionId=diagram_template.versionId,
                                                                          errorResponseFlag=False,
                                                                          objectName=new_diagram_name,
                                                                          diagramDescription=diagram_description))

    create_result: ResponseDto = response_save.body

    outer_diagram_name = new_diagram_name
    saved_version_id = create_result["uuid"]

    yield {"outer_diagram_template": diagram_template, "outer_diagram_create_result": create_result,
           "subdiagram_version_id": subdiagram_version_id, "subdiagram_id": subdiagram_id,
           "outer_diagram_name": outer_diagram_name, "subdiagram_name": subdiagram_name,
           "outer_diagram_var": diagram_var}

    # delete_diagram(super_user, str(saved_version_id))


@pytest.fixture()
def diagram_subdiagram_submit_working(super_user, diagram_subdiagram_working, get_env):
    diagram_id = diagram_subdiagram_working["outer_diagram_template"].diagramId
    version_id = diagram_subdiagram_working["outer_diagram_create_result"]["uuid"]
    diagram_name = diagram_subdiagram_working["outer_diagram_name"]
    diagram_param = diagram_subdiagram_working["outer_diagram_var"]
    subdiagram_id = diagram_subdiagram_working["subdiagram_id"]
    subdiagram_version_id = diagram_subdiagram_working["subdiagram_version_id"]
    subdiagram_name = diagram_subdiagram_working["subdiagram_name"]
    put_diagram_submit(super_user, str(diagram_id))
    env_id = get_env.get_env_id("default_dev")
    deploy_objects = find_deploy_with_children(super_user, diagram_name, diagram_id)
    deploy_id = deploy_objects["deploy_id"]
    child_deploys = deploy_objects["child_deploys"]
    deploys_with_dependencies = [deploy_id] + child_deploys
    return {"deploy_id": deploy_id, "env_id": env_id, "diagram_param": diagram_param,
            "diagram_id": diagram_id, "subdiagram_id": subdiagram_id,
            "diagram_name": diagram_name, "subdiagram_name": subdiagram_name,
            "version_id": version_id, "subdiagram_version_id": subdiagram_version_id,
            "deploys_with_dependencies": deploys_with_dependencies}


@pytest.fixture(scope='class')
def create_custom_types_gen(super_user):
    class CreateCTypes:
        type_ids = []

        @staticmethod
        def create_type(type_name, attrs, catalog_id=None):
            create_response = create_custom_type(super_user,
                                                 body=ComplexTypeCreate(objectName=type_name,
                                                                        displayName=type_name,
                                                                        description=None,
                                                                        catalogId=catalog_id,
                                                                        attributes=attrs))

            create_result: ResponseDto = ResponseDto.construct(**create_response.body)
            custom_type_version_id = create_result.uuid
            CreateCTypes.type_ids.append(custom_type_version_id)
            return create_result

        @staticmethod
        def create_type_in_catalog(catalog_id):
            type_name = "ag_test_type_" + generate_string()
            create_response = create_custom_type(super_user,
                                                 body=ComplexTypeCreate(objectName=type_name,
                                                                        displayName=type_name,
                                                                        description=None,
                                                                        catalogId=catalog_id,
                                                                        attributes=[attribute_construct()]))
            create_result: ResponseDto = ResponseDto.construct(**create_response.body)
            custom_type_version_id = create_result.uuid
            complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_custom_type(super_user, custom_type_version_id).body
            )
            CreateCTypes.type_ids.append(custom_type_version_id)
            return complex_type

        @staticmethod
        def try_create_type(type_name, attrs, catalog_id=None):
            create_response = create_custom_type(super_user,
                                                 body=ComplexTypeCreate(objectName=type_name,
                                                                        displayName=type_name,
                                                                        description=None,
                                                                        catalogId=catalog_id,
                                                                        attributes=attrs))
            if create_response.status == 201:
                CreateCTypes.type_ids.append(create_response.body["uuid"])
            return create_response

    yield CreateCTypes

    # for i in range(len(CreateCTypes.type_ids) - 1, -1, -1):
    #     delete_custom_type(super_user, CreateCTypes.type_ids[i])

    # for type_id in CreateCTypes.type_ids:
    #     delete_custom_type(super_user, type_id)

    # Custom Codes


@pytest.fixture(scope='class')
def create_code_gen(super_user):
    class CreateCode:
        script_vers_ids = []

        @staticmethod
        def create_python_code_user_version(script_id, script_text, script_name, vers_name, inp_var, out_var):
            user_body = code_user_version_construct(script_id=script_id,
                                                    script_type="python", script_name=script_name,
                                                    script_text=script_text, version_name=vers_name,
                                                    variables=[inp_var, out_var], description=None,
                                                    version_description="different name")
            vers_create_result = ResponseDto.construct(
                **create_python_script_user_version(super_user, user_body).body)
            CreateCode.script_vers_ids.append(vers_create_result.uuid)

            return {"vers_create_result": vers_create_result,
                    "out_var": out_var, "inp_var": inp_var}

        @staticmethod
        def create_groovy_code_user_version(script_id, script_text, script_name, vers_name, inp_var, out_var):
            user_body = code_user_version_construct(script_id=script_id,
                                                    script_type="groovy", script_name=script_name,
                                                    script_text=script_text, version_name=vers_name,
                                                    variables=[inp_var, out_var], description=None,
                                                    version_description="different name")
            vers_create_result = ResponseDto.construct(
                **create_groovy_script_user_version(super_user, user_body).body)
            CreateCode.script_vers_ids.append(vers_create_result.uuid)

            return {"vers_create_result": vers_create_result,
                    "out_var": out_var, "inp_var": inp_var}

        @staticmethod
        def create_python_code(script_text, script_name, inp_var, out_var, catalog_id=None):
            script = code_construct(script_type="python",
                                    script_name=script_name,
                                    script_text=script_text,
                                    catalog_id=catalog_id,
                                    variables=[inp_var, out_var])
            python_code_create_result = ScriptFullView.construct(**create_python_script(super_user, body=script).body)
            CreateCode.script_vers_ids.append(python_code_create_result.versionId)
            script_view = ScriptFullView.construct(
                **get_python_script_by_id(super_user, python_code_create_result.versionId).body)
            input_var_with_id = None
            output_var_with_id = None
            variables = []
            for var in script_view.variables:
                variables.append(ScriptVariableFullView.construct(**var))
            for var in variables:
                if var.variableType == "IN":
                    input_var_with_id = var
                if var.variableType == "OUT":
                    output_var_with_id = var

            return {"code_create_result": python_code_create_result,
                    "out_var": output_var_with_id, "inp_var": input_var_with_id}

        @staticmethod
        def create_groovy_code(script_text, script_name, inp_var=None, out_var=None, variables: list = None):
            variables_with_ids: dict[str, ScriptVariableFullView] = {}
            script = code_construct(script_type="groovy",
                                    script_name=script_name,
                                    script_text=script_text,
                                    variables=[inp_var, out_var])
            if variables is not None:
                script = code_construct(script_type="groovy",
                                        script_name=script_name,
                                        script_text=script_text,
                                        variables=variables)
            groovy_code_create_result = ScriptFullView.construct(**create_groovy_script(super_user, body=script).body)
            CreateCode.script_vers_ids.append(groovy_code_create_result.versionId)
            script_view = ScriptFullView.construct(
                **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body)
            input_var_with_id = None
            output_var_with_id = None
            variables = []
            for var in script_view.variables:
                variables.append(ScriptVariableFullView.construct(**var))
            for var in variables:
                if var.variableType == "IN":
                    input_var_with_id = var
                if var.variableType == "OUT":
                    output_var_with_id = var
            for var in variables:
                variables_with_ids[var.variableName] = var
            return {"code_create_result": groovy_code_create_result,
                    "out_var": output_var_with_id, "inp_var": input_var_with_id,
                    "variables_with_ids": variables_with_ids}

        @staticmethod
        def try_create_groovy(script_text, script_name, inp_var, out_var):
            script = code_construct(script_type="groovy",
                                    script_name=script_name,
                                    script_text=script_text,
                                    variables=[inp_var, out_var])
            groovy_code_create_response = create_groovy_script(super_user, body=script)
            if groovy_code_create_response.status == 201:
                CreateCode.script_vers_ids.append(groovy_code_create_response.body["versionId"])

            return {"code_create_response": groovy_code_create_response,
                    "out_var": out_var, "inp_var": inp_var}

        @staticmethod
        def try_create_python(script_text, script_name, inp_var, out_var):
            script = code_construct(script_type="python",
                                    script_name=script_name,
                                    script_text=script_text,
                                    variables=[inp_var, out_var])
            python_code_create_response = create_python_script(super_user, body=script)
            if python_code_create_response.status == 201:
                CreateCode.script_vers_ids.append(python_code_create_response.body["versionId"])

            return {"code_create_response": python_code_create_response,
                    "out_var": out_var, "inp_var": inp_var}

        @staticmethod
        def create_p_code_in_catalog(catalog_id):
            inp_var = script_vars_construct(
                var_name="input_int",
                var_type=VariableType1.IN,
                is_array=False,
                primitive_id="1",
            )
            out_var = script_vars_construct(
                var_name="output_int",
                var_type=VariableType1.OUT,
                is_array=False,
                primitive_id="1",
            )
            script_text = "output_int = input_int + 2"
            script_name = (
                    "test_python_script_" + generate_string()
            )
            script = code_construct(script_type="python",
                                    script_name=script_name,
                                    script_text=script_text,
                                    catalog_id=catalog_id,
                                    variables=[inp_var, out_var])
            python_code_create_result = ScriptFullView.construct(**create_python_script(super_user, body=script).body)
            CreateCode.script_vers_ids.append(python_code_create_result.versionId)
            script_view = ScriptFullView.construct(
                **get_python_script_by_id(super_user, python_code_create_result.versionId).body)
            input_var_with_id = None
            output_var_with_id = None
            variables = []
            for var in script_view.variables:
                variables.append(ScriptVariableFullView.construct(**var))
            for var in variables:
                if var.variableType == "IN":
                    input_var_with_id = var
                if var.variableType == "OUT":
                    output_var_with_id = var

            return {"code_create_result": python_code_create_result,
                    "out_var": output_var_with_id, "inp_var": input_var_with_id,
                    "script_info": script_view}

    yield CreateCode

    # for script_vers in CreateCode.script_vers_ids:
    #     delete_script_by_id(super_user, script_vers)


@pytest.fixture(scope='class')
def create_offer_gen(super_user):
    class CreateOffer:
        offer_ids = []
        type_ids = []
        script_ids = []

        @staticmethod
        def create_offer(offer):
            create_resp: ResponseDto = ResponseDto.construct(
                **create_offer(super_user, body=offer).body)
            CreateOffer.offer_ids.append(create_resp.uuid)

            return create_resp

        @staticmethod
        def create_offer_user_version(offer_user_version, offer_id):
            create_resp: ResponseDto = ResponseDto.construct(
                **create_offer_user_version(super_user,
                                            offer_id=offer_id,
                                            body=offer_user_version).body)
            CreateOffer.offer_ids.append(create_resp.uuid)

            return create_resp

        @staticmethod
        def try_create_offer(offer):
            create_resp = create_offer(super_user, body=offer)
            if create_resp.status == 201:
                version_id = ResponseDto.construct(**create_resp.body).uuid
                CreateOffer.offer_ids.append(version_id)

            return create_resp

        @staticmethod
        def create_full_offer(catalog_id=None):
            custom_type_version_id = "7ff5da96-20b2-4b07-986e-7448782a8f02"
            complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_custom_type(super_user, custom_type_version_id).body
            )

            script_in_var_name = "input_int"
            script_out_var_name = "output_offers"
            script_inp_var = script_vars_construct(var_name=script_in_var_name,
                                                   var_type=VariableType1.IN,
                                                   is_array=False,
                                                   primitive_id="1"
                                                   )
            script_out_var = script_vars_construct(var_name=script_out_var_name,
                                                   var_type=VariableType1.OUT,
                                                   is_array=True,
                                                   complex_vers_id=complex_type.versionId
                                                   )
            script_text = "import java.util.UUID;\n\n" \
                          "def offer = [\"offerId\": UUID.randomUUID().toString(), \n             " \
                          "\"clientId\": \"23\", \n             " \
                          "\"clientIdType\": \"customer\", \n             " \
                          "\"controlGroup\": false,\n             " \
                          "\"productCode\": \"product_code\",\n             " \
                          "\"score\": 1.0D,\n            " \
                          "\"startAt\": \"2023-07-10T14:10:20.111+01:00\",\n             " \
                          "\"endAt\": " \
                          "\"2023-08-10T14:10:20.111+01:00\"]\n" \
                          "output_offers = [offer] "

            print(script_text)
            script_name = ("test_groovy_offer_script_" + generate_string())
            script = code_construct(script_type="python",
                                    script_name=script_name,
                                    script_text=script_text,
                                    variables=[script_inp_var, script_out_var])
            groovy_code_create_result: ScriptFullView = ScriptFullView.construct(
                **create_groovy_script(super_user, body=script).body)
            script_view = ScriptFullView.construct(
                **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body
            )
            input_var_with_id = None
            output_var_with_id = None
            variables = []
            for var in script_view.variables:
                variables.append(ScriptVariableFullView.construct(**var))
            for var in variables:
                if var.variableType == "IN":
                    input_var_with_id = var
                if var.variableType == "OUT":
                    output_var_with_id = var
            CreateOffer.script_ids.append(script_view.versionId)
            offer_var = offer_variable_construct(variable_name="test_var",
                                                 script_variable_name=script_inp_var.variableName,
                                                 array_flag=False,
                                                 data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                                 mandatory_flag=False,
                                                 primitive_type_id="1",
                                                 complex_type_version_id=None,
                                                 min_value=None,
                                                 max_value=None,
                                                 max_size=None,
                                                 dictionary_id=None,
                                                 dynamic_list_type=None)
            offer_name = "test_ag_offer_" + generate_string()
            offer = offer_construct(offer_name=offer_name,
                                    script_version_id=script_view.versionId,
                                    script_id=script_view.scriptId,
                                    script_name=script_view.objectName,
                                    offer_complex_type_version_id=complex_type.versionId,
                                    offer_variables=[offer_var])
            if catalog_id is not None:
                offer.catalogId = catalog_id
            create_resp: ResponseDto = ResponseDto.construct(
                **create_offer(super_user, body=offer).body)
            CreateOffer.offer_ids.append(create_resp.uuid)
            search_response: OfferFullViewDto = OfferFullViewDto.construct(
                **get_offer_info(super_user, create_resp.uuid).body)

            return {"offer_info": search_response, "script_info": script_view,
                    "script_inp_var": input_var_with_id, "script_out_var": output_var_with_id,
                    "offer_c_type": complex_type, "offer_var": offer_var}

    yield CreateOffer

    # for offer_vers_id in CreateOffer.offer_ids:
    #     delete_offer(super_user, offer_vers_id)
    # for script_vers_id in CreateOffer.script_ids:
    #     delete_script_by_id(super_user, script_vers_id)
    # for type_vers_id in CreateOffer.type_ids:
    #     delete_custom_type(super_user, type_vers_id)


# удалить из diagrams\conftest - если всё ок - поменял на offer_runtime => будет 2 похожие версии (в той не нрав, что комплексная переменная сквозная)
@pytest.fixture()
def diagram_offer_for_runtime(super_user,
                              create_code_gen,
                              create_offer_gen,
                              create_temp_diagram_gen):
    custom_type_version_id = "7ff5da96-20b2-4b07-986e-7448782a8f02"
    complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
        **get_custom_type(super_user, custom_type_version_id).body
    )

    script_in_var_name = "input_int"
    script_out_var_name = "output_offers"
    script_inp_var = script_vars_construct(var_name=script_in_var_name,
                                           var_type=VariableType1.IN,
                                           is_array=False,
                                           primitive_id="1"
                                           )
    script_out_var = script_vars_construct(var_name=script_out_var_name,
                                           var_type=VariableType1.OUT,
                                           is_array=True,
                                           complex_vers_id=complex_type.versionId
                                           )
    script_text = "import java.util.UUID;\n\ndef offer = [\"offerId\": UUID.randomUUID().toString(), \n             " \
                  "\"clientId\": \"23\", \n             \"clientIdType\": \"customer\", \n             " \
                  "\"controlGroup\": false,\n             \"productCode\": \"product_code\",\n             \"score\": " \
                  "1.0D,\n             \"startAt\": \"2023-07-10T14:10:20.111+01:00\",\n             \"endAt\": " \
                  "\"2023-08-10T14:10:20.111+01:00\"]\noutput_offers = [offer] "

    print(script_text)
    script_name = ("test_groovy_offer_script_" + generate_string())
    groovy_code_create_result: ScriptFullView = \
        create_code_gen.create_groovy_code(script_text, script_name, script_inp_var, script_out_var)[
            "code_create_result"]
    script_view = ScriptFullView.construct(
        **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body
    )

    offer_var = offer_variable_construct(variable_name="test_var",
                                         script_variable_name=script_inp_var.variableName,
                                         array_flag=False,
                                         data_source_type=DataSourceType.DIAGRAM_ELEMENT,
                                         mandatory_flag=False,
                                         primitive_type_id="1",
                                         complex_type_version_id=None,
                                         min_value=None,
                                         max_value=None,
                                         max_size=None,
                                         dictionary_id=None,
                                         dynamic_list_type=None)
    offer_name = "test_ag_offer_" + generate_string()
    offer = offer_construct(offer_name=offer_name,
                            script_version_id=script_view.versionId,
                            script_id=script_view.scriptId,
                            script_name=script_view.objectName,
                            offer_complex_type_version_id=complex_type.versionId,
                            offer_variables=[offer_var])
    create_response: ResponseDto = create_offer_gen.create_offer(offer=offer)
    search_response: OfferFullViewDto = OfferFullViewDto.construct(
        **get_offer_info(super_user, create_response.uuid).body)

    diagram_template = dict(create_temp_diagram_gen.create_template())
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template["inOutParameters"][0])
    temp_version_id = diagram_template["versionId"]
    diagram_id = diagram_template["diagramId"]
    parameter_in_version_id = str(uuid.uuid4())
    parameter_out_version_id = str(uuid.uuid4())
    new_var_in = variable_construct(array_flag=False,
                                    complex_flag=False,
                                    default_value=None,
                                    is_execute_status=None,
                                    order_num=1,
                                    param_name="in_int_variable",
                                    parameter_type="in",
                                    parameter_version_id=parameter_in_version_id,
                                    type_id="1",
                                    parameter_id=parameter_in_version_id)
    new_var_out = variable_construct(array_flag=True,
                                     complex_flag=True,
                                     default_value=None,
                                     is_execute_status=None,
                                     order_num=2,
                                     param_name="out_cmplx_var",
                                     parameter_type="out",
                                     parameter_version_id=parameter_out_version_id,
                                     type_id=custom_type_version_id,
                                     parameter_id=parameter_out_version_id)
    params_response = update_diagram_parameters(super_user,
                                                temp_version_id,
                                                [diagram_exec_var,
                                                 new_var_in,
                                                 new_var_out])
    update_response: ResponseDto = params_response.body

    start_variables = variables_for_node("start", False, False, new_var_in.parameterName, new_var_in.typeId,
                                         parameter_in_version_id, None, None, None, None)
    finish_variables = variables_for_node("finish", True, True, new_var_out.parameterName, new_var_out.typeId,
                                          parameter_out_version_id, None, None, None, None)
    node_start_raw = node_construct(142, 202.22915649414062, "start", temp_version_id, [start_variables])
    node_offer_raw = offer_node_construct(x=700, y=202.22915649414062, temp_version_id=temp_version_id)
    node_finish_raw = node_construct(1400, 202.22915649414062, "finish", temp_version_id, [finish_variables])
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)
    node_offer: ResponseDto = ResponseDto.construct(**create_node(super_user, node_offer_raw).body)
    link_s_o = link_construct(temp_version_id, node_start.uuid, node_offer.uuid)
    link_s_o_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_o).body)
    link_s_o_id = link_s_o_create_response.uuid
    link_o_f = link_construct(temp_version_id, node_offer.uuid, node_end.uuid)
    link_o_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_o_f).body)
    link_o_f_id = link_o_f_create_response.uuid
    # offer_var = offer_variable(var_id=search_response.offerVariables[0]["id"], value=5)
    node_var_mapping = variables_for_node(node_type="offer_mapping",
                                          is_arr=False,
                                          is_compl=False,
                                          is_dict=False,
                                          type_id="1",
                                          node_variable=offer_var.variableName,
                                          name=new_var_in.parameterName,
                                          outer_variable_id=search_response.offerVariables[0]["id"],
                                          param_id=new_var_in.parameterId)
    output_var_mapping = variables_for_node(node_type="offer_output",
                                            is_arr=True,
                                            is_compl=True,
                                            is_dict=False,
                                            type_id=complex_type.versionId,
                                            node_variable=new_var_out.parameterName,
                                            name=new_var_out.parameterName,
                                            param_id=new_var_out.parameterId)
    node_offer_properties = offer_properties(offer_id=search_response.id,
                                             offer_version_id=search_response.versionId,
                                             offer_variables=[],
                                             node_variables_mapping=[node_var_mapping],
                                             output_variable_mapping=output_var_mapping)
    update_body = offer_node_construct(x=700, y=202.22915649414062,
                                       node_id=str(node_offer.uuid),
                                       temp_version_id=temp_version_id,
                                       properties=node_offer_properties,
                                       operation="update")
    update_node(super_user, node_id=node_offer.uuid, body=update_body)
    finish_up_body = node_update_construct(x=1400, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variables])
    update_node(super_user, node_id=node_end.uuid, body=finish_up_body)
    new_diagram_name = "diagram" + "_" + generate_string()
    diagram_description = 'diagram created in test'
    diagram_data = DiagramCreateNewVersion(diagramId=uuid.UUID(diagram_id),
                                           versionId=temp_version_id,
                                           errorResponseFlag=False,
                                           objectName=new_diagram_name,
                                           diagramDescription=diagram_description)
    response_save = save_diagram(super_user, body=diagram_data)
    create_result: ResponseDto = ResponseDto.construct(**response_save.body)

    yield {"node_start": node_start, "node_end": node_end, "node_offer": node_offer,
           "diagram_in_param": new_var_in, "diagram_out_param": new_var_out, "template": diagram_template,
           "create_result": create_result, "diagram_data": diagram_data,
           "complex_type": complex_type, "script": script_view, "offer": search_response,
           "diagram_id": diagram_id, "diagram_name": new_diagram_name}
    # delete_diagram(super_user, str(create_result.uuid))


@pytest.fixture()
def diagram_offer_submit(super_user,
                         diagram_offer_for_runtime,
                         get_env):
    diagram_id = diagram_offer_for_runtime["diagram_id"]
    version_id = diagram_offer_for_runtime["create_result"].uuid
    diagram_name = diagram_offer_for_runtime["diagram_name"]
    # теперь надо придумать как комплексный тип в переменную сделать
    diagram_param_out = diagram_offer_for_runtime["diagram_out_param"]
    diagram_param_in = diagram_offer_for_runtime["diagram_in_param"]
    put_diagram_submit(super_user, str(diagram_id))
    env_id = get_env.get_env_id("default_dev")
    deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
    return {"deploy_id": deploy_id, "env_id": env_id, "diagram_param_out": diagram_param_out,
            "diagram_param_in": diagram_param_in,
            "diagram_id": diagram_id, "diagram_name": diagram_name}


@pytest.fixture()
def diagram_fork_join_saved(super_user,
                            create_temp_diagram_gen):
    diagram_template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template.inOutParameters[0])
    diagram_id = diagram_template.diagramId
    temp_version_id = diagram_template.versionId
    param_name = "diagram_variable"
    parameter_version_id2 = str(uuid.uuid4())
    new_var = variable_construct(array_flag=False,
                                 complex_flag=False,
                                 default_value=None,
                                 is_execute_status=None,
                                 order_num=0,
                                 param_name=param_name,
                                 parameter_type="in_out",
                                 parameter_version_id=parameter_version_id2,
                                 type_id=1,
                                 parameter_id=parameter_version_id2)
    params_response = update_diagram_parameters(super_user, temp_version_id,
                                                [diagram_exec_var, new_var])
    update_response: ResponseDto = params_response.body

    start_variables = variables_for_node(node_type="start", is_arr=False, is_compl=False,
                                         name=param_name, type_id=1,
                                         vers_id=parameter_version_id2)

    node_start_raw = node_construct(x=-183, y=246, node_type="start",
                                    temp_version_id=temp_version_id,
                                    variables=[start_variables])
    node_finish_raw = node_construct(x=1128, y=721, node_type="finish",
                                     temp_version_id=temp_version_id)
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)

    node_fork = fork_node_construct(x=304,
                                    y=246,
                                    temp_version_id=temp_version_id,
                                    branches=None)
    node_fork_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_fork).body)
    node_fork_id = node_fork_response.uuid

    node_calc1 = node_construct(x=777,
                                y=446,
                                node_type="var_calc",
                                temp_version_id=temp_version_id,
                                variables=None)
    node_calc1_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_calc1).body)
    node_calc1_id = node_calc1_response.uuid

    node_calc2 = node_construct(x=777,
                                y=46,
                                node_type="var_calc",
                                temp_version_id=temp_version_id,
                                variables=None)
    node_calc2_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_calc2).body)
    node_calc2_id = node_calc2_response.uuid

    node_join = join_node_construct(x=1200,
                                    y=246,
                                    temp_version_id=temp_version_id,
                                    branches=None)
    node_join_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_join).body)
    node_join_id = node_join_response.uuid

    link_s_f = link_construct(temp_version_id, node_start.uuid, node_fork_id)
    link_s_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_f).body)
    link_s_f_id = link_s_f_create_response.uuid

    link_f_c1 = link_construct(temp_version_id, node_fork_id, node_calc1_id)
    link_f_c1_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_f_c1).body)
    link_f_c1_id = link_f_c1_create_response.uuid

    link_f_c2 = link_construct(temp_version_id, node_fork_id, node_calc2_id)
    link_f_c2_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_f_c2).body)
    link_f_c2_id = link_f_c2_create_response.uuid

    link_c1_j = link_construct(temp_version_id, node_calc1_id, node_join_id)
    link_c1_j_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_c1_j).body)
    link_c1_j_id = link_c1_j_create_response.uuid

    link_c2_j = link_construct(temp_version_id, node_calc2_id, node_join_id)
    link_c2_j_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_c2_j).body)
    link_c2_j_id = link_c2_j_create_response.uuid

    link_j_e = link_construct(temp_version_id, node_join_id, node_end.uuid)
    link_j_e_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_j_e).body)
    link_j_e_id = link_j_e_create_response.uuid

    fork_branch1 = default_branch(node_calc1_id, link_id=link_f_c1_id)
    fork_branch2 = default_branch(node_calc2_id, link_id=link_f_c2_id)
    def_branch = default_branch(node_join_id)
    node_fork_up_body = fork_node_construct(
        x=304,
        y=246,
        temp_version_id=temp_version_id,
        branches=[fork_branch1, fork_branch2],
        default_join_path=def_branch,
        node_ids_with_join_node_ids=[node_calc1_id, node_calc2_id, ""],
        operation="update",
    )
    update_node(super_user, node_id=node_fork_id, body=node_fork_up_body)

    join_branch1 = join_branch(path=node_calc1_id, priority=1)
    join_branch2 = join_branch(path=node_calc2_id, priority=2)
    node_join_up_body = join_node_construct(
        x=1200,
        y=246,
        temp_version_id=temp_version_id,
        branches=[join_branch1, join_branch2],
        join_condition_type=JoinConditionType.COMPLETION_OF_ALL_PREVIOUS_BLOCKS,
        timeout=6000,
        operation="update",
    )
    update_node(super_user, node_id=node_join_id, body=node_join_up_body)

    node_fork_view: NodeViewWithVariablesDto = (
        NodeViewWithVariablesDto.construct(
            **get_node_by_id(super_user, node_fork_id).body
        )
    )

    node_calc_var_name = "some_v"
    node_calc1_var = variables_for_node(
        node_type="var_calc",
        is_arr=False,
        is_compl=False,
        name=node_calc_var_name,
        type_id=1,
        calc_val="1",
        calc_type_id="2"
    )
    node_calc1_upd = node_update_construct(
        x=777,
        y=446,
        node_type="var_calc",
        temp_version_id=temp_version_id,
        variables=[node_calc1_var],
    )
    update_node(
        super_user, node_id=node_calc1_id, body=node_calc1_upd
    )
    node_calc2_var = variables_for_node(
        node_type="var_calc",
        is_arr=False,
        is_compl=False,
        name=node_calc_var_name,
        type_id=1,
        calc_val="2",
        calc_type_id="2"
    )
    node_calc2_upd = node_update_construct(
        x=777,
        y=46,
        node_type="var_calc",
        temp_version_id=temp_version_id,
        variables=[node_calc2_var],
    )
    update_node(
        super_user, node_id=node_calc2_id, body=node_calc2_upd
    )

    finish_variable = variables_for_node(node_type="finish_out", is_arr=False, is_compl=False,
                                         name=node_calc_var_name,
                                         param_name=param_name,
                                         type_id=1,
                                         vers_id=parameter_version_id2)
    finish_up_body = node_update_construct(x=1128, y=721,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variable])
    update_node(
        super_user, node_id=node_end.uuid, body=finish_up_body
    )

    new_diagram_name = "diagram" + "_" + generate_string()
    diagram_description = 'diagram created in test'

    response_save = save_diagram(super_user, body=DiagramCreateNewVersion(diagramId=diagram_id,
                                                                          versionId=temp_version_id,
                                                                          errorResponseFlag=False,
                                                                          objectName=new_diagram_name,
                                                                          diagramDescription=diagram_description))

    create_result: ResponseDto = response_save.body

    saved_version_id = create_result["uuid"]

    yield {"template": diagram_template,
           "diagram_name": new_diagram_name,
           "diagram_param": new_var,
           "node_fork_id": node_fork_id,
           "node_join_id": node_join_id,
           "node_calc1_id": node_calc1_id,
           "node_calc2_id": node_calc2_id,
           "link_s_f_id": link_s_f_id,
           "link_f_c1_id": link_f_c1_id,
           "link_f_c2_id": link_f_c2_id,
           "link_c1_j_id": link_c1_j_id,
           "link_c2_j_id": link_c2_j_id,
           "link_j_e_id": link_j_e_id,
           "node_end_id": node_end.uuid}

    delete_diagram(super_user, str(saved_version_id))


@pytest.fixture()
def diagram_fork_join_submit(super_user, diagram_fork_join_saved, get_env):
    diagram_id = diagram_fork_join_saved["template"].diagramId
    diagram_param: DiagramInOutParameterFullViewDto = diagram_fork_join_saved["diagram_param"]
    diagram_name = diagram_fork_join_saved["diagram_name"]
    put_diagram_submit(super_user, diagram_id)
    deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
    env_id = get_env.get_env_id("default_dev")
    return {"deploy_id": deploy_id, "diagram_param": diagram_param,
            "env_id": env_id, "diagram_id": diagram_id,
            "diagram_name": diagram_name}


@pytest.fixture()
def diagram_external_service_saved(super_user, create_temp_diagram_gen, get_env,
                                   create_service_gen, save_diagrams_gen):
    env_id = get_env.get_env_id("default_dev")

    setting = service_setting_construct(environment_settings_id=env_id,
                                        host="http-ext-service.decision-qa",
                                        service_type=ServiceType.HTTP,
                                        endpoint="/CRE",
                                        port=8080,
                                        second_attempts_cnt=1,
                                        transactions_per_second=1,
                                        interval=10,
                                        timeout=15)

    var_in = service_var_construct(variable_name="firstname",
                                   variable_type=VariableType2.IN,
                                   array_flag=False,
                                   primitive_type_id="2",
                                   complex_type_version_id=None,
                                   source_path="/",
                                   expression="")

    var_out = service_var_construct(variable_name="cat_weight",
                                    variable_type=VariableType2.OUT,
                                    array_flag=False,
                                    primitive_type_id="0",
                                    complex_type_version_id=None,
                                    source_path="weight",
                                    expression="")

    service_name = "ag_service_" + generate_string()
    service = service_construct(protocol=Protocol.REST,
                                sync_type=SyncType.SYNC,
                                service_name=service_name,
                                batch_flag=False,
                                description=None,
                                file_format=FileFormat.JSON,
                                method=Method.GET,
                                body="{\"name\":$firstname}",
                                service_settings=[setting],
                                headers=[ExternalServiceHeaderViewWithoutIdDto(headerName='passport',
                                                                               headerValue='cre.txt')],
                                variables=[var_in, var_out])

    create_response: ResponseDto = create_service_gen.create_service(service)

    service: ExternalServiceFullViewDto = ExternalServiceFullViewDto.construct(
        **find_service_by_id(super_user, create_response.uuid).body)

    diagram_template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template.inOutParameters[0])
    diagram_id = diagram_template.diagramId
    temp_version_id = diagram_template.versionId
    in_param_name = "in_s"
    in_parameter_version_id = str(uuid.uuid4())
    out_param_name = "out_d"
    out_parameter_version_id = str(uuid.uuid4())
    inp_diagram_var = variable_construct(array_flag=False,
                                         complex_flag=False,
                                         default_value=None,
                                         is_execute_status=None,
                                         order_num=0,
                                         param_name=in_param_name,
                                         parameter_type="in",
                                         parameter_version_id=in_parameter_version_id,
                                         type_id=2,
                                         parameter_id=in_parameter_version_id
                                         )
    out_diagram_var = variable_construct(array_flag=False,
                                         complex_flag=False,
                                         default_value=None,
                                         is_execute_status=None,
                                         order_num=0,
                                         param_name=out_param_name,
                                         parameter_type="out",
                                         parameter_version_id=out_parameter_version_id,
                                         type_id=0,
                                         parameter_id=out_parameter_version_id
                                         )
    update_diagram_parameters(super_user, str(temp_version_id),
                              [diagram_exec_var, inp_diagram_var, out_diagram_var])

    start_variable = variables_for_node(node_type="start",
                                        is_arr=False,
                                        is_compl=False,
                                        name=in_param_name,
                                        type_id=2,
                                        vers_id=in_parameter_version_id)
    finish_variable = variables_for_node(node_type="finish",
                                         is_arr=False,
                                         is_compl=False,
                                         name=out_param_name,
                                         type_id=0,
                                         vers_id=out_parameter_version_id)

    node_start_raw = node_construct(-183, 246, "start", temp_version_id, [start_variable])
    node_finish_raw = node_construct(1128, 721, "finish", temp_version_id, [finish_variable])
    node_start_response = create_node(super_user, node_start_raw)
    node_start: ResponseDto = ResponseDto.construct(**node_start_response.body)
    node_end_response = create_node(super_user, node_finish_raw)
    node_end: ResponseDto = ResponseDto.construct(**node_end_response.body)

    node_ext_serv = external_service_node_construct(x=700, y=202.22915649414062, temp_version_id=temp_version_id)
    node_ext_response: ResponseDto = ResponseDto.construct(**create_node(super_user, node_ext_serv).body)
    node_ext_id = node_ext_response.uuid

    link_s_e = link_construct(temp_version_id, node_start.uuid, node_ext_id)
    link_s_e_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_s_e).body)
    link_s_e_id = link_s_e_create_response.uuid

    link_e_f = link_construct(temp_version_id, node_ext_id, node_end.uuid)
    link_e_f_create_response: ResponseDto = ResponseDto.construct(**create_link(super_user, body=link_e_f).body)
    link_e_f_id = link_e_f_create_response.uuid

    mapping_properties: ExternalService = remap_external_service_node(super_user, node_id=node_ext_id,
                                                                      service_id=service.serviceId,
                                                                      service_version_id=service.versionId)
    for var in mapping_properties.outputVariablesMapping:
        if var.nodeVariable != "externalServiceStatusCode":
            var.variableName = out_diagram_var.parameterName
            var.id = out_diagram_var.parameterId

    mapping_properties.inputVariablesMapping[0].variableName = inp_diagram_var.parameterName
    mapping_properties.inputVariablesMapping[0].id = inp_diagram_var.parameterId
    node_up = external_service_node_construct(
        x=700,
        y=202.22915649414062,
        temp_version_id=temp_version_id,
        properties=mapping_properties,
        operation="update",
    )
    update_node(super_user, node_id=node_ext_id, body=node_up)

    finish_up_body = node_update_construct(x=1128, y=721,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=[finish_variable])
    update_node(
        super_user, node_id=node_end.uuid, body=finish_up_body
    )

    new_diagram_name = "ag_diagram_ext_s" + "_" + generate_string()
    diagram_description = 'diagram created in test'

    create_result = save_diagrams_gen.save_diagram(
        diagram_id, temp_version_id, new_diagram_name, diagram_description
    ).body
    saved_version_id = create_result["uuid"]

    return {"template": diagram_template,
            "diagram_name": new_diagram_name,
            "in_diagram_param": inp_diagram_var,
            "out_diagram_param": out_diagram_var,
            "external_service": service,
            "diagram_id": diagram_id,
            "saved_version_id": saved_version_id,
            "service": service,
            "node_service": node_ext_response}


@pytest.fixture()
def diagram_ext_serv_submit(super_user, diagram_external_service_saved, get_env):
    diagram_id = diagram_external_service_saved["template"].diagramId
    in_diagram_param: DiagramInOutParameterFullViewDto = diagram_external_service_saved["in_diagram_param"]
    out_diagram_param: DiagramInOutParameterFullViewDto = diagram_external_service_saved["out_diagram_param"]
    diagram_name = diagram_external_service_saved["diagram_name"]
    put_diagram_submit(super_user, diagram_id)
    deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
    env_id = get_env.get_env_id("default_dev")
    return {"deploy_id": deploy_id, "in_diagram_param": in_diagram_param,
            "out_diagram_param": out_diagram_param,
            "env_id": env_id, "diagram_id": diagram_id,
            "diagram_name": diagram_name}


@pytest.fixture(scope='function')
def deploy_diagrams_gen(super_user):
    class SendDeploy:
        deployed_ids = []

        @staticmethod
        def deploy_diagram(deploy_id, env_id):
            config: DeployConfigurationFullDto = DeployConfigurationFullDto.construct(
                **deploy_config(super_user, deploy_version_id=deploy_id))
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
            response: DeployViewDto = start_deploy_async(super_user, deploy_id, env_id,
                                                         body=[config])
            SendDeploy.deployed_ids.append(deploy_id)
            return {"deploy_reponse": response, "config": config}

        @staticmethod
        def deploy_multiple_diagram(deploy_ids: list, env_id):
            configs: list[DeployConfigurationFullDto] = [
                DeployConfigurationFullDto.construct(**config)
                for config in deploy_configs(super_user, deploy_ids=deploy_ids)
            ]
            response: list[DeployViewDto] = start_multiple_diagram_deploy(super_user, deploy_ids=deploy_ids,
                                                                          environment_id=env_id,
                                                                          body=configs)
            SendDeploy.deployed_ids.extend(deploy_ids)
            return {"deploy_response": response, "configs": configs}

    yield SendDeploy

    for deployed_id in SendDeploy.deployed_ids:
        try:
            stop_deploy(super_user, deployed_id)
        except:
            print("already stopped")


@pytest.fixture()
def create_python_code_int_vars(super_user):
    inp_var = script_vars_construct(var_name="input_int",
                                    var_type=VariableType1.IN,
                                    is_array=False, primitive_id="1")
    out_var = script_vars_construct(var_name="output_int",
                                    var_type=VariableType1.OUT,
                                    is_array=False, primitive_id="1")
    script_text = "output_int = input_int + 2"
    script_name = "test_python_script_" + generate_string()
    script = code_construct(script_type="python",
                            script_name=script_name,
                            script_text=script_text,
                            variables=[inp_var, out_var])
    python_code_create_result = ScriptFullView.construct(**create_python_script(super_user, body=script).body)
    script_view = ScriptFullView.construct(
        **get_python_script_by_id(super_user, python_code_create_result.versionId).body)
    input_var_with_id = None
    output_var_with_id = None
    variables = []
    for var in script_view.variables:
        variables.append(ScriptVariableFullView.construct(**var))
    for var in variables:
        if var.variableType == "IN":
            input_var_with_id = var
        if var.variableType == "OUT":
            output_var_with_id = var

    yield {"code_create_result": python_code_create_result, "code_view": script_view,
           "out_var": output_var_with_id, "inp_var": input_var_with_id, "script_name": script_name,
           "script_text": script_text}

    # object_type = ObjectType.CUSTOM_CODE_RELATION.value
    # related_objects_response = get_objects_relation_by_object_id(
    #     super_user, object_type, script_view.scriptId
    # )
    # if related_objects_response.status != 204:
    #     for rel in related_objects_response.body["content"]:
    #         if rel["objectToType"] == ObjectType.COMMUNICATION_CHANNEL.value:
    #             delete_communication(super_user, version_id=rel["objectToVersionId"])
    #
    # delete_script_by_id(super_user, python_code_create_result.versionId)


@pytest.fixture()
def create_groovy_code_int_vars(super_user):
    inp_var = script_vars_construct(var_name="input_int",
                                    var_type=VariableType1.IN,
                                    is_array=False, primitive_id="1")
    out_var = script_vars_construct(var_name="output_int",
                                    var_type=VariableType1.OUT,
                                    is_array=False, primitive_id="1")
    script_text = "output_int = input_int + 2"
    script_name = "test_groovy_script_" + generate_string()
    script = code_construct(script_type="groovy",
                            script_name=script_name,
                            script_text=script_text,
                            variables=[inp_var, out_var])
    groovy_code_create_result = ScriptFullView.construct(**create_groovy_script(super_user, body=script).body)
    script_view = ScriptFullView.construct(
        **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body)
    input_var_with_id = None
    output_var_with_id = None
    variables = []
    for var in script_view.variables:
        variables.append(ScriptVariableFullView.construct(**var))
    for var in variables:
        if var.variableType == "IN":
            input_var_with_id = var
        if var.variableType == "OUT":
            output_var_with_id = var

    yield {"code_create_result": groovy_code_create_result, "code_view": script_view,
           "out_var": output_var_with_id, "inp_var": input_var_with_id, "script_name": script_name,
           "script_text": script_text}

    # object_type = ObjectType.CUSTOM_CODE_RELATION.value
    # related_objects_response = get_objects_relation_by_object_id(
    #     super_user, object_type, script_view.scriptId
    # )
    # if related_objects_response.status != 204:
    #     for rel in related_objects_response.body["content"]:
    #         if rel["objectToType"] == ObjectType.COMMUNICATION_CHANNEL.value:
    #             delete_communication(super_user, version_id=rel["objectToVersionId"])
    # delete_script_by_id(super_user, groovy_code_create_result.versionId)


@pytest.fixture(scope="class")
def create_communication_gen(super_user):
    class CreateComm:
        version_ids = []

        @staticmethod
        def create_communication_channel(communication_channel_body):
            create_response: ResponseDto = ResponseDto.construct(
                **create_communication(super_user, body=communication_channel_body).body)
            CreateComm.version_ids.append(create_response.uuid)

            return create_response

        @staticmethod
        def create_channel_in_catalog(catalog_id):
            inp_var = script_vars_construct(var_name="input_int",
                                            var_type=VariableType1.IN,
                                            is_array=False, primitive_id="1")
            out_var = script_vars_construct(var_name="output_int",
                                            var_type=VariableType1.OUT,
                                            is_array=False, primitive_id="1")
            script_text = "output_int = input_int + 2"
            script_name = "test_groovy_script_" + generate_string()
            script = code_construct(script_type="groovy",
                                    script_name=script_name,
                                    script_text=script_text,
                                    variables=[inp_var, out_var])
            groovy_code_create_result = ScriptFullView.construct(**create_groovy_script(super_user, body=script).body)
            script_view = ScriptFullView.construct(
                **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body)
            channel_name = "channel_" + generate_string()
            var = communication_var_construct(variable_name="comm_v",
                                              script_var_name=inp_var.variableName,
                                              primitive_type_id=inp_var.primitiveTypeId,
                                              data_source_type=DataSourceType1.USER_INPUT)
            comm = communication_construct(communication_channel_name=channel_name,
                                           script_version_id=script_view.versionId,
                                           communication_variables=[var],
                                           description="made_in_test",
                                           catalog_id=catalog_id)
            create_response: ResponseDto = ResponseDto.construct(
                **create_communication(super_user, body=comm).body)
            search_response = CommunicationChannelFullViewDto.construct(
                **get_communication_channel(super_user, version_id=create_response.uuid).body)

            return search_response

        @staticmethod
        def try_create_communication_channel(communication_channel_body):
            create_resp = create_communication(super_user, body=communication_channel_body)
            if create_resp.status == 201:
                version_id = ResponseDto.construct(**create_resp.body).uuid
                CreateComm.version_ids.append(version_id)

            return create_resp

        @staticmethod
        def create_user_version(version_id, user_version_body):
            create_response: ResponseDto = ResponseDto.construct(
                **create_channel_user_version(super_user,
                                              version_id=version_id,
                                              body=user_version_body).body)
            CreateComm.version_ids.append(create_response.uuid)

            return create_response

    yield CreateComm

    # for vers_id in CreateComm.version_ids:
    #     delete_communication(super_user, version_id=vers_id)


@pytest.fixture(scope='class')
def create_dict_gen(super_user):
    class CreateDict:
        dict_ids = []

        @staticmethod
        def create_dict(dict_body):
            create_response: ResponseDto = ResponseDto.construct(
                **create_custom_attribute(super_user, body=dict_body).body)
            CreateDict.dict_ids.append(create_response.uuid)

            return create_response

        @staticmethod
        def try_create_dict(dict_body):
            create_resp = create_custom_attribute(super_user, body=dict_body)
            if create_resp.status == 201:
                dict_id = ResponseDto.construct(**create_resp.body).uuid
                CreateDict.dict_ids.append(dict_id)

            return create_resp

    yield CreateDict

    for d_id in CreateDict.dict_ids:
        try:
            delete_custom_attribute(super_user, dict_id=d_id)
        except:
            print("can't delete dictionary")


@pytest.fixture()
def custom_code_communication(super_user):
    script_inp_date_time_var = script_vars_construct(
        var_name="date_time_in_attr",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="5",
    )
    script_inp_time_var = script_vars_construct(
        var_name="time_in_attr",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="6",
    )
    script_inp_str_restrict_var = script_vars_construct(
        var_name="str_in_attr_restrict",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="2",
    )
    script_inp_long_var_us_input = script_vars_construct(
        var_name="long_in_attr_us_input",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="7",
    )
    script_inp_str_dict_var = script_vars_construct(
        var_name="str_in_attr_dict",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="2",
    )
    script_inp_bool_var = script_vars_construct(
        var_name="bool_in_attr",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="4",
    )
    script_inp_date_var = script_vars_construct(
        var_name="date_in_attr",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="3",
    )
    script_inp_double_restrict_var = script_vars_construct(
        var_name="double_in_attr_restrict",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="0",
    )
    script_inp_int_dict_var = script_vars_construct(
        var_name="int_in_attr_dict",
        var_type=VariableType1.IN,
        is_array=False,
        primitive_id="1",
    )
    script_out_date_time_var = script_vars_construct(
        var_name="date_time_out_attr",
        var_type=VariableType1.OUT,
        is_array=False,
        primitive_id="5",
    )
    script_out_date_var = script_vars_construct(
        var_name="date_out_attr",
        var_type=VariableType1.OUT,
        is_array=False,
        primitive_id="3",
    )
    script_out_bool_var = script_vars_construct(
        var_name="bool_out_attr",
        var_type=VariableType1.OUT,
        is_array=False,
        primitive_id="4",
    )
    script_out_time_var = script_vars_construct(
        var_name="time_out_attr",
        var_type=VariableType1.OUT,
        is_array=False,
        primitive_id="6",
    )
    script_text = f"bool_out_attr = {script_inp_bool_var.variableName}" \
                  f"\ndate_time_out_attr = {script_inp_date_time_var.variableName}" \
                  f"\ntime_out_attr = {script_inp_time_var.variableName}" \
                  f"\ndate_out_attr = {script_inp_date_var.variableName}"

    script_name = "test_groovy_script_" + generate_string()
    script = code_construct(script_type="groovy",
                            script_name=script_name,
                            script_text=script_text,
                            variables=[script_inp_date_time_var, script_inp_time_var, script_inp_str_restrict_var,
                                       script_inp_long_var_us_input, script_inp_str_dict_var, script_inp_bool_var,
                                       script_inp_date_var, script_inp_double_restrict_var, script_inp_int_dict_var,
                                       script_out_date_time_var, script_out_date_var, script_out_bool_var,
                                       script_out_time_var])
    groovy_code_create_result = ScriptFullView.construct(**create_groovy_script(super_user, body=script).body)
    script_view = ScriptFullView.construct(
        **get_groovy_script_by_id(super_user, groovy_code_create_result.versionId).body)
    variables = []
    for var in script_view.variables:
        variables.append(ScriptVariableFullView.construct(**var))
    variables_with_ids: dict[str, ScriptVariableFullView] = {}
    for var in variables:
        variables_with_ids[var.variableName] = var
    inout_var_with_id = []
    for var in variables:
        inout_var_with_id.append(var)

    inp_date_time_var: ScriptVariableFullView = variables_with_ids[script_inp_date_time_var.variableName]
    inp_time_var: ScriptVariableFullView = variables_with_ids[script_inp_time_var.variableName]
    inp_str_restrict_var: ScriptVariableFullView = variables_with_ids[script_inp_str_restrict_var.variableName]
    inp_long_var_us_input: ScriptVariableFullView = variables_with_ids[script_inp_long_var_us_input.variableName]
    inp_str_dict_var: ScriptVariableFullView = variables_with_ids[script_inp_str_dict_var.variableName]
    inp_bool_var: ScriptVariableFullView = variables_with_ids[script_inp_bool_var.variableName]
    inp_date_var: ScriptVariableFullView = variables_with_ids[script_inp_date_var.variableName]
    inp_double_restrict_var: ScriptVariableFullView = variables_with_ids[script_inp_double_restrict_var.variableName]
    inp_int_dict_var: ScriptVariableFullView = variables_with_ids[script_inp_int_dict_var.variableName]
    out_date_time_var: ScriptVariableFullView = variables_with_ids[script_out_date_time_var.variableName]
    out_date_var: ScriptVariableFullView = variables_with_ids[script_out_date_var.variableName]
    out_bool_var: ScriptVariableFullView = variables_with_ids[script_out_bool_var.variableName]
    out_time_var: ScriptVariableFullView = variables_with_ids[script_out_time_var.variableName]

    return {"code_view": script_view, "script_name": script_name, "script_text": script_text,
            "inp_date_time_var": inp_date_time_var, "inp_time_var": inp_time_var,
            "inp_str_restrict_var": inp_str_restrict_var, "inp_long_var_us_input": inp_long_var_us_input,
            "inp_str_dict_var": inp_str_dict_var, "inp_bool_var": inp_bool_var, "inp_date_var": inp_date_var,
            "inp_double_restrict_var": inp_double_restrict_var, "inp_int_dict_var": inp_int_dict_var,
            "out_date_time_var": out_date_time_var, "out_date_var": out_date_var, "out_bool_var": out_bool_var,
            "out_time_var": out_time_var, "inout_var_with_id": inout_var_with_id}


@pytest.fixture()
def diagram_constructor(super_user,
                        create_temp_diagram_gen,
                        create_custom_types_gen,
                        create_offer_gen,
                        save_diagrams_gen,
                        request):
    """
    Выполняет определенные операции и возвращает словарь, содержащий различную информацию.
    Returns:
        dict: Словарь, содержащий следующие пары ключ-значение:

            "node_end_id": Идентификатор узла завершения.

            "temp_version_id": Идентификатор временной версии.

            "diagram_id": Идентификатор диаграммы.

            "diagram_exec_var": Переменная выполнения диаграммы.

            "diagram_info": Информация о диаграмме. DiagramViewDto

            "nodes_info": Информация об узлах. list[NodeViewShortInfo]

            "vars_info": Информация о переменных. DiagramInOutParameterFullViewDto

            "saved_data" : Сохраненные данные. DiagramViewDto

            "complex_type": Информация о сложном типе. ComplexTypeGetFullView

            "var_complex_types": Информация о сложных типах переменных. dict[str, ComplexTypeGetFullView]

            "type_attributes": Атрибуты сложных типов. dict[str, AttributeShortView]

            "inner_complex_type": Информация о внутренних сложных типах. ComplexTypeGetFullView

            "offer": Информация о предложении. OfferFullViewDto

            "script": Информация о сценарии. ScriptFullView

            "script_inp_var": Входная переменная для сценария. ScriptVariableFullView

            "script_out_var": Выходная переменная для сценария. ScriptVariableFullView

            "nodes": Информация об узлах. dict[str, NodeViewShortInfo]

            "variables": Информация о переменных. dict[str, DiagramInOutParameterFullViewDto]

            "links": Информация о связях с именами. list[LinkViewDto]
    """
    diagram_template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
    diagram_id = diagram_template.diagramId
    temp_version_id = diagram_template.versionId
    diagram_exec_var: DiagramInOutParameterFullViewDto = DiagramInOutParameterFullViewDto.construct(
        **diagram_template.inOutParameters[0])

    variable_marker = request.node.get_closest_marker("variable_data")
    node_full_marker = request.node.get_closest_marker("node_full_info")
    nodes_marker = request.node.get_closest_marker("nodes")
    save_marker = request.node.get_closest_marker("save_diagram")

    complex_type = None
    inner_complex_type = None
    script = None
    offer = None
    script_inp_v = None
    script_out_v = None
    start_vars = []
    finish_vars = []
    diagram_vars_in: list[DiagramInOutParameterFullViewDto] = []
    diagram_vars_out: list[DiagramInOutParameterFullViewDto] = [diagram_exec_var]
    links: list[LinkViewDto] = []
    nodes: dict[str, NodeViewShortInfo] = {}
    variables: dict[str, DiagramInOutParameterFullViewDto] = {}
    links_with_names: dict[str, str] = {}
    var_complex_types: dict[str, ComplexTypeGetFullView] = {}
    cmplx_type_attrs: dict[str, AttributeShortView] = {}
    save_data: DiagramViewDto = None

    if variable_marker is None:
        vers_id_in = str(uuid.uuid4())
        vers_id_out = str(uuid.uuid4())
        in_int_var = variable_construct(array_flag=False,
                                        complex_flag=False,
                                        default_value=None,
                                        is_execute_status=None,
                                        order_num=1,
                                        param_name="in_int_v",
                                        parameter_type="in",
                                        parameter_version_id=vers_id_in,
                                        type_id=1,
                                        parameter_id=vers_id_in)
        out_int_var = variable_construct(array_flag=False,
                                         complex_flag=False,
                                         default_value=None,
                                         is_execute_status=None,
                                         order_num=2,
                                         param_name="out_int_v",
                                         parameter_type="out",
                                         parameter_version_id=vers_id_out,
                                         type_id=1,
                                         parameter_id=vers_id_out)
        finish_vars.append(variables_for_node(node_type="finish_out", is_arr=False, is_compl=False,
                                              name="1",
                                              param_name=out_int_var.parameterName,
                                              type_id=out_int_var.typeId,
                                              vers_id=out_int_var.parameterVersionId))
        start_vars.append(variables_for_node(node_type="start", is_arr=False, is_compl=False,
                                             name=in_int_var.parameterName,
                                             type_id=in_int_var.typeId,
                                             vers_id=in_int_var.parameterVersionId))
        diagram_vars_in.append(in_int_var)
        diagram_vars_out.append(out_int_var)
        # defaults
    else:
        var_data: list[VariableParams] = variable_marker.args[0]
        order_num = 1

        for data in var_data:
            order_num += 1
            vers_id = str(uuid.uuid4())
            if not data.isComplex:
                var = variable_construct(array_flag=data.isArray,
                                         complex_flag=False,
                                         default_value=None,
                                         is_execute_status=None,
                                         order_num=order_num,
                                         param_name=data.varName,
                                         parameter_type=data.varType,
                                         parameter_version_id=vers_id,
                                         type_id=data.varDataType,
                                         parameter_id=vers_id)
                # primitives
                if data.varType.lower() == "in":
                    diagram_vars_in.append(var)
                    start_vars.append(variables_for_node(node_type="start", is_arr=var.arrayFlag, is_compl=False,
                                                         name=var.parameterName,
                                                         type_id=var.typeId,
                                                         vers_id=var.parameterVersionId))

                if data.varType.lower() == "out":
                    var_value = None
                    literal_flag = None
                    if data.isConst:
                        literal_flag = True
                        if str(data.varDataType) == "0":
                            var_value = "1.0"
                        if str(data.varDataType) == "1":
                            var_value = "1"
                        if str(data.varDataType) == "2":
                            var_value = "'some_string'"
                        if str(data.varDataType) == "3":
                            var_value = "'2023-04-23'"
                        if str(data.varDataType) == "4":
                            var_value = "'true'"
                        if str(data.varDataType) == "5":
                            var_value = "'2023-04-24 17:06:13'"
                        if str(data.varDataType) == "6":
                            var_value = "'09:00:00'"
                        if str(data.varDataType) == "7":
                            var_value = "1"
                    else:
                        var_value = data.varValue
                    diagram_vars_out.append(var)
                    if var_value == var.parameterName:
                        finish_vars.append(
                            variables_for_node(node_type="finish_out", is_arr=data.isArray, is_compl=False,
                                               name=var_value,
                                               param_name=var.parameterName,
                                               type_id=var.typeId,
                                               vers_id=var.parameterVersionId,
                                               param_id=var.parameterId))
                    else:
                        finish_vars.append(
                            variables_for_node(node_type="finish_out", is_arr=data.isArray, is_compl=False,
                                               name=var_value,
                                               param_name=var.parameterName,
                                               type_id=var.typeId,
                                               vers_id=var.parameterVersionId,
                                               is_literal=literal_flag))
                if data.varType.lower() == "in_out":
                    start_vars.append(variables_for_node(node_type="start", is_arr=var.arrayFlag, is_compl=False,
                                                         name=var.parameterName,
                                                         type_id=var.typeId,
                                                         vers_id=var.parameterVersionId))
                    var_value = None
                    literal_flag = None
                    if data.isConst:
                        literal_flag = True
                        if str(data.varDataType) == "0":
                            var_value = "1.0"
                        if str(data.varDataType) == "1":
                            var_value = "1"
                        if str(data.varDataType) == "2":
                            var_value = "'some_string'"
                        if str(data.varDataType) == "3":
                            var_value = "'2023-04-23'"
                        if str(data.varDataType) == "4":
                            var_value = "'true'"
                        if str(data.varDataType) == "5":
                            var_value = "'2023-04-24 17:06:13'"
                        if str(data.varDataType) == "6":
                            var_value = "'09:00:00'"
                        if str(data.varDataType) == "7":
                            var_value = "1"
                    else:
                        var_value = data.varValue
                    diagram_vars_out.append(var)
                    if data.varValue != "empty_finish" and var_value != var.parameterName:
                        finish_vars.append(
                            variables_for_node(node_type="finish_out", is_arr=data.isArray, is_compl=False,
                                               name=var_value,
                                               param_name=var.parameterName,
                                               type_id=var.typeId,
                                               vers_id=var.parameterVersionId, is_literal=literal_flag))
                    if data.varValue != "empty_finish" and var_value == var.parameterName:
                        finish_vars.append(
                            variables_for_node(node_type="finish_out", is_arr=data.isArray, is_compl=False,
                                               name=var_value,
                                               param_name=var.parameterName,
                                               type_id=var.typeId,
                                               vers_id=var.parameterVersionId,
                                               param_id=var.parameterId))

            else:
                # activate complex var
                if data.isConst:
                    type_name = "ag_test_type_" + generate_string()
                    attr = attribute_construct()
                    create_result: ResponseDto = create_custom_types_gen.create_type(type_name, [attr])
                    custom_type_version_id = create_result.uuid
                    complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                        **get_custom_type(super_user, custom_type_version_id).body
                    )
                    var_complex_types[f"{data.varName}"] = complex_type
                    complex_var = variable_construct(array_flag=data.isArray,
                                                     complex_flag=True,
                                                     default_value=None,
                                                     is_execute_status=None,
                                                     order_num=order_num,
                                                     param_name=data.varName,
                                                     parameter_type=data.varType,
                                                     parameter_version_id=vers_id,
                                                     type_id=custom_type_version_id,
                                                     parameter_id=vers_id)
                    if data.varType.lower() == "in":
                        diagram_vars_in.append(complex_var)
                        start_vars.append(variables_for_node(node_type="start", is_arr=complex_var.arrayFlag,
                                                             is_compl=True,
                                                             name=complex_var.parameterName,
                                                             type_id=complex_var.typeId,
                                                             vers_id=complex_var.parameterVersionId))
                        in_complex_var = complex_var
                    if data.varType.lower() == "out":
                        diagram_vars_out.append(complex_var)
                        finish_vars.append(
                            variables_for_node(node_type="finish_out", is_arr=data.isArray, is_compl=True,
                                               name=complex_var.parameterName,
                                               param_name=complex_var.parameterName,
                                               type_id=complex_var.typeId,
                                               vers_id=complex_var.parameterVersionId,
                                               param_id=complex_var.parameterId))
                    if data.varType.lower() == "in_out":
                        diagram_vars_in.append(complex_var)
                        start_vars.append(variables_for_node(node_type="start", is_arr=complex_var.arrayFlag,
                                                             is_compl=True,
                                                             name=complex_var.parameterName,
                                                             type_id=complex_var.typeId,
                                                             vers_id=complex_var.parameterVersionId))
                        finish_vars.append(
                            variables_for_node(node_type="finish_out", is_arr=data.isArray, is_compl=True,
                                               name=complex_var.parameterName,
                                               param_name=complex_var.parameterName,
                                               type_id=complex_var.typeId,
                                               vers_id=complex_var.parameterVersionId,
                                               param_id=complex_var.parameterId))
                else:
                    if data.cmplxAttrInfo is not None:
                        attr_list = []
                        real_attr_list = []
                        type_name = "ag_test_type_" + generate_string()
                        for attribute in data.cmplxAttrInfo:
                            attr = attribute_construct(array_flag=attribute.isArray,
                                                       complex_flag=attribute.isComplex,
                                                       complex_type_version_id=attribute.complexTypeVersionId,
                                                       attr_name=attribute.attrName,
                                                       primitive_type_id=attribute.intAttrType)
                            attr_list.append(attr)
                        type_create_result: ResponseDto = create_custom_types_gen.create_type(type_name, attr_list)
                        custom_type_version_id = type_create_result.uuid
                        complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                            **get_custom_type(super_user, custom_type_version_id).body
                        )
                        var_complex_types[f"{data.varName}"] = complex_type
                        for attribute in complex_type.attributes:
                            real_attr_list.append(AttributeShortView.construct(**attribute))
                        for attribute in real_attr_list:
                            cmplx_type_attrs[f"{attribute.attributeName}"] = attribute

                        complex_var = variable_construct(array_flag=data.isArray,
                                                         complex_flag=True,
                                                         default_value=None,
                                                         is_execute_status=None,
                                                         order_num=order_num,
                                                         param_name=data.varName,
                                                         parameter_type=data.varType,
                                                         parameter_version_id=vers_id,
                                                         type_id=complex_type.versionId,
                                                         parameter_id=vers_id)
                        if data.varType.lower() == "out":
                            diagram_vars_out.append(complex_var)
                            finish_vars.append(variables_for_node(node_type="finish", is_arr=True,
                                                                  is_compl=True,
                                                                  name=complex_var.parameterName,
                                                                  type_id=complex_var.typeId,
                                                                  vers_id=complex_var.parameterVersionId,
                                                                  param_id=complex_var.parameterId))
                        elif data.varType.lower() == "in":
                            diagram_vars_in.append(complex_var)
                            start_vars.append(variables_for_node(node_type="start", is_arr=data.isArray,
                                                                 is_compl=True,
                                                                 name=complex_var.parameterName,
                                                                 type_id=complex_var.typeId,
                                                                 vers_id=complex_var.parameterVersionId))
                            in_complex_var = complex_var
                        elif data.varType.lower() == "in_out":
                            diagram_vars_in.append(complex_var)
                            start_vars.append(variables_for_node(node_type="start", is_arr=data.isArray,
                                                                 is_compl=True,
                                                                 name=complex_var.parameterName,
                                                                 type_id=complex_var.typeId,
                                                                 vers_id=complex_var.parameterVersionId))
                            finish_vars.append(variables_for_node(node_type="finish", is_arr=data.isArray,
                                                                  is_compl=True,
                                                                  name=complex_var.parameterName,
                                                                  type_id=complex_var.typeId,
                                                                  vers_id=complex_var.parameterVersionId,
                                                                  param_id=complex_var.parameterId))

                    else:
                        if data.varType.lower() == "in":
                            if data.varValue == "complex_type_complex_attr":
                                inner_type_name = "ag_test_type_" + generate_string()
                                inner_attr = attribute_construct()
                                inner_create_result: ResponseDto = create_custom_types_gen.create_type(
                                    inner_type_name, [inner_attr])
                                inner_custom_type_version_id = inner_create_result.uuid
                                inner_complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                                    **get_custom_type(super_user, inner_custom_type_version_id).body
                                )
                                type_name = "ag_test_type_" + generate_string()
                                attr = attribute_construct(array_flag=False,
                                                           complex_flag=True,
                                                           attr_name="cmplx_attr",
                                                           complex_type_version_id=inner_complex_type.versionId,
                                                           primitive_type_id=None)
                                create_result: ResponseDto = create_custom_types_gen.create_type(type_name, [attr])
                                custom_type_version_id = create_result.uuid
                                complex_type: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                                    **get_custom_type(super_user, custom_type_version_id).body
                                )
                                var_complex_types[f"{data.varName}"] = complex_type
                                complex_var = variable_construct(array_flag=data.isArray,
                                                                 complex_flag=True,
                                                                 default_value=None,
                                                                 is_execute_status=None,
                                                                 order_num=order_num,
                                                                 param_name=data.varName,
                                                                 parameter_type=data.varType,
                                                                 parameter_version_id=vers_id,
                                                                 type_id=complex_type.versionId,
                                                                 parameter_id=vers_id)
                                diagram_vars_in.append(complex_var)
                                start_vars.append(variables_for_node(node_type="start", is_arr=data.isArray,
                                                                     is_compl=True,
                                                                     name=complex_var.parameterName,
                                                                     type_id=complex_var.typeId,
                                                                     vers_id=complex_var.parameterVersionId))
                                in_complex_var = complex_var
                        elif data.varType.lower() == "out" or data.varType.lower() == "in_out":
                            if data.varValue == "offer_complex_type":
                                offer_data = create_offer_gen.create_full_offer()
                                offer: OfferFullViewDto = offer_data["offer_info"]
                                script: ScriptFullView = offer_data["script_info"]
                                script_inp_v: ScriptVariableFullView = offer_data["script_inp_var"]
                                script_out_v: ScriptVariableFullView = offer_data["script_out_var"]
                                complex_type: ComplexTypeGetFullView = offer_data["offer_c_type"]
                                var_complex_types[f"{data.varName}"] = complex_type
                                complex_var = variable_construct(array_flag=data.isArray,
                                                                 complex_flag=True,
                                                                 default_value=None,
                                                                 is_execute_status=None,
                                                                 order_num=order_num,
                                                                 param_name=data.varName,
                                                                 parameter_type=data.varType,
                                                                 parameter_version_id=vers_id,
                                                                 type_id=complex_type.versionId,
                                                                 parameter_id=vers_id)
                                diagram_vars_out.append(complex_var)
                                finish_vars.append(variables_for_node(node_type="finish", is_arr=True,
                                                                      is_compl=True,
                                                                      name=complex_var.parameterName,
                                                                      type_id=complex_var.typeId,
                                                                      vers_id=complex_var.parameterVersionId,
                                                                      param_id=complex_var.parameterId))
                                out_complex_var = complex_var
                            elif data.varValue == "Task" or data.varValue == "Task_Root" or data.varValue == "Offer":
                                all_types_response: dict = get_data_type_list(super_user).body
                                all_types = [DataTypeGetFullView.construct(**t) for t in all_types_response.values()]
                                found_type: DataTypeGetFullView = None
                                for t in all_types:
                                    if t.displayName == data.varValue:
                                        found_type = t
                                complex_type = ComplexTypeGetFullView.construct(**get_custom_type(super_user,
                                                                                                  found_type.typeId).body)
                                var_complex_types[f"{data.varName}"] = complex_type
                                complex_var = variable_construct(array_flag=data.isArray,
                                                                 complex_flag=True,
                                                                 default_value=None,
                                                                 is_execute_status=None,
                                                                 order_num=order_num,
                                                                 param_name=data.varName,
                                                                 parameter_type=data.varType,
                                                                 parameter_version_id=vers_id,
                                                                 type_id=found_type.typeId,
                                                                 parameter_id=vers_id)
                                diagram_vars_out.append(complex_var)
                                finish_vars.append(variables_for_node(node_type="finish", is_arr=complex_var.arrayFlag,
                                                                      is_compl=True,
                                                                      name=complex_var.parameterName,
                                                                      type_id=complex_var.typeId,
                                                                      vers_id=complex_var.parameterVersionId,
                                                                      param_id=complex_var.parameterId))
                                out_complex_var = complex_var
                            else:
                                complex_var = variable_construct(array_flag=data.isArray,
                                                                 complex_flag=True,
                                                                 default_value=None,
                                                                 is_execute_status=None,
                                                                 order_num=order_num,
                                                                 param_name=data.varName,
                                                                 parameter_type=data.varType,
                                                                 parameter_version_id=vers_id,
                                                                 type_id=data.varDataType,
                                                                 parameter_id=vers_id)
                                diagram_vars_out.append(complex_var)
                                finish_vars.append(variables_for_node(node_type="finish", is_arr=complex_var.arrayFlag,
                                                                      is_compl=True,
                                                                      name=complex_var.parameterName,
                                                                      type_id=complex_var.typeId,
                                                                      vers_id=complex_var.parameterVersionId,
                                                                      param_id=complex_var.parameterId))
                                out_complex_var = complex_var

    update_diagram_parameters(super_user, temp_version_id,
                              diagram_vars_in + diagram_vars_out)
    node_start_raw = node_construct(142, 202, "start", temp_version_id,
                                    variables=start_vars)
    node_finish_raw = node_construct(1800, 202, "finish", temp_version_id,
                                     variables=finish_vars)
    node_start_id = ResponseDto.construct(
        **create_node(super_user, node_start_raw).body).uuid
    node_end_id = ResponseDto.construct(
        **create_node(super_user, node_finish_raw).body).uuid
    finish_up_body = node_update_construct(x=1800, y=202,
                                           temp_version_id=temp_version_id,
                                           node_type="finish",
                                           variables=finish_vars)

    # ветвь с заполненным маркером полной информации об узлах
    if node_full_marker is not None:
        nodes_full_data: list[NodeFullInfo] = node_full_marker.args[0]
        created_nodes = []
        for node in nodes_full_data:
            node_body = empty_node_construct(x=node.coordinates[0], y=node.coordinates[1],
                                             node_type=node.nodeType,
                                             diagram_version_id=temp_version_id,
                                             node_name=node.nodeName)
            node_id = ResponseDto.construct(
                **create_node(super_user, node_body).body).uuid
            created_nodes.append(NodeViewShortInfo.construct(nodeId=node_id,
                                                             nodeName=node_body.nodeName,
                                                             nodeTypeId=node_body.nodeTypeId))

        for node in nodes_full_data:
            # find own node_id
            this_node_id = None
            this_node_name = None
            for created_node in created_nodes:
                if created_node.nodeName == node.nodeName:
                    this_node_id = created_node.nodeId
                    this_node_name = created_node.nodeName
                    break
            next_node_ids = []
            next_nodes: dict[str, str] = {}
            prev_node_ids = []
            prev_nodes: dict[str, str] = {}
            # поиск айдишников, которые подвязываются к текущему узлу
            if node.linksFrom is not None:
                for node_name_for_link in node.linksFrom:
                    if node_name_for_link == "Начало":
                        link = link_construct(temp_version_id, node_start_id, this_node_id)
                        link_id = ResponseDto.construct(
                            **create_link(super_user, body=link).body).uuid
                        links_with_names[f"Начало->{this_node_name}"] = str(link_id)
                    else:
                        for created_node in created_nodes:
                            if node_name_for_link == created_node.nodeName:
                                prev_node_ids.append(created_node.nodeId)
                                prev_nodes[created_node.nodeName] = str(created_node.nodeId)
                                break
            # поиск айдишников, к которым подвязывается текущий узел
            if node.linksTo is not None:
                for node_name_for_link in node.linksTo:
                    if node_name_for_link == "Завершение":
                        link = link_construct(temp_version_id, this_node_id, node_end_id)
                        link_id = ResponseDto.construct(
                            **create_link(super_user, body=link).body).uuid
                        links_with_names[f"{this_node_name}->Завершение"] = str(link_id)
                    else:
                        for created_node in created_nodes:
                            if node_name_for_link == created_node.nodeName:
                                next_node_ids.append(created_node.nodeId)
                                next_nodes[created_node.nodeName] = str(created_node.nodeId)
                                break
            # создание связей
            for p_node_name, p_node_id in prev_nodes.items():
                link = link_construct(temp_version_id, p_node_id, this_node_id)
                link_id = ResponseDto.construct(
                    **create_link(super_user, body=link).body).uuid
                links_with_names[f"{p_node_name}->{this_node_name}"] = str(link_id)
            for n_node_name, n_node_id in next_nodes.items():
                link = link_construct(temp_version_id, this_node_id, n_node_id)
                link_id = ResponseDto.construct(
                    **create_link(super_user, body=link).body).uuid
                links_with_names[f"{this_node_name}->{n_node_name}"] = str(link_id)

    elif nodes_marker is not None:
        node_names: list[str] = nodes_marker.args[0]
        node_ids = []
        base_x = node_start_raw.metaInfo.position.x
        base_y = node_start_raw.metaInfo.position.y
        for i in range(len(node_names)):
            base_x += 650
            node_type_id = None
            if node_names[i].startswith("расчет переменной"):
                node_type_id = IntNodeType.varCalc
            if node_names[i].startswith("кастомный код"):
                node_type_id = IntNodeType.customCode
            if node_names[i].startswith("предложение"):
                node_type_id = IntNodeType.offer
            if node_names[i].startswith("чтение"):
                node_type_id = IntNodeType.jdbcRead
            if node_names[i].startswith("запись"):
                node_type_id = IntNodeType.jdbcWrite
            if node_names[i].startswith("скоркарта"):
                node_type_id = IntNodeType.scorecard
            if node_names[i].startswith("набор правил"):
                node_type_id = IntNodeType.rule
            if node_names[i].startswith("расчет агрегата"):
                node_type_id = IntNodeType.aggregateCompute
            if node_names[i].startswith("чтение агрегата"):
                node_type_id = IntNodeType.aggregateRead
            if node_names[i].startswith("слияние"):
                node_type_id = IntNodeType.join
            if node_names[i].startswith("распараллеливание"):
                node_type_id = IntNodeType.fork
            if node_names[i].startswith("ветвление"):
                node_type_id = IntNodeType.branch
            if node_names[i].startswith("внешний сервис"):
                node_type_id = IntNodeType.externalService
            if node_names[i].startswith("поддиаграмма"):
                node_type_id = IntNodeType.subdiagram
            if node_names[i].startswith("коммуникация"):
                node_type_id = IntNodeType.communication
            if node_names[i].startswith("чтение тарантул"):
                node_type_id = IntNodeType.tarantoolRead
            if node_names[i].startswith("запись тарантул"):
                node_type_id = IntNodeType.tarantoolWrite
            if node_names[i].startswith("запись commhub"):
                node_type_id = IntNodeType.communicationHub
            if node_names[i].startswith("чтение commhub"):
                node_type_id = IntNodeType.commHubRead
            if node_names[i].startswith("запись OS"):
                node_type_id = IntNodeType.offerStorageWrite
            if node_names[i].startswith("чтение OS"):
                node_type_id = IntNodeType.offerStorageRead
            if node_names[i].startswith("проверка policy"):
                node_type_id = IntNodeType.policyRead
            node_body = empty_node_construct(x=base_x, y=base_y,
                                             node_type=node_type_id,
                                             diagram_version_id=temp_version_id,
                                             node_name=node_names[i])
            node_id = ResponseDto.construct(
                **create_node(super_user, node_body).body).uuid
            node_ids.append(node_id)
        if len(node_ids) == 1:
            link_start = link_construct(temp_version_id, node_start_id, node_ids[0])
            link_start_id = ResponseDto.construct(
                **create_link(super_user, body=link_start).body).uuid
            link = link_construct(temp_version_id, node_ids[0], node_end_id)
            link_id = ResponseDto.construct(
                **create_link(super_user, body=link).body).uuid
        elif len(node_ids) == 2:
            link_start = link_construct(temp_version_id, node_start_id, node_ids[0])
            link_start_id = ResponseDto.construct(
                **create_link(super_user, body=link_start).body).uuid
            link = link_construct(temp_version_id, node_ids[0], node_ids[1])
            link_id = ResponseDto.construct(
                **create_link(super_user, body=link).body).uuid
            link_finish = link_construct(temp_version_id, node_ids[1], node_end_id)
            link_id = ResponseDto.construct(
                **create_link(super_user, body=link_finish).body).uuid
        else:
            for i in range(len(node_ids) - 1):
                if i == 0:
                    link_start = link_construct(temp_version_id, node_start_id, node_ids[i])
                    link_start_id = ResponseDto.construct(
                        **create_link(super_user, body=link_start).body).uuid
                    link = link_construct(temp_version_id, node_ids[i], node_ids[i + 1])
                    link_id = ResponseDto.construct(
                        **create_link(super_user, body=link).body).uuid
                elif i == len(node_ids) - 2:
                    link = link_construct(temp_version_id, node_ids[i], node_ids[i + 1])
                    link_id = ResponseDto.construct(
                        **create_link(super_user, body=link).body).uuid
                    link_finish = link_construct(temp_version_id, node_ids[i + 1], node_end_id)
                    link_id = ResponseDto.construct(
                        **create_link(super_user, body=link_finish).body).uuid
                else:
                    link = link_construct(temp_version_id, node_ids[i], node_ids[i + 1])
                    link_id = ResponseDto.construct(
                        **create_link(super_user, body=link).body).uuid

    else:
        link_s_f = link_construct(temp_version_id, node_start_id, node_end_id)
        link_s_f_id = ResponseDto.construct(
            **create_link(super_user, body=link_s_f).body).uuid
        links.append(LinkViewDto.construct(linkId=link_s_f_id,
                                           prevNodeId=node_start_id,
                                           nextNodeId=node_end_id))

    update_node(super_user, node_id=node_end_id, body=finish_up_body)
    get_node_by_id(super_user, node_end_id)

    diagram: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, temp_version_id).body)
    nodes_info = []
    for node in diagram.nodes.values():
        nodes_info.append(NodeViewShortInfo.construct(**node))
    for node in nodes_info:
        if node.nodeName.lower().startswith("начало") or node.nodeName.lower().startswith("завершение"):
            nodes[node.nodeName.lower()] = node
        else:
            nodes[node.nodeName] = node
    vars_info = []
    parameters = get_diagram_parameters(super_user, temp_version_id).body
    for var in parameters["inOutParameters"]:
        vars_info.append(DiagramInOutParameterFullViewDto.construct(**var))
    for var in vars_info:
        variables[var.parameterName] = var

    if save_marker is not None:
        new_diagram_name = "ag_test_diagram_" + generate_string()
        diagram_description = "diagram created in test"
        create_result = save_diagrams_gen.save_diagram(
            diagram_id, temp_version_id, new_diagram_name, diagram_description
        ).body
        saved_version_id = create_result["uuid"]
        save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
            super_user, saved_version_id).body)

    return {"node_end_id": node_end_id,
            "temp_version_id": temp_version_id,
            "diagram_id": diagram_id,
            "diagram_exec_var": diagram_exec_var,
            "diagram_info": diagram,
            "nodes_info": nodes_info,
            "vars_info": vars_info,
            "saved_data": save_data,
            "complex_type": complex_type,
            "var_complex_types": var_complex_types,
            "type_attributes": cmplx_type_attrs,
            "inner_complex_type": inner_complex_type,
            "offer": offer,
            "script": script,
            "script_inp_var": script_inp_v,
            "script_out_var": script_out_v,
            "nodes": nodes,
            "variables": variables,
            "links": links_with_names}


@pytest.fixture()
def diagram_constructor_balalaika(super_user,
                                  create_temp_diagram_gen,
                                  save_diagrams_gen,
                                  request):
    diagram_template: DiagramViewDto = create_temp_diagram_gen.create_template()
    diagram_id = diagram_template.diagramId
    temp_version_id = diagram_template.versionId

    source_marker = request.node.get_closest_marker("source")
    target_marker = request.node.get_closest_marker("target")
    node_full_marker = request.node.get_closest_marker("node_full_info")
    nodes_marker = request.node.get_closest_marker("nodes")
    save_marker = request.node.get_closest_marker("save_diagram")

    links: list[LinkViewDto] = []
    nodes: dict[str, NodeViewShortInfo] = {}

    save_data: DiagramViewDto = None
    node_source_id = None
    node_target_id = None
    data_source_info = None
    data_target_info = None

    # ЗАПОЛНЕНИЕ ИСТОЧНИКА И ПРИЁМНИКА
    if source_marker is not None and target_marker is not None:
        env_id = env_id_by_name(super_user, env_name="default_dev")
        source_data: SourceSettings = source_marker.args[0]
        target_data: TargetSettings = target_marker.args[0]
        source_node_type_id = None
        source_node_name = None
        source_properties = None
        target_node_type_id = None
        target_node_name = None
        target_properties = None
        # НАСТРОЙКИ КАФКИ
        if source_data.sourceType == "kafka":
            source_node_type_id = IntNodeType.kafkaSource
            source_node_name = "Источник - Kafka"
            kafka_param1 = KafkaAdditionalSettingsWithoutIdDto.construct(propertyName="security.protocol",
                                                                         propertyValue="SASL_PLAINTEXT",
                                                                         propertySecure=False)
            kafka_param2 = KafkaAdditionalSettingsWithoutIdDto.construct(propertyName="sasl.mechanism",
                                                                         propertyValue="SCRAM-SHA-512",
                                                                         propertySecure=False)
            kafka_param3 = KafkaAdditionalSettingsWithoutIdDto.construct(propertyName="sasl.jaas.config",
                                                                         propertyValue="org.apache.kafka.common"
                                                                                       ".security.scram"
                                                                                       ".ScramLoginModule required "
                                                                                       "username=\"qa-dev-user\" "
                                                                                       "password=\"fiUXC6rS2Iu953ecF1k3\";",
                                                                         propertySecure=False)
            kafka_settings = KafkaSettingsWithoutIdDto.construct(
                bootstrapServers="datasapience-kafka-bootstrap.kafka:9092",
                environmentId=env_id,
                kafkaAdditionalSettings=[kafka_param2,
                                         kafka_param1,
                                         kafka_param3])
            broker_body = KafkaCreateDto.construct(name="qa_test_kafka_" + generate_string(),
                                                   description=None,
                                                   kafkaSettings=[kafka_settings])
            kafka_create_result = ResponseDto.construct(**create_kafka(super_user, broker_body).body)
            data_source_info: KafkaGetFullViewDto = get_kafka_info(super_user, kafka_create_result.uuid)
            schema_url = None
            if source_data.kafkaSettings.schema is not None:
                scheme_data = source_data.kafkaSettings.schema
                schema_body = schema_construct(name="ag_scheme_" + generate_string(),
                                               schema_data=scheme_data)
                schema_id = SchemaIdDto(**create_schema(super_user, schema_body).body).id
                schema_url = SchemaFullDto(**find_schema_by_id(super_user, schema_id).body).url
            else:
                schema_url = "http://sp:8083/schema/1/content"

            source_properties = kafka_source_construct(kafka_id=data_source_info.id,
                                                       schema_url=schema_url,
                                                       topic=source_data.kafkaSettings.topic,
                                                       start_offsets_type=source_data.kafkaSettings.startOffset,
                                                       stop_offsets_type=source_data.kafkaSettings.stopOffsets,
                                                       parallelism=source_data.kafkaSettings.parallelism)
        if source_data.sourceType == "postgres":
            node_type_id = IntNodeType.postgresCdcSource
            node_name = "Источник - PostgreSQL CDC"
        if source_data.sourceType == "oracle":
            node_type_id = IntNodeType.oracleCdcSource
            node_name = "Источник - Oracle CDC"
        source_node_body = empty_node_construct(x=142, y=202,
                                                node_type=source_node_type_id,
                                                diagram_version_id=temp_version_id,
                                                node_name=source_node_name,
                                                properties=source_properties)
        node_source_id = ResponseDto.construct(
            **create_node(super_user, source_node_body).body).uuid

        if target_data.sourceType == "kafka":
            target_node_type_id = IntNodeType.kafkaSinc
            target_node_name = "Приёмник - Kafka"
            if target_data.isSameAsSource:
                data_target_info = data_source_info
            if not target_data.isSameAsSource:
                t_kafka_param1 = KafkaAdditionalSettingsWithoutIdDto.construct(propertyName="security.protocol",
                                                                               propertyValue="SASL_PLAINTEXT",
                                                                               propertySecure=False)
                t_kafka_param2 = KafkaAdditionalSettingsWithoutIdDto.construct(propertyName="sasl.mechanism",
                                                                               propertyValue="SCRAM-SHA-512",
                                                                               propertySecure=False)
                t_kafka_param3 = KafkaAdditionalSettingsWithoutIdDto.construct(propertyName="sasl.jaas.config",
                                                                               propertyValue="org.apache.kafka.common"
                                                                                             ".security.scram"
                                                                                             ".ScramLoginModule required "
                                                                                             "username=\"qa-dev-user\" "
                                                                                             "password=\"fiUXC6rS2Iu953ecF1k3\";",
                                                                               propertySecure=False)
                t_kafka_settings = KafkaSettingsWithoutIdDto.construct(bootstrapServers=None,
                                                                       environmentId=env_id,
                                                                       kafkaAdditionalSettings=[t_kafka_param2,
                                                                                                t_kafka_param1,
                                                                                                t_kafka_param3])
                t_broker_body = KafkaCreateDto.construct(name="qa_test_kafka_" + generate_string(),
                                                         description=None,
                                                         kafkaSettings=[t_kafka_settings])
                t_kafka_create_result = ResponseDto.construct(**create_kafka(super_user, t_broker_body).body)
                data_target_info: KafkaGetFullViewDto = get_kafka_info(super_user, t_kafka_create_result.uuid)

            target_properties = kafka_target_construct(kafka_id=data_target_info.id,
                                                       topic=target_data.kafkaSettings.topic,
                                                       parallelism=target_data.kafkaSettings.parallelism)
        if source_data.sourceType == "postgres":
            node_type_id = IntNodeType.postgresCdcSource
            node_name = "Источник - PostgreSQL CDC"
        if source_data.sourceType == "oracle":
            node_type_id = IntNodeType.oracleCdcSource
            node_name = "Источник - Oracle CDC"

        target_node_body = empty_node_construct(x=1800, y=202,
                                                node_type=target_node_type_id,
                                                diagram_version_id=temp_version_id,
                                                node_name=target_node_name,
                                                properties=target_properties)
        node_target_id = ResponseDto.construct(
            **create_node(super_user, target_node_body).body).uuid

    # ветвь с заполненным маркером полной информации об узлах
    if node_full_marker is not None:
        nodes_full_data: list[NodeFullInfo] = node_full_marker.args[0]
        created_nodes = []
        for node in nodes_full_data:
            node_body = empty_node_construct(x=node.coordinates[0], y=node.coordinates[1],
                                             node_type=node.nodeType,
                                             diagram_version_id=temp_version_id,
                                             node_name=node.nodeName)
            node_id = ResponseDto.construct(
                **create_node(super_user, node_body).body).uuid
            created_nodes.append(NodeViewShortInfo.construct(nodeId=node_id,
                                                             nodeName=node_body.nodeName,
                                                             nodeTypeId=node_body.nodeTypeId))

        for node in nodes_full_data:
            # find own node_id
            this_node_id = None
            for created_node in created_nodes:
                if created_node.nodeName == node.nodeName:
                    this_node_id = created_node.nodeId
                    break
            next_node_ids = []
            prev_node_ids = []
            # поиск айдишников, которые подвязываются к текущему узлу
            if node.linksFrom is not None:
                for node_name_for_link in node.linksFrom:
                    if node_name_for_link == "Источник":
                        link = link_construct(temp_version_id, node_source_id, this_node_id)
                        link_id = ResponseDto.construct(
                            **create_link(super_user, body=link).body).uuid
                    else:
                        for created_node in created_nodes:
                            if node_name_for_link == created_node.nodeName:
                                prev_node_ids.append(created_node.nodeId)
                                break
            # поиск айдишников, к которым подвязывается текущий узел
            if node.linksTo is not None:
                for node_name_for_link in node.linksTo:
                    if node_name_for_link == "Приёмник":
                        link = link_construct(temp_version_id, this_node_id, node_target_id)
                        link_id = ResponseDto.construct(
                            **create_link(super_user, body=link).body).uuid
                    else:
                        for created_node in created_nodes:
                            if node_name_for_link == created_node.nodeName:
                                next_node_ids.append(created_node.nodeId)
                                break
            # создание связей
            for p_node_id in prev_node_ids:
                link = link_construct(temp_version_id, p_node_id, this_node_id)
                link_id = ResponseDto.construct(
                    **create_link(super_user, body=link).body).uuid
            for n_node_id in next_node_ids:
                link = link_construct(temp_version_id, this_node_id, n_node_id)
                link_id = ResponseDto.construct(
                    **create_link(super_user, body=link).body).uuid

    elif nodes_marker is not None:
        node_names: list[str] = nodes_marker.args[0]
        node_ids = []
        base_x = 142
        base_y = 202
        for i in range(len(node_names)):
            base_x += 400
            node_type_id = None
            if node_names[i].startswith("трансформация маппинг"):
                node_type_id = IntNodeType.transformMap
            if node_names[i].startswith("трансформация фильтр"):
                node_type_id = IntNodeType.transformFilter
            if node_names[i].startswith("трансформация соединение"):
                node_type_id = IntNodeType.transformConnection
            if node_names[i].startswith("трансформация обогащение jdbc"):
                node_type_id = IntNodeType.transformJdbcEnrich
            if node_names[i].startswith("трансформация groovy"):
                node_type_id = IntNodeType.transformGroovy
            node_body = empty_node_construct(x=base_x, y=base_y,
                                             node_type=node_type_id,
                                             diagram_version_id=temp_version_id,
                                             node_name=node_names[i])
            node_id = ResponseDto.construct(
                **create_node(super_user, node_body).body).uuid
            node_ids.append(node_id)
        if len(node_ids) == 1:
            link_start = link_construct(temp_version_id, node_source_id, node_ids[0])
            link_start_id = ResponseDto.construct(
                **create_link(super_user, body=link_start).body).uuid
            link = link_construct(temp_version_id, node_ids[0], node_target_id)
            link_id = ResponseDto.construct(
                **create_link(super_user, body=link).body).uuid
        elif len(node_ids) == 2:
            link_start = link_construct(temp_version_id, node_source_id, node_ids[0])
            link_start_id = ResponseDto.construct(
                **create_link(super_user, body=link_start).body).uuid
            link = link_construct(temp_version_id, node_ids[0], node_ids[1])
            link_id = ResponseDto.construct(
                **create_link(super_user, body=link).body).uuid
            link_finish = link_construct(temp_version_id, node_ids[1], node_target_id)
            link_id = ResponseDto.construct(
                **create_link(super_user, body=link_finish).body).uuid
        else:
            for i in range(len(node_ids) - 1):
                if i == 0:
                    link_start = link_construct(temp_version_id, node_source_id, node_ids[i])
                    link_start_id = ResponseDto.construct(
                        **create_link(super_user, body=link_start).body).uuid
                    link = link_construct(temp_version_id, node_ids[i], node_ids[i + 1])
                    link_id = ResponseDto.construct(
                        **create_link(super_user, body=link).body).uuid
                elif i == len(node_ids) - 2:
                    link = link_construct(temp_version_id, node_ids[i], node_ids[i + 1])
                    link_id = ResponseDto.construct(
                        **create_link(super_user, body=link).body).uuid
                    link_finish = link_construct(temp_version_id, node_ids[i + 1], node_target_id)
                    link_id = ResponseDto.construct(
                        **create_link(super_user, body=link_finish).body).uuid
                else:
                    link = link_construct(temp_version_id, node_ids[i], node_ids[i + 1])
                    link_id = ResponseDto.construct(
                        **create_link(super_user, body=link).body).uuid

    else:
        link_s_f = link_construct(temp_version_id, node_source_id, node_target_id)
        link_s_f_id = ResponseDto.construct(
            **create_link(super_user, body=link_s_f).body).uuid

    diagram: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
        super_user, temp_version_id).body)
    nodes_info = []
    for node in diagram.nodes.values():
        nodes_info.append(NodeViewShortInfo(**node))
    for node in nodes_info:
        if node.nodeName.lower().startswith("источник") or node.nodeName.lower().startswith("приёмник"):
            nodes[node.nodeName.lower()] = node
        else:
            nodes[node.nodeName] = node

    if save_marker is not None:
        new_diagram_name = "ag_test_diagram_" + generate_string()
        diagram_description = "diagram created in test"
        create_result = save_diagrams_gen.save_diagram(
            diagram_id, temp_version_id, new_diagram_name, diagram_description
        ).body
        saved_version_id = create_result["uuid"]
        save_data: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
            super_user, saved_version_id).body)

    return {"node_target_id": node_target_id,
            "data_target_info": data_target_info,
            "data_source_info": data_source_info,
            "temp_version_id": temp_version_id,
            "diagram_id": diagram_id,
            "diagram_info": diagram,
            "nodes_info": nodes_info,
            "saved_data": save_data,
            "nodes": nodes}


# def test_clean_up(admin):
#     id_list = []
#     list_users = get_users(admin)
#     for users in list_users:
#         if users["username"] != "TK2zZsBF@testrestapi.com":
#             if "testrestapi.com" in users["username"]:
#                 id_list.append(users["id"])
#     for ident in id_list:
#         delete_realm_user(admin, ident)


@pytest.fixture(scope="class", autouse=True)
def objects_clean_up(request, admin, email, super_user, product_db_user) -> None:
    def clean_up():
        diagram_list = diagram_list_by_name(super_user, name="ag_test")
        offer_list = offer_list_by_name(super_user, name="test")
        provider_list = providers_list(super_user).body
        script_list1 = script_list_by_name(super_user, name="test")
        script_list2 = script_list_by_name(super_user, name="ag_")
        types_list = type_list_by_name(super_user, name="test")
        dict_list = dict_list_by_name(super_user, name="test")
        for diagram in diagram_list:
            vers_id = diagram["versionId"]
            try:
                delete_diagram(super_user, vers_id)
            except:
                print(f"can't delete diagram: {vers_id}")
        for offer in offer_list:
            vers_id = offer["versionId"]
            try:
                delete_offer(super_user, offer["versionId"])
            except:
                print(f"can't delete offer: {vers_id}")
        for p in provider_list:
            if p["sourceName"].startswith("data_provider"):
                vers_id = p["sourceId"]
                try:
                    delete_data_provider(super_user, p["sourceId"])
                except:
                    print(f"can't delete provider: {vers_id}")
        for s in script_list1 + script_list2:
            vers_id = s["versionId"]
            try:
                delete_script_by_id(super_user, s["versionId"])
            except:
                print(f"can't delete script: {vers_id}")
        for t in types_list:
            vers_id = t["versionId"]
            try:
                delete_custom_type(super_user, t["versionId"])
            except:
                print(f"can't delete type: {vers_id}")
        for dictionary in dict_list:
            vers_id = dictionary["id"]
            try:
                delete_custom_attribute(super_user, dictionary["id"])
            except:
                print(f"can't delete dict: {vers_id}")

    @allure.title("Очистка объектов созданных тестовым пользователем")
    def clean_up_by_user():
        with allure.step("Получение тестовых объектов по пользователю"):
            interface_username = "autotest_user autotest_user"
            user_id = json.dumps([search_user(admin, email)[0]["id"]])
            filt = ('{"filters":[{"columnName":"lastChangeByUser","operator":"IN",'
                    f'"values":{user_id}}}],"sorts":[{{"direction":'
                    '"ASC","columnName":"changeDt"}],"page":1,"size":999}')
            list_query = {"searchRequest": base64.b64encode(bytes(filt, 'utf-8')).decode(
                "utf-8")}
            provider_list = providers_list(super_user).body
            objects = get_objects_by_query(super_user, list_query)
            objects[ObjectType.AGGREGATE.value] = aggregate_list_by_name(super_user, name="auto_test_aggregate_")
            objects[ObjectType.DEPLOY.value] = deploy_list_by_username(super_user, interface_username)
            python_env_list = get_environments_python_list(super_user, name="test_python_environment")
            python_versions = get_python_version_list(super_user)

            provider_ids = [provider["sourceId"] for provider in provider_list
                            if provider["createByUser"] == interface_username]

            extra_diagrams_list = []

        with allure.step("Удаление тестовых диаграмм"):
            for diagram in objects[ObjectType.DIAGRAM.value]:
                vers_id = diagram["versionId"]
                try:
                    delete_diagram_check_locking(super_user, vers_id)
                except:
                    extra_diagrams_list.append(vers_id)

            for vers_id in extra_diagrams_list:
                try:
                    delete_diagram_check_locking(super_user, vers_id)
                except:
                    print(f"Невозможно удалить диаграмму: {vers_id}")

        with allure.step("Удаление тестовых деплоев"):
            for deploy in objects[ObjectType.DEPLOY.value]:
                deploy_id = [deploy["deployId"]]
                try:
                    deploy_delete(super_user, deploy_id)
                except:
                    print(f"Невозможно удалить деплой: {deploy_id}")

        with allure.step("Удаление тестовых предложений"):
            for offer in objects[ObjectType.OFFER.value]:
                vers_id = offer["versionId"]
                try:
                    delete_offer(super_user, vers_id)
                except:
                    print(f"Невозможно удалить предложение: {vers_id}")

        with allure.step("Удаление тестовых каналов коммуникации"):
            for communication in objects[ObjectType.COMMUNICATION_CHANNEL.value]:
                vers_id = communication["versionId"]
                try:
                    delete_communication(super_user, vers_id)
                except:
                    print(f"Невозможно удалить канал коммуникации: {vers_id}")

        with allure.step("Удаление тестовых сервисов"):
            for ext_serivice in objects[ObjectType.SERVICE.value]:
                vers_id = ext_serivice["versionId"]
                try:
                    delete_service(super_user, vers_id)
                except:
                    print(f"Невозможно удалить словарь: {vers_id}")

        with allure.step("Удаление тестовых агрегатов"):
            for aggregate in objects[ObjectType.AGGREGATE.value]:
                vers_id = aggregate["versionId"]
                try:
                    delete_aggregate(super_user, vers_id)
                except:
                    print(f"Невозможно удалить агрегат: {vers_id}")

        with allure.step("Удаление тестовых скриптов"):
            for script in objects[ObjectType.CUSTOM_CODE.value]:
                vers_id = script["versionId"]
                try:
                    delete_script_by_id(super_user, vers_id)
                except:
                    print(f"Невозможно удалить скрипт: {vers_id}")

        with allure.step("Удаление тестовых окружений и версий python"):
            old_p_vers_list = []
            for p_env in python_env_list:
                vers_id = p_env.versionId
                try:
                    delete_python_environment(super_user, vers_id)
                except:
                    print(f"Невозможно удалить окружение: {vers_id}")
            for p_vers in python_versions:
                if not p_vers.versionName.startswith("test_python_3.6"):
                    old_p_vers_list.append(p_vers)
            try:
                create_python_version(super_user, old_p_vers_list)
            except:
                print(f"Не удалось вернуть версии python к исходному виду")

        with allure.step("Удаление тестовых провайдеров"):
            if len(provider_ids) > 0:
                delete_constraint(product_db_user)
                delete_from_table(product_db_user, object_ids=provider_ids)

                for vers_id in provider_ids:
                    try:
                        delete_data_provider(super_user, vers_id)
                    except:
                        print(f"Невозможно удалить провайдера: {vers_id}")
                return_constraint(product_db_user)

        with allure.step("Удаление тестовых сложных типов"):
            for complex_type in objects[ObjectType.COMPLEX_TYPE.value]:
                vers_id = complex_type["versionId"]
                try:
                    delete_custom_type(super_user, vers_id)
                except:
                    print(f"Невозможно удалить тип: {vers_id}")

        with allure.step("Удаление тестовых словарей"):
            for dictionary in objects[ObjectType.CUSTOM_ATTRIBUTE_DICTIONARY.value]:
                vers_id = dictionary["id"]
                try:
                    delete_custom_attribute(super_user, vers_id)
                except:
                    print(f"Невозможно удалить словарь: {vers_id}")
        # TODO добавить последним каталоги и убрать из самих каталогов удаление

    request.addfinalizer(clean_up_by_user)
