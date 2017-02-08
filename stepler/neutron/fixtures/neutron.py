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

from neutronclient.common import exceptions
from neutronclient.v2_0.client import Client
import pytest

from stepler import config
from stepler.neutron.client import client
from stepler.third_party import waiter

__all__ = [
    'neutron_client',
    'get_neutron_client',
    'net_subnet_router',
    'set_dhcp_agents_count_for_net',
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
    def _wait_client_availability(**credentials):
        rest_client = Client(session=get_session(**credentials))
        neutron_client = client.NeutronClient(rest_client)
        neutron_client.networks.find_all()
        return neutron_client

    def _get_neutron_client(**credentials):
        return waiter.wait(
            _wait_client_availability,
            kwargs=credentials,
            timeout_seconds=config.NEUTRON_AVAILABILITY_TIMEOUT,
            expected_exceptions=exceptions.NeutronClientException)

    return _get_neutron_client


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
def set_dhcp_agents_count_for_net(request,
                                  network_steps,
                                  os_faults_steps,
                                  patch_ini_file_and_restart_services):
    """Function fixture to set DHCP agents count for network.

    This fixture must be parametrized with DHCP agents count for
    each network.

    Example:
        @pytest.mark.parametrize('set_dhcp_agents_count_for_net',
                                 [1],
                                 indirect=True)
        def test_foo(set_dhcp_agents_count_for_net):
            # Will be set 1 DHCP agent for network

    Args:
        request (obj): py.test SubRequest
        network_steps (object): instantiated network steps
        os_faults_steps (object): instantiated os_faults steps
        patch_ini_file_and_restart_services (function): callable fixture to
            patch ini file and restart services
    """
    if not hasattr(request, 'param'):
        err_msg = ("set_dhcp_agents_count_for_net fixture can't be used "
                   "without parameterization.")
        raise AttributeError(err_msg)

    agents_count = int(request.param)
    nodes = os_faults_steps.get_nodes(
        service_names=[config.NEUTRON_SERVER_SERVICE])

    with patch_ini_file_and_restart_services(
            [config.NEUTRON_SERVER_SERVICE],
            file_path=config.NEUTRON_CONFIG_PATH,
            option='dhcp_agents_per_network',
            value=agents_count):
        os_faults_steps.check_service_state(
            config.NEUTRON_SERVER_SERVICE,
            nodes,
            timeout=config.SERVICE_START_TIMEOUT)
        # wait for neutron availability
        get_neutron_client()

        yield

    os_faults_steps.check_service_state(config.NEUTRON_SERVER_SERVICE,
                                        nodes,
                                        timeout=config.SERVICE_START_TIMEOUT)
    # wait for neutron availability
    get_neutron_client()
