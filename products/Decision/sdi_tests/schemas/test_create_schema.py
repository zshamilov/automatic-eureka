import allure
import pytest

from common.generators import generate_string
from products.Decision.framework.model import SchemaIdDto, SchemaFullDto
from products.Decision.framework.steps.decision_steps_schema import create_schema, find_schema_by_id
from products.Decision.utilities.schema_constructors import schema_construct


@allure.epic("Схемы")
@allure.feature("Создание схемы")
@pytest.mark.scenario("DEV-13329")
class TestCreateSchema:

    @allure.story("Найти схему после создания, увидеть, что создалась с заданными данными")
    @allure.title("Созданную схему возможно найти в системе")
    def test_create_schema(self, super_user):
        with allure.step("Создание схемы с целочисленным и строковым полем"):
            scheme_data = {"id": "int", "some_name": "string"}
            schema_name = "ag_scheme_" + generate_string()
            schema_body = schema_construct(name=schema_name,
                                           schema_data=scheme_data)
            schema_id = SchemaIdDto(**create_schema(super_user, schema_body).body).id
        with allure.step("Поиск информации о созданной схеме"):
            schema_info = SchemaFullDto(**find_schema_by_id(super_user, schema_id).body)
        with allure.step("У соданной схемы информация соответствует параметрам при задании"):
            assert schema_info.id is not None
            assert schema_info.url is not None
            assert schema_info.name == schema_name