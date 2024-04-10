import random
import string
import uuid

import glamor as allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import DiagramShortInfoView
from products.Decision.framework.model import (
    ResponseDto,
    DiagramViewDto,
    VersionType,
    DiagramShortInfoVersionsView, DiagramInOutParametersViewDto, )
from products.Decision.framework.steps.decision_steps_diagram import diagrams_list
from products.Decision.framework.steps.decision_steps_diagram import (
    get_diagram_by_version,
    get_diagram_versions,
)
from sdk.user.interface.api.request import ApiRequest


def generate_diagram_name_description(name_length, description_length, starts_with=''):
    letters = string.ascii_lowercase
    rand_string_diagram_name = starts_with + "".join(
        random.choice(letters) for i in range(name_length - len(starts_with))
    )
    description = "".join(random.choice(letters) for i in range(description_length))

    return {"rand_name": rand_string_diagram_name, "rand_description": description}


@allure.epic("Диаграммы")
@allure.feature("Добавление диаграммы")
class TestDiagramsAdd:
    @allure.story("Временную версию можно сохранить, как новую")
    @allure.title(
        "Создать диаграмму, сохранить как новую, проверить, что айди не совпадает с временной"
    )
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_create_diagram_as_new(
            self, super_user, create_temp_diagram, save_diagrams_gen
    ):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            version_id = diagram_template["versionId"]
        with allure.step("генерация информации о новой диаграмме"):
            new_diagram_name = (
                    "diagram_as_new"
                    + "_"
                    + generate_diagram_name_description(16, 1)["rand_name"]
            )
            diagram_description = "new diagram created in test"
        with allure.step("Сохранение временной диаграммы, как новой"):
            create_as_new_result = save_diagrams_gen.save_diagram_as_new(
                diagram_id, version_id, new_diagram_name, diagram_description
            ).body
            version_uuid = create_as_new_result["uuid"]
        with allure.step("Поиск диаграммы по айди версии"):
            get_diagram_by_version_response = get_diagram_by_version(
                super_user, version_uuid
            )
            diagram: DiagramViewDto = DiagramViewDto(
                **get_diagram_by_version_response.body
            )
        with allure.step(
                "Проверка, что новая диаграмма найдена и её айди и версия не совпадает с версией временной диаграммы"
        ):
            assert (
                    diagram.objectName == new_diagram_name
                    and diagram.versionId != version_id
                    and diagram.diagramId != diagram_id
            )

    @allure.story(
        "Имя диаграммы уникально. "
        "Невозможно повторно сохранить диаграмму с diagramName уже присутствующим в списке GET /diagrams"
    )
    @allure.title(
        "Проверить невозможность сохранения диаграммы как новой с существующим именем"
    )
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-5853")
    def test_save_diagram_as_new_with_existed_name(
            self, super_user, create_temp_diagram, save_diagrams_gen
    ):
        with allure.step("Получение списка существующих диаграмм"):
            response_diagram_list = diagrams_list(super_user)
            diagram_list = []
            for diagram in response_diagram_list.body["content"]:
                diagram_list.append(DiagramShortInfoView.construct(**diagram))
        with allure.step("Получение имени из списка существующих диаграмм"):
            diagram_name = ""
            for name in diagram_list:
                diagram_name = name.objectName
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            version_id = diagram_template["versionId"]
        with allure.step(
                "Генерация информации о новой диаграмме c указанием существующего имени"
        ):
            new_diagram_name = diagram_name
            diagram_description = "new diagram created in test"
        # with allure.step("Сохранение диаграммы, как новой"):
        #     response_save = save_diagrams_gen.save_diagram_as_new(
        #         diagram_id, version_id, new_diagram_name, diagram_description
        #     )
        # with allure.step("Проверка запрета на сохранение диаграммы с существующем именем"):
        #     assert response_save.status == 400
        with allure.step(
                "Попытка сохранения диаграммы как новой с существующим именем должна провалиться с ошибкой <400> "):
            with pytest.raises(HTTPError):
                assert save_diagrams_gen.save_diagram_as_new(
                    diagram_id, version_id, new_diagram_name, diagram_description
                ).status == 400

    @allure.story("После сохранения диаграмма отображается в общем списке диаграмм")
    @allure.title(
        "Создать диаграмму, сохранить, проверить что айди совпадает с временной"
    )
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-5853")
    @pytest.mark.smoke
    def test_create_diagram(self, super_user, create_temp_diagram, save_diagrams_gen):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Генерация информации о диаграмме"):
            new_diagram_name = (
                    "diagram" + "_" + generate_diagram_name_description(16, 1)["rand_name"]
            )
            diagram_description = "diagram created in test"
        with allure.step("Сохранение диаграммы"):
            create_result = save_diagrams_gen.save_diagram(
                diagram_id, temp_version_id, new_diagram_name, diagram_description
            ).body
            saved_version_id = create_result["uuid"]
        with allure.step("Поиск диаграммы по айди версии"):
            get_diagram_by_version_response = get_diagram_by_version(
                super_user, saved_version_id
            )
            diagram: DiagramViewDto = DiagramViewDto(
                **get_diagram_by_version_response.body
            )
        with allure.step(
                "Проверка, что версия не совпадает с версией временной диаграммы,а айди совпадает"
        ):
            assert (
                    diagram.objectName == new_diagram_name
                    and str(diagram.versionId) != temp_version_id
                    and str(diagram.diagramId) == diagram_id
            )

    @allure.story("Можно создать временную версию диаграммы")
    @allure.title("Создать временную версию диаграммы")
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-727")
    def test_create_template(self, super_user, create_temp_diagram):
        template_diagram = DiagramInOutParametersViewDto.construct(
            **create_temp_diagram
        )
        assert (
                template_diagram.objectName is not None
                and template_diagram.diagramId is not None
                and template_diagram.versionId is not None
        )

    @allure.story("Длина имени диаграммы больше допустимой в бд(100 символов)")
    @allure.title("Проверить ограничение имени диаграммы по длине")
    @pytest.mark.scenario("DEV-5853")
    @pytest.mark.parametrize(
        "name,status",
        [
            (generate_diagram_name_description(99, 1)["rand_name"], 201),
            (generate_diagram_name_description(100, 1)["rand_name"], 201),
        ],
    )
    @pytest.mark.sdi
    def test_diagram_name(self, super_user, create_temp_diagram, name, status):
        template_diagram = create_temp_diagram
        diagram_id = template_diagram["diagramId"]
        temp_version_id = template_diagram["versionId"]
        description = generate_diagram_name_description(1, 8)["rand_description"]
        with allure.step("Сохранение диаграммы с именем заданной длины возврщает ожидаемый статус"):
            response_save = super_user.with_api.send(
                ApiRequest(
                    method="POST",
                    path="/diagrams/createAsNew",
                    query={},
                    body={
                        "diagramId": f"{uuid.UUID(diagram_id)}",
                        "versionId": f"{temp_version_id}",
                        "errorResponseFlag": "false",
                        "objectName": f"{name}",
                        "diagramDescription": f"{description}",
                    },
                    headers={"Content-Type": "application/json"},
                )
            )
        with allure.step("Проверка, статуса"):
            assert response_save.status == status

    @allure.story("Длина имени диаграммы больше допустимой в бд(100 символов)")
    @allure.title("Проверить ограничение имени диаграммы по длине")
    @pytest.mark.scenario("DEV-5853")
    @pytest.mark.parametrize(
        "name,status",
        [
            (generate_diagram_name_description(101, 1)["rand_name"], 400),
        ],
    )
    @pytest.mark.sdi
    def test_diagram_name_neg(self, super_user, create_temp_diagram, name, status):
        template_diagram = create_temp_diagram
        diagram_id = template_diagram["diagramId"]
        temp_version_id = template_diagram["versionId"]
        description = generate_diagram_name_description(1, 8)["rand_description"]
        with allure.step("Сохранение диаграммы с именем заданной длины возврщает ожидаемый статус"):
            with pytest.raises(HTTPError):
                assert super_user.with_api.send(
                    ApiRequest(
                        method="POST",
                        path="/diagrams/createAsNew",
                        query={},
                        body={
                            "diagramId": f"{uuid.UUID(diagram_id)}",
                            "versionId": f"{temp_version_id}",
                            "errorResponseFlag": "false",
                            "objectName": f"{name}",
                            "diagramDescription": f"{description}",
                        },
                        headers={"Content-Type": "application/json"},
                    )
                ).status == status

    @allure.story("Длина описания диаграммы больше допустимой в бд(2000 символов)")
    @allure.title("Проверить ограничение описания диаграммы по длине")
    @pytest.mark.scenario("DEV-5853")
    @pytest.mark.parametrize(
        "description,status",
        [
            (generate_diagram_name_description(1, 1999)["rand_description"], 201),
            (generate_diagram_name_description(1, 2000)["rand_description"], 201),
        ],
    )
    @pytest.mark.sdi
    def test_diagram_description(
            self, super_user, create_temp_diagram, description, status
    ):
        template_diagram = create_temp_diagram
        diagram_id = template_diagram["diagramId"]
        temp_version_id = template_diagram["versionId"]
        name = generate_diagram_name_description(8, 1)["rand_name"]
        with allure.step("Сохранение диаграммы с описанием заданной длины происходит с ожидаемым кодом"):
            assert super_user.with_api.send(
                ApiRequest(
                    method="POST",
                    path="/diagrams/createAsNew",
                    query={},
                    body={
                        "diagramId": f"{uuid.UUID(diagram_id)}",
                        "versionId": f"{temp_version_id}",
                        "errorResponseFlag": "false",
                        "objectName": f"{name}",
                        "diagramDescription": f"{description}",
                    },
                    headers={"Content-Type": "application/json"},
                )
            ).status == status

    @allure.story("Длина описания диаграммы больше допустимой в бд(2000 символов)")
    @allure.title("Проверить ограничение описания диаграммы по длине")
    @pytest.mark.scenario("DEV-5853")
    @pytest.mark.parametrize(
        "description,status",
        [
            (generate_diagram_name_description(1, 2001)["rand_description"], 400),
        ],
    )
    @pytest.mark.sdi
    def test_diagram_description_neg(
            self, super_user, create_temp_diagram, description, status
    ):
        template_diagram = create_temp_diagram
        diagram_id = template_diagram["diagramId"]
        temp_version_id = template_diagram["versionId"]
        name = generate_diagram_name_description(8, 1)["rand_name"]
        with allure.step("Сохранение диаграммы с описанием заданной длины происходит с ожидаемым кодом"):
            with pytest.raises(HTTPError):
                assert super_user.with_api.send(
                    ApiRequest(
                        method="POST",
                        path="/diagrams/createAsNew",
                        query={},
                        body={
                            "diagramId": f"{uuid.UUID(diagram_id)}",
                            "versionId": f"{temp_version_id}",
                            "errorResponseFlag": "false",
                            "objectName": f"{name}",
                            "diagramDescription": f"{description}",
                        },
                        headers={"Content-Type": "application/json"},
                    )
                ).status == status

    @allure.story(
        "Невозможно сохранить диаграмму, как новую, с именем, которое уже есть в списке диаграмм"
    )
    @allure.issue("DEV-5017")
    @allure.title("Нельзя сохранить 2 диаграммы с одинаковым именем")
    @pytest.mark.scenario("DEV-5853")
    @pytest.mark.sdi
    def test_unique_diagram_name(
            self, super_user, create_two_temp_diagram, save_diagrams_gen
    ):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_two_temp_diagram["first_template"]
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Генерация информации о диаграмме"):
            new_diagram_name = (
                    "diagram" + "_" + generate_diagram_name_description(16, 1)["rand_name"]
            )
            diagram_description = "diagram created in test"
        with allure.step("Сохранение диаграммы"):
            save_diagrams_gen.save_diagram(
                diagram_id, temp_version_id, new_diagram_name, diagram_description
            )
        with allure.step("Создание второй template диаграммы"):
            diagram_template2 = create_two_temp_diagram["second_template"]
            diagram_id2 = diagram_template2["diagramId"]
            temp_version_id2 = diagram_template2["versionId"]
        with allure.step("Сохранение второй диаграммы с тем же именем запрещено с кодом 400"):
            with pytest.raises(HTTPError):
                assert save_diagrams_gen.save_diagram(
                    diagram_id2, temp_version_id2, new_diagram_name, diagram_description
                ).status == 400

    @allure.story("Возможно создать пользовательскую версию диаграммы")
    @allure.title(
        "Создать диаграмму, сохранить, создать пользовательскую версию, проверить, что найдена"
    )
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_create_diagram_user_version(
            self, super_user, create_temp_diagram, save_diagrams_gen
    ):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Генерация информации о диаграмме"):
            new_diagram_name = (
                    "diagram" + "_" + generate_diagram_name_description(16, 1)["rand_name"]
            )
            diagram_description = "diagram created in test"
        with allure.step("Сохранение диаграммы"):
            create_result = save_diagrams_gen.save_diagram(
                diagram_id, temp_version_id, new_diagram_name, diagram_description
            ).body
            saved_version_id = create_result["uuid"]
        with allure.step("Создание пользовательской версии диаграммы"):
            uv_create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram_user_vers(
                    diagram_id=diagram_id,
                    saved_version_id=saved_version_id,
                    version_name="diagram_user_version",
                    global_flag=False,
                ).body
            )
            user_version_id = uv_create_result.uuid
        with allure.step("Поиск пользовательской версии диаграммы"):
            get_diagram_by_version_response = get_diagram_by_version(
                super_user, str(user_version_id)
            )
            diagram: DiagramViewDto = DiagramViewDto.construct(
                **get_diagram_by_version_response.body
            )
        with allure.step("Проверка, что версия найдена и её тип user local"):
            assert diagram.versionType == VersionType.USER_LOCAL

    @allure.story("Возможно сохранить пользовательскую версию диаграммы")
    @allure.title(
        "Создать диаграмму, сохранить, создать пользовательскую версию, проверить, что появилась в списке "
        "версий"
    )
    @pytest.mark.sdi
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.smoke
    def test_user_version_appear_in_vers(
            self, super_user, create_temp_diagram, save_diagrams_gen
    ):
        version_found_in_vers_list = False
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Генерация информации о диаграмме"):
            new_diagram_name = (
                    "diagram" + "_" + generate_diagram_name_description(16, 1)["rand_name"]
            )
            diagram_description = "diagram created in test"
        with allure.step("Сохранение диаграммы"):
            create_result = save_diagrams_gen.save_diagram(
                diagram_id, temp_version_id, new_diagram_name, diagram_description
            ).body
            saved_version_id = create_result["uuid"]
        with allure.step("Создание пользовательской версии диаграммы"):
            uv_create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram_user_vers(
                    diagram_id=diagram_id,
                    saved_version_id=saved_version_id,
                    version_name="diagram_user_version",
                    global_flag=False,
                ).body
            )
            user_version_id = uv_create_result.uuid
        with allure.step("Загрузка списка диаграмм"):
            version_list = []
            for vers in get_diagram_versions(super_user, diagram_id).body:
                version_list.append(DiagramShortInfoVersionsView.construct(**vers))
            for vers in version_list:
                if (
                        vers.versionId == user_version_id
                        and vers.versionType == VersionType.USER_LOCAL
                ):
                    version_found_in_vers_list = True
            assert version_found_in_vers_list

    @allure.story(
        "Из существующей latest версии диаграммы возможно создать Template версию"
    )
    @allure.title("Проверить, что созданная из latest версии версия является временной")
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_create_from_latest_diagram(
            self,
            super_user,
            create_temp_diagram,
            save_diagrams_gen,
            create_temp_diagram_gen,
    ):
        with allure.step("Генерация информации о диаграмме"):
            diagram_name = (
                    "diagram_" + generate_diagram_name_description(16, 1)["rand_name"]
            )
            diagram_desc = "test"
        with allure.step("Создание template диаграммы"):
            diagram_temp = create_temp_diagram
            diagram_id = diagram_temp["diagramId"]
            temp_version_id = diagram_temp["versionId"]
        with allure.step("Сохранение диаграммы"):
            create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram(
                    diagram_id, temp_version_id, diagram_name, diagram_desc
                ).body
            )
            version_id = create_result.uuid
        with allure.step("создание teplate версии из latest версии диаграмм"):
            template_from_latest: DiagramViewDto = (
                create_temp_diagram_gen.create_temp_from_latest(version_id)
            )
        with allure.step("Проверка, что create_from_latest является TEMP-версией"):
            assert template_from_latest.versionType == "TEMP"

    @allure.story("Временную версию можно сохранить")
    @allure.title(
        "Проверить, что версия, созданная из latest версии, появляется в списке версий"
    )
    @pytest.mark.scenario("DEV-727")
    def test_create_from_latest_diagram_vers_list(
            self,
            super_user,
            create_temp_diagram,
            save_diagrams_gen,
            create_temp_diagram_gen,
    ):
        temp_version_is_in_versions = False
        with allure.step("Генерация информации о диаграмме"):
            diagram_name = (
                    "diagram_" + generate_diagram_name_description(16, 1)["rand_name"]
            )
            diagram_desc = "test"
        with allure.step("Создание template диаграммы"):
            diagram_temp = create_temp_diagram
            diagram_id = diagram_temp["diagramId"]
            temp_version_id = diagram_temp["versionId"]
        with allure.step("Сохранение диаграммы"):
            create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram(
                    diagram_id, temp_version_id, diagram_name, diagram_desc
                ).body
            )
            version_id = create_result.uuid
        with allure.step("создание teplate версии из latest версии диаграмм"):
            template_from_latest: DiagramViewDto = (
                create_temp_diagram_gen.create_temp_from_latest(version_id)
            )
        with allure.step(
                "Проверка, что версия находится в списке и её тип -- временный"
        ):
            versions = []
            for vers in get_diagram_versions(super_user, diagram_id).body:
                versions.append(DiagramShortInfoVersionsView.construct(**vers))
            for vers in versions:
                if (
                        vers.versionId == template_from_latest.versionId
                        and vers.versionType == "TEMP"
                ):
                    temp_version_is_in_versions = True
            assert temp_version_is_in_versions

    @allure.story("Возможно создать user global версию диаграммы")
    @allure.title(
        "Создать диаграмму, сохранить, создать глобальную версию, проверить, что найдена"
    )
    @pytest.mark.scenario("DEV-727")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_create_diagram_global_version(
            self, super_user, create_temp_diagram, save_diagrams_gen
    ):
        with allure.step("Создание template диаграммы"):
            diagram_template = create_temp_diagram
            diagram_id = diagram_template["diagramId"]
            temp_version_id = diagram_template["versionId"]
        with allure.step("Генерация информации о диаграмме"):
            new_diagram_name = (
                    "diagram" + "_" + generate_diagram_name_description(16, 1)["rand_name"]
            )
            diagram_description = "diagram created in test"
        with allure.step("Сохранение диаграммы"):
            create_result = save_diagrams_gen.save_diagram(
                diagram_id, temp_version_id, new_diagram_name, diagram_description
            ).body
            saved_version_id = create_result["uuid"]
        with allure.step("Создание глобальной версии диаграммы"):
            gv_create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram_user_vers(
                    diagram_id=diagram_id,
                    saved_version_id=saved_version_id,
                    version_name="diagram_user_version",
                    global_flag=True,
                ).body
            )
            global_version_id = gv_create_result.uuid
        with allure.step("Поиск глобальной версии диаграммы"):
            get_diagram_by_version_response = get_diagram_by_version(
                super_user, str(global_version_id)
            )
            diagram: DiagramViewDto = DiagramViewDto.construct(
                **get_diagram_by_version_response.body
            )
        with allure.step("Проверка, что версия найдена и её тип user Global"):
            assert diagram.versionType == VersionType.USER_GLOBAL

    # @pytest.mark.source(SourceSettings(sourceType="kafka",
    #                                    kafkaSettings=KafkaSettings(topic="qa.topik",
    #                                                                schema={"id": "int", "some_name": "string"})))
    # @pytest.mark.target(TargetSettings(sourceType="kafka",
    #                                    isSameAsSource=True,
    #                                    kafkaSettings=KafkaSettings(topic="qa.topik3")))
    # @pytest.mark.nodes(["трансформация фильтр", "трансформация маппинг"])
    # @pytest.mark.save_diagram(True)
    # def test_bal_diag(self, diagram_constructor_balalaika):
    #     a = diagram_constructor_balalaika["data_source_info"]



