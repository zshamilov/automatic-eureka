from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine


class DbSkills:
    def __init__(self,
                 username: str,
                 password: str,
                 host: str,
                 port: str,
                 db_name: str,
                 db_type: str = 'postgresql',
                 db_api: str = 'psycopg2',
                 echo: bool = False):

        self.settings: str = f'{db_type}+{db_api}://{username}:{password}@{host}:{port}/{db_name}'
        self.engine: Engine = create_engine(self.settings, echo=echo)

    def get_column_names(self, table: str, schema: str = None) -> list[str]:
        return [
            column['name']
            for column in inspect(self.engine).get_columns(table, schema)
        ]
