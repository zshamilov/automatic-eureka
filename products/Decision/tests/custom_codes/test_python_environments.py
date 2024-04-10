import allure
from requests import HTTPError

from products.Decision.framework.model import PythonVersionFullViewDto, ResponseDto
from products.Decision.framework.steps.decision_steps_python_environment import update_python_environment
from products.Decision.framework.steps.decision_steps_python_version import create_python_version, \
    get_python_version_id
from products.Decision.runtime_tests.runtime_fixtures.custom_code_fixtures import *
from products.Decision.utilities.custom_code_constructors import python_version_construct, \
    script_update_environment_construct, python_environment_setting_update_construct
from products.Decision.utilities.custom_models import VariableParams, IntValueType


@allure.epic("Кастомные коды")
@allure.feature("Окружения Python")
class TestPythonEnvironment:
    @allure.story("Можно создать окружение Python с существующей версией")
    @allure.title("Создание окружния с существующей версией Питона")
    @pytest.mark.scenario("DEV-8830")
    @pytest.mark.environment_dependent
    def test_create_python_environment(self, super_user, get_env):
        with allure.step("заполнение настроек окружения"):
            environment_id = get_env.get_env_id()
            environment = python_environment_setting_construct(
                limits_cpu=0.3,
                requests_cpu=0.1,
                limits_memory=128,
                requests_memory=64,
                environment_id=environment_id)

        with allure.step("Выбор версии"):
            python_version_ids = get_python_version_list(super_user)
            python_version_id = python_version_ids[0].id

        with allure.step("Сохранение окружения"):
            requirements_txt = "pandas"
            environment_name = "test_python_environment_" + generate_string()
            python_body = script_environment_construct(name=environment_name,
                                                       python_version_id=python_version_id,
                                                       requirements_txt=requirements_txt,
                                                       python_environment_setting=[environment])
            python_environment = create_python_environment(super_user, python_body)
            vers_id = python_environment.body["uuid"]

        with allure.step("Поиск окружения по айди версии"):
            resp = get_environment_python_version(super_user, vers_id)

        with allure.step("Проверка что окружение создалось "):
            assert python_environment.status == 201 \
                   and python_environment.body["operation"] == "save" \
                   and resp.body["name"] == environment_name

    @allure.story("Создание окружение Python с существующей версией с последущей заменой версии")
    @allure.title("Создать окружние с существующей версией Питона затем изменить версию у окружения")
    @pytest.mark.scenario("DEV-8830")
    @pytest.mark.environment_dependent
    def test_update_python_environment(self, super_user, get_env):
        with allure.step("заполнение настроек окружения"):
            environment_id = get_env.get_env_id()
            environment = python_environment_setting_construct(
                limits_cpu=0.3,
                requests_cpu=0.1,
                limits_memory=128,
                requests_memory=64,
                environment_id=environment_id)

        with allure.step("Выбор версии"):
            python_version_ids = get_python_version_list(super_user)
            python_version_id = python_version_ids[0].id

        with allure.step("Сохранение окружения"):
            requirements_txt = "pandas"
            environment_name = "test_python_environment_" + generate_string()
            python_body = script_environment_construct(name=environment_name,
                                                       python_version_id=python_version_id,
                                                       requirements_txt=requirements_txt,
                                                       python_environment_setting=[environment])
            python_environment = create_python_environment(super_user, python_body)
            vers_id = python_environment.body["uuid"]
        with allure.step("Поиск окружения по версии айди"):
            resp = get_environment_python_version(super_user, vers_id)
            python_vers_id = resp.body["id"]
            setting_id = resp.body["pythonEnvironmentSettings"][0]["id"]
            ver_id = resp.body["versionId"]
        with allure.step("Изменение версии окружения"):
            environment_name_up = "test_python_environment_up_" + generate_string()
            environment = python_environment_setting_update_construct(
                limits_cpu=0.3,
                requests_cpu=0.1,
                limits_memory=128,
                requests_memory=64,
                environment_id=environment_id,
                id=setting_id)
            python_body2 = script_update_environment_construct(name=environment_name_up,
                                                               id=python_vers_id,
                                                               version_id=ver_id,
                                                               python_version_id=python_version_id,
                                                               requirements_txt=requirements_txt,
                                                               python_environment_setting=[environment])
            update_python_environment(super_user, python_vers_id, python_body2)

        with allure.step("Поиск окружения по версии айди"):
            updated_vers = get_environment_python_version(super_user, vers_id)

        with allure.step("Проверка что изменилась версия окружения"):
            assert updated_vers.body["name"] == environment_name_up

    @allure.story("Удаление окружения Python")
    @allure.title("Создать окружния с существующей версией Питона, удалить окружение")
    @pytest.mark.scenario("DEV-8830")
    @pytest.mark.environment_dependent
    def test_delete_python_environment(self, super_user, get_env):
        with allure.step("заполнение настроек окружения"):
            environment_id = get_env.get_env_id()
            environment = python_environment_setting_construct(
                limits_cpu=0.3,
                requests_cpu=0.1,
                limits_memory=128,
                requests_memory=64,
                environment_id=environment_id)

        with allure.step("Выбор версии"):
            python_version_ids = get_python_version_list(super_user)
            python_version_id = python_version_ids[0].id

        with allure.step("Сохранение окружения"):
            requirements_txt = "pandas"
            environment_name = "test_python_environment_" + generate_string()
            python_body = script_environment_construct(name=environment_name,
                                                       python_version_id=python_version_id,
                                                       requirements_txt=requirements_txt,
                                                       python_environment_setting=[environment])
            python_environment = create_python_environment(super_user, python_body)
            vers_id = python_environment.body["uuid"]

        with allure.step("Удаление окружения по версии айди"):
            delete_environment_python = delete_python_environment(super_user, vers_id)

        with allure.step("Проверка что окружение удалилось "):
            assert delete_environment_python.body["httpCode"] == 200 \
                   and delete_environment_python.body["operation"] == "delete"

    @allure.story("Создание скрипта с окружением Python с существующей версией")
    @allure.title("Создать окружения с существующей версией Питона и создать скрипт")
    @pytest.mark.scenario("DEV-8830")
    @pytest.mark.environment_dependent
    def test_create_script_python_environment(self, super_user, get_env):
        with allure.step("заполнение настроек окружения"):
            environment_id = get_env.get_env_id()
            environment = python_environment_setting_construct(
                limits_cpu=0.3,
                requests_cpu=0.1,
                limits_memory=128,
                requests_memory=64,
                environment_id=environment_id)

        with allure.step("Выбор версии"):
            python_version_ids = get_python_version_list(super_user)
            python_version_id = python_version_ids[0].id
        with allure.step("Сохранение окружения"):
            requirements_txt = "pandas"
            environment_name = "test_python_environment_" + generate_string()
            python_body = script_environment_construct(name=environment_name,
                                                       python_version_id=python_version_id,
                                                       requirements_txt=requirements_txt,
                                                       python_environment_setting=[environment])
            python_environment = create_python_environment(super_user, python_body)
            vers_id = python_environment.body["uuid"]

        with allure.step("Поиск окружения по версии айди"):
            resp = get_environment_python_version(super_user, vers_id)
            python_environment_version = resp.body["versionId"]
        with allure.step("Создание переменных"):
            inp_var = script_vars_construct(var_name="input_int",
                                            var_type=VariableType1.IN,
                                            is_array=False, primitive_id="1")
            out_var = script_vars_construct(var_name="output_int",
                                            var_type=VariableType1.OUT,
                                            is_array=False, primitive_id="1")
        with allure.step("Создание параметров скрипта"):
            script_text = "import pandas\ndef run(data: dict):\n  return {'output_int': data['input_int'] * 5}"
            script_name = "ag_python_script_" + generate_string()
            script = code_construct(script_type="python",
                                    script_name=script_name,
                                    script_text=script_text,
                                    python_environment_version_id=python_environment_version,
                                    variables=[inp_var, out_var])
            python_code_create_result = ScriptFullView.construct(
                **create_python_script(super_user, body=script).body)
            script_view = get_python_script_by_id(super_user, python_code_create_result.versionId)

        with allure.step("Проверка что окружение создалось с заданным окружением"):
            assert script_view.body["pythonEnvironmentVersionId"] == vers_id

    @allure.story("Можно отредактировать  окружение из  скрипта ")
    @allure.title("Создание окружения с  версией Питона и создать скрипт, отредактировать окружение")
    @pytest.mark.scenario("DEV-8830")
    @pytest.mark.environment_dependent
    def test_update_python_version_environment_script(self, super_user, get_env):
        with allure.step("Создать версию"):
            v_id = str(uuid.uuid4())
            version_name = "test_python_3.6_" + generate_string()
            image = "harbor.k8s.datasapience.ru/datasapience-registry/st-di/udf-server"
            current_vers_list = get_python_version_list(super_user)

            python_version = python_version_construct(v_id=v_id,
                                                      version_name=version_name,
                                                      image=image)
            new_list = current_vers_list + [python_version]

            python_new = create_python_version(super_user, new_list)

        with allure.step("заполнение настроек окружения"):
            environment_id = get_env.get_env_id()
            environment = python_environment_setting_construct(
                limits_cpu=0.3,
                requests_cpu=0.1,
                limits_memory=128,
                requests_memory=64,
                environment_id=environment_id)

        with allure.step("Сохранение окружения"):
            requirements_txt = "pandas"
            environment_name = "test_python_environment_" + generate_string()
            python_body = script_environment_construct(name=environment_name,
                                                       python_version_id=v_id,
                                                       requirements_txt=requirements_txt,
                                                       python_environment_setting=[environment])
            python_environment = create_python_environment(super_user, python_body)
            vers_id = python_environment.body["uuid"]
        with allure.step("Поиск окружения по версии айди"):
            resp = get_environment_python_version(super_user, vers_id)
            python_environment_version = resp.body["versionId"]
        with allure.step("Создание переменных"):
            inp_var = script_vars_construct(var_name="input_int",
                                            var_type=VariableType1.IN,
                                            is_array=False, primitive_id="1")
            out_var = script_vars_construct(var_name="output_int",
                                            var_type=VariableType1.OUT,
                                            is_array=False, primitive_id="1")
        with allure.step("Создание параметров скрипта"):
            script_text = "import pandas\ndef run(data: dict):\n  return {'output_int': data['input_int'] * 5}"
            script_name = "ag_python_script_" + generate_string()
            script = code_construct(script_type="python",
                                    script_name=script_name,
                                    script_text=script_text,
                                    python_environment_version_id=python_environment_version,
                                    variables=[inp_var, out_var])
            python_code_create_result = ScriptFullView.construct(
                **create_python_script(super_user, body=script).body)
            script_view = get_python_script_by_id(super_user, python_code_create_result.versionId)

        with allure.step("Редактировать окружение"):
            environment_name2 = "test_python_environment_2_" + generate_string()
            resp = get_environment_python_version(super_user, vers_id)
            id = resp.body["id"]
            id_env = resp.body["pythonEnvironmentSettings"][0]["id"]
            ver_id = resp.body["versionId"]
            environment = python_environment_setting_update_construct(
                limits_cpu=0.3,
                requests_cpu=0.1,
                limits_memory=128,
                requests_memory=64,
                environment_id=environment_id,
                id=id_env)
            python_body2 = script_update_environment_construct(name=environment_name2,
                                                               id=id,
                                                               version_id=ver_id,
                                                               python_version_id=v_id,
                                                               requirements_txt=requirements_txt,
                                                               python_environment_setting=[environment])
            python_environment_up = update_python_environment(super_user, id, python_body2)

        with allure.step("Поиск окружения по версии айди"):
            resp2 = get_environment_python_version(super_user, vers_id)

        with allure.step("Проверка что в скрипте та же версия окружения и что имя окружения изменилось"):
            script_view2 = get_python_script_by_id(super_user, python_code_create_result.versionId)
            assert script_view2.body["pythonEnvironmentVersionId"] == vers_id \
                   and resp2.body["name"] == environment_name2

    @allure.story("Создание версии Python для окружения")
    @allure.title("Создание версию для окружния Питон и создать с ним окружение")
    @pytest.mark.scenario("DEV-19864")
    @pytest.mark.environment_dependent
    def test_create_python_environment_version(self, super_user, get_env):
        with allure.step("Создать версию"):
            v_id = str(uuid.uuid4())
            version_name = "test_python_3.6_" + generate_string()
            image = "harbor.k8s.datasapience.ru/datasapience-registry/st-di/udf-server"
            current_vers_list = get_python_version_list(super_user)

            python_version = python_version_construct(v_id=v_id,
                                                      version_name=version_name,
                                                      image=image)
            new_list = current_vers_list + [python_version]

            python_new = create_python_version(super_user, new_list)

        with allure.step("заполнение настроек окружения"):
            environment_id = get_env.get_env_id()
            environment = python_environment_setting_construct(
                limits_cpu=0.3,
                requests_cpu=0.1,
                limits_memory=128,
                requests_memory=64,
                environment_id=environment_id)

        with allure.step("Сохранение окружения"):
            requirements_txt = "pandas"
            environment_name = "test_python_environment_" + generate_string()
            python_body = script_environment_construct(name=environment_name,
                                                       python_version_id=v_id,
                                                       requirements_txt=requirements_txt,
                                                       python_environment_setting=[environment])
            python_environment = create_python_environment(super_user, python_body)
            vers_id = python_environment.body["uuid"]

        with allure.step("Поиск окружения по версии айди"):
            resp = get_environment_python_version(super_user, vers_id)

        with allure.step("Проверка что окружение создалось с новой версией "):
            assert python_environment.status == 201 \
                   and python_environment.body["operation"] == "save" \
                   and resp.body["pythonVersionId"] == v_id

    @allure.story("Редактирование Версии  Python для окружения")
    @allure.title("Создание версию для окружния Питон и создать с ним окружение,"
                  " редактировать версию")
    @pytest.mark.scenario("DEV-19864")
    @pytest.mark.environment_dependent
    def test_update_python_environment_version(self, super_user, get_env):
        with allure.step("Создать версию"):
            v_id = str(uuid.uuid4())
            version_name = "test_python_3.6_" + generate_string()
            image = "harbor.k8s.datasapience.ru/datasapience-registry/st-di/udf-server"
            current_vers_list = get_python_version_list(super_user)

            python_version = python_version_construct(v_id=v_id,
                                                      version_name=version_name,
                                                      image=image)
            new_list = current_vers_list + [python_version]

            python_new = create_python_version(super_user, new_list)
            number_of_versions = len(get_python_version_list(super_user))

        with allure.step("заполнение настроек окружения"):
            environment_id = get_env.get_env_id()
            environment = python_environment_setting_construct(
                limits_cpu=0.3,
                requests_cpu=0.1,
                limits_memory=128,
                requests_memory=64,
                environment_id=environment_id)

        with allure.step("Сохранение окружения"):
            requirements_txt = "pandas"
            environment_name = "test_python_environment_" + generate_string()
            python_body = script_environment_construct(name=environment_name,
                                                       python_version_id=v_id,
                                                       requirements_txt=requirements_txt,
                                                       python_environment_setting=[environment])
            python_environment = create_python_environment(super_user, python_body)
            vers_id = python_environment.body["uuid"]

        with allure.step("Редактировать версию"):
            v_id = v_id
            new_version_name = "test_python_3.6_" + generate_string()
            image = "harbor.k8s.datasapience.ru/datasapience-registry/st-di/udf-server"
            current_vers_list = get_python_version_list(super_user)

            python_version = python_version_construct(v_id=v_id,
                                                      version_name=new_version_name,
                                                      image=image)
            new_list = current_vers_list + [python_version]

            python_new = create_python_version(super_user, new_list)

        with allure.step("Поиск версии"):
            number_of_versions_2 = len(get_python_version_list(super_user))
            resp = get_python_version_id(super_user, v_id)

        with allure.step("Проверка что окружение создалось с отредактированной версией,"
                         " проверка изменения имени по айди и что версий не стало больше"):
            assert number_of_versions_2 == number_of_versions \
                   and resp.body["versionName"] == new_version_name

    @allure.story("Удаление  Версии  Python ")
    @allure.title("Создать версию для окружния Питон "
                  " удалить версию, проверить что удалилась")
    @pytest.mark.scenario("DEV-19864")
    @pytest.mark.environment_dependent
    def test_delete_version_python(self, super_user):
        with allure.step("Узнать сколько существует версий"):
            current_vers_list = get_python_version_list(super_user)
        with allure.step("Создание новой версии Python"):
            v_id = str(uuid.uuid4())
            version_name = "test_python_3.6_" + generate_string()
            image = "harbor.k8s.datasapience.ru/datasapience-registry/st-di/udf-server"
            python_version = python_version_construct(v_id=v_id,
                                                      version_name=version_name,
                                                      image=image)
            new_list = current_vers_list + [python_version]
            create_python_version(super_user, new_list)
        with allure.step("Удаление версии"):
            create_python_version(super_user, current_vers_list)
        with allure.step("Проверить что версий осталось столько же сколько было до создания новой"):
            new_vers_list = get_python_version_list(super_user)
            assert new_vers_list == current_vers_list

    @allure.story("Нельзя удалить  Версию  Python связанную с  окружением")
    @allure.title("Создание версию для окружния Питон и создать с ним окружение,"
                  " удалить версию, проверить что удаление невозможно")
    @pytest.mark.scenario("DEV-19864")
    @pytest.mark.environment_dependent
    def test_delete_version_python_environment_link(self, super_user, get_env):
        with allure.step("Создать версию"):
            v_id = str(uuid.uuid4())
            version_name = "test_python_3.6_" + generate_string()
            image = "harbor.k8s.datasapience.ru/datasapience-registry/st-di/udf-server"
            current_vers_list = get_python_version_list(super_user)

            python_version = python_version_construct(v_id=v_id,
                                                      version_name=version_name,
                                                      image=image)
            new_list = current_vers_list + [python_version]

            python_new = create_python_version(super_user, new_list)

        with allure.step("заполнение настроек окружения"):
            environment_id = get_env.get_env_id()
            environment = python_environment_setting_construct(
                limits_cpu=0.3,
                requests_cpu=0.1,
                limits_memory=128,
                requests_memory=64,
                environment_id=environment_id)

        with allure.step("Сохранение окружения"):
            requirements_txt = "pandas"
            environment_name = "test_python_environment_" + generate_string()
            python_body = script_environment_construct(name=environment_name,
                                                       python_version_id=v_id,
                                                       requirements_txt=requirements_txt,
                                                       python_environment_setting=[environment])
            python_environment = create_python_environment(super_user, python_body)
            vers_id = python_environment.body["uuid"]

        with allure.step("Поиск версии, проверка  что версии не удалилась"):
            with pytest.raises(HTTPError, match="400"):
                python_new.body = create_python_version(super_user, current_vers_list)
                assert python_new["message"] == "Ошибка при сохранении версии python: " \
                                                "Нельзя удалить одну или несколько версий Python, " \
                                                "так как она (они) связана (-ы) с другими объектами."

    @allure.story("Нельзя удалить связанное со скриптом окружение")
    @allure.title("Создать окружние с  версией Питона и создать скрипт, удалить окружение, получить ошибку удаления "
                  "связанного со скриптом окружения")
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.scenario("DEV-19864")
    @pytest.mark.environment_dependent
    def test_delete_python_version_environment_script(self, super_user, get_env):
        with allure.step("Создать версию"):
            v_id = str(uuid.uuid4())
            version_name = "test_python_3.6_" + generate_string()
            image = "harbor.k8s.datasapience.ru/datasapience-registry/st-di/udf-server"
            current_vers_list = get_python_version_list(super_user)

            python_version = python_version_construct(v_id=v_id,
                                                      version_name=version_name,
                                                      image=image)
            new_list = current_vers_list + [python_version]

            create_python_version(super_user, new_list)

        with allure.step("заполнение настроек окружения"):
            environment_id = get_env.get_env_id()
            environment = python_environment_setting_construct(
                limits_cpu=0.3,
                requests_cpu=0.1,
                limits_memory=128,
                requests_memory=64,
                environment_id=environment_id)

        with allure.step("Сохранение окружения"):
            requirements_txt = "pandas"
            environment_name = "test_python_environment_" + generate_string()
            python_body = script_environment_construct(name=environment_name,
                                                       python_version_id=v_id,
                                                       requirements_txt=requirements_txt,
                                                       python_environment_setting=[environment])
            python_environment = create_python_environment(super_user, python_body)
            vers_id = python_environment.body["uuid"]
        with allure.step("Поиск окружения по версии айди"):
            resp = get_environment_python_version(super_user, vers_id)
            python_environment_version = resp.body["versionId"]
        with allure.step("Создание переменных"):
            inp_var = script_vars_construct(var_name="input_int",
                                            var_type=VariableType1.IN,
                                            is_array=False, primitive_id="1")
            out_var = script_vars_construct(var_name="output_int",
                                            var_type=VariableType1.OUT,
                                            is_array=False, primitive_id="1")
        with allure.step("Создание параметров скрипта"):
            script_text = "import pandas\ndef run(data: dict):\n  return {'output_int': data['input_int'] * 5}"
            script_name = "ag_python_script_" + generate_string()
            script = code_construct(script_type="python",
                                    script_name=script_name,
                                    script_text=script_text,
                                    python_environment_version_id=python_environment_version,
                                    variables=[inp_var, out_var])
            python_code_create_result = ScriptFullView.construct(
                **create_python_script(super_user, body=script).body)

        with allure.step("Удаление окружения связанного со скриптом по версии айди"):
            with pytest.raises(HTTPError, match='400') as e:
                delete_python_environment(super_user, vers_id)
            delete_response: ResponseDto = ResponseDto(**e.value.response.json())

        with allure.step("Проверка что окружение удалилось и действительно было связано со скриптом"):
            assert delete_response.message == f"Ошибка при удалении окружения Python: Окружение используется в " \
                                              f"следующих кастомных кодах (имя (идентификатор версии)): " \
                                              f"{python_code_create_result.objectName} " \
                                              f"({str(python_code_create_result.versionId)})"

    @allure.story("Можно удалить  Версию  Python связанную с  окружением, если окружение удалить")
    @allure.title("Создание версию для окружния Питон и создать с ним окружение,"
                  " удалить окружение, удалить версию, проверить что удаление успешно")
    @pytest.mark.scenario("DEV-19864")
    @pytest.mark.environment_dependent
    def test_delete_version_python_environment_without_link(self, super_user, get_env):
        with allure.step("Создать версию"):
            v_id = str(uuid.uuid4())
            version_name = "test_python_3.6_" + generate_string()
            image = "harbor.k8s.datasapience.ru/datasapience-registry/st-di/udf-server"
            current_vers_list = get_python_version_list(super_user)

            python_version = python_version_construct(v_id=v_id,
                                                      version_name=version_name,
                                                      image=image)
            new_list = current_vers_list + [python_version]

            create_python_version(super_user, new_list)

        with allure.step("заполнение настроек окружения"):
            environment_id = get_env.get_env_id()
            environment = python_environment_setting_construct(
                limits_cpu=0.3,
                requests_cpu=0.1,
                limits_memory=128,
                requests_memory=64,
                environment_id=environment_id)

        with allure.step("Сохранение окружения"):
            requirements_txt = "pandas"
            environment_name = "test_python_environment_" + generate_string()
            python_body = script_environment_construct(name=environment_name,
                                                       python_version_id=v_id,
                                                       requirements_txt=requirements_txt,
                                                       python_environment_setting=[environment])
            python_environment = create_python_environment(super_user, python_body)
            vers_id = python_environment.body["uuid"]

        with allure.step("Удаление окружения по айди версии"):
            delete_python_environment(super_user, vers_id)
        with allure.step("Удалить версию"):
            create_python_version(super_user, current_vers_list)
        with allure.step("Получение списка версий python"):
            new_vers_list = get_python_version_list(super_user)
        with allure.step("Актуальный список версий соответствует списку версий до создания версии"):
            assert new_vers_list == current_vers_list
