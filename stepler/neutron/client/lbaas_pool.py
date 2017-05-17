"""
--------------------------
Neutron LBaaS pool manager
--------------------------
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
from stepler.neutron.client import lbaas_member


class Pool(base.Resource):

    @property
    def members(self):
        return lbaas_member.MemberManager(self.client, self['id'])


class PoolManager(base.BaseNeutronManager):
    """LBaaS pool manager."""

    NAME = "pool"
    API_NAME = 'lbaas_pool'
    _resource_class = Pool
    _allowed_protocols = ['HTTP', 'HTTPS', 'TCP']
    _allowed_algorithms = ['ROUND_ROBIN', 'LEAST_CONNECTIONS', 'SOURCE_IP']

    def create(self, protocol, lb_algorithm, **kwargs):
        if protocol not in self._allowed_protocols:
            raise ValueError(
                "protocol should be on of {}".format(self._allowed_protocols))
        if lb_algorithm not in self._allowed_algorithms:
            raise ValueError("lb_algorithm should be on of {}".format(
                self._allowed_algorithms))
        return super(PoolManager, self).create(
            protocol=protocol, lb_algorithm=lb_algorithm, **kwargs)

    @base.filter_by_project
    def find_all(self, **kwargs):
        return super(PoolManager, self).find_all(**kwargs)
