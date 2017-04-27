"""
------------------------------
Neutron LBaaS listener manager
------------------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from stepler.neutron.client import base


class Listener(base.Resource):
    pass


class ListenerManager(base.BaseNeutronManager):
    """LBaaS listener manager."""

    NAME = 'listener'
    _resource_class = Listener
    _allowed_protocols = ['HTTP', 'HTTPS', 'TCP', 'TERMINATED_HTTPS']

    @base.transform_one
    def create(self, protocol, **kwargs):
        if protocol not in self._allowed_protocols:
            raise ValueError(
                "protocol should be on of {}".format(self._allowed_protocols))
        return super(ListenerManager, self).create(protocol=protocol, **kwargs)

    @base.filter_by_project
    def find_all(self, **kwargs):
        return super(ListenerManager, self).find_all(**kwargs)
