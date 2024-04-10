import random
import string

from products.Decision.framework.model import ExternalServiceCreateDto, ExternalServiceSettingsViewWithoutIdDto, \
    ExternalServiceHeaderViewWithoutIdDto, ExternalServiceVariableViewWithoutIdDto, VariableType2, \
    ExternalServiceUpdateDto, ExternalServiceCreateUserVersionDto


def rnd_service_str(name_length):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(name_length))

    return rand_string


def service_var_construct(variable_name, variable_type: VariableType2, array_flag=False,
                          is_compl=False,
                          primitive_type_id=None, complex_type_version_id=None,
                          source_path=None, expression=None, child_vars=None,
                          func_ids=None):
    return ExternalServiceVariableViewWithoutIdDto.construct(variableName=variable_name,
                                                             primitiveTypeId=primitive_type_id,
                                                             complexTypeVersionId=complex_type_version_id,
                                                             variableType=variable_type,
                                                             isArray=array_flag,
                                                             isComplex=is_compl,
                                                             sourcePath=source_path,
                                                             expression=expression,
                                                             childVariables=child_vars,
                                                             functionIds=func_ids)


def service_header_construct(header_name, header_value):
    return ExternalServiceHeaderViewWithoutIdDto.construct(headerName=header_name, headerValue=header_value)


def service_setting_construct(environment_settings_id, host, service_type, endpoint, port,
                              second_attempts_cnt=None, transactions_per_second=None,
                              interval=None, timeout=None, keycloak_client_id=None,
                              keycloak_client_secret=None, keycloak_user=None,
                              keycloak_password=None, keycloak_grant_type=None,
                              keycloak_server=None, keycloak_realm=None,
                              keycloak_auth=False):
    return ExternalServiceSettingsViewWithoutIdDto.construct(environmentSettingsId=environment_settings_id,
                                                             host=host,
                                                             serviceType=service_type,
                                                             endpoint=endpoint,
                                                             port=port,
                                                             secondAttemptsCnt=second_attempts_cnt,
                                                             transactionsPerSecond=transactions_per_second,
                                                             interval=interval,
                                                             timeout=timeout,
                                                             keycloakClientId=keycloak_client_id,
                                                             keycloakClientSecret=keycloak_client_secret,
                                                             keycloakUser=keycloak_user,
                                                             keycloakPassword=keycloak_password,
                                                             keycloakGrantType=keycloak_grant_type,
                                                             keycloakServer=keycloak_server,
                                                             keycloakRealm=keycloak_realm,
                                                             isKeyCloakAuth=keycloak_auth)


def service_construct(protocol, sync_type, service_name,
                      batch_flag=None, description=None, file_format=None,
                      method=None, body=None, service_settings=None, headers=None,
                      variables=None, catalog_id=None):
    return ExternalServiceCreateDto.construct(batchFlag=batch_flag,
                                              description=description,
                                              fileFormat=file_format,
                                              method=method,
                                              protocol=protocol,
                                              syncType=sync_type,
                                              objectName=service_name,
                                              body=body,
                                              serviceSettings=service_settings,
                                              headers=headers,
                                              variables=variables,
                                              catalogId=catalog_id)


def service_update_construct(protocol, sync_type, service_name,
                             batch_flag=None, description=None, file_format=None,
                             method=None, body=None, service_settings=None, headers=None,
                             variables=None):
    return ExternalServiceUpdateDto.construct(batchFlag=batch_flag,
                                              description=description,
                                              fileFormat=file_format,
                                              method=method,
                                              protocol=protocol,
                                              syncType=sync_type,
                                              objectName=service_name,
                                              body=body,
                                              serviceSettings=service_settings,
                                              headers=headers,
                                              variables=variables)


def service_user_version_construct(protocol, sync_type, service_name,
                                   batch_flag=None, description=None, file_format=None,
                                   method=None, body=None, version_description=None, version_name=None,
                                   service_settings=None, headers=None,
                                   variables=None):
    return ExternalServiceCreateUserVersionDto.construct(batchFlag=batch_flag,
                                                         description=description,
                                                         fileFormat=file_format,
                                                         method=method,
                                                         protocol=protocol,
                                                         syncType=sync_type,
                                                         objectName=service_name,
                                                         body=body,
                                                         versionDescription=version_description,
                                                         versionName=version_name,
                                                         serviceSettings=service_settings,
                                                         headers=headers,
                                                         variables=variables)
