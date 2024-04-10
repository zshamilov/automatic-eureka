import time
from random import randint

import allure

from products.Decision.framework.db_framework import db_model
from products.Decision.framework.db_framework.db_steps.db_steps_test_tables import insert_rows_with_values_in_table, \
    get_row_count, lv_get_row_count, select_all_where
from products.Decision.framework.model import DeployConfigurationFullDto, DiagramInOutParameterFullViewDto
from products.Decision.framework.steps.decision_steps_deploy import check_deploy_status, deploy_config, find_deploy_id
from products.Decision.framework.steps.decision_steps_diagram import put_diagram_submit
from products.Decision.framework.steps.decision_steps_integration import send_message
from products.Decision.runtime_tests.runtime_fixtures.jdbc_write_fixtures import *
from products.Decision.utilities.custom_models import VariableParams, BasicPrimitiveValues, AttrInfo


@allure.epic("Сохранение данных")
@allure.feature("Сохранение данных")
class TestRuntimeInsert:

    @allure.story("Диаграмма с узлом сохранения данных отправляется на развёртку")
    @allure.title("Создать диаграмму, отправить на развертывание, проверить, что успешно")
    @pytest.mark.postgres
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.nodes(["запись"])
    def test_submit_diagram_insert(self, db_user, create_db_all_tables_and_scheme,
                                   super_user, diagram_insert_saved_2):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = diagram_insert_saved_2["diagram_id"]
            version_id = diagram_insert_saved_2["saved_version_id"]
            diagram_name = diagram_insert_saved_2["diagram_name"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Проверка, что диаграмма найдена в списке деплоев"):
            diagram_submitted = check_deploy_status(super_user,
                                                    diagram_name=diagram_name,
                                                    diagram_id=diagram_id,
                                                    status="READY_FOR_DEPLOY")
            assert diagram_submitted

    @allure.story(
        "Диаграмма с узлом чтения отправляется на развёртку"
    )
    @allure.title(
        "Отправить сообщение в диаграмму с узлом записи, проверить, что ответ верный"
    )
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["запись"])
    def test_send_message_diagram_with_insert_node(self, db_user, create_db_all_tables_and_scheme,
                                                   super_user, diagram_insert_submitted_2,
                                                   integration_user,
                                                   deploy_diagrams_gen):
        with allure.step("Деплой подготовленной диаграммы"):
            diagram_id = diagram_insert_submitted_2["diagram_id"]
            diagram_name = diagram_insert_submitted_2["diagram_name"]
            deploy_id = diagram_insert_submitted_2["deploy_id"]
            diagram_param: DiagramInOutParameterFullViewDto = diagram_insert_submitted_2["diagram_param"]
            env_id = diagram_insert_submitted_2["env_id"]
            config: DeployConfigurationFullDto = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["config"]
            table_name = diagram_insert_submitted_2["table_name"]
            column_name = diagram_insert_submitted_2["int_column"]
            random_in_value = primitive_value_message_contsructor(IntValueType.int.value)[0]
        with allure.step("Проверить, что статус диаграммы DEPLOYED"):
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
        with allure.step("Получить настройки развёрнутого деплоя"):
            call_uri = config.callUri
        with allure.step("Отправка сообщения в развёрнутый деплой"):
            time.sleep(10)
            send_message(
                integration_user,
                call_uri=call_uri,
                body={f"{diagram_param.parameterName}": random_in_value},
            )
            time.sleep(5)
        with allure.step("Чтение значений из таблицы базы данных"):
            db_table = create_db_all_tables_and_scheme[table_name]
            db_column = getattr(db_table.c, column_name)
            select_response = select_all_where(db_user, [db_column],
                                               db_column == random_in_value)
        with allure.step("В БД появилась соответствующая сообщению запись"):
            assert len(select_response[db_column.name]) == 1
            assert (select_response[db_column.name][0] == random_in_value)

    @allure.story("В диаграмму с узлом сохранение данных с записью примитивного массива с флагом записи множества "
                  "элементов в узле можно отправить сообщение")
    @allure.title("Отправить сообщение в диаграмму с узлом сохранение данных с записью примитивного массива, "
                  "проверить, что ответ корректный")
    @pytest.mark.scenario("DEV-7611")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_int", varType="in_out", varDataType=IntValueType.int.value, isArray=True,
                        isConst=False, varValue="in_int")])
    @pytest.mark.nodes(["запись"])
    @pytest.mark.array_flag(True)
    @allure.issue("DEV-19850")
    def test_send_message_diagram_with_insert_node_array_flag(self, db_user, create_db_all_tables_and_scheme,
                                                              super_user,
                                                              integration_user, insert_primitive_array_saved, get_env,
                                                              deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = insert_primitive_array_saved["diagram_data"].diagramId
            diagram_name = insert_primitive_array_saved["diagram_name"]
            table_name = insert_primitive_array_saved["table_name"]
            column_name = insert_primitive_array_saved["int_column"]
            random_in_values = primitive_value_message_contsructor(IntValueType.int.value, 2)
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Запомнить деплой айди"):
            deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
        with allure.step("Деплой подготовленной диаграммы"):
            env_id = get_env.get_env_id("default_dev")
            config: DeployConfigurationFullDto = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["config"]
        with allure.step("Проверить, что статус диаграммы DEPLOYED"):
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
            call_uri = config.callUri
        with allure.step("Отправка сообщения в развёрнутую диаграмму"):
            time.sleep(10)
            send_message(
                integration_user,
                call_uri=call_uri,
                body={
                    "in_int":
                        random_in_values
                }
            )
            time.sleep(5)
        with allure.step("Чтение значений из таблицы базы данных"):
            db_table = create_db_all_tables_and_scheme[table_name]
            db_column = getattr(db_table.c, column_name)
            select_response = select_all_where(db_user, [db_column],
                                               db_column.in_(random_in_values))
        with allure.step("Проверка, что в таблицу записалось столько строк, сколько подано на вход"):
            assert len(select_response[db_column.name]) == len(random_in_values)
            assert set(select_response[db_column.name]) == set(random_in_values)

    @allure.story("В диаграмму с узлом сохранение данных с записью примитивного массива без флага записи множества "
                  "элементов в узле можно отправить сообщение")
    @allure.title("Отправить сообщение в диаграмму с узлом сохранение данных с записью примитивного массива, "
                  "проверить, что ответ корректный")
    @pytest.mark.scenario("DEV-7611")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_int", varType="in_out", varDataType=IntValueType.int.value, isArray=True,
                        isConst=False, varValue="in_int")])
    @pytest.mark.nodes(["запись"])
    def test_send_message_diagram_with_insert_node_not_array_flag(self, db_user, super_user,
                                                                  create_db_all_tables_and_scheme,
                                                                  integration_user, insert_primitive_array_saved,
                                                                  get_env,
                                                                  deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = insert_primitive_array_saved["diagram_data"].diagramId
            diagram_name = insert_primitive_array_saved["diagram_name"]
            table_name = insert_primitive_array_saved["table_name"]
            column_name = insert_primitive_array_saved["int_column"]
            random_in_values = primitive_value_message_contsructor(IntValueType.int.value, 2)
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Запомнить деплой айди"):
            deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
        with allure.step("Деплой подготовленной диаграммы"):
            env_id = get_env.get_env_id("default_dev")
            config: DeployConfigurationFullDto = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["config"]
        with allure.step("Проверить, что статус диаграммы DEPLOYED"):
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
            call_uri = config.callUri
        with allure.step("Отправка сообщения в развёрнутую диаграмму"):
            time.sleep(10)
            send_message(
                integration_user,
                call_uri=call_uri,
                body={
                    "in_int":
                        random_in_values
                }
            )
            time.sleep(5)
        with allure.step("Чтение значений из таблицы базы данных"):
            db_table = create_db_all_tables_and_scheme[table_name]
            db_column = getattr(db_table.c, column_name)
            select_response = select_all_where(db_user, [db_column],
                                               db_column.in_(random_in_values))
        with allure.step("Проверка, что в таблицу записалась 1 строка"):
            assert len(select_response[db_column.name]) == 1
            assert select_response[db_column.name][0] in random_in_values

    @allure.story("После отправки сообщения в диаграмму, с узлом сохранение данных с записью массива пользовательского "
                  "типа с флагом записи множества элементов в узле, в БД происходится запись соответствующих значений ")
    @allure.title("Отправить сообщение в диаграмму с узлом сохранение данных с записью массива пользовательского "
                  "типа с флагом записи множества элементов в узле, проверить, что запись произошла")
    @pytest.mark.scenario("DEV-7611")
    @pytest.mark.postgres
    @pytest.mark.table_name(db_model.insert_node_table.name)
    @pytest.mark.variable_data(
        [VariableParams(varName="in_ctype", varType="in_out", isArray=True,
                        isComplex=True, isConst=False, varValue="in_ctype",
                        cmplxAttrInfo=[AttrInfo(attrName="float_attr",
                                                intAttrType=IntValueType.float),
                                       AttrInfo(attrName="int_attr",
                                                intAttrType=IntValueType.int),
                                       AttrInfo(attrName="str_attr",
                                                intAttrType=IntValueType.str),
                                       AttrInfo(attrName="date_attr",
                                                intAttrType=IntValueType.date),
                                       AttrInfo(attrName="bool_attr",
                                                intAttrType=IntValueType.bool),
                                       AttrInfo(attrName="time_attr",
                                                intAttrType=IntValueType.time),
                                       AttrInfo(attrName="datetime_attr",
                                                intAttrType=IntValueType.dateTime),
                                       AttrInfo(attrName="long_attr",
                                                intAttrType=IntValueType.long)])])
    @pytest.mark.array_flag(True)
    @pytest.mark.nodes(["запись"])
    def test_send_message_diagram_with_insert_node_ctype_array_flag(self, db_user, super_user,
                                                                    create_db_all_tables_and_scheme,
                                                                    integration_user, insert_ctype_array_saved,
                                                                    get_env,
                                                                    deploy_diagrams_gen):
        with allure.step("Создание и сохранение диаграммы с заданными параметрами"):
            diagram_id = insert_ctype_array_saved["diagram_data"].diagramId
            diagram_name = insert_ctype_array_saved["diagram_name"]
            table_name = insert_ctype_array_saved["table_name"]
            mapped_ctype_attr_to_db_column = insert_ctype_array_saved["mapped_ctype_attr_to_db_column"]
            ctype_attrs = insert_ctype_array_saved["in_var_attrs"]
        with allure.step("Сабмит подготовленной диаграммы"):
            put_diagram_submit(super_user, diagram_id)
        with allure.step("Запомнить деплой айди"):
            deploy_id = find_deploy_id(super_user, diagram_name, diagram_id)
        with allure.step("Деплой подготовленной диаграммы"):
            env_id = get_env.get_env_id("default_dev")
            config: DeployConfigurationFullDto = deploy_diagrams_gen.deploy_diagram(deploy_id, env_id)["config"]
        with allure.step("Проверить, что статус диаграммы DEPLOYED"):
            assert check_deploy_status(user=super_user,
                                       diagram_name=diagram_name,
                                       diagram_id=diagram_id,
                                       status="DEPLOYED")
            call_uri = config.callUri
        with allure.step("Генерация входного сообщения диаграммы с переменной массивом пользовательского типа"
                         " заданной длины"):
            in_message_array_of_dicts = []

            # генерируем из атрибутов комплексного типа список длины 2 из словарей для последующей отправки
            for el in range(2):
                array_el = dict()
                for attribute in ctype_attrs:
                    array_el[attribute.attributeName] = primitive_value_message_contsructor(attribute.primitiveTypeId)[0]
                in_message_array_of_dicts.append(array_el)
        with allure.step("Отправка сообщения в развёрнутую диаграмму"):
            time.sleep(10)
            send_message(
                integration_user,
                call_uri=call_uri,
                body={
                    "in_ctype":
                        in_message_array_of_dicts
                }
            )
            time.sleep(5)
        with allure.step("Чтение значений из таблицы базы данных"):
            db_table = create_db_all_tables_and_scheme[table_name]
            all_db_columns = db_table.columns
            db_column_name = mapped_ctype_attr_to_db_column["int_attr"]
            db_column = getattr(db_table.c, db_column_name)
            inserted_values_in = [attr["int_attr"] for attr in in_message_array_of_dicts]

            # читаем все столбцы из БД по int колонке значения, отправленные в сообщении(условие in)
            select_response = select_all_where(db_user, all_db_columns,
                                               db_column.in_(inserted_values_in))
        with allure.step("Приведение к единому виду вставленных и прочитанных значений"):
            all_values_from_db = []
            all_message_values = []

            # так как из селекта нам возвращает словарь, где ключ - название колонки, а значение список прочитанных из бд
            # значений - создаём один большой список прочитанного
            for value in select_response.values():
                all_values_from_db.extend(value)

            # для каждого элемента списка словарей берём все значения словаря и добавляем в 1 большой список
            for elem in in_message_array_of_dicts:
                all_message_values.extend(elem.values())
        with allure.step("Проверка, что все переданные в диаграмму значения присутствуют в таблице"):
            assert all(message_value in all_values_from_db for message_value in all_message_values)
