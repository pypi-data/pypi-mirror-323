# Copyright 2025 The casbin Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from typing import Dict, List, Tuple, Union

import requests

from . import util


class HttpClient:
    def do(self, request):
        pass


class Response:
    def __init__(
        self, status: str, msg: str, data: Union[Dict, List], data2: Union[Dict, List]
    ):
        self.status = status
        self.msg = msg
        self.data = data
        self.data2 = data2


# Global HTTP client
client = requests.Session()


def set_http_client(http_client: HttpClient):
    global client
    client = http_client


class BaseClient:
    def __init__(self, clientId: str, clientSecret: str, endpoint: str):
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.endpoint = endpoint

    def do_get_response(self, url: str) -> Response:
        resp_bytes = self.do_get_bytes_raw_without_check(url)
        response = json.loads(resp_bytes)
        if response["status"] != "ok":
            raise Exception(response["msg"])
        return Response(
            response["status"], response["msg"], response["data"], response["data2"]
        )

    def do_get_bytes(self, url: str) -> bytes:
        response = self.do_get_response(url)
        return json.dumps(response.data).encode("utf-8")

    def do_get_bytes_raw(self, url: str) -> bytes:
        resp_bytes = self.do_get_bytes_raw_without_check(url)
        response = json.loads(resp_bytes)
        if response["status"] == "error":
            raise Exception(response["msg"])
        return resp_bytes

    def do_post(
        self,
        action: str,
        query_map: Dict[str, str],
        post_bytes: bytes,
        is_form: bool,
        is_file: bool,
    ) -> Response:
        url = util.get_url(self.endpoint, action, query_map)
        content_type, body = self.prepare_body(post_bytes, is_form, is_file)
        resp_bytes = self.do_post_bytes_raw(url, content_type, body)
        response = json.loads(resp_bytes)
        if response["status"] != "ok":
            raise Exception(response["msg"])
        return Response(
            response["status"], response["msg"], response["data"], response["data2"]
        )

    def do_post_bytes_raw(self, url: str, content_type: str, body: bytes) -> bytes:
        if not content_type:
            content_type = "text/plain;charset=UTF-8"

        headers = {"Content-Type": content_type}
        resp = client.post(
            url, headers=headers, data=body, auth=(self.clientId, self.clientSecret)
        )
        return resp.content

    def do_get_bytes_raw_without_check(self, url: str) -> bytes:
        resp = client.get(url, auth=(self.clientId, self.clientSecret))
        return resp.content

    def prepare_body(
        self, post_bytes: bytes, is_form: bool, is_file: bool
    ) -> Tuple[str, bytes]:
        if is_form:
            if is_file:
                return util.create_form_file({"file": post_bytes})
            else:
                params = json.loads(post_bytes)
                return util.create_form(params)
        else:
            return "text/plain;charset=UTF-8", post_bytes
