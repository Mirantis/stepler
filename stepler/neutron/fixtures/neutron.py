"""
----------------
Neutron fixtures
----------------
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

from neutronclient.v2_0.client import Client
import pytest

from stepler import config
from stepler.neutron.client import client

__all__ = [
    'neutron_client',
    'get_neutron_client',
    'net_subnet_router',
    'neutron_network_type',
]


@pytest.fixture(scope="session")
def get_neutron_client(get_session):
    """Callable session fixture to get neutron client wrapper.

    Args:
        get_session (function): function to get authenticated keystone
            session

    Returns:
        function: function to get instantiated neutron client wrapper
    """
    def _get_client():
        rest_client = Client(session=get_session())
        return client.NeutronClient(rest_client)

    return _get_client


@pytest.fixture
def neutron_client(get_neutron_client):
    """Function fixture to get neutron client wrapper.

    Args:
        get_neutron_client (function): function to get instantiated neutron
            client wrapper
    """
    return get_neutron_client()


@pytest.fixture
def net_subnet_router(network, subnet, router, add_router_interfaces):
    """Function fixture to create net, subnet, router and link them.

    It deletes all created resources after test.

    Args:
        network (obj): network object
        subnet (obj): subnet object
        router (obj): router object
        add_router_interfaces (function): function to add router interfaces to
            subnets

    Returns:
        tuple: network, subnet, router objects
    """
    add_router_interfaces(router, [subnet])
    return network, subnet, router


@pytest.fixture
def neutron_network_type(os_faults_steps):
    """Function fixture to retrieve network type from neutron config.

    Network type can be VLAN or VxLAN

    Args:
        os_faults_steps (obj): instantiated os-faults steps

    Returns:
        str: network type (vlan or vxlan)
    """
    cmd = "grep -P '^tenant_network_types\s*=\s*.+vxlan' {}".format(
        config.NEUTRON_ML2_CONFIG_PATH)
    controllers = os_faults_steps.get_nodes(
        service_names=[config.NEUTRON_OVS_SERVICE])
    result = os_faults_steps.execute_cmd(controllers, cmd, check=False)
    if all(node_result.status == config.STATUS_OK for node_result in result):
        return config.NETWORK_TYPE_VXLAN
    else:
        return config.NETWORK_TYPE_VLAN
