#import allure
import requests
import json

from sdk.user.interface.api.request import ApiRequest
from sdk.user.interface.api.response import ApiResponse
from sdk.clients.interface.reporter import Reporter
from sdk.reporters.dummy import Dummy

from rich import print
import traceback
from json.decoder import JSONDecodeError
from requests.exceptions import RequestException, HTTPError


# > This class is used to make API calls to the server
class ApiClient:
    def __init__(self, *, host: str, reporter: Reporter = Dummy, timeout: int = 300):
        self._host = host
        self._reporter = reporter
        self._timeout = timeout
        self._session = requests.Session()

        with self._reporter.step(f"Start api client with config"):
            self._reporter.attach("Host", f"{self._host}")
            self._reporter.attach("Timeout", f"{self._timeout}")

    def _to_their_request(self, request: ApiRequest) -> requests.Request:
        """
        It converts a request from our API to a request from the requests library

        :param request: The request object that you created
        :type request: ApiRequest
        """

        if request.files is not None:
            if request.headers["Content-Type"]:
                del request.headers["Content-Type"]

            files = {}
            for file in request.files:
                if isinstance(file, str):
                    files.update({"file": open(file, "rb")})
                elif isinstance(file, dict):
                    files.update(file)
                else:
                    files.update({"file": file})

            return requests.Request(
                method=request.method,
                url=f"{self._host}{request.path}",
                headers=request.headers,
                data=request.body,
                params=request.query,
                files=files,
            )
        # application/json
        if "Content-Type" in request.headers:
            if request.headers.get("Content-Type") in "application/json":
                return requests.Request(
                    method=request.method,
                    url=f"{self._host}{request.path}",
                    headers=request.headers,
                    json=request.body,
                    params=request.query,
                )
        # all the rest
        return requests.Request(
            method=request.method,
            url=f"{self._host}{request.path}",
            headers=request.headers,
            data=request.body,
            params=request.query,
        )

    @staticmethod
    def _to_our_response(
        response: requests.Response, error: RequestException = None
    ) -> ApiResponse:
        """
        It takes a `requests.Response` object and returns an `ApiResponse` object

        :param response: requests.Response
        :type response: requests.Response
        :return: A function that takes a requests.Response and returns an ApiResponse
        """
        try:
            body = (
                response.json()
                if response.headers.get("Content-Type") == "application/json"
                else {}
            )
        except JSONDecodeError:
            body = {}
            print(f"Can't deserialize response\n{traceback.format_exc()}")

        return ApiResponse(
            status=response.status_code,
            reason=response.reason,
            body=body,
            headers=dict(response.headers),
            elapsed=response.elapsed,
            content=response.content,
            raw=response,
        )

    def _make_request(self, request: ApiRequest, timeout: int) -> ApiResponse:
        """
        > It takes an ApiRequest object, converts it to a requests.PreparedRequest object, sends it to the server, and
        converts the response back to an ApiResponse object

        :param request: ApiRequest
        :type request: ApiRequest
        :param timeout: The number of seconds to wait for the server to send data before giving up, as a float, or a
        (connect timeout, read timeout) tuple
        :type timeout: int
        :return: An ApiResponse object
        """
        their_request = self._to_their_request(request)

        response = self._session.send(request=their_request.prepare(), timeout=timeout)
        response.raise_for_status()

        return self._to_our_response(response)

    def make_request(self, request: ApiRequest, timeout: int = None) -> ApiResponse:
        """
        > Send a request to the API and attach the request and response to the report

        :param request: ApiRequest - the request to send
        :type request: ApiRequest
        :param timeout: The timeout for the request
        :type timeout: int
        :return: ApiResponse
        """

        with self._reporter.step(
            f"\nSend {request.method} request to {self._host}{request.path}"
        ):
            if request.files:
                self._reporter.attach(
                    "ApiRequest",
                    f"{request.method} {self._host}{request.path} File to upload: {request.files}",
                    data=request,
                )
            else:
                self._reporter.attach(
                    "ApiRequest",
                    f"{request.method} {self._host}{request.path}",
                    data=request,
                )
            try:
                response = self._make_request(
                    request, timeout if timeout else self._timeout
                )
            except HTTPError as e:
                self._reporter.attach("RequestException", f"{e.response}", data=e)
                raise

            except RequestException as err:
                self._reporter.attach(
                    "RequestException", f"{err.response}", data=err
                )
                raise

            self._reporter.attach(
                "ApiResponse",
                f"{response.status} {response.reason} [{response.elapsed.seconds}s {response.elapsed.microseconds}ms]",
                data=response,
            )
            return response
