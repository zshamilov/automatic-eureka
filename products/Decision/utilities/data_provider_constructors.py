from typing import Literal

from products.Decision.framework.model import DataProviderCreateDto, DataProviderSettingsViewWithoutIdDto, \
    TestConnectionRequestDto, DataProviderSettingsFullViewDto, DataProviderUpdateDto


def provider_setting_construct(environment_settings_id,
                               server_name=None,
                               port=None, username=None,
                               password=None,
                               additional_properties=None, scheme=None, database=None,
                               input_type: Literal["parameters", "url"] = None, url=None):
    return DataProviderSettingsViewWithoutIdDto.construct(environmentSettingsId=environment_settings_id,
                                                          serverName=server_name,
                                                          port=port,
                                                          username=username,
                                                          password=password,
                                                          additionalProperties=additional_properties,
                                                          scheme=scheme,
                                                          database=database,
                                                          inputType=input_type,
                                                          url=url)


def provider_setting_update_construct(environment_settings_id,
                                      server_name,
                                      port, username,
                                      password,
                                      additional_properties,
                                      source_settings_id, scheme=None, database=None,
                                      input_type: Literal["parameters", "url"] = None, url=None):
    return DataProviderSettingsFullViewDto.construct(environmentSettingsId=environment_settings_id,
                                                     serverName=server_name,
                                                     port=port,
                                                     username=username,
                                                     password=password,
                                                     additionalProperties=additional_properties,
                                                     sourceSettingsId=source_settings_id,
                                                     scheme=scheme,
                                                     database=database,
                                                      inputType=input_type,
                                                      url=url)


def data_provider_construct(source_name, source_type=None, connection_type=None,
                            description=None, settings=None):
    return DataProviderCreateDto.construct(sourceName=source_name,
                                           description=description,
                                           sourceType=source_type,
                                           connectionType=connection_type,
                                           settings=settings)


def data_provider_update_construct(source_name, source_type, connection_type,
                                   description=None, settings=None):
    return DataProviderUpdateDto(sourceName=source_name,
                                 description=description,
                                 sourceType=source_type,
                                 connectionType=connection_type,
                                 settings=settings)


def connection_test_construct(source_type, connection_type, settings=None):
    return TestConnectionRequestDto.construct(sourceType=source_type,
                                              connectionType=connection_type,
                                              settings=settings)
