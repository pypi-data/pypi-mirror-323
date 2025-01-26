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
from typing import Dict, List, Optional, Tuple

from . import util
from .base import BaseClient, Response


class Record:
    def __init__(
        self,
        createdTime: Optional[str] = None,
        organization: Optional[str] = None,
        clientIp: Optional[str] = None,
        user: Optional[str] = None,
        method: Optional[str] = None,
        requestUri: Optional[str] = None,
        action: Optional[str] = None,
        language: Optional[str] = None,
        object: Optional[str] = None,
        response: Optional[str] = None,
        provider: Optional[str] = None,
        block: Optional[str] = None,
        isTriggered: Optional[bool] = None,
        id: Optional[int] = None,
        owner: Optional[str] = None,
        name: Optional[str] = None,
    ):
        self.id = id
        self.owner = owner
        self.name = name
        self.createdTime = createdTime
        self.organization = organization
        self.clientIp = clientIp
        self.user = user
        self.method = method
        self.requestUri = requestUri
        self.action = action
        self.language = language
        self.object = object
        self.response = response
        self.provider = provider
        self.block = block
        self.isTriggered = isTriggered

    def to_dict(self) -> Dict:
        return self.__dict__

    @classmethod
    def from_dict(cls, data: Dict) -> "Record":
        return cls(**data)


class _RecordSDK:
    def __init__(self, base_client: BaseClient, organizationName: str):
        self.baseClient = base_client
        self.organizationName = organizationName

    def get_records(self) -> List[Record]:
        query_map = {"owner": self.organizationName}
        url = util.get_url(self.baseClient.endpoint, "get-records", query_map)
        bytes = self.baseClient.do_get_bytes(url)
        return [Record.from_dict(record) for record in json.loads(bytes)]

    def get_record(self, name: str) -> Record:
        query_map = {"id": f"{self.organizationName}/{name}"}
        url = util.get_url(self.baseClient.endpoint, "get-record", query_map)
        bytes = self.baseClient.do_get_bytes(url)
        return Record.from_dict(json.loads(bytes))

    def get_pagination_records(
        self, p: int, pageSize: int, query_map: Dict[str, str]
    ) -> Tuple[List[Record], int]:
        query_map["owner"] = self.organizationName
        query_map["p"] = str(p)
        query_map["pageSize"] = str(pageSize)
        url = util.get_url(self.baseClient.endpoint, "get-records", query_map)
        response = self.baseClient.do_get_response(url)
        return [Record.from_dict(record) for record in response.data], response.data2

    def update_record(self, record: Record) -> bool:
        _, affected = self.modify_record("update-record", record, None)
        return affected

    def add_record(self, record: Record) -> bool:
        if not record.owner:
            record.owner = self.organizationName
        if not record.organization:
            record.organization = self.organizationName
        _, affected = self.modify_record("add-record", record, None)
        return affected

    def delete_record(self, record: Record) -> bool:
        _, affected = self.modify_record("delete-record", record, None)
        return affected

    def modify_record(
        self, action: str, record: Record, columns: Optional[List[str]]
    ) -> Tuple[Response, bool]:
        query_map = {"id": f"{record.owner}/{record.name}"}
        if columns:
            query_map["columns"] = ",".join(columns)
        if not record.owner:
            record.owner = "admin"
        post_bytes = json.dumps(record.to_dict()).encode("utf-8")
        resp = self.baseClient.do_post(action, query_map, post_bytes, False, False)
        return resp, resp.data == "Affected"
