from products.Decision.framework.model import ScriptVariableViewWithoutVersionIdDto, VariableType1, PythonCreate, \
    GroovyCreate, PythonUpdate, GroovyUpdate, ScriptType, GroovyCreateUserVersion, PythonCreateUserVersion, \
    PythonEnvironmentCreateDto, PythonEnvironmentSettingsWithoutIdDto, PythonVersionFullViewDto, \
    PythonEnvironmentUpdateDto, PythonEnvironmentSettingsWithIdDto


def script_vars_construct(var_name, var_type: VariableType1, is_array, primitive_id=None, complex_vers_id=None):
    return ScriptVariableViewWithoutVersionIdDto.construct(variableName=var_name,
                                                           primitiveTypeId=primitive_id,
                                                           complexTypeVersionId=complex_vers_id,
                                                           variableType=var_type,
                                                           arrayFlag=is_array)


def python_environment_setting_construct(limits_cpu, requests_cpu, limits_memory,
                                         requests_memory, environment_id):
    return PythonEnvironmentSettingsWithoutIdDto.construct(limitsCpu=limits_cpu,
                                                           requestsCpu=requests_cpu,
                                                           limitsMemory=limits_memory,
                                                           requestsMemory=requests_memory,
                                                           environmentId=environment_id)


def python_environment_setting_update_construct(limits_cpu, requests_cpu, limits_memory,
                                                requests_memory, environment_id, id):
    return PythonEnvironmentSettingsWithIdDto.construct(limitsCpu=limits_cpu,
                                                        requestsCpu=requests_cpu,
                                                        limitsMemory=limits_memory,
                                                        requestsMemory=requests_memory,
                                                        environmentId=environment_id,
                                                        id=id)


def python_version_construct(v_id, version_name, image):
    return PythonVersionFullViewDto.construct(id=v_id,
                                              versionName=version_name,
                                              image=image)


def script_environment_construct(name, python_version_id, requirements_txt, python_environment_setting):
    return PythonEnvironmentCreateDto.construct(name=name,
                                                pythonVersionId=python_version_id,
                                                requirementsTxt=requirements_txt,
                                                pythonEnvironmentSettings=python_environment_setting)


def script_update_environment_construct(name, python_version_id, id, requirements_txt,
                                        python_environment_setting, version_id=None):
    return PythonEnvironmentUpdateDto.construct(name=name,
                                                pythonVersionId=python_version_id,
                                                id=id,
                                                versionId=version_id,
                                                requirementsTxt=requirements_txt,
                                                pythonEnvironmentSettings=python_environment_setting)


def code_construct(script_type, script_name, script_text, variables=None, description=None,
                   python_environment_version_id=None,
                   catalog_id=None):
    if script_type == "python":
        return PythonCreate.construct(scriptText=script_text,
                                      description=description,
                                      pythonEnvironmentVersionId=python_environment_version_id,
                                      catalogId=catalog_id,
                                      variables=variables,
                                      objectName=script_name)
    if script_type == "groovy":
        return GroovyCreate.construct(scriptText=script_text,
                                      description=description,
                                      catalogId=catalog_id,
                                      variables=variables,
                                      objectName=script_name)


def code_update_construct(script_id, version_id, script_type, script_name,
                          script_text, variables=None, description=None):
    if script_type == "python":
        return PythonUpdate.construct(scriptType=ScriptType.PYTHON.value,
                                      scriptText=script_text,
                                      description=description,
                                      variables=variables,
                                      objectName=script_name,
                                      scriptId=script_id,
                                      versionId=version_id)
    if script_type == "groovy":
        return GroovyUpdate.construct(scriptType=ScriptType.GROOVY.value,
                                      scriptText=script_text,
                                      description=description,
                                      variables=variables,
                                      objectName=script_name,
                                      scriptId=script_id,
                                      versionId=version_id)


def code_user_version_construct(script_id, script_type, script_name, script_text, version_name,
                                variables=None, description=None, version_description=None,
                                catalog_id=None):
    if script_type == "python":
        return PythonCreateUserVersion.construct(scriptId=script_id,
                                                 scriptText=script_text,
                                                 description=description,
                                                 catalogId=catalog_id,
                                                 variables=variables,
                                                 objectName=script_name,
                                                 versionName=version_name,
                                                 versionDescription=version_description)
    if script_type == "groovy":
        return GroovyCreateUserVersion.construct(scriptId=script_id,
                                                 scriptText=script_text,
                                                 description=description,
                                                 catalogId=catalog_id,
                                                 variables=variables,
                                                 objectName=script_name,
                                                 versionName=version_name,
                                                 versionDescription=version_description)
