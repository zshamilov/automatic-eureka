import uuid

import glamor as allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from config import settings
from products.Decision.framework.model import (
    ResponseDto,
    DataProviderGetFullView,
    TablesDto,
    SourceType,
    ColumnsDto, ConnectionType, )
from products.Decision.framework.steps.decision_steps_data_provider_api import (
    create_data_provider,
    delete_data_provider,
    get_data_provider,
    providers_list,
    get_data_provider_tables,
    make_test_connection,
    get_data_provider_table,
    update_data_provider,
)
from products.Decision.utilities.data_provider_constructors import *
from products.Template.framework.steps.template_variables import generate_rnd_string


@allure.epic("Источники данных")
@allure.feature("Настройка источников данных")
@pytest.mark.scenario("DEV-523")
class TestAdministrationDataSource:
    @allure.story("Удалённый источник данных не находится по id")
    @allure.title("Удалить источник данных, проверить, что не найден")
    @allure.issue("DEV-7099")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_delete_provider(self, super_user, get_env):
        provider_name = "data_provider_" + generate_string()
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                port=settings["DB_POSTGRESQL_PORT"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}'
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="made in test",
                settings=[setting],
            )
        with allure.step("Создание источника данных"):
            create_response: ResponseDto = ResponseDto.construct(
                **create_data_provider(super_user, body=data_provider).body
            )
        with allure.step("Удаление источника данных по id"):
            delete_data_provider(super_user, create_response.uuid)
        with allure.step("Поиск источника данных по id"):
            search_resp = get_data_provider(super_user, create_response.uuid)
        with allure.step("Проверка, что не найден"):
            assert search_resp.status == 204

    @allure.story("Удалённый источник данных пропадает из списка источников данных")
    @allure.title("Удалить источник данных, проверить, что пропал из списка источников")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_delete_provider_list(self, super_user, get_env):
        provider_created = False
        provider_name = "data_provider_" + generate_string()
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                port=settings["DB_POSTGRESQL_PORT"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}'
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="made in test",
                settings=[setting],
            )
        with allure.step("Создание источника данных"):
            create_response: ResponseDto = ResponseDto.construct(
                **create_data_provider(super_user, body=data_provider).body
            )
        with allure.step("Удаление источника данных по id"):
            delete_data_provider(super_user, create_response.uuid)
        with allure.step("Получение списка источников данных"):
            prov_list = []
            for prov in providers_list(super_user).body:
                prov_list.append(DataProviderGetFullView.construct(**prov))
            for provider in prov_list:
                if provider.sourceId == create_response.uuid:
                    provider_created = True
        with allure.step("Проверка что удалённый источник пропал из списка"):
            assert not provider_created

    @allure.story("Возможно создать валидный источник данных")
    @allure.title("Создать источник данных, проверить, что появилось в списке")
    @pytest.mark.sdi
    @pytest.mark.smoke
    @pytest.mark.postgres
    def test_create_provider(self, super_user, get_env, create_data_provider_gen):
        provider_created = False
        provider_name = "data_provider_" + generate_string()
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                port=settings["DB_POSTGRESQL_PORT"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}'
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="made in test",
                settings=[setting],
            )
        with allure.step("Создание источника данных"):
            create_response: ResponseDto = create_data_provider_gen.create_provider(
                data_provider
            )
        with allure.step("Получение списка источников данных"):
            prov_list = []
            for prov in providers_list(super_user).body:
                prov_list.append(DataProviderGetFullView.construct(**prov))
            for provider in prov_list:
                if provider.sourceId == create_response.uuid:
                    provider_created = True
        with allure.step("Проверка что источник данных появился в списке"):
            assert provider_created

    @allure.story(
        "При задании несуществующего окружения или с пропущенными полями в настройках окружении - "
        "сохранение источника запрещено"
    )
    @allure.title("Создать источник данных с недопустимыми параметрами")
    @allure.issue("DEV-6536")
    @pytest.mark.parametrize(
        "env_type, status", [("exist, field lost", 400), ("not exist, all fields", 400)]
    )
    @pytest.mark.scenario("DEV-5839")
    @pytest.mark.sdi
    @pytest.mark.postgres
    def test_create_provider_bad(
            self, super_user, get_env, create_data_provider_gen, env_type, status
    ):
        provider_name = "data_provider_" + generate_string()
        env_id = None
        port = None
        if env_type == "exist, field lost":
            env_id = get_env.get_env_id("default_dev")
        if env_type == "not exist, all fields":
            env_id = str(uuid.uuid4())
            port = 5432
        with allure.step("Подготовка параметров источника данных"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                port=port,
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}'
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="made in test",
                settings=[setting],
            )
        with allure.step("Проверка что клиенту запрещено создание такого источника"):
            with pytest.raises(HTTPError, match=str(status)):
                assert create_data_provider_gen.try_create_provider(
                    data_provider
                ).status == status

    @allure.story("Возможно получить конкретный источник данных")
    @allure.title("Получить источник данных, проверить поля")
    @pytest.mark.sdi
    @pytest.mark.smoke
    @pytest.mark.postgres
    def test_search_provider(self, super_user, get_env, create_data_provider_gen):
        provider_name = "data_provider_" + generate_string()
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                port=settings["DB_POSTGRESQL_PORT"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}'
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="made in test",
                settings=[setting],
            )
        with allure.step("Создание источника данных"):
            create_response: ResponseDto = create_data_provider_gen.create_provider(
                data_provider
            )
        with allure.step("Поиск источника данных по id"):
            search_resp: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
        with allure.step(
                "Проверка, что поля найденного источника соответствуют заданным"
        ):
            assert (
                    search_resp.sourceId == create_response.uuid
                    and search_resp.sourceType == "POSTGRES"
                    and search_resp.sourceName == provider_name
                    and search_resp.connectionType == ConnectionType.JDBC
            )

    @allure.story("Для валидного источника данных возможно получить список таблиц ")
    @allure.title("Для созданного источника данных запросить список таблиц")
    @pytest.mark.sdi
    @pytest.mark.smoke
    @pytest.mark.postgres
    def test_search_provider_tables(
            self, super_user, get_env, create_data_provider_gen, create_db_all_tables_and_scheme
    ):
        provider_name = "data_provider_" + generate_string()
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                port=settings["DB_POSTGRESQL_PORT"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}'
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="description",
                settings=[setting],
            )
        with allure.step("Создание источника данных"):
            create_response: ResponseDto = create_data_provider_gen.create_provider(
                data_provider
            )
        with allure.step("Поиск источника данных по id"):
            prov_list = []
            for prov in providers_list(super_user).body:
                prov_list.append(DataProviderGetFullView.construct(**prov))
            search_resp: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
        with allure.step("Поиск списка таблиц по id источника данных"):
            table_list = []
            for table in get_data_provider_tables(
                    super_user, search_resp.sourceId
            ).body:
                table_list.append(TablesDto(**table))
        with allure.step("Проверка, что таблицы подгружены и поля таблиц не пустые"):
            assert len(table_list) != 0 and all(
                table.tableName is not None and table.schemaName is not None
                for table in table_list
            )

    @allure.story(
        "Для валидного источника данных можно получить таблицу из списка таблиц"
    )
    @allure.title("Для созданного источника данных получить таблицу из списка")
    @pytest.mark.sdi
    @pytest.mark.smoke
    @pytest.mark.postgres
    def test_search_provider_table(self, super_user, get_env, create_data_provider_gen,
                                   create_db_all_tables_and_scheme):
        provider_name = "data_provider_" + generate_string()
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                port=settings["DB_POSTGRESQL_PORT"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}'
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="description",
                settings=[setting],
            )
        with allure.step("Создание источника данных"):
            create_response: ResponseDto = create_data_provider_gen.create_provider(
                data_provider
            )
        with allure.step("Поиск источника данных по id"):
            search_resp: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
            source_id = search_resp.sourceId
        with allure.step("Поиск списка таблиц по id источника данных"):
            table_list = []
            for table in get_data_provider_tables(
                    super_user, search_resp.sourceId
            ).body:
                table_list.append(TablesDto(**table))
            table_name = table_list[0].tableName
        with allure.step("Поиск таблицы по id источника данных и названию"):
            columns = []
            for column in get_data_provider_table(
                    super_user, source_id=source_id, table_name=table_name
            ).body:
                columns.append(ColumnsDto(**column))
        with allure.step(
                "Проверка, что у таблицы есть колонки и у них есть тип данных"
        ):
            assert len(columns) != 0 and all(
                column.columnName is not None and column.dataType is not None
                for column in columns
            )

    @allure.story("Возможно протестировать подключение к конкретному источнику данных")
    @allure.title("Для созданного источника данных протестировать соединение")
    @pytest.mark.parametrize(
        "provider_type, connection_result",
        [("valid", "SUCCESS"), ("not valid", "FAILED"), ("not existing", "FAILED")],
    )
    @pytest.mark.sdi
    @pytest.mark.smoke
    @pytest.mark.postgres
    def test_search_provider_connection(
            self,
            super_user,
            get_env,
            create_data_provider_gen,
            provider_type,
            connection_result
    ):
        user_name = None
        password = None
        env_id = None
        server_name = None
        provider_name = "data_provider_" + generate_string()
        port = settings["DB_POSTGRESQL_PORT"]
        additional_properties = ""
        env_id = get_env.get_env_id("default_dev")
        with allure.step("Задание параметризированных данных"):
            if provider_type == "valid":
                user_name = settings["DB_POSTGRESQL_USERNAME"]
                password = settings["DB_POSTGRESQL_PASSWORD"]
                server_name = settings["DB_POSTGRESQL_HOST"]
            if provider_type == "not valid":
                user_name = "postgresss"
                password = "postgresss"
                server_name = "decision-postgresql"
            if provider_type == "not existing":
                user_name = "postgres"
                password = "postgres"
                server_name = "believe me, i'm a server"
        with allure.step("Подготовка параметров источника данных"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=server_name,
                port=port,
                username=user_name,
                password=password,
                additional_properties=additional_properties,
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}'
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="description",
                settings=[setting],
            )
        with allure.step("Создание источника данных"):
            create_response: ResponseDto = create_data_provider_gen.create_provider(
                data_provider
            )
        with allure.step("Запуск теста соединения для источника данных"):
            connection_body = connection_test_construct(
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                settings=[setting],
            )
            connection_response = make_test_connection(
                super_user, body=connection_body
            ).body
        with allure.step(
                "Проверка, что результат соединения соответствует параметрам соединения"
        ):
            assert connection_response["result"] == connection_result

    @allure.story("Возможно обновить источника данных")
    @allure.title("Обновить настройки, имя и описание источника данных")
    @pytest.mark.sdi
    @pytest.mark.smoke
    @pytest.mark.postgres
    def test_update_provider(self, super_user, get_env, create_data_provider_gen):
        provider_name = "data_provider_" + generate_string()
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                port=settings["DB_POSTGRESQL_PORT"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}'
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="made in test",
                settings=[setting],
            )
        with allure.step("Создание источника данных"):
            create_response: ResponseDto = create_data_provider_gen.create_provider(
                data_provider
            )
        with allure.step("Поиск источника данных по id"):
            search_resp: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
        settings_up = provider_setting_update_construct(
            environment_settings_id=env_id,
            server_name=settings["DB_POSTGRESQL_HOST"],
            port=settings["DB_POSTGRESQL_PORT"],
            username="postgres_update",
            password="postgres_update",
            additional_properties="",
            database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
            input_type="parameters",
            url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}',
            source_settings_id=search_resp.settings[0]["sourceSettingsId"],
        )
        provider_name_up = "data_provider_up_" + generate_string()
        provider_up = data_provider_update_construct(
            source_name=provider_name_up,
            source_type=SourceType.POSTGRES,
            connection_type=ConnectionType.JDBC,
            description="updated",
            settings=[settings_up],
        )
        update_data_provider(
            super_user, source_id=search_resp.sourceId, body=provider_up
        )
        with allure.step("Поиск источника данных по id"):
            search_resp_up: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
            assert (
                    search_resp_up.sourceName == provider_name_up
                    and search_resp_up.description == "updated"
                    and search_resp_up.settings[0]["username"] == "postgres_update"
                    and search_resp_up.settings[0]["password"] == "postgres_update"
            )

    @allure.story(
        "Для источника данных можно указать схему"
    )
    @allure.title("Создать источник данных, при создании указать схему, проверить что подключение дает таблицы,"
                  " которые есть в этой схеме")
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-13502")
    @pytest.mark.postgres
    def test_scheme_provider_table(self, super_user, get_env,
                                   create_db_all_tables_and_scheme, create_data_provider_gen):
        schema_name = create_db_all_tables_and_scheme["schema_name"]
        table_name = create_db_all_tables_and_scheme["table_in_schema"].name
        provider_name = "data_provider_" + generate_string()
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                port=settings["DB_POSTGRESQL_PORT"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}',
                scheme=schema_name
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="description",
                settings=[setting],
            )
        with allure.step("Создание источника данных со схемойб"):
            create_response: ResponseDto = create_data_provider_gen.create_provider(
                data_provider
            )
        with allure.step("Поиск источника данных по id"):
            search_resp: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
        with allure.step("Поиск списка таблиц по id источника данных"):
            table_list = []
            for table in get_data_provider_tables(
                    super_user, search_resp.sourceId
            ).body:
                table_list.append(TablesDto(**table))
            assert all(table.tableName == table_name and table.schemaName == schema_name for table in table_list)

    @allure.story(
        "Для источника данных можно указать схему, получить таблицы и колонки этих таблиц"
    )
    @allure.title("Создать источник данных, при создании указать схему, проверить что подключение дает таблицы,"
                  " которые есть в этой схеме и их колонки")
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-13502")
    @allure.issue("DEV-19716")
    @pytest.mark.postgres
    def test_scheme_provider_table_columns(self, super_user, get_env, create_db_all_tables_and_scheme,
                                           create_data_provider_gen):
        schema_name = create_db_all_tables_and_scheme["schema_name"]
        table_name = create_db_all_tables_and_scheme["table_in_schema"].name
        provider_name = "data_provider_" + generate_string()
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                port=settings["DB_POSTGRESQL_PORT"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}',
                scheme=schema_name
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="description",
                settings=[setting],
            )
        with allure.step("Создание источника данных со схемой"):
            create_response: ResponseDto = create_data_provider_gen.create_provider(
                data_provider
            )
        with allure.step("Поиск источника данных по id"):
            search_resp: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
        with allure.step("Поиск таблицы по id источника данных и названию"):
            columns_resp = get_data_provider_table(
                super_user, source_id=search_resp.sourceId, table_name=table_name
            )
        with allure.step(
                "Проверка, что у таблицы вернулись колонки"
        ):
            assert len(columns_resp.body) != 0

    @allure.story(
        "Для источника данных можно указать схему, обновив источник данных"
    )
    @allure.title("Создать источник данных, при создании не указывать схему, обновить( указав схему) "
                  "проверить что подключение дает таблицы,которые есть в этой схеме")
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-13502")
    @pytest.mark.postgres
    def test_scheme_update_provider_table(self, super_user, get_env,
                                          create_data_provider_gen, create_db_all_tables_and_scheme):
        provider_name = "data_provider_" + generate_string()
        expected_table_name = create_db_all_tables_and_scheme["table_in_schema"].name
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                port=settings["DB_POSTGRESQL_PORT"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}',
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="description",
                settings=[setting],
            )
        with allure.step("Создание источника данных без схемы"):
            create_response: ResponseDto = create_data_provider_gen.create_provider(
                data_provider
            )
        with allure.step("Поиск источника данных по id"):
            search_resp1: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
        with allure.step("обновление источника данных по id с указанием схемы"):
            setting_up = setting
            setting_up.scheme = create_db_all_tables_and_scheme["schema_name"]
            data_provider_up = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="description",
                settings=[setting_up],
            )
            update_data_provider(
                super_user, source_id=search_resp1.sourceId, body=data_provider_up
            )
        with allure.step("Поиск источника данных по id"):
            search_resp: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
        with allure.step("Поиск списка таблиц по id источника данных"):
            table_list = []
            for table in get_data_provider_tables(
                    super_user, search_resp.sourceId
            ).body:
                table_list.append(TablesDto(**table))
            assert table_list[0].tableName == expected_table_name

    @allure.story(
        "Для источника с указанием не существующей схемы приходит пустой список таблиц"
    )
    @allure.title("Создать источник данных, при создании  указать не существующую схему,"
                  " проверить что приходит пустой список")
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-13502")
    @pytest.mark.postgres
    def test_random_scheme_provider_table(self, super_user, get_env, create_data_provider_gen):
        provider_name = "data_provider_" + generate_string()
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных"):
            scheme_name = generate_string(10)
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                port=settings["DB_POSTGRESQL_PORT"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}',
                scheme=scheme_name
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="description",
                settings=[setting],
            )
        with allure.step("Создание источника данных с не существующей схемой схемой"):
            create_response: ResponseDto = create_data_provider_gen.create_provider(
                data_provider
            )
        with allure.step("Поиск источника данных по id"):
            search_resp: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
        with allure.step("Проверка на то, что список таблиц пуст"):
            table_list = []
            for table in get_data_provider_tables(
                    super_user, search_resp.sourceId
            ).body:
                table_list.append(TablesDto(**table))
            assert len(table_list) == 0

    @allure.story(
        "Для источника с указанием не существующей схемы при обновлении приходит пустой список таблиц"
    )
    @allure.title("Создать источник данных, при создании не указывать схему, обновить( указав не существующую схему) "
                  "проверить что приходит пустой список ")
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-13502")
    @pytest.mark.postgres
    def test_random_scheme_update_provider_table(self, super_user, get_env, create_data_provider_gen):
        provider_name = "data_provider_" + generate_string()
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                port=settings["DB_POSTGRESQL_PORT"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}',
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="description",
                settings=[setting],
            )
        with allure.step("Создание источника данных без схемы"):
            create_response: ResponseDto = create_data_provider_gen.create_provider(
                data_provider
            )
        with allure.step("Поиск источника данных по id"):
            search_resp1: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
        with allure.step("обновление источника данных по id с указанием не существующей схемы"):
            scheme_name = generate_rnd_string(10)
            setting_up = setting
            setting_up.scheme = scheme_name
            data_provider_up = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="description",
                settings=[setting_up],
            )
            update_data_provider(
                super_user, source_id=search_resp1.sourceId, body=data_provider_up
            )
        with allure.step("Поиск источника данных по id"):
            search_resp: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
        with allure.step("Проверка на то, что список таблиц пуст"):
            table_list = []
            for table in get_data_provider_tables(
                    super_user, search_resp.sourceId
            ).body:
                table_list.append(TablesDto(**table))
            assert len(table_list) == 0

    @allure.story(
        "Для источника данных можно указать только URL"
    )
    @allure.title("Создать источник данных, при создании указать URL, проверить что подключение дает таблицы,"
                  " и схему из указанной бд в URL")
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-22009")
    @pytest.mark.postgres
    @pytest.mark.parametrize("server_name, port, database", [("10.22.0.77", 99, "test"), ("", "", "")])
    def test_url_provider_table(self, super_user, get_env,
                                create_db_all_tables_and_scheme, create_data_provider_gen, server_name, port, database):
        with allure.step("Поиск названия  схемы и таблицы в созданной бд"):
            schema_name = create_db_all_tables_and_scheme["schema_name"]
            table_name = create_db_all_tables_and_scheme["table_in_schema"].name
            provider_name = "data_provider_" + generate_string()
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных, "
                         "задаем в значениях порта, бд и сервера произвольные значения либо пустые, "
                         "в input_type выбираем url, где указываем нужный адрес бд"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=server_name,
                port=port,
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=database,
                input_type="url",
                scheme="kk_schema",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}'
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="description",
                settings=[setting],
            )
        with allure.step("Создание источника данных"):
            create_response: ResponseDto = create_data_provider_gen.create_provider(
                data_provider
            )
        with allure.step("Поиск источника данных по id"):
            search_resp: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
        with allure.step("Поиск списка таблиц по id источника данных"):
            table_list = []
            for table in get_data_provider_tables(
                    super_user, search_resp.sourceId
            ).body:
                table_list.append(TablesDto(**table))
            assert all(table.tableName == table_name and table.schemaName == schema_name for table in table_list)


    @allure.story(
          "При выборе input_type parameters, бэк сам формирует url не зависимо от значения поля url"
    )
    @allure.title("Создать источник данных, при создании не указывать URL, проверить что подключение дает таблицы,"
                  " и схему из указанной бд в параметрах")
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-22009")
    @pytest.mark.postgres
    def test_parameters_provider_table(self, super_user, get_env,
                                       create_db_all_tables_and_scheme, create_data_provider_gen):
        with allure.step("Поиск названия  схемы и таблицы в созданной бд"):
            schema_name = create_db_all_tables_and_scheme["schema_name"]
            table_name = create_db_all_tables_and_scheme["table_in_schema"].name
            provider_name = "data_provider_" + generate_string()
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных, "
                         "задаем в значениях порта, бд и сервера верное значение, "
                         "в input_type выбираем parameters. url -оставляем не заполненным"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name=settings["DB_POSTGRESQL_HOST"],
                port=settings["DB_POSTGRESQL_PORT"],
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database=settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"],
                input_type="parameters",
                url="",
                scheme=schema_name
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.POSTGRES,
                connection_type=ConnectionType.JDBC,
                description="description",
                settings=[setting],
            )
        with allure.step("Создание источника данных со схемой"):
            create_response: ResponseDto = create_data_provider_gen.create_provider(
                data_provider
            )
        with allure.step("Поиск источника данных по id"):
            search_resp: DataProviderGetFullView = DataProviderGetFullView.construct(
                **get_data_provider(super_user, create_response.uuid).body
            )
        with allure.step("Поиск списка таблиц по id источника данных"):
            table_list = []
            for table in get_data_provider_tables(
                    super_user, search_resp.sourceId
            ).body:
                table_list.append(TablesDto(**table))
            assert all(table.tableName == table_name and table.schemaName == schema_name for table in table_list)

    @allure.story(
        "Для источника данных где inputType: url, предусмотренна валидация на соответствие типу источника"
    )
    @allure.title("Создать источник данных, при создании указать URL и тип источника указать не верно")
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-22009")
    @pytest.mark.postgres
    def test_url_provider_another_type(self, super_user, get_env,
                                       create_db_all_tables_and_scheme, create_data_provider_gen):
        with allure.step("Поиск названия  схемы и таблицы в созданной бд"):
            schema_name = create_db_all_tables_and_scheme["schema_name"]
            table_name = create_db_all_tables_and_scheme["table_in_schema"].name
            provider_name = "data_provider_" + generate_string()
        with allure.step("Поиск окружения"):
            env_id = get_env.get_env_id("default_dev")
        with allure.step("Подготовка параметров источника данных, "
                         "задаем в значениях порта, бд и сервера произвольные значения, "
                         "в input_type выбираем url, где указываем нужный адрес бд, "
                         "выбираем не верный тип источника"):
            setting = provider_setting_construct(
                environment_settings_id=env_id,
                server_name="10.22.0.77",
                port=99,
                username=settings["DB_POSTGRESQL_USERNAME"],
                password=settings["DB_POSTGRESQL_PASSWORD"],
                additional_properties="",
                database="test",
                input_type="url",
                scheme="kk_schema",
                url=f'jdbc:postgresql://{settings["DB_POSTGRESQL_HOST"]}:{settings["DB_POSTGRESQL_PORT"]}/'
                    f'{settings["DB_POSTGRESQL_ADDITIONAL_PROPERTIES"]}'
            )
            data_provider = data_provider_construct(
                source_name=provider_name,
                source_type=SourceType.ORACLE,
                connection_type=ConnectionType.JDBC,
                description="description",
                settings=[setting],
            )
        with allure.step("Создание источника данных"):
            with pytest.raises(HTTPError, match="400"):
                assert create_data_provider_gen.create_provider(data_provider)
