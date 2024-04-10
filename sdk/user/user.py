from sdk.user.interface.api.client import ApiClient
from sdk.user.interface.web.client import WebClient
from sdk.user.skills.api import ApiSkills
from sdk.user.skills.db import DbSkills
from sdk.user.skills.web import WebSkills


class User:
    username: str
    password: str
    permissions: list
    with_api: ApiSkills
    with_web: WebSkills
    with_db: DbSkills

    def __init__(self, *, username: str = None, password: str = None):
        self.username = username
        self.password = password
        self.permissions = []

    def add_api_client(self, *, client: ApiClient, client_id="frontend", client_secret="frontend", scope=None):
        self.with_api = ApiSkills(username=self.username, password=self.password, client=client,
                                  client_id=client_id, client_secret=client_secret, scope=scope)

    def add_db_client(self, *, username: str, password: str, host: str, port: str, db_name: str,
                      echo: bool = False, db_type: str = 'postgresql', db_api: str = 'psycopg2'):
        self.with_db = DbSkills(username, password, host, port, db_name, db_type, db_api, echo)

    def add_web_client(self, *, client: WebClient):
        self.with_web = WebSkills(client)
