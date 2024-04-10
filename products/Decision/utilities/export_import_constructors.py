from products.Decision.framework.model import GenerateConfirmExportDtoRequest, ObjectsType, ExportStatusDto, \
    ExportObjectInfo, SelectedImportDto, SelectedImportStatusDto, ImportObjectInfo, \
    ImportResponseDto
from products.Decision.framework.steps.decision_steps_migration import upload_import_file, confirm_import
from sdk.user import User


def generate_export_objects_construct(objects_type: ObjectsType, object_ids: list[str],
                                      is_include_all_versions=False,
                                      is_include_dependencies=True):
    return GenerateConfirmExportDtoRequest(objectsType=objects_type,
                                           objectIds=object_ids,
                                           isIncludeAllVersions=is_include_all_versions,
                                           isIncludeDependencies=is_include_dependencies)


def export_object_construct(object_type, object_name, object_id,
                            object_version_id, object_version_type,
                            status=None, object_version_name=None,
                            root_objects=None, is_selected=True):
    return ExportObjectInfo.construct(objectType=object_type,
                                      objectName=object_name,
                                      objectId=object_id,
                                      objectVersionId=object_version_id,
                                      objectVersionName=object_version_name,
                                      objectVersionType=object_version_type,
                                      rootObjects=root_objects,
                                      isSelected=is_selected,
                                      status=status)


def export_construct(diagrams=None,
                     deploys=None,
                     complex_types=None,
                     scripts=None,
                     external_services=None,
                     aggregates=None,
                     data_providers=None,
                     dictionaries=None,
                     communications=None,
                     offers=None):
    return ExportStatusDto.construct(deploys=deploys,
                                     diagrams=diagrams,
                                     complexTypes=complex_types,
                                     scripts=scripts,
                                     externalServices=external_services,
                                     aggregates=aggregates,
                                     dataProviders=data_providers,
                                     dictionaries=dictionaries,
                                     communications=communications,
                                     offers=offers)


def import_object_construct(object_type, object_name, object_id,
                            object_version_id, object_version_type,
                            status=None, object_version_name=None,
                            root_objects=None, is_selected=True, is_exists=None):
    return ImportObjectInfo.construct(objectType=object_type,
                                      objectName=object_name,
                                      objectId=object_id,
                                      objectVersionId=object_version_id,
                                      objectVersionName=object_version_name,
                                      objectVersionType=object_version_type,
                                      rootObjects=root_objects,
                                      isExists=is_exists,
                                      isSelected=is_selected,
                                      status=status)


def import_object_info_construct(diagrams=[],
                                 deploys=[],
                                 complex_types=[],
                                 scripts=[],
                                 external_services=[],
                                 aggregates=[],
                                 data_providers=[],
                                 dictionaries=[],
                                 communications=[],
                                 offers=[]):
    return SelectedImportStatusDto.construct(deploys=deploys,
                                             diagrams=diagrams,
                                             complexTypes=complex_types,
                                             scripts=scripts,
                                             externalServices=external_services,
                                             aggregates=aggregates,
                                             dataProviders=data_providers,
                                             dictionaries=dictionaries,
                                             communications=communications,
                                             offers=offers)


def import_construct(objects_info, file_name):
    return SelectedImportDto(objectsInfo=objects_info, fileName=file_name)


def export_object_auto_construct(object_for_export: dict,
                                 status=None,
                                 is_selected=True, is_exists=None):
    return ExportObjectInfo.construct(isExists=is_exists,
                                      isSelected=is_selected,
                                      status=status, **object_for_export)


def import_object_auto_construct(object_for_import: dict,
                                 status=None,
                                 is_selected=True):
    return ImportObjectInfo.construct(isSelected=is_selected,
                                      status=status, **object_for_import)


def import_objects_from_file(user: User, file_path: str):
    import_analysis = upload_import_file(user, file=file_path).body
    import_file_name = import_analysis["fileName"]
    import_objects = import_analysis["objectsInfo"]
    for key in import_objects:
        for element in import_objects[key]:
            element["isSelected"] = True
    import_object_info = SelectedImportStatusDto.construct(**import_objects)
    import_body = import_construct(objects_info=import_object_info, file_name=import_file_name)
    import_result = ImportResponseDto.construct(**confirm_import(user, import_body).body)
    return import_result

