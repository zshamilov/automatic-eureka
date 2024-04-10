import allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import DiagramInOutParametersViewDto, ResponseDto, DiagramViewDto
from products.Decision.framework.steps.decision_steps_diagram import create_template_from_latest, delete_diagram
from products.Decision.framework.steps.decision_steps_locking import locking_list, delete_locking


@allure.epic("Блокировки")
@allure.feature("Блокировки")
@pytest.mark.scenario("DEV-530")
class TestAdministrationLockings:

    @allure.story("Создать блокировку выполнив createTemplateFromLatest сохранённой диаграммы")
    @allure.title("Блокировка создаётся при первом открытии сохранённой диаграммы")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_create_locking(self, super_user, create_temp_diagram_gen, save_diagrams_gen):
        with allure.step("Создание диаграммы"):
            diagram_name = "diagram_for_lock_" + generate_string()
            template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
            diagram_id = template.diagramId
            temp_vers_id = template.versionId
        with allure.step("Сохранение диаграммы"):
            create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram(
                    diagram_id, temp_vers_id, diagram_name
                ).body
            )
            version_id = create_result.uuid
        with allure.step("Создание блокировки, путём открытия сохранённой диаграммы"):
            create_template_from_latest(super_user, version_id)
        with allure.step("Получение списка блокировок"):
            lockings = locking_list(super_user, diagram_name=diagram_name)
        assert any(locking.objectName == diagram_name for locking in lockings)

    @allure.story("Удалить блокировку, посмотреть, что пропала из списка блокировок")
    @allure.title("Удалённая блокировка не отображается в списке блокировок")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_delete_locking(self, super_user, create_temp_diagram_gen, save_diagrams_gen):
        with allure.step("Создание диаграммы"):
            diagram_name = "diagram_for_lock_" + generate_string()
            template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
            diagram_id = template.diagramId
            temp_vers_id = template.versionId
        with allure.step("Сохранение диаграммы"):
            create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram(
                    diagram_id, temp_vers_id, diagram_name
                ).body
            )
            version_id = create_result.uuid
        with allure.step("Создание блокировки, путём открытия сохранённой диаграммы"):
            create_template_from_latest(super_user, version_id)
        with allure.step("Получение списка блокировок"):
            lockings = locking_list(super_user, diagram_name=diagram_name)
            locking_id = None
            for locking in lockings:
                if locking.objectName == diagram_name:
                    locking_id = str(locking.objectId)
                    break
        with allure.step("Удаление блокировки"):
            delete_locking(super_user, locking_id)
        with allure.step("Получение обновлённого списка блокировок"):
            lockings_up = locking_list(super_user, diagram_name=diagram_name)
        assert not any(locking.objectName == diagram_name for locking in lockings_up)

    @allure.story("Удалить заблокированную диаграмму, увидеть, что блокировка удалена")
    @allure.title("Блокировка удаляется при удалении заблокированной диаграммы")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_delete_diagram_delete_locking(self, super_user, create_temp_diagram_gen, save_diagrams_gen):
        with allure.step("Создание диаграммы"):
            diagram_name = "diagram_for_lock_" + generate_string()
            template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
            diagram_id = template.diagramId
            temp_vers_id = template.versionId
        with allure.step("Сохранение диаграммы"):
            create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram(
                    diagram_id, temp_vers_id, diagram_name
                ).body
            )
            version_id = create_result.uuid
        with allure.step("Создание блокировки, путём открытия сохранённой диаграммы"):
            create_template_from_latest(super_user, version_id)
        with allure.step("Удаление диаграммы"):
            delete_diagram(super_user, version_id)
        with allure.step("Получение обновлённого списка блокировок"):
            lockings_up = locking_list(super_user, diagram_name=diagram_name)
        assert not any(locking.objectName == diagram_name for locking in lockings_up)

    @allure.story("Заблокировать диаграмму одним пользователем7*. попытаться открыть другим - увидеть, что запрещено")
    @allure.title("Другие юзеры не могут открыть заблокированную диаграмму")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_locking_locks_for_other_user(self, super_user, user_gen, create_temp_diagram_gen, save_diagrams_gen):
        other_user = user_gen.create_user()
        with allure.step("Подготовка параметров окружения"):
            diagram_name = "diagram_for_lock_" + generate_string()
            template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
            diagram_id = template.diagramId
            temp_vers_id = template.versionId
        with allure.step("Сохранение диаграммы"):
            create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram(
                    diagram_id, temp_vers_id, diagram_name
                ).body
            )
            version_id = create_result.uuid
        with allure.step("Юзер, создавший диаграмму, блокирует её посредством открытия"):
            create_template_from_latest(super_user, version_id)
        with allure.step("Второй юзеру запрещено открывать заблокированную диаграмму"):
            with pytest.raises(HTTPError, match="409"):
                assert create_template_from_latest(other_user, version_id)

    @allure.story("Создать блокировку юзером, удалить блокировку, другим юзером открыть - увидеть. что открывается")
    @allure.title("После снятия блокировки другие юзеры могут открывать диаграмму")
    @pytest.mark.sdi
    @pytest.mark.smoke
    def test_unlocks_for_users_after_locking_delete(self, super_user, user_gen, create_temp_diagram_gen,
                                                    save_diagrams_gen):
        with allure.step("Создание второго юзера"):
            other_user = user_gen.create_user()
        with allure.step("Создание диаграммы"):
            diagram_name = "diagram_for_lock_" + generate_string()
            template: DiagramInOutParametersViewDto = create_temp_diagram_gen.create_template()
            diagram_id = template.diagramId
            temp_vers_id = template.versionId
        with allure.step("Сохранение диаграммы"):
            create_result: ResponseDto = ResponseDto.construct(
                **save_diagrams_gen.save_diagram(
                    diagram_id, temp_vers_id, diagram_name
                ).body
            )
            version_id = create_result.uuid
        with allure.step("Создание блокировки, путём открытия сохранённой диаграммы"):
            create_template_from_latest(super_user, version_id)
        with allure.step("Получение списка блокировок"):
            lockings = locking_list(super_user, diagram_name=diagram_name)
            locking_id = None
            for locking in lockings:
                if locking.objectName == diagram_name:
                    locking_id = str(locking.objectId)
                    break
        with allure.step("Удаление блокировки"):
            delete_locking(super_user, locking_id)
        with allure.step("Другой юзер может открыть разблокированную диаграмму"):
            assert create_template_from_latest(other_user, version_id).status == 201
