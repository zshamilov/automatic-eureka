import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import ResponseDto, ComplexTypeGetFullView
from products.Decision.framework.steps.decision_steps_complex_type import create_custom_type, complex_type_list, \
    delete_custom_type, get_custom_type
from products.Decision.utilities.custom_type_constructors import type_create_construct, attribute_construct, \
    generate_attr_type_name


@allure.epic("Пользовательские типы данных")
@allure.feature("Удаление пользовательского типа данных")
@pytest.mark.scenario("DEV-15468")
class TestCustomTypeDelete:

    @allure.story("Удалённая версия комплексного типа не находится на контуре")
    @allure.issue("DEV-5103")
    @allure.title("удалить кастомный тип, проверить, что пропал из списка")
    @pytest.mark.smoke
    def test_delete_custom_type(self, super_user):
        type_name = generate_attr_type_name(True, False, True, "")
        create_response = create_custom_type(super_user,
                                             body=type_create_construct(type_name,
                                                                        [attribute_construct()]))

        create_result: ResponseDto = ResponseDto.construct(**create_response.body)
        custom_type_version_id = create_result.uuid

        delete_response = delete_custom_type(super_user, str(custom_type_version_id))

        type_list = []
        for obj in complex_type_list(super_user).body["content"]:
            type_list.append(ComplexTypeGetFullView.construct(**obj))
        assert delete_response.status == 200 and all([complex_type.objectName != type_name
                                                      and complex_type.versionId != custom_type_version_id
                                                      for complex_type in type_list])

    @allure.story("Возможно удалить пользовательский тип вложенный в другой пользовательский тип")
    @allure.title("Удалить вложенный пользовательский тип в другой пользовательский тип")
    @allure.issue("DEV-7548")
    @pytest.mark.smoke
    def test_delete_custom_type_inside_another_type(self, super_user, create_custom_types_gen):
        type_name1 = generate_attr_type_name(True, False, True, "")
        type_name2 = generate_attr_type_name(True, False, True, "")
        with allure.step("Создание кастом типа"):
            create_response: ResponseDto = create_custom_types_gen.create_type(type_name1, [attribute_construct()])
            type1_version_id = create_response.uuid
        with allure.step("Создание второго кастом типа с первым внутри"):
            create_custom_types_gen.create_type(type_name2,
                                                [attribute_construct(False, True,
                                                                     "complex_attr",
                                                                     type1_version_id,
                                                                     None)])
        delete_custom_type(super_user, str(type1_version_id))
        with allure.step("Проверка, что удаление успешно и удалённый тип не найден"):
            with pytest.raises(HTTPError):
                assert get_custom_type(super_user, type1_version_id).status == 404
