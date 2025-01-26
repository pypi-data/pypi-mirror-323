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


from typing import Dict, Tuple

from requests_toolbelt.multipart.encoder import MultipartEncoder


def get_url(base_url: str, action: str, query_map: Dict[str, str]) -> str:
    query = "&".join([f"{k}={v}" for k, v in query_map.items()])
    return f"{base_url}/api/{action}?{query}"


def create_form_file(form_data: Dict[str, bytes]) -> Tuple[str, bytes]:
    encoder = MultipartEncoder(fields={k: ("file", v) for k, v in form_data.items()})
    return encoder.content_type, encoder.to_string()


def create_form(form_data: Dict[str, str]) -> Tuple[str, bytes]:
    encoder = MultipartEncoder(fields=form_data)
    return encoder.content_type, encoder.to_string()
