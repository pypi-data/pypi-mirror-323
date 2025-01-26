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

from .base import BaseClient
from .record import _RecordSDK


class CasvisorSDK(_RecordSDK):
    def __init__(
        self,
        endpoint: str,
        clientId: str,
        clientSecret: str,
        organizationName: str,
        applicationName: str,
    ):
        self.endpoint = endpoint
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.organizationName = organizationName
        self.applicationName = applicationName

        # Initialize the base client
        self.baseClient = BaseClient(clientId, clientSecret, endpoint)
