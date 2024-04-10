from sqlalchemy import (MetaData,
                        Table, Column, Integer, String, Boolean, Date, DateTime, Time, Double, BigInteger, Identity)

metadata_obj = MetaData()
new_schema = "autotests_schema"

read_node_table = Table(
    "read_node_table",
    metadata_obj,
    Column("double_val", Double),
    Column("int_val", Integer),
    Column("str_val", String),
    Column("date_val", Date),
    Column("bool_val", Boolean),
    Column("date_time_val", DateTime),
    Column("time_val", Time),
    Column("long_val", BigInteger),
    schema="public"
)

insert_node_table = Table(
    "insert_node_table",
    metadata_obj,
    Column("double_val", Double),
    Column("int_val", Integer),
    Column("str_val", String),
    Column("date_val", Date),
    Column("bool_val", Boolean),
    Column("date_time_val", DateTime),
    Column("time_val", Time),
    Column("long_val", BigInteger),
    Column("int_val2", Integer),
    schema="public"
)

insert_node_e2e_table = Table(
    "insert_node_e2e_table",
    metadata_obj,
    Column("int_val", Integer, primary_key=True, nullable=False),
    Column("bool_val", Boolean),
    schema="public"
)

default_pk_autoincrement_table = Table(
    "default_pk_autoincrement_table",
    metadata_obj,
    Column("double_val", Double, primary_key=True, nullable=False, autoincrement=False),
    Column("int_val", Integer, Identity(on_null=True, start=1, increment=1, minvalue=1, maxvalue=1000, cache=1,
                                        cycle=True), autoincrement=True, nullable=False),
    Column("str_val", String, server_default="stroka", default=True, nullable=False),
    Column("date_val", Date, nullable=False),
    Column("bool_val", Boolean),
    Column("date_time_val", DateTime),
    Column("time_val", Time),
    Column("long_val", BigInteger),
    schema="public"
)

metadata_with_scheme = MetaData(schema=new_schema)

table_in_schema = Table(
    "table_in_schema",
    metadata_with_scheme,
    Column("double_val", Double),
    Column("int_val", Integer),
    Column("str_val", String),
    Column("date_val", Date),
    Column("bool_val", Boolean),
    Column("date_time_val", DateTime),
    Column("time_val", Time),
    Column("long_val", BigInteger))