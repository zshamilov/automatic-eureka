import datetime
from typing import List, Dict

import sqlalchemy as sa
from sqlalchemy import select, func, insert, Table, Column

from sdk.user import User


def insert_rows_with_values_in_table(user: User, table, rows):
    select_stmt = select(func.generate_series(1, 1))
    stmt1 = insert(table).from_select(rows, select_stmt)
    print(stmt1)
    with user.with_db.engine.connect() as connection:
        results = connection.execute(stmt1)
        connection.commit()
    return results


def get_row_count(user: User, table):
    select(table.c.id_int)
    stmt_s = select(func.count("*")).select_from(table)
    with user.with_db.engine.connect() as connection:
        results = connection.execute(stmt_s).all()
        print(results)
    return results


def lv_get_row_count(user: User, table):
    qry = sa.text(f'SELECT count (*) from {table}')
    with user.with_db.engine.connect() as connection:
        resultset = connection.execute(qry)
        results_as_dict = resultset.mappings().all()
    return results_as_dict


def insert_values(user: User, table: Table, values: dict):
    """
    :param user: пользователь БД
    :param table: Таблица для вставки
    :param values: Словарь {столбец таблицы: вставляемое значение}
    """
    stmt = insert(table).values(values)
    print(stmt)
    with user.with_db.engine.connect() as connection:
        results = connection.execute(stmt)
        connection.commit()
    return results


def select_all_where(user: User, columns: List[Column], where_statement) -> Dict[str, List]:
    """
    :param user: Пользователь базы данных
    :param columns: Список объектов Column для выбора
    :param where_statement: Выражение SQLAlchemy, описывающее условие `where` для выборки. (например model.table.c.col_name == 123)
    :return: Словарь, где ключи - это имена столбцов, а значения - списки значений столбцов
    """

    stmt = select(*columns).filter(where_statement)
    print(stmt)
    with user.with_db.engine.connect() as connection:
        results = connection.execute(stmt).all()

        result = {column.name: [] for column in columns}
        for row in results:
            for column in columns:
                cur_val = row._mapping[column.name]
                if isinstance(cur_val, datetime.datetime):
                    cur_val = cur_val.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                if isinstance(cur_val, datetime.date):
                    cur_val = cur_val.strftime('%Y-%m-%d')
                if isinstance(cur_val, datetime.time):
                    cur_val = cur_val.strftime('%H:%M:%S')
                result[column.name].append(cur_val)

    return result
