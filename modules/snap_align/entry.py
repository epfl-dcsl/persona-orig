# Copyright 2019 École Polytechnique Fédérale de Lausanne. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from . import snap_align
from ..common import service

class CephSNAPSingleton(service.ServiceSingleton):
  class_type = snap_align.CephSnapService

class LocalSNAPSingleton(service.ServiceSingleton):
  class_type = snap_align.LocalSnapService

_singletons = [ CephSNAPSingleton(), LocalSNAPSingleton() ]
_service_map = { a.get_shortname(): a for a in _singletons }

def get_tooltip():
  return "Alignment using the SNAP aligner"

def get_services():
  return _singletons

def lookup_service(name):
  return _service_map[name]
