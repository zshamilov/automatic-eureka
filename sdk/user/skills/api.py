import json
import uuid
from enum import Enum
from uuid import UUID
import os
from sdk.user.interface.api.client import ApiClient
from sdk.user.interface.api.request import ApiRequest
from sdk.user.interface.api.response import ApiResponse
from requests.exceptions import RequestException, HTTPError


# from rich import print


class ApiSkills:
    def __init__(
        self,
        *,
        username: str,
        password: str,
        client: ApiClient,
        client_id: str,
        client_secret: str,
        scope: str
    ):
        self.username = username
        self.password = password
        self.permissions = None
        self.client = client
        self.token = None
        self.refresh_token = None
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope

    def authorize(self) -> str:
        request = ApiRequest(
            method="POST",
            path=f'/realms/{os.getenv("AUTH_REALM")}/protocol/openid-connect/token',
            query={},
            body={
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": self.scope
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        response = self.client.make_request(request)
        self.token = response.body["access_token"]
        self.refresh_token = response.body["refresh_token"]

        return self.token

    def make_refresh_token(self) -> str:
        request = ApiRequest(
            method="POST",
            path=f'/realms/{os.getenv("AUTH_REALM")}/protocol/openid-connect/token',
            query={},
            body={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        self.client._host = os.getenv("AUTH_SERVICE")
        try:
            response = self.client.make_request(request)
            self.token = response.body["access_token"]
            self.refresh_token = response.body["refresh_token"]
        finally:
            if self.username != "writer":
                self.client._host = os.getenv("ENDPOINT")
                print("вернул хост на место")
        return self.token

    # def get_binary_file(self, request: ApiRequest, file_path: str, headers: dict = None) -> ApiResponse:
    #     # add access token header
    #     if self.token is not None:
    #         request.headers["Authorization"] = f"Bearer {self.token}"
    #
    #     # add custom headers
    #     if headers is not None:
    #         request.headers |= headers
    #
    #     response = self.client.make_request(request)
    #     byte_file = response.content
    #     test_file = open(file_path, "wb")
    #     test_file.write(byte_file)
    #     test_file.close()
    #
    #     return response

    def send(
        self, request: ApiRequest, headers: dict = None, file_path: str = None
    ) -> ApiResponse:
        # add access token header
        if self.token is not None:
            request.headers["Authorization"] = f"Bearer {self.token}"

        # add custom headers
        if headers is not None:
            request.headers |= headers

        if (
            request.body != {}
            and not isinstance(request.body, list)
            and not isinstance(request.body, str)
        ):
            for key, value in request.body.items():
                if isinstance(value, uuid.UUID):
                    request.body[key] = str(request.body[key])
                if isinstance(value, Enum):
                    request.body[key] = f"{request.body[key].value}"

        if isinstance(request.body, list):
            for i in range(len(request.body)):
                if (
                    not isinstance(request.body[i], str)
                    and not isinstance(request.body[i], dict)
                    and not isinstance(request.body[i], int)
                    and not isinstance(request.body[i], bool)
                    and not isinstance(request.body[i], int)
                    and not isinstance(request.body[i], float)
                    and not isinstance(request.body[i], set)
                    and not isinstance(request.body[i], tuple)
                ):
                    request.body[i] = request.body[i].dict()
                    for key, value in request.body[i].items():
                        if isinstance(value, uuid.UUID):
                            request.body[i][key] = str(request.body[i][key])
                        if isinstance(value, Enum):
                            request.body[i][key] = f"{request.body[i][key].value}"

        try:
            response = self.client.make_request(request)
        except HTTPError as e:
            raise e
        # response.raise_for_status()
        # try:
        #     r = requests.get(url, timeout=3)
        #     r.raise_for_status()
        # except requests.exceptions.HTTPError as errh:
        #     print("Http Error:", errh)
        # except requests.exceptions.ConnectionError as errc:
        #     print("Error Connecting:", errc)
        # except requests.exceptions.Timeout as errt:
        #     print("Timeout Error:", errt)
        # except requests.exceptions.RequestException as err:
        #     print("OOps: Something Else", err)
        if file_path is not None:
            byte_file = response.content
            if isinstance(file_path, str):
                test_file = open(file_path, "wb")
                test_file.write(byte_file)
                test_file.close()
        return response
        # if str(response.status).startswith("5"):
        #     raise Exception(f"Unexpected status code {response.status}")
        # else:
        #     return response
