import allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import ResponseDto, CustomAttributeDictionaryFullView, \
    CustomAttributeDictionaryShortInfo
from products.Decision.framework.steps.decision_steps_custom_attr_dict import get_custom_attribute, \
    update_custom_attribute, custom_attributes_list
from products.Decision.tests.diagrams.test_add_diagrams import generate_diagram_name_description
from products.Decision.utilities.dict_constructors import dict_value_construct, dict_construct


@allure.epic("Справочники")
@allure.feature("Изменение справочника")
@pytest.mark.scenario("DEV-5628")
class TestCustomAttributesUpdate:

    @allure.story("Невозможно изменить справочник с dictName пустым или длиной <1 или >100")
    @allure.title("Создать справочник, изменить имя")
    @pytest.mark.parametrize('name_len,update_status', [(1, True),
                                                        (100, True)])
    def test_update_custom_attr_name(self, super_user, create_dict_gen,
                                     name_len, update_status):
        dict_name_up = generate_diagram_name_description(name_len, 1)["rand_name"]
        real_updated = False
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="15",
                                         dict_value_display_name="")
            custom_attr = dict_construct(
                dict_name="ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"],
                dict_value_type_id="1",
                values=[value])
            create_result: ResponseDto = create_dict_gen.create_dict(dict_body=custom_attr)
        with allure.step("Получение информации о справочнике"):
            attr_info: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
                **get_custom_attribute(super_user, dict_id=create_result.uuid).body)
        with allure.step("Обновление имени справочника"):
            value_up = dict_value_construct(dict_value="15",
                                            dict_value_display_name="",
                                            value_id=attr_info.values[0]["id"],
                                            op="update")
            custom_attr_up = dict_construct(
                dict_name=dict_name_up,
                dict_id=create_result.uuid,
                dict_value_type_id="1",
                values=[value_up],
                op="update")
            update_custom_attribute(super_user,
                                    dict_id=create_result.uuid,
                                    body=custom_attr_up)
        with allure.step("Получение информации о справочнике"):
            attr_info_up: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
                **get_custom_attribute(super_user, dict_id=create_result.uuid).body)
            if attr_info_up.dictName == dict_name_up:
                real_updated = True
        with allure.step("Проверка, что результат обновления имени соответствует ожидаемому"):
            assert real_updated == update_status

    @allure.story("Невозможно изменить справочник с dictName пустым или длиной <1 или >100")
    @allure.title("Создать справочник, изменить имя")
    @pytest.mark.parametrize('name_len,update_status', [(0, 400),
                                                        (101, 400)])
    def test_update_custom_attr_name(self, super_user, create_dict_gen,
                                     name_len, update_status):
        dict_name_up = generate_diagram_name_description(name_len, 1)["rand_name"]
        real_updated = False
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="15",
                                         dict_value_display_name="")
            custom_attr = dict_construct(
                dict_name="ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"],
                dict_value_type_id="1",
                values=[value])
            create_result: ResponseDto = create_dict_gen.create_dict(dict_body=custom_attr)
        with allure.step("Получение информации о справочнике"):
            attr_info: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
                **get_custom_attribute(super_user, dict_id=create_result.uuid).body)
        with allure.step("Обновление имени справочника"):
            value_up = dict_value_construct(dict_value="15",
                                            dict_value_display_name="",
                                            value_id=attr_info.values[0]["id"],
                                            op="update")
            custom_attr_up = dict_construct(
                dict_name=dict_name_up,
                dict_id=create_result.uuid,
                dict_value_type_id="1",
                values=[value_up],
                op="update")
        with allure.step("Проверка, что результат обновления имени соответствует ожидаемому"):
            with pytest.raises(HTTPError, match=str(update_status)):
                assert update_custom_attribute(super_user,
                                               dict_id=create_result.uuid,
                                               body=custom_attr_up).status == update_status

    @allure.story("При изменении имени справочника, в списке справочников id остаётся неизменным, а dictName меняется")
    @allure.title("Создать справочник, изменить, проверить, что id остался прежним")
    @pytest.mark.smoke
    def test_update_attr_id_old(self, super_user, create_dict_gen):
        dict_name_up = generate_diagram_name_description(8, 1)["rand_name"]
        id_same_as_old = False
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="15",
                                         dict_value_display_name="")
            custom_attr = dict_construct(
                dict_name="ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"],
                dict_value_type_id="1",
                values=[value])
            create_result: ResponseDto = create_dict_gen.create_dict(dict_body=custom_attr)
        with allure.step("Получение информации о справочнике"):
            attr_info: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
                **get_custom_attribute(super_user, dict_id=create_result.uuid).body)
        with allure.step("Обновление имени справочника"):
            value_up = dict_value_construct(dict_value="15",
                                            dict_value_display_name="",
                                            value_id=attr_info.values[0]["id"],
                                            op="update")
            custom_attr_up = dict_construct(
                dict_name=dict_name_up,
                dict_id=create_result.uuid,
                dict_value_type_id="1",
                values=[value_up],
                op="update")
            update_custom_attribute(super_user,
                                    dict_id=create_result.uuid,
                                    body=custom_attr_up)
        with allure.step("Получение информации о справочнике"):
            attr_info_up: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
                **get_custom_attribute(super_user, dict_id=create_result.uuid).body)
            if attr_info_up.id == attr_info.id:
                id_same_as_old = True
        with allure.step("Проверка, что после апдейта справочника id не сменился"):
            assert id_same_as_old

    @allure.story("Невозможно изменить справочник не указав id значений справочника")
    @allure.title("Попробовать обновить справочник без указания идентификатора значения")
    def test_update_attr_without_value_id(self, super_user, create_dict_gen):
        dict_name_up = generate_diagram_name_description(8, 1)["rand_name"]
        dict_name = "ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"]
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="15",
                                         dict_value_display_name="")
            custom_attr = dict_construct(
                dict_name=dict_name,
                dict_value_type_id="1",
                values=[value])
            create_result: ResponseDto = create_dict_gen.create_dict(dict_body=custom_attr)
        with allure.step("Получение информации о справочнике"):
            attr_info: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
                **get_custom_attribute(super_user, dict_id=create_result.uuid).body)
        with allure.step("Обновление имени справочника с передачей значения без id"):
            value_up = dict_value_construct(dict_value="15",
                                            dict_value_display_name="",
                                            value_id=None,
                                            op="update")
            custom_attr_up = dict_construct(
                dict_name=dict_name_up,
                dict_id=create_result.uuid,
                dict_value_type_id="1",
                values=[value_up],
                op="update")
        with allure.step("Получение информации о справочнике"):
            with pytest.raises(HTTPError, match="400"):
                assert update_custom_attribute(super_user,
                                               dict_id=create_result.uuid,
                                               body=custom_attr_up)

    @allure.story("Невозможно изменить справочник с dictValueTypeId пустым или отличным от строки с числом от 0 до 6 "
                  "включительно.")
    @allure.title("Проверить недопустимые значения значений при обновлении справочника")
    @pytest.mark.parametrize('value_type,update_status', [("", 400),
                                                          ("8", 400),
                                                          ("-1", 400),
                                                          ("hellow", 400)])
    def test_update_custom_attr_value_type(self, super_user, create_dict_gen,
                                           value_type, update_status):
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="15",
                                         dict_value_display_name="")
            custom_attr = dict_construct(
                dict_name="ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"],
                dict_value_type_id="1",
                values=[value])
            create_result: ResponseDto = create_dict_gen.create_dict(dict_body=custom_attr)
        with allure.step("Получение информации о справочнике"):
            attr_info: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
                **get_custom_attribute(super_user, dict_id=create_result.uuid).body)
        with allure.step("Обновление типа значения справочника"):
            value_up = dict_value_construct(dict_value="15",
                                            dict_value_display_name="",
                                            value_id=attr_info.values[0]["id"],
                                            op="update")
            custom_attr_up = dict_construct(
                dict_name="ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"],
                dict_id=create_result.uuid,
                dict_value_type_id=value_type,
                values=[value_up],
                op="update")
        with allure.step("Проверка, что результат обновления типа значения соответствует ожидаемому"):
            with pytest.raises(HTTPError, match=str(update_status)):
                assert update_custom_attribute(super_user,
                                               dict_id=create_result.uuid,
                                               body=custom_attr_up).status == update_status

    @allure.story("Невозможно сохранить справочник без value")
    @allure.title("Попытаться сменить значение справочника на пустое")
    def test_update_custom_attr_empty_value(self, super_user, create_dict_gen):
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="15",
                                         dict_value_display_name="")
            custom_attr = dict_construct(
                dict_name="ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"],
                dict_value_type_id="1",
                values=[value])
            create_result: ResponseDto = create_dict_gen.create_dict(dict_body=custom_attr)
        with allure.step("Обновление типа значения справочника"):
            custom_attr_up = dict_construct(
                dict_name="ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"],
                dict_id=create_result.uuid,
                dict_value_type_id="1",
                values=[],
                op="update")
        with allure.step("Проверка, что запрещено при изменении справочника не передавать значений"):
            with pytest.raises(HTTPError, match="400"):
                assert update_custom_attribute(super_user,
                                               dict_id=create_result.uuid,
                                               body=custom_attr_up)

    @allure.story("При наличии у хотя бы одного из value непустого значения в dictValueDisplayName"
                  " - он должен присутствовать у всех value(иначе - невозможно изменить)")
    @allure.title("Создать справочник с одним значением с заполненным отображаемым именем, а другим без")
    @allure.issue("DEV-7531")
    def test_update_custom_attr_not_all_values(self, super_user, create_dict_gen):
        dict_name = "ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"]
        update_denied = False
        with allure.step("Создание справочника valueDispayName не у всех значений"):
            value1 = dict_value_construct(dict_value="52",
                                          dict_value_display_name="Nizhniy_Novgorod")
            value2 = dict_value_construct(dict_value="77",
                                          dict_value_display_name="Kazan")
            custom_attr = dict_construct(dict_name=dict_name,
                                         dict_value_type_id="1",
                                         values=[value1, value2])
            create_result: ResponseDto = create_dict_gen.create_dict(dict_body=custom_attr)
        with allure.step("Получение информации о справочнике"):
            attr_info: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
                **get_custom_attribute(super_user, dict_id=create_result.uuid).body)
            value1_id = None
            value2_id = None
            for value in attr_info.values:
                if value["dictValue"] == 52:
                    value1_id = value["id"]
                if value["dictValue"] == 77:
                    value2_id = value["id"]
        with allure.step("Обновление типа значения справочника"):
            value_up1 = dict_value_construct(dict_value="52",
                                             dict_value_display_name="Nizhniy_Novgorod",
                                             value_id=value1_id,
                                             op="update")
            value_up2 = dict_value_construct(dict_value="77",
                                             dict_value_display_name="",
                                             value_id=value2_id,
                                             op="update")
            custom_attr_up = dict_construct(
                dict_name="ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"],
                dict_id=create_result.uuid,
                dict_value_type_id="1",
                values=[value_up1, value_up2],
                op="update")
            update_custom_attribute(super_user,
                                    dict_id=create_result.uuid,
                                    body=custom_attr_up)
        with allure.step("Получение информации о справочнике"):
            attr_info_up: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
                **get_custom_attribute(super_user, dict_id=create_result.uuid).body)
        with allure.step("Проверка, что созданный справочник не найден"):
            for value in attr_info_up.values:
                if value["id"] == value2_id and value["dictValueDisplayName"] == "Kazan":
                    update_denied = True
            assert update_denied

    @allure.story("Невозможно изменить справочник с именем, которое уже присутствует в списке справочников")
    @allure.title("Изменить справочнику имя на уже существующее в списке")
    @allure.issue("DEV-7535")
    def test_update_custom_attr_non_unique_name(self, super_user, create_dict_gen):
        dict_name_up = generate_diagram_name_description(8, 1)["rand_name"]
        with allure.step("Получение списка справочников и поиск существующего имени"):
            custom_attrs_list = []
            for custom_attribute in custom_attributes_list(super_user).body["content"]:
                custom_attrs_list.append(
                    CustomAttributeDictionaryShortInfo.construct(**custom_attribute))
            existing_name = custom_attrs_list[0].dictName
        real_updated = False
        with allure.step("Создание справочника"):
            value = dict_value_construct(dict_value="15",
                                         dict_value_display_name="")
            custom_attr = dict_construct(
                dict_name="ag_test_dict" + generate_diagram_name_description(8, 1)["rand_name"],
                dict_value_type_id="1",
                values=[value])
            create_result: ResponseDto = create_dict_gen.create_dict(dict_body=custom_attr)
        with allure.step("Получение информации о справочнике"):
            attr_info: CustomAttributeDictionaryFullView = CustomAttributeDictionaryFullView.construct(
                **get_custom_attribute(super_user, dict_id=create_result.uuid).body)
        with allure.step("Обновление имени справочника"):
            value_up = dict_value_construct(dict_value="15",
                                            dict_value_display_name="",
                                            value_id=attr_info.values[0]["id"],
                                            op="update")
            custom_attr_up = dict_construct(
                dict_name=existing_name,
                dict_id=create_result.uuid,
                dict_value_type_id="1",
                values=[value_up],
                op="update")
        with allure.step("Проверка, что имя не изменилось"):
            with pytest.raises(HTTPError, match="400"):
                assert update_custom_attribute(super_user,
                                               dict_id=create_result.uuid,
                                               body=custom_attr_up)
