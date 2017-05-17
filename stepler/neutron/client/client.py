"""
----------------------
Neutron client wrapper
----------------------
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

from stepler.neutron.client import agent
from stepler.neutron.client import floating_ip
from stepler.neutron.client import lbaas_listener
from stepler.neutron.client import lbaas_loadbalancer
from stepler.neutron.client import lbaas_pool
from stepler.neutron.client import network
from stepler.neutron.client import port
from stepler.neutron.client import quota
from stepler.neutron.client import router
from stepler.neutron.client import security_group
from stepler.neutron.client import security_group_rule
from stepler.neutron.client import subnet


class NeutronClient(object):
    """Wrapper for python-neutronclient."""
    def __init__(self, client):
        self._rest_client = client

    @property
    def agents(self):
        return agent.AgentManager(self)

    @property
    def lbaas_listeners(self):
        return lbaas_listener.ListenerManager(self)

    @property
    def lbaas_loadbalancers(self):
        return lbaas_loadbalancer.LoadBalancerManager(self)

    @property
    def lbaas_pools(self):
        return lbaas_pool.PoolManager(self)

    @property
    def floating_ips(self):
        return floating_ip.FloatingIPManager(self)

    @property
    def networks(self):
        return network.NetworkManager(self)

    @property
    def ports(self):
        return port.PortManager(self)

    @property
    def quotas(self):
        return quota.QuotaManager(self)

    @property
    def routers(self):
        return router.RouterManager(self)

    @property
    def security_groups(self):
        return security_group.SecurityGroupManager(self)

    @property
    def security_group_rules(self):
        return security_group_rule.SecurityGroupRuleManager(self)

    @property
    def subnets(self):
        return subnet.SubnetManager(self)
