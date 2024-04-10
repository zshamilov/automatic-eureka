from products.Decision.framework.model import SchemaSaveDto


def schema_construct(name: str, schema_data: dict) -> SchemaSaveDto:
    fields = []
    for key, value in schema_data.items():
        fields.append({"name": key, "type": value})
    schema_json = {"type": "record", "name": name, "namespace": "ru.glowbyte.streaming", "fields": fields}
    schema_body = SchemaSaveDto.construct(name=name,
                                          version="1",
                                          schemaJson=schema_json)
    return schema_body
