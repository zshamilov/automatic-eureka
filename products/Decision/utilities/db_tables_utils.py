import sqlalchemy
from products.Decision.framework.model import DiagramInOutParameterFullViewDto, ColumnsDto
from products.Decision.utilities.custom_models import PrimitiveToDatabaseTypeMappings


def get_db_column_name(db_table: sqlalchemy.Table, diagram_param: DiagramInOutParameterFullViewDto = None,
                       type_id: str = None):
    db_table_columns = db_table.columns
    if diagram_param:
        db_datatype = PrimitiveToDatabaseTypeMappings.primitive_to_pg[diagram_param.typeId]
    elif type_id:
        db_datatype = PrimitiveToDatabaseTypeMappings.primitive_to_pg[type_id]
    db_column = list(
        filter(lambda column: type(column.type) is type(db_datatype), db_table_columns)).pop().name
    return db_column


def get_column_properties(columns: ColumnsDto, column_type: str = None, column_name: str = None) -> ColumnsDto:
    if column_type:
        column = list(filter(lambda column: column.dataType == column_type, columns)).pop()
    elif column_name:
        column = list(filter(lambda column: column.columnName == column_name, columns)).pop()
    return column


def get_nullable_columns(columns: ColumnsDto):
    null_columns = list(filter(lambda column: column.isNullable, columns))
    return null_columns


def get_primary_key(columns: ColumnsDto):
    primary_key_columns = list(filter(lambda column: column.isPrimary, columns)).pop()
    return primary_key_columns