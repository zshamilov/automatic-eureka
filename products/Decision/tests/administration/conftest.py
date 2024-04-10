# Fixtures for environments Range
import pytest

from products.Decision.framework.model import ResponseDto, StateStoreServerType
from products.Decision.framework.steps.decision_steps_environments_api import create_environment, \
    delete_environment_by_id
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description
from products.Decision.utilities.environment_constructors import integration_platform_env_settings, \
    state_store_env_settings, streaming_platform_env_settings, kafka_env_settings, env_construct



@pytest.fixture(scope='class')
def create_environment_gen(super_user):
    class CreateEnv:
        env_ids = []

        @staticmethod
        def create_env(env):
            create_env_resp: ResponseDto = ResponseDto.construct(**create_environment(super_user, body=env).body)
            env_id = create_env_resp.uuid
            CreateEnv.env_ids.append(env_id)
            return create_env_resp

        @staticmethod
        def try_create_env(env):
            create_env_resp = create_environment(super_user, body=env)
            if create_env_resp.status == 201:
                CreateEnv.env_ids.append(create_env_resp.body["uuid"])
            return create_env_resp

    yield CreateEnv

    for environment_id in CreateEnv.env_ids:
        delete_environment_by_id(super_user, environment_id)


@pytest.fixture()
def fake_env_model():
    integration_env_settings = integration_platform_env_settings(
        generate_diagram_name_description(8, 1)["rand_name"])
    state_env_settings = state_store_env_settings(state_store_username="decision_root",
                                                  state_store_password="decision_root",
                                                  state_store_schema="11",
                                                  state_store_server_name="1231",
                                                  state_store_server_port="1231",
                                                  state_store_server_type=StateStoreServerType.POSTGRESQL,
                                                  state_store_additional_properties="")
    str_env_settings = streaming_platform_env_settings(
        streaming_platform_url=generate_diagram_name_description(8, 1)["rand_name"],
        streaming_platform_username="",
        streaming_platform_password="")
    kafka_settings = kafka_env_settings(kafka_url="11", kafka_environment_additional_settings=[])
    env = env_construct(environment_name="env_" + generate_diagram_name_description(8, 1)["rand_name"],
                        integration_platform_environment_settings=integration_env_settings,
                        state_store_environment_settings=state_env_settings,
                        streaming_platform_environment_settings=str_env_settings,
                        default_flag=False,
                        kafka_environment_settings=kafka_settings)
    return env



