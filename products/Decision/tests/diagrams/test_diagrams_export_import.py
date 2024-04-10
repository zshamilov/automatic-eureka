import os

import glamor as allure
import pytest
from requests import HTTPError

from products.Decision.framework.model import (
    DiagramCreateNewVersion,
    ConfirmExportDto,
    ExportResponseDto,
    Status1,
    ConfirmImportResponseDto,
    ComplexTypeGetFullView,
    ScriptFullView, OfferFullViewDto, DataProviderGetFullView,
    ExternalServiceFullViewDto,
)
from products.Decision.framework.steps.decision_steps_complex_type import (
    get_custom_type, delete_custom_type,
)
from products.Decision.framework.steps.decision_steps_data_provider_api import get_data_provider, delete_data_provider
from products.Decision.framework.steps.decision_steps_deploy import deploy_delete, deploy_list_by_name
from products.Decision.framework.steps.decision_steps_diagram import delete_diagram, diagram_list_by_name
from products.Decision.framework.steps.decision_steps_external_service_api import find_service_by_id, delete_service
from products.Decision.framework.steps.decision_steps_migration import (
    generate_export_objects,
    set_export,
    upload_import_file,
)
from products.Decision.framework.steps.decision_steps_offer_api import get_offer_info, delete_offer
from products.Decision.framework.steps.decision_steps_script_api import (
    get_python_script_by_id, get_groovy_script_by_id, delete_script_by_id,
)
from products.Decision.runtime_tests.runtime_fixtures.tarantool_insert_fixtures import *
from products.Decision.utilities.custom_models import VariableParams
from products.Decision.utilities.export_import_constructors import *
from products.Decision.runtime_tests.runtime_fixtures.tarantool_insert_fixtures import tarantool_insert_update_saved
from products.Decision.runtime_tests.runtime_fixtures.custom_code_fixtures import diagram_custom_code_python_2


@allure.epic("Диаграммы")
@allure.feature("Экспорт импорт диаграммы")
@pytest.mark.scenario("DEV-15465")
class TestDiagramsExportImport:
    @allure.story(
        "Пользователю отдается поток для скачивания файла, имя которого указано в пути запроса"
    )
    @allure.title(
        "Экспортировать диаграмму без зависимостей, проверить, что файл появился"
    )
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_diagram_export_without_dependencies(
            self,
            super_user,
            diagram_constructor,
            export_import_file,
    ):
        with allure.step("Создание и сохранение диаграммы для экспорта"):
            diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        with allure.step("Анализ экспортируемых объектов"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[str(diagram_data.diagramId)],
            )
            gen_response: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
            gen_diagram = gen_response.diagrams[0]
        with allure.step("Генерация экспорт файла на сервере"):
            export_diagram = export_object_construct(
                object_type=gen_diagram["objectType"],
                object_name=gen_diagram["objectName"],
                object_id=gen_diagram["objectId"],
                object_version_id=gen_diagram["objectVersionId"],
                object_version_type=gen_diagram["objectVersionType"],
                root_objects=gen_diagram["rootObjects"],
            )
            export_body = export_construct(diagrams=[export_diagram])
            export_resp: ExportResponseDto = ExportResponseDto.construct(
                **set_export(super_user, body=export_body).body
            )
            file_name = export_resp.fileName
        with allure.step("Загрузка файла с экспортированной диаграммой"):
            file_path = export_import_file.download_export_file(file_name=file_name)
        with allure.step("Проверка, что файл загружен"):
            assert os.path.isfile(file_path)

    @allure.story(
        "Объекты export_object из списка с флагом isSelected= false не экспортируются,"
        " для них фиксируется status = 'Экспорт отклонен пользователем'"
    )
    @allure.title("Сгенерировать файлы в кластере с разными статусами")
    @pytest.mark.save_diagram(True)
    @pytest.mark.parametrize(
        "selected, status", [(True, Status1.SUCCESS), (False, Status1.CANCELED)]
    )
    @pytest.mark.smoke
    def test_diagram_temp_export_canceled_success(
            self,
            super_user,
            diagram_constructor,
            selected,
            status,
    ):
        with allure.step("Создание и сохранение диаграммы для экспорта"):
            diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        with allure.step("Анализ экспортируемых объектов"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[str(diagram_data.diagramId)],
            )
            gen_response: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
            gen_diagram = gen_response.diagrams[0]
        with allure.step("Генерация экспорт файла на сервере с флагом isSelected"):
            export_diagram = export_object_construct(
                object_type=gen_diagram["objectType"],
                object_name=gen_diagram["objectName"],
                object_id=gen_diagram["objectId"],
                object_version_id=gen_diagram["objectVersionId"],
                object_version_type=gen_diagram["objectVersionType"],
                root_objects=gen_diagram["rootObjects"],
                is_selected=selected,
            )
            export_body = export_construct(diagrams=[export_diagram])
            export_resp: ExportResponseDto = ExportResponseDto.construct(
                **set_export(super_user, body=export_body).body
            )
        with allure.step("Проверка статуса экспортируемых объектов"):
            assert export_resp.exportStatus["diagrams"][0]["status"] == status

    @allure.story("Если указанный файл отсутствует, то выдается сообщение об ошибке")
    @allure.title("Загружать существующий/несуществующий файлы")
    @pytest.mark.save_diagram(True)
    @pytest.mark.parametrize(
        "file, path, status", [("existing", True, 200)]
    )
    @pytest.mark.smoke
    def test_diagram_file_export_correct(
            self,
            super_user,
            diagram_constructor,
            export_import_file,
            file,
            path,
            status,
    ):
        with allure.step("Создание и сохранение диаграммы для экспорта"):
            diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        with allure.step("Анализ экспортируемых объектов"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[str(diagram_data.diagramId)],
            )
            gen_response: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
            gen_diagram = gen_response.diagrams[0]
        with allure.step("Генерация экспорт файла на сервере"):
            export_diagram = export_object_construct(
                object_type=gen_diagram["objectType"],
                object_name=gen_diagram["objectName"],
                object_id=gen_diagram["objectId"],
                object_version_id=gen_diagram["objectVersionId"],
                object_version_type=gen_diagram["objectVersionType"],
                root_objects=gen_diagram["rootObjects"],
            )
            export_body = export_construct(diagrams=[export_diagram])
            export_resp: ExportResponseDto = ExportResponseDto.construct(
                **set_export(super_user, body=export_body).body
            )
            if file == "existing":
                file_name = export_resp.fileName
            else:
                file_name = "he-he_i_am_not_a_file.json"
            with allure.step("Загрузка файла под выбранным именем файла"):
                response = export_import_file.try_download_export_file(
                    file_name, path=path
                )
            assert response.status == status

    @allure.story("Если указанный файл отсутствует, то выдается сообщение об ошибке")
    @allure.title("Загружать существующий/несуществующий файлы")
    @pytest.mark.save_diagram(True)
    @pytest.mark.parametrize(
        "file, path, status", [("not existing", False, 404)]
    )
    @pytest.mark.smoke
    def test_diagram_file_export_correct_wrong(
            self,
            super_user,
            diagram_constructor,
            export_import_file,
            file,
            path,
            status,
    ):
        with allure.step("Создание и сохранение диаграммы для экспорта"):
            diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        with allure.step("Анализ экспортируемых объектов"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[str(diagram_data.diagramId)],
            )
            gen_response: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
            gen_diagram = gen_response.diagrams[0]
        with allure.step("Генерация экспорт файла на сервере"):
            export_diagram = export_object_construct(
                object_type=gen_diagram["objectType"],
                object_name=gen_diagram["objectName"],
                object_id=gen_diagram["objectId"],
                object_version_id=gen_diagram["objectVersionId"],
                object_version_type=gen_diagram["objectVersionType"],
                root_objects=gen_diagram["rootObjects"],
            )
            export_body = export_construct(diagrams=[export_diagram])
            export_resp: ExportResponseDto = ExportResponseDto.construct(
                **set_export(super_user, body=export_body).body
            )
            if file == "existing":
                file_name = export_resp.fileName
            else:
                file_name = "he-he_i_am_not_a_file.json"
            with allure.step("Загрузка файла под несуществующим именем файла"):
                with pytest.raises(HTTPError):
                    assert export_import_file.try_download_export_file(
                        file_name, path=path
                    ).status == status

    @allure.story(
        "Если isIncludeDependencies= true, то для версий объектов из п.1 производится поиск вложенных "
        "версий комплексных типов complex_type_version_id в таблице diagram_variable (поиск по version_id) "
        "(internal_flag = true"
    )
    @allure.title(
        "Проверить, что в диаграмме с вложенным комплекс типом, тип попадает в экспорт с диаграммой"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_cmplx",
                                               varType="in", isComplex=True, isArray=False),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_diagram_export_with_dependencies_ctype(
            self, super_user, diagram_constructor
    ):
        with allure.step(
                "Создание и сохранение диаграммы с вложенным комплекс типом для экспорта"
        ):
            diagram_data: DiagramCreateNewVersion = diagram_constructor["saved_data"]
        with allure.step("Анализ экспортируемых объектов"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[str(diagram_data.diagramId)],
            )
            gen_response: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
        with allure.step(
                "Проверка, что вложенные комплекс типы обнаружены и подготовлены для экспорта"
        ):
            assert (
                    len(gen_response.diagrams) == 1 and len(gen_response.complexTypes) == 1
            )

    @allure.story("Экспорт импорт вложенным скриптом")
    @allure.title(
        "Проверить, что в диаграмме с вложенным скриптом, скрипт попадает в экспорт с диаграммой"
    )
    @allure.issue("DEV-6550")
    @pytest.mark.smoke
    def test_diagram_export_with_dependencies_script(
            self, super_user, diagram_custom_code_submit
    ):
        with allure.step(
                "Создание и сохранение диаграммы с вложенным комплекс типом для экспорта"
        ):
            diagram_data: DiagramCreateNewVersion = diagram_custom_code_submit["diagram_data"]
        with allure.step("Анализ экспортируемых объектов"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[str(diagram_data.diagramId)],
            )
            gen_response: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
        with allure.step(
                "Проверка, что вложенные скрипты обнаружены и подготовлены для экспорта"
        ):
            assert len(gen_response.diagrams) == 1 and len(gen_response.scripts) == 1

    @allure.story(
        "Производится парсинг сохраненного ранее во временной директории контейнера файла fileName"
    )
    @allure.title(
        "Импортировать файл с диаграммой без вложений, проверить. что появился на контуре"
    )
    @pytest.mark.smoke
    @pytest.mark.save_diagram(True)
    def test_diagram_import_without_dependencies(self, super_user, diagram_constructor,
                                                 export_import_file):
        with allure.step("Получение необходимых идентификаторов, экспорт диаграммы"):
            diagram_before_import = diagram_constructor["saved_data"]
            diagram_id = diagram_constructor["diagram_id"]
            latest_version_id = diagram_constructor["saved_data"].versionId
            diagram_nodes_before_import = diagram_before_import.nodes.keys()
            diagram_name_before_import = diagram_constructor["saved_data"].objectName
            file_path = export_import_file.export_objects_file_with_all_dependencies([diagram_id])
        with allure.step("Удаление диаграммы перед импортом"):
            delete_diagram(super_user, str(latest_version_id))
        with allure.step("Импорт всех объектов из файла"):
            import_res = import_objects_from_file(super_user, file_path)
        with allure.step("Получение информации об объекте по идентификаторам полученным до удаления"):
            diagram_after_import: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
                super_user, latest_version_id
            ).body)
            diagram_name_after_import = diagram_after_import.objectName
            diagram_nodes_after_import = diagram_after_import.nodes.keys()
        with allure.step("Проверка, что диаграмма найдена под импортируемым именем и все узлы в ней сохранились"):
            assert diagram_after_import.objectName == diagram_name_before_import
            assert diagram_nodes_after_import == diagram_nodes_before_import

    @allure.story(
        "Если для импорта выбрать сломанный json файл, то произойдёт ошибка импорта"
    )
    @allure.title("Импортировать сломанный json файл, получить ошибку")
    def test_diagram_import_bad_json(self, super_user):
        file_name = "import_bad.json"
        with allure.step("Проверка, что сервер не даёт клиенту загрузить битый файл"):
            with pytest.raises(HTTPError, match="400"):
                assert upload_import_file(
                    super_user, file=f"products/Decision/resources/{file_name}"
                )

    @allure.story(
        "Если для импорта выбрать корректный json файл с некорректными для контура данными, "
        "то в objectsInfo не будет никаких данных для импорта"
    )
    @allure.title(
        "Импортировать файл с некорректными данными, проверить, что анализ ничего не распознал"
    )
    def test_diagram_import_wrong_data(self, super_user):
        file_name = "import_unexisting.json"
        with allure.step(
                "Анализ импортируемых объектов при загрузке корректного файла с невалидными данными"
        ):
            import_analysis: ConfirmImportResponseDto = (
                ConfirmImportResponseDto.construct(
                    **upload_import_file(
                        super_user, file=f"products/Decision/resources/{file_name}"
                    ).body
                )
            )
        with allure.step(
                "Проверка, что набор импортируемых объектов пуст, так как данные файла невалидны"
        ):
            assert not import_analysis.objectsInfo

    @allure.story(
        "Для объектов из списка import_objects с флагом isSelected= false импорт не производится ("
        "import_status = 'CANCELED')"
    )
    @allure.title(
        "Импортировать с флагом isSelected=false, проверить, что не появился на контуре"
    )
    @pytest.mark.save_diagram(True)
    def test_diagram_import_not_selected(self, super_user, diagram_constructor,
                                         export_import_file, import_file):
        with allure.step("Получение необходимых идентификаторов, экспорт диаграммы и удаление перед импортом"):
            diagram_id = diagram_constructor["diagram_id"]
            latest_version_id = diagram_constructor["saved_data"].versionId
            file_path = export_import_file.export_objects_file_with_all_dependencies([diagram_id])
            delete_diagram(super_user, str(latest_version_id))
        with allure.step("Анализ импортируемых объектов"):
            import_analysis: ConfirmImportResponseDto = (
                ConfirmImportResponseDto.construct(
                    **upload_import_file(
                        super_user, file=file_path
                    ).body
                )
            )
            import_file_name = import_analysis.fileName
            diagram_name = import_analysis.objectsInfo["diagrams"][0]["objectName"]
            diagram_version = import_analysis.objectsInfo["diagrams"][0][
                "objectVersionId"
            ]
            diagram_id = import_analysis.objectsInfo["diagrams"][0]["objectId"]
            root_objects = import_analysis.objectsInfo["diagrams"][0]["rootObjects"]
            is_exists = import_analysis.objectsInfo["diagrams"][0]["isExists"]
            object_type = import_analysis.objectsInfo["diagrams"][0]["objectType"]
            version_type = import_analysis.objectsInfo["diagrams"][0][
                "objectVersionType"
            ]
            import_object = import_object_construct(
                object_type=object_type,
                object_name=diagram_name,
                object_id=diagram_id,
                object_version_id=diagram_version,
                object_version_type=version_type,
                root_objects=root_objects,
                is_exists=is_exists,
                is_selected=False,
            )
            import_object_info = import_object_info_construct(diagrams=[import_object])
            import_body = import_construct(
                objects_info=import_object_info, file_name=import_file_name
            )
        with allure.step("Импорт объекта с флагом isSelected = False"):
            import_file.confirm_import_gen(body=import_body)
        with allure.step("Получение информации об импортируемом объекте"):
            get_diagram_by_version_response = diagram_list_by_name(
                super_user, diagram_id
            )
        with allure.step("Проверка, что диаграмма не найдена"):
            assert len(get_diagram_by_version_response) == 0

    @allure.story(
        "При анализе импортируемого файла для диаграммы с вложениями распознаётся, как диаграмма, "
        "так и вложенный тип"
    )
    @allure.title(
        "Импортировать файл диаграммы с вложенным пользовательским типом, проверить. что при анализе "
        "распознались"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_ctype", varType="in_out", isArray=True,
                                               isComplex=True, varValue="in_ctype")])
    @pytest.mark.save_diagram(True)
    def test_diagram_import_analysis_diagram_with_dependent_ctype(self, super_user,
                                                                  export_import_file, diagram_constructor):
        with allure.step("Получение экспорт файла диаграммы"):
            diagram_id = diagram_constructor["diagram_id"]
            file_path = export_import_file.export_objects_file_with_all_dependencies([diagram_id])
        with allure.step(
                "Анализ импортируемых объектов при импорте диаграммы с вложенным пользовательским типом"
        ):
            import_analysis: ConfirmImportResponseDto = (
                ConfirmImportResponseDto.construct(
                    **upload_import_file(
                        super_user, file=file_path
                    ).body
                )
            )
        with allure.step(
                "Проверка, что распозналась, как диаграмма, так и пользовательский тип при анализе файла"
        ):
            assert (
                    len(import_analysis.objectsInfo["diagrams"]) == 1
                    and len(import_analysis.objectsInfo["complexTypes"]) == 1
            )

    @allure.story("Если импортировать файл с вложенным скриптом со всеми версиями, при анализе распознается")
    @allure.title(
        "Импортировать файл диаграммы с вложенным скриптом со всеми версиями, проверить. что при анализе "
        "распознались"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["кастомный код"])
    def test_diagram_import_analysis_diagram_with_dependent_script(self, super_user,
                                                                   diagram_custom_code_python_2, export_import_file):

        with allure.step(
                "Экспорт диаграммы со всеми связанными объектами"
        ):
            diagram_id = diagram_custom_code_python_2["diagram_id"]
            file_path = export_import_file.export_objects_file_with_all_dependencies([diagram_id])
        with allure.step(
                "Анализ импортируемых объектов при импорте диаграммы с вложенным скриптом"
        ):
            import_analysis: ConfirmImportResponseDto = (
                ConfirmImportResponseDto.construct(
                    **upload_import_file(
                        super_user, file=file_path
                    ).body
                )
            )
        with allure.step(
                "Проверка, что распознались, как диаграмма, так и скрипт и их версии при анализе файла"
        ):
            assert (
                    len(import_analysis.objectsInfo["diagrams"]) == 1
                    and len(import_analysis.objectsInfo["scripts"]) == 1
            )

    @allure.story(
        "При импорте диаграммы с вложенным пользовательским типом на контуре появляется диаграмма и "
        "комплексный тип с распознанными при импорте параметрами"
    )
    @allure.title(
        "Импортировать файл с диаграммой и пользовательским типом, проверить. что появились на контуре"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_ctype", varType="in_out", isArray=True,
                                               isComplex=True, varValue="in_ctype")])
    @pytest.mark.save_diagram(True)
    def test_diagram_import_diagram_with_dependent_ctype(self, super_user, diagram_constructor,
                                                         export_import_file):
        with allure.step("Получение необходимых идентификаторов, экспорт диаграммы со всеми связями"):
            diagram_before_import = diagram_constructor["saved_data"]
            diagram_id = diagram_constructor["diagram_id"]
            ctype_before_import = diagram_constructor["complex_type"]
            diagram_nodes_before_import = diagram_before_import.nodes.keys()
            diagram_name_before_import = diagram_before_import.objectName
            file_path = export_import_file.export_objects_file_with_all_dependencies([diagram_id])
        with allure.step("Удаление пользовательского типа и диаграммы"):
            delete_diagram(super_user, diagram_before_import.versionId)
            delete_custom_type(super_user, ctype_before_import.versionId)
        with allure.step("Импорт из файла удаленных пользовательского типа и диаграммы"):
            import_res = import_objects_from_file(super_user, file_path)
        with allure.step("Получение информации об объекте по идентификаторам полученным до удаления"):
            diagram_after_import: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
                super_user, diagram_before_import.versionId
            ).body)
            diagram_name_after_import = diagram_after_import.objectName
            diagram_nodes_after_import = diagram_after_import.nodes.keys()
            ctype_after_import: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_custom_type(super_user, ctype_before_import.versionId).body
            )
        with allure.step(
                "Проверка, что диаграмма и пользовательский тип найдены и данные их корректны"
        ):
            assert (
                    diagram_name_after_import == diagram_name_before_import
                    and diagram_nodes_after_import == diagram_nodes_before_import
                    and ctype_after_import.typeId == ctype_before_import.typeId
                    and ctype_after_import.objectName == ctype_before_import.objectName
                    and ctype_after_import.attributes == ctype_before_import.attributes
            )

    @allure.story("Если импортировать файл с диаграммой и кастомным кодом, то информация появится на контуре")
    @allure.title(
        "Импортировать файл с диаграммой и кастомным кодом, проверить. что появились на контуре"
    )
    @pytest.mark.variable_data([VariableParams(varName="in_out_var", varType="in_out",
                                               varDataType=IntValueType.int.value)])
    @pytest.mark.nodes(["кастомный код"])
    def test_diagram_import_diagram_with_dependent_script(
            self, super_user, diagram_custom_code_python_2, export_import_file
    ):
        with allure.step(
                "Экспорт диаграммы со всеми связанными объектами"
        ):
            diagram_id = diagram_custom_code_python_2["diagram_id"]
            file_path = export_import_file.export_objects_file_with_all_dependencies([diagram_id])
            latest_version_id = diagram_custom_code_python_2["saved_version_id"]
            diagram_before_import: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
                super_user, latest_version_id).body)
            diagram_name_before_import = diagram_before_import.objectName
            diagram_nodes_before_import = diagram_before_import.nodes.keys()
            script_before_import = diagram_custom_code_python_2["script_view"]
        with allure.step("Удаление диаграммы и скрипта перед импортом"):
            delete_diagram(super_user, diagram_before_import.versionId)
            delete_script_by_id(super_user, script_before_import.versionId)
        with allure.step("Импорт из файла удаленных скрипта и диаграммы"):
            import_res = import_objects_from_file(super_user, file_path)
        with allure.step("Получение информации об импортируемых объектах"):
            diagram_after_import: DiagramViewDto = DiagramViewDto.construct(
                **get_diagram_by_version(super_user, diagram_before_import.versionId).body
            )
            script_after_import: ScriptFullView = ScriptFullView.construct(
                **get_python_script_by_id(super_user, script_before_import.versionId).body
            )
            diagram_name_after_import = diagram_after_import.objectName
            diagram_nodes_after_import = diagram_after_import.nodes.keys()
        with allure.step(
                "Проверка, что диаграмма и пользовательский тип найдены и данные их корректны"
        ):
            assert (
                    diagram_name_after_import == diagram_name_before_import
                    and diagram_nodes_after_import == diagram_nodes_before_import
                    and script_after_import.scriptId == script_before_import.scriptId
                    and script_after_import.objectName == script_before_import.objectName
                    and script_after_import.scriptText == script_before_import.scriptText
            )

    @allure.story(
        "Для объектов из списка import_objects с флагом isSelected= true производится импорт объекта путем "
        "обновления данных о текущей версии объекта. Для версии типа latest при несовпадении version_id "
        "загружаемым объектам присваивается идентификатор версии, существующей на контуре"
    )
    @allure.title(
        "Импортировать экспортированную диаграмму, проверить, что id диаграммы и версии не изменились"
    )
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_diagram_export_import_check_correct(
            self,
            super_user,
            diagram_constructor,
            export_import_file):
        with allure.step("Экспорт диаграммы и сохранение всех идентификаторов"):
            diagram_before_import = diagram_constructor["saved_data"]
            old_diagram_id = diagram_constructor["diagram_id"]
            old_latest_version_id = diagram_constructor["saved_data"].versionId
            diagram_nodes_before_import = diagram_before_import.nodes.keys()
            diagram_name_before_import = diagram_constructor["saved_data"].objectName
            file_path = export_import_file.export_objects_file_with_all_dependencies([old_diagram_id])
        with allure.step("Импорт всех объектов из файла"):
            import_res = import_objects_from_file(super_user, file_path)
        with allure.step("Получение информации об импортируемом объекте"):
            get_diagram_by_version_response = get_diagram_by_version(
                super_user, old_latest_version_id
            )
            diagram: DiagramViewDto = DiagramViewDto.construct(
                **get_diagram_by_version_response.body
            )
        with allure.step("Проверка, что диаграмма id версии и диаграммы совпадают"):
            assert (
                    diagram.diagramId == old_diagram_id
                    and diagram.versionId == old_latest_version_id
            )

    @allure.story(
        "Если в диаграмме присутствует комплексный тип с комплексным атрибутом, то оба комплексных типа попадают в "
        "список для экспорта "
    )
    @allure.title(
        "Проверить, что в диаграмме с вложенным комплекс типом имеющем в себе комплексный тип, оба типа попадают в "
        "экспорт с диаграммой "
    )
    @pytest.mark.variable_data([VariableParams(varName="in_cmplx_with_cmplx_attr",
                                               varType="in", isComplex=True, isArray=False,
                                               isConst=False, varValue="complex_type_complex_attr"),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_diagram_export_with_dependencies_ctype_with_ctype_attr(
            self, super_user, diagram_constructor
    ):
        with allure.step("Создание и сохранение диаграммы с вложенным комплекс типом для экспорта"):
            diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        with allure.step("Анализ экспортируемых объектов"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[str(diagram_data.diagramId)],
            )
            gen_export_objects: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
        with allure.step(
                "Проверка, что вложенные комплекс типы обнаружены и подготовлены для экспорта"
        ):
            assert (
                    len(gen_export_objects.diagrams) == 1 and len(gen_export_objects.complexTypes) == 2
            )

    @allure.story(
        "Если в диаграмме присутствует комплексный тип с комплексным атрибутом, файл экспорта успешно скачивается"
    )
    @allure.title(
        "Проверить, что в диаграмме с вложенным комплекс типом имеющем в себе атрибут комплексного тип, файл успешно "
        "скачивается "
    )
    @pytest.mark.variable_data([VariableParams(varName="in_cmplx_with_cmplx_attr",
                                               varType="in", isComplex=True, isArray=False,
                                               isConst=False, varValue="complex_type_complex_attr"),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_diagram_export_download_with_dependencies_ctype_with_ctype_attr(
            self, super_user,
            diagram_constructor,
            export_import_file
    ):
        with allure.step(
                "Создание и сохранение диаграммы с вложенным комплекс типом для экспорта"
        ):
            diagram_data: DiagramViewDto = diagram_constructor["saved_data"]
        with allure.step("Анализ экспортируемых объектов"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[str(diagram_data.diagramId)],
            )
            gen_export_objects: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
            gen_diagram = gen_export_objects.diagrams[0]
            gen_ctype1 = gen_export_objects.complexTypes[0]
            gen_ctype2 = gen_export_objects.complexTypes[1]
        with allure.step("Генерация экспорт файла на сервере"):
            export_diagram = export_object_construct(
                object_type=gen_diagram["objectType"],
                object_name=gen_diagram["objectName"],
                object_id=gen_diagram["objectId"],
                object_version_id=gen_diagram["objectVersionId"],
                object_version_type=gen_diagram["objectVersionType"],
                root_objects=gen_diagram["rootObjects"]
            )
            export_ctype1 = export_object_construct(
                object_type=gen_ctype1["objectType"],
                object_name=gen_ctype1["objectName"],
                object_id=gen_ctype1["objectId"],
                object_version_id=gen_ctype1["objectVersionId"],
                object_version_type=gen_ctype1["objectVersionType"],
                root_objects=gen_ctype1["rootObjects"]
            )
            export_ctype2 = export_object_construct(
                object_type=gen_ctype2["objectType"],
                object_name=gen_ctype2["objectName"],
                object_id=gen_ctype2["objectId"],
                object_version_id=gen_ctype2["objectVersionId"],
                object_version_type=gen_ctype2["objectVersionType"],
                root_objects=gen_ctype2["rootObjects"]
            )
            export_body = export_construct(diagrams=[export_diagram], complex_types=[export_ctype1, export_ctype2])
            export_resp: ExportResponseDto = ExportResponseDto.construct(
                **set_export(super_user, body=export_body).body
            )
        with allure.step("Проверка, что диаграмма, комплекс тип и комплекс атрибут были экспортированы"):
            assert export_resp.totalNumberOfObjects == export_resp.numberOfExportedObjects == 3

    @allure.story(
        "Если в диаграмме присутствует комплексный тип с комплексным атрибутом, удаленная диаграмма появляется на "
        "контуре "
    )
    @allure.title(
        "Проверить, что в диаграмме с вложенным комплексным типом имеющем в себе атрибут комплексного тип, "
        "импорт происходит корректно "
    )
    @pytest.mark.variable_data([VariableParams(varName="in_cmplx_with_cmplx_attr",
                                               varType="in", isComplex=True, isArray=False,
                                               isConst=False, varValue="complex_type_complex_attr"),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_diagram_import_with_dependencies_ctype_with_ctype_attr(
            self, super_user,
            diagram_constructor, export_import_file):
        with allure.step("Получение необходимых идентификаторов, экспорт диаграммы со всеми связями"):
            diagram_before_import = diagram_constructor["saved_data"]
            diagram_id = diagram_constructor["diagram_id"]
            outer_ctype_before_import = diagram_constructor["complex_type"]
            inner_ctype_before_import = diagram_constructor["inner_complex_type"]
            diagram_nodes_before_import = diagram_before_import.nodes.keys()
            diagram_name_before_import = diagram_before_import.objectName
            file_path = export_import_file.export_objects_file_with_all_dependencies([diagram_id])
        with allure.step("Удаление пользовательских типов и диаграммы"):
            delete_diagram(super_user, diagram_before_import.versionId)
            delete_custom_type(super_user, outer_ctype_before_import.versionId)
            delete_custom_type(super_user, inner_ctype_before_import.versionId)
        with allure.step("Импорт из файла удаленных пользовательсих типов и диаграммы"):
            import_res = import_objects_from_file(super_user, file_path)
        with allure.step("Получение информации об импортированных объектах"):
            get_diagram_after_import = get_diagram_by_version(
                super_user, diagram_before_import.versionId
            )
            get_outer_ctype_after_import = get_custom_type(
                super_user, outer_ctype_before_import.versionId
            )
            get_inner_ctype_after_import = get_custom_type(
                super_user, inner_ctype_before_import.versionId
            )
        with allure.step("Получение информации по импортированным объектам на стенде"):
            diagram_after_import: DiagramViewDto = DiagramViewDto.construct(
                **get_diagram_after_import.body
            )
            outer_ctype_after_import: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_outer_ctype_after_import.body
            )
            inner_ctype_after_import: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_inner_ctype_after_import.body
            )
            diagram_name_after_import = diagram_after_import.objectName
            diagram_nodes_after_import = diagram_after_import.nodes.keys()
        with allure.step(
                "Проверка, что диаграмма, комплексный атрибут и комплексный тип найдены под импортируемым uuid"):
            assert (
                    diagram_name_after_import == diagram_name_before_import
                    and diagram_nodes_after_import == diagram_nodes_before_import
                    and outer_ctype_after_import.typeId == outer_ctype_before_import.typeId
                    and outer_ctype_after_import.objectName == outer_ctype_before_import.objectName
                    and outer_ctype_after_import.attributes == outer_ctype_before_import.attributes
                    and inner_ctype_after_import.typeId == inner_ctype_before_import.typeId
                    and inner_ctype_after_import.objectName == inner_ctype_before_import.objectName
                    and inner_ctype_after_import.attributes == inner_ctype_before_import.attributes
            )

    @allure.story(
        "При экспорте деплоя диаграммы с поддиаграммой, в список для экспорта попадают 2 деплоя и 4 версии диаграммы"
    )
    @allure.title(
        "Проверить, что в список деплоя попадает 2 деплоя и 4 версии для деплоя диаграммы с узлом поддиаграммы")
    @pytest.mark.smoke
    def test_deploy_export_with_dependencies_subdiagram(
            self, super_user, diagram_subdiagram_submit_working
    ):
        with allure.step("Анализ экспортируемых объектов"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DEPLOY,
                object_ids=diagram_subdiagram_submit_working["deploys_with_dependencies"],
                is_include_all_versions=True
            )
            gen_export_objects: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
        with allure.step(
                "Проверка, что деплои и диаграммы обнаружены и подготовлены для экспорта"
        ):
            assert (
                    len(gen_export_objects.deploys) == 2 and len(gen_export_objects.diagrams) == 4
            )

    @allure.story("Если экспортируется деплой диаграммы с поддиаграммой, файл экспорта успешно скачивается")
    @allure.title("Проверить, что файл экспорта успешно скачивается для деплоя диаграммы с поддиаграммой")
    # @allure.issue("DEV-15720")
    @pytest.mark.smoke
    def test_deploy_export_download_with_dependencies_subdiagram(
            self, super_user,
            diagram_subdiagram_submit_working,
            export_import_file
    ):
        with allure.step("Анализ экспортируемых объектов"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DEPLOY,
                object_ids=diagram_subdiagram_submit_working["deploys_with_dependencies"],
                is_include_all_versions=True
            )
            gen_export_objects: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
            gen_diagram1 = gen_export_objects.diagrams[0]
            gen_diagram2 = gen_export_objects.diagrams[1]
            gen_diagram3 = gen_export_objects.diagrams[2]
            gen_diagram4 = gen_export_objects.diagrams[3]
            gen_deploy1 = gen_export_objects.deploys[0]
            gen_deploy2 = gen_export_objects.deploys[1]
        with allure.step("Генерация экспорт файла на сервере"):
            export_diagrams = [export_object_auto_construct(gen_diagram1),
                               export_object_auto_construct(gen_diagram2),
                               export_object_auto_construct(gen_diagram3),
                               export_object_auto_construct(gen_diagram4)]
            export_deploys = [export_object_auto_construct(gen_deploy1),
                              export_object_auto_construct(gen_deploy2)]
            export_body = export_construct(diagrams=export_diagrams, deploys=export_deploys)
            export_resp: ExportResponseDto = ExportResponseDto.construct(
                **set_export(super_user, body=export_body).body
            )
        with allure.step("Проверка, что диаграммы и деплои были экспортированы"):
            assert export_resp.totalNumberOfObjects == export_resp.numberOfExportedObjects == 6

    @allure.story(
        "Если происходит импорт диаграммы с поддиаграммой, удаленная диаграмма и поддиграмма появляются на контуре ")
    @allure.title("Проверить, что при импорте деплоя диаграммы с поддиаграммой, импорт происходит корректно")
    # @allure.issue("DEV-15720")
    @pytest.mark.smoke
    def test_deploy_import_with_dependencies_subdiagram(
            self, super_user, diagram_subdiagram_submit_working, export_import_file):
        with allure.step("Экспорт деплоя со всеми связанными объектами"):
            deploy_id_before_import = diagram_subdiagram_submit_working["deploy_id"]
            latest_version_id_before_import = diagram_subdiagram_submit_working["version_id"]
            latest_subdiagram_version_id_before_import = diagram_subdiagram_submit_working["subdiagram_version_id"]
            file_path = export_import_file.export_objects_file_with_all_dependencies([deploy_id_before_import],
                                                                                     object_type=ObjectsType.DEPLOY)
            diagram_id_before_import = diagram_subdiagram_submit_working["diagram_id"]
            subdiagram_id_before_import = diagram_subdiagram_submit_working["subdiagram_id"]
        with allure.step("Удаление деплоя и диаграммы и поддиаграммы"):
            delete_diagram(super_user, latest_version_id_before_import)
            delete_diagram(super_user, latest_subdiagram_version_id_before_import)
            deploy_delete(super_user, ids=deploy_id_before_import)
        with allure.step("Импорт из файла удаленных деплоев и диаграмм"):
            import_res = import_objects_from_file(super_user, file_path)
        with allure.step("Получение информации об импортирванном объекте"):
            get_diagram_after_import = get_diagram_by_version(
                super_user, latest_version_id_before_import
            )
            get_subdiagram_after_import = get_diagram_by_version(
                super_user, latest_subdiagram_version_id_before_import
            )

        with allure.step("Получение информации по импортированным объектам на стенде"):
            diagram_after_import: DiagramViewDto = DiagramViewDto.construct(
                **get_diagram_after_import.body
            )
            subdiagram_after_import: DiagramViewDto = DiagramViewDto.construct(
                **get_subdiagram_after_import.body
            )
            finded_deploys = deploy_list_by_name(super_user, diagram_after_import.objectName)
        with allure.step("Проверка, что диаграмма и поддиаграмма найдены под импортируемым uuid"):
            assert diagram_after_import.diagramId == diagram_id_before_import
            assert subdiagram_after_import.diagramId == subdiagram_id_before_import
            assert len(finded_deploys)==1

    @allure.story(
        "При экспорте диаграммы с предложением, в список для экспорта попадают диаграмма, пользовательский тип,"
        "кастомный код и предложение")
    @allure.title(
        "Проверить, что в список экспорта попадают по 1 объекту типов диаграмма, пользовательский тип, кастомный"
        "код и предложение")
    # @allure.issue("DEV-11818")
    @pytest.mark.smoke
    def test_diagram_export_with_dependencies_offer(
            self, super_user, diagram_offer_for_runtime
    ):
        with allure.step("Анализ экспортируемых объектов"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[diagram_offer_for_runtime["diagram_id"]],
                is_include_all_versions=True
            )
            gen_export_objects: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
        with allure.step(
                "Проверка, что диаграмма, предложение, комплекс тип и кастомный код обнаружены"
                " и подготовлены для экспорта"
        ):
            assert (len(gen_export_objects.diagrams) == len(gen_export_objects.offers)
                    == len(gen_export_objects.scripts) == 1) and len(gen_export_objects.complexTypes) == 4

    @allure.story("Если экспортируется диаграмма с предложением, файл экспорта успешно скачивается")
    @allure.title("Проверить, что файл экспорта успешно скачивается для диаграммы с предложением")
    # @allure.issue("DEV-11818")
    @pytest.mark.smoke
    def test_diagram_export_download_with_dependencies_offer(
            self, super_user,
            diagram_offer_for_runtime,
            export_import_file
    ):
        with allure.step("Анализ экспортируемых объектов"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[diagram_offer_for_runtime["diagram_id"]],
                is_include_all_versions=True
            )
            gen_export_objects: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
            gen_diagram = gen_export_objects.diagrams[0]
            gen_offer = gen_export_objects.offers[0]
            gen_ctype = gen_export_objects.complexTypes[0]
            gen_script = gen_export_objects.scripts[0]
        with allure.step("Генерация экспорт файла на сервере"):
            export_diagrams = [export_object_auto_construct(gen_diagram)]
            export_offers = [export_object_auto_construct(gen_offer)]
            export_ctypes = [export_object_auto_construct(gen_ctype)]
            export_scripts = [export_object_auto_construct(gen_script)]
            export_body = export_construct(diagrams=export_diagrams,
                                           complex_types=export_ctypes,
                                           scripts=export_scripts,
                                           offers=export_offers)
            export_resp: ExportResponseDto = ExportResponseDto.construct(
                **set_export(super_user, body=export_body).body
            )
        with allure.step("Проверка, что диаграмма, предложение, кастомный код и пользовательский тип успешно "
                         "экспортировались"):
            assert export_resp.totalNumberOfObjects == export_resp.numberOfExportedObjects == 4

    @allure.story("Если происходит импорт диаграммы с предложением, удаленные диаграмма, скрипт, комплексный тип и "
                  "предложение появляются на контуре ")
    @allure.title("Проверить, что при импорте диаграммы с предложением, импорт происходит корректно")
    # @allure.issue("DEV-11818")
    @pytest.mark.smoke
    def test_diagram_import_with_dependencies_offer(self, super_user,
                                                    diagram_offer_for_runtime, export_import_file):
        with allure.step("Получение идентификаторов объектов и экспорт диаграммы со всеми связями"):
            diagram_id = diagram_offer_for_runtime["diagram_id"]
            diagram_before_import = diagram_offer_for_runtime["diagram_data"]
            offer_before_import = diagram_offer_for_runtime["offer"]
            ctype_before_import = diagram_offer_for_runtime["complex_type"]
            script_before_import = diagram_offer_for_runtime["script"]
            latest_version_id = diagram_offer_for_runtime["create_result"].uuid
            offer_version_id = offer_before_import.versionId
            ctype_version_id = ctype_before_import.versionId
            script_version_id = script_before_import.versionId

            file_path = export_import_file.export_objects_file_with_all_dependencies([diagram_id])
        with allure.step("Удаление всех объектов перед импортом"):
            delete_diagram(super_user, latest_version_id)
            delete_offer(super_user, offer_version_id)
            delete_script_by_id(super_user, script_version_id)
            # delete_custom_type(super_user, ctype_version_id) потому что тип системный
        with allure.step("Импорт из файла удаленных диаграммы, предложения, кастомного кода и комплексного типа"):
            import_res = import_objects_from_file(super_user, file_path)
        with allure.step("Получение информации по импортированным диаграмме, "
                         "предложению, кастомному коду и комплексному типу на стенде"):
            get_diagram_by_version_response = get_diagram_by_version(
                super_user, latest_version_id
            )
            get_offer_by_version_response = get_offer_info(
                super_user, offer_version_id
            )
            get_script_by_version_response = get_groovy_script_by_id(
                super_user, script_version_id
            )
            get_ctype_by_version_response = get_custom_type(
                super_user, ctype_version_id
            )
        with allure.step("Встраивание информации по импортированным диаграмме, "
                         "предложению, кастомному коду и комплексному типу на стенде"):
            diagram_after_import: DiagramViewDto = DiagramViewDto.construct(
                **get_diagram_by_version_response.body
            )
            ctype_after_import: ComplexTypeGetFullView = ComplexTypeGetFullView.construct(
                **get_ctype_by_version_response.body
            )
            script_after_import: ScriptFullView = ScriptFullView.construct(
                **get_script_by_version_response.body
            )
            offer_after_import: OfferFullViewDto = OfferFullViewDto.construct(
                **get_offer_by_version_response.body
            )
        with allure.step("Проверка, что диаграмма, предложение, кастомный код и пользовательский тип "
                         "найдены под импортируемым uuid"):
            assert diagram_after_import.objectName == diagram_before_import.objectName
            assert ctype_after_import.objectName == ctype_before_import.objectName
            assert script_after_import.objectName == script_before_import.objectName
            assert offer_after_import.objectName == offer_before_import.objectName

    @allure.story(
        "При экспорте диаграммы с пустыми узлами всех ссылающихся на объекты типов - экспорт происходит успешно")
    @allure.title(
        "Проверить, что в список на экспорт попадает только диаграмма для диаграммы с пустыми узлами")
    @pytest.mark.variable_data([VariableParams(varName="in_int", varType="in", varDataType=1),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.nodes(["чтение", "расчет переменной", "кастомный код", "предложение", "запись", "расчет агрегата",
                        "внешний сервис", "поддиаграмма", "коммуникация", "чтение тарантул", "запись тарантул"])
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_diagram_export_with_no_dependencies_all_nodes(self, super_user, diagram_constructor):
        with allure.step("Генерация состава экспортируемых объектов по заданному uuid диаграммы"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[diagram_constructor["diagram_id"]],
                is_include_all_versions=True
            )
            gen_export_objects: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
        with allure.step(
                "Проверка что в списке на экспорт обнаружена диаграмма"
        ):
            assert len(gen_export_objects.diagrams) == 1

    @allure.story("Если экспортируется диаграмма с пустыми узлами всех типов ссылающихся на объекты, файл экспорта"
                  " успешно скачивается")
    @allure.title(
        "Проверить, что файл экспорта успешно скачивается для диаграммы пустыми узлами всех типов ссылающихся "
        "на объекты")
    @pytest.mark.variable_data([VariableParams(varName="in_int", varType="in", varDataType=1),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.nodes(["чтение", "расчет переменной", "кастомный код", "предложение", "запись", "расчет агрегата",
                        "внешний сервис", "поддиаграмма", "коммуникация", "чтение тарантул", "запись тарантул"])
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_diagram_export_download_with_no_dependencies_all_nodes(
            self, super_user,
            diagram_constructor,
            export_import_file
    ):
        with allure.step("Генерация состава экспортируемых объектов по заданному uuid диаграммы"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[diagram_constructor["diagram_id"]],
                is_include_all_versions=True
            )
            gen_export_objects: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
        with allure.step("Запрос экспорт файла по полученной диаграмме"):
            gen_diagram = gen_export_objects.diagrams[0]
            export_diagrams = [export_object_auto_construct(gen_diagram)]
            export_body = export_construct(diagrams=export_diagrams)
            export_resp: ExportResponseDto = ExportResponseDto.construct(
                **set_export(super_user, body=export_body).body
            )
        with allure.step("Проверка, что диаграмма успешно экспортировалась в файл"):
            assert export_resp.totalNumberOfObjects == export_resp.numberOfExportedObjects == 1

    @allure.story(
        "Если происходит импорт диаграммы с пустыми узлами всех типов, удаленная диаграмма появляется на контуре ")
    @allure.title("Проверить, что при импорте диаграммы с пустыми узлами всех типов, импорт происходит корректно")
    @pytest.mark.variable_data([VariableParams(varName="in_int", varType="in", varDataType=1),
                                VariableParams(varName="out_int", varType="out", varDataType=1)])
    @pytest.mark.nodes(["чтение", "расчет переменной", "кастомный код", "предложение", "запись", "расчет агрегата",
                        "внешний сервис", "поддиаграмма", "коммуникация", "чтение тарантул", "запись тарантул"])
    @pytest.mark.save_diagram(True)
    @pytest.mark.smoke
    def test_diagram_import_with_no_dependencies_all_nodes(
            self, super_user,
            diagram_constructor, export_import_file):
        with allure.step("Получение необходимых идентификаторов, экспорт диаграммы"):
            diagram_before_import = diagram_constructor["saved_data"]
            diagram_id = diagram_constructor["diagram_id"]
            latest_version_id = diagram_constructor["saved_data"].versionId
            diagram_nodes_before_import = diagram_before_import.nodes.keys()
            diagram_name_before_import = diagram_constructor["saved_data"].objectName
            file_path = export_import_file.export_objects_file_with_all_dependencies([diagram_id])
        with allure.step("Удаление диаграммы перед импортом"):
            delete_diagram(super_user, str(latest_version_id))
        with allure.step("Импорт всех объектов из файла"):
            import_res = import_objects_from_file(super_user, file_path)
        with allure.step("Получение информации по импортированной диаграмме на стенде"):
            diagram_after_import: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
                super_user, latest_version_id
            ).body)
            diagram_name_after_import = diagram_after_import.objectName
            diagram_nodes_after_import = diagram_after_import.nodes.keys()
        with allure.step("Проверка, что диаграмма найдена под и все узлы на месте"):
            assert diagram_after_import.objectName == diagram_name_before_import
            assert diagram_nodes_after_import == diagram_nodes_before_import

    @allure.story(
        "При экспорте диаграммы с узлом записи в Tarantool - экспорт происходит успешно")
    @allure.title(
        "Проверить, что в список на экспорт попадает источник данных и диаграмма для диаграммы с узлом записи Tarantool")
    @pytest.mark.tarantool
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("UNIQUE")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_1", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_2", varType="in", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    @pytest.mark.smoke
    def test_diagram_export_with_dependencies_trntl_insert(self, super_user, tarantool_insert_update_saved):
        with allure.step("Генерация состава экспортируемых объектов по заданному uuid диаграммы"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[tarantool_insert_update_saved["diagram_data"].diagramId],
                is_include_all_versions=True
            )
            gen_export_objects: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
        with allure.step(
                "Проверка, что диаграмма и источник данных обнаружены и подготовлены для экспорта"
        ):
            assert (len(gen_export_objects.diagrams) == len(gen_export_objects.dataProviders) == 1)

    @allure.story("Если экспортируется диаграмма с узлом записи Tarantool файл экспорта успешно скачивается")
    @allure.title("Проверить, что файл экспорта успешно скачивается для диаграммы с узлом записи Tarantool")
    @pytest.mark.tarantool
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("UNIQUE")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_1", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_2", varType="in", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    @pytest.mark.smoke
    def test_diagram_export_download_with_dependencies_trntl_insert(
            self, super_user,
            tarantool_insert_update_saved,
            export_import_file
    ):
        with allure.step("Генерация состава экспортируемых объектов по заданному uuid диаграммы"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[tarantool_insert_update_saved["diagram_data"].diagramId],
                is_include_all_versions=True
            )
            gen_export_objects: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
        with allure.step("Запрос экспорт файла по полученным диаграмме и источнику данных"):
            gen_diagram = gen_export_objects.diagrams[0]
            gen_data_provider = gen_export_objects.dataProviders[0]
            export_diagrams = [export_object_auto_construct(gen_diagram)]
            export_data_providers = [export_object_auto_construct(gen_data_provider)]
            export_body = export_construct(diagrams=export_diagrams,
                                           data_providers=export_data_providers)
            export_resp: ExportResponseDto = ExportResponseDto.construct(
                **set_export(super_user, body=export_body).body
            )
        with allure.step("Проверка, что диаграмма и источник данных найдены успешно экспортировались в файл"):
            assert export_resp.totalNumberOfObjects == export_resp.numberOfExportedObjects == 2

    @allure.story("Если происходит импорт диаграммы с узлом записи Tarantool, удаленные диаграмма и источник данных"
                  "появляются на контуре")
    @allure.title("Проверить, что при импорте диаграммы с узлом записи Tarantool, импорт происходит корректно")
    @pytest.mark.tarantool
    @pytest.mark.provider_type("tdg")
    @pytest.mark.table_name("CONTACT")
    @pytest.mark.index_type("UNIQUE")
    @pytest.mark.variable_data(
        [VariableParams(varName="in_out_int", varType="in_out", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_1", varType="in", varDataType=IntValueType.long.value),
         VariableParams(varName="in_int_2", varType="in", varDataType=IntValueType.long.value)])
    @pytest.mark.nodes(["запись тарантул"])
    @pytest.mark.smoke
    def test_diagram_import_with_dependencies_trntl_insert(self, super_user,
                                                           tarantool_insert_update_saved, export_import_file):
        with allure.step("Получение списка объектов в импортируемом файле и подготовка данных"):
            diagram_id = tarantool_insert_update_saved["diagram_data"].diagramId
            file_path = export_import_file.export_objects_file_with_all_dependencies([diagram_id])
            diagram_before_import = tarantool_insert_update_saved["diagram_data"]
            diagram_nodes_before_import = diagram_before_import.nodes.keys()
            data_provider_before_import = tarantool_insert_update_saved["provider_info"]
            latest_version_id = diagram_before_import.versionId
            data_provider_id = data_provider_before_import.sourceId
            provider_settings_before_import = tuple(data_provider_before_import.settings[0].values())
        with allure.step("Удаление диаграммы и провайдера перед импортом"):
            delete_diagram(super_user, latest_version_id)
            delete_data_provider(super_user, str(data_provider_id))
        with allure.step("Импорт диаграммы и источника данных из файла"):
            import_res = import_objects_from_file(super_user, file_path)
        with allure.step("Встраивание информации по импортированным диаграмме и источнику данных в модель"):
            diagram_after_import: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
                super_user, latest_version_id).body)
            data_provider_after_import: DataProviderGetFullView = DataProviderGetFullView.construct(**get_data_provider(
                super_user, data_provider_id).body)
            diagram_nodes_after_import = diagram_after_import.nodes.keys()
            provider_settings_after_import = tuple(data_provider_after_import.settings[0].values())

        with allure.step(
                "Проверка, что диаграмма и источник данных найдены под импортируемым uuid"):
            assert diagram_nodes_after_import == diagram_nodes_before_import
            assert provider_settings_after_import == provider_settings_before_import

    @allure.story(
        "При экспорте диаграммы с узлом внешнего сервиса - экспорт происходит успешно")
    @allure.title(
        "Проверить, что в список экспорта попадает внешний сервис и диаграмма для диаграммы с внешним сервисом")
    @pytest.mark.smoke
    def test_diagram_export_with_dependencies_ext_service(self, super_user, diagram_external_service_saved):
        with allure.step("Генерация состава экспортируемых объектов по заданному uuid диаграммы"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[diagram_external_service_saved["diagram_id"]],
                is_include_all_versions=True
            )
            gen_export_objects: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
        with allure.step(
                "Проверка, что диаграмма и внешний сервис обнаружены и подготовлены для экспорта"
        ):
            assert (len(gen_export_objects.diagrams) == len(gen_export_objects.externalServices) == 1)

    @allure.story("Если экспортируется диаграмма с узлов внешнего сервиса, файл экспорта успешно скачивается")
    @allure.title("Проверить, что файл экспорта успешно формируется и скачивается для диаграммы с внешним сервисом")
    @pytest.mark.smoke
    def test_diagram_export_download_with_dependencies_ext_service(
            self, super_user,
            diagram_external_service_saved,
            export_import_file
    ):
        with allure.step("Генерация состава экспортируемых объектов по заданному uuid диаграммы"):
            gen_body = generate_export_objects_construct(
                objects_type=ObjectsType.DIAGRAM,
                object_ids=[diagram_external_service_saved["diagram_id"]],
                is_include_all_versions=True
            )
            gen_export_objects: ConfirmExportDto = ConfirmExportDto.construct(
                **generate_export_objects(super_user, body=gen_body).body
            )
        with allure.step("Запрос экспорт файла по полученным диаграмме и внешнему сервису"):
            gen_diagram = gen_export_objects.diagrams[0]
            gen_ext_service = gen_export_objects.externalServices[0]
            export_diagrams = [export_object_auto_construct(gen_diagram)]
            export_ext_services = [export_object_auto_construct(gen_ext_service)]
            export_body = export_construct(diagrams=export_diagrams,
                                           external_services=export_ext_services)
            export_resp: ExportResponseDto = ExportResponseDto.construct(
                **set_export(super_user, body=export_body).body
            )
        with allure.step("Проверка, что диаграмма и внешний сервис успешно экспортировались в файл"):
            assert export_resp.totalNumberOfObjects == export_resp.numberOfExportedObjects == 2

    @allure.story(
        "Если происходит импорт диаграммы со внешним сервисом, удаленные диаграмма, скрипт, комплексный тип и "
        "предложение появляются на контуре ")
    @allure.title("Проверить, что при импорте диаграммы со внешним сервисом, импорт происходит корректно")
    @pytest.mark.smoke
    def test_diagram_import_with_dependencies_ext_service(
            self, super_user,
            diagram_external_service_saved, export_import_file):
        with allure.step("Получение необходимых идентификаторов, экспорт диаграммы"):
            diagram_id = diagram_external_service_saved["diagram_id"]
            ext_service_before_import = diagram_external_service_saved["external_service"]
            ext_service_version_id = ext_service_before_import.versionId
            latest_version_id = diagram_external_service_saved["saved_version_id"]
            diagram_before_import: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
                    super_user, latest_version_id).body)
            file_path = export_import_file.export_objects_file_with_all_dependencies([diagram_id])
            diagram_nodes_before_import = diagram_before_import.nodes.keys()
            ext_service_settings_before_import = tuple(ext_service_before_import.serviceSettings[0].values())
        with allure.step("Удаление диаграммы и внешнего сервиса перед импортом"):
            delete_diagram(super_user, latest_version_id)
            delete_service(super_user, str(ext_service_version_id))
        with allure.step("Импорт диаграммы и внешнего сервиса из файла"):
            import_res = import_objects_from_file(super_user, file_path)
        with allure.step("Встраивание информации по импортированным диаграмме и источнику данных в модель"):
            diagram_after_import: DiagramViewDto = DiagramViewDto.construct(**get_diagram_by_version(
                super_user, latest_version_id).body)
            ext_service_after_import: ExternalServiceFullViewDto = ExternalServiceFullViewDto.construct(**find_service_by_id(
                super_user, ext_service_version_id).body)
            diagram_name_after_import = diagram_after_import.objectName
            diagram_nodes_after_import = diagram_after_import.nodes.keys()
            ext_service_settings_after_import = tuple(ext_service_after_import.serviceSettings[0].values())

        with allure.step(
                "Проверка, что диаграмма и источник данных найдены под импортируемым uuid"):
            assert diagram_nodes_after_import == diagram_nodes_before_import
            assert ext_service_settings_after_import == ext_service_settings_before_import
