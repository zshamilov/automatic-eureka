from products.Decision.conftest import super_user
from products.Decision.framework.model import EnvironmentCreateDto, IntegrationPlatformEnvironmentFullViewDto, \
    StateStoreEnvironmentFullViewDto, StreamingPlatformEnvironmentFullViewDto, KafkaEnvironmentCreateDto, \
    EnvironmentUpdateDto, KafkaAdditionalSettingsWithoutIdDto, EnvironmentShortInfoDto
from products.Decision.framework.steps.decision_steps_environments_api import get_environments_list


def integration_platform_env_settings(integration_url):
    return IntegrationPlatformEnvironmentFullViewDto(integrationUrl=integration_url)


def state_store_env_settings(state_store_username, state_store_password, state_store_schema,
                             state_store_server_name, state_store_server_port, state_store_server_type,
                             state_store_additional_properties=""):
    return StateStoreEnvironmentFullViewDto(stateStoreUsername=state_store_username,
                                            stateStorePassword=state_store_password,
                                            stateStoreSchema=state_store_schema,
                                            stateStoreServerName=state_store_server_name,
                                            stateStoreServerPort=state_store_server_port,
                                            stateStoreAdditionalProperties=state_store_additional_properties,
                                            stateStoreServerType=state_store_server_type)


def streaming_platform_env_settings(streaming_platform_url,
                                    streaming_platform_username="",
                                    streaming_platform_password=""):
    return StreamingPlatformEnvironmentFullViewDto(streamingPlatformUsername=streaming_platform_username,
                                                   streamingPlatformPassword=streaming_platform_password,
                                                   streamingPlatformUrl=streaming_platform_url)


def kafka_additional_settings_construct(property_name, property_value, property_secure=False):
    return KafkaAdditionalSettingsWithoutIdDto(propertyName=property_name,
                                               propertyValue=property_value,
                                               propertySecure=property_secure)


def kafka_env_settings(kafka_url, kafka_environment_additional_settings=[]):
    return KafkaEnvironmentCreateDto(kafkaUrl=kafka_url,
                                     kafkaEnvironmentAdditionalSettings=kafka_environment_additional_settings)


def env_construct(environment_name,
                  integration_platform_environment_settings,
                  state_store_environment_settings,
                  streaming_platform_environment_settings,
                  default_flag,
                  kafka_environment_settings):
    return EnvironmentCreateDto(environmentName=environment_name,
                                integrationPlatformEnvSettings=integration_platform_environment_settings,
                                stateStoreEnvSettings=state_store_environment_settings,
                                streamingPlatformEnvSettings=streaming_platform_environment_settings,
                                defaultFlag=default_flag,
                                kafkaEnvSettings=kafka_environment_settings)


def env_update_construct(environment_name,
                         integration_platform_environment_settings,
                         state_store_environment_settings,
                         streaming_platform_environment_settings,
                         default_flag,
                         kafka_environment_settings):
    return EnvironmentUpdateDto(environmentName=environment_name,
                                integrationPlatformEnvSettings=integration_platform_environment_settings,
                                stateStoreEnvSettings=state_store_environment_settings,
                                streamingPlatformEnvSettings=streaming_platform_environment_settings,
                                defaultFlag=default_flag,
                                kafkaEnvSettings=kafka_environment_settings)
