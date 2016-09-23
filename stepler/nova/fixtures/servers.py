"""
Server fixtures.

@author: schipiga@mirantis.com
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

import pytest

from stepler.nova.steps import ServerSteps
from stepler.utils import generate_ids

__all__ = [
    'create_server',
    'create_servers',
    'server',
    'server_steps',
    'ssh_proxy_data'
]


@pytest.fixture
def server_steps(nova_client):
    """Fixture to get nova steps."""
    return ServerSteps(nova_client.servers)


@pytest.yield_fixture
def create_servers(server_steps):
    """Fixture to create servers with options.

    Can be called several times during test.
    """
    servers = []

    def _create_servers(server_names, *args, **kwgs):
        _servers = server_steps.create_servers(server_names, *args, **kwgs)
        servers.extend(_servers)
        return _servers

    yield _create_servers

    if servers:
        server_steps.delete_servers(servers)


@pytest.fixture
def create_server(create_servers):
    """Fixture to create server with options.

    Can be called several times during test.
    """
    def _create_server(server_name, *args, **kwgs):
        return create_servers([server_name], *args, **kwgs)[0]

    return _create_server


@pytest.fixture
def server(create_server, image):
    """Fixture to create server with default options before test."""
    server_name = next(generate_ids('server'))
    return create_server(server_name, image)


@pytest.fixture
def ssh_proxy_data(admin_ssh_key_path, ip_by_host,
                   neutron_steps, server_steps):
    """Fixture to get ssh proxy data of server."""
    def _ssh_proxy_data(server):
        ip_info = server_steps.get_ips(server, 'fixed').values()[0]
        server_ip = ip_info['ip']
        server_mac = ip_info['mac']
        net_id = neutron_steps.network_id_by_mac(server_mac)
        dhcp_netns = "qdhcp-{}".format(net_id)
        dhcp_host = neutron_steps.dhcp_host_by_network(net_id)
        dhcp_server_ip = ip_by_host(dhcp_host)
        cmd = 'ssh -i {} root@{} ip netns exec {} netcat {} 22'.format(
            admin_ssh_key_path, dhcp_server_ip, dhcp_netns, server_ip)

        return cmd, server_ip

    return _ssh_proxy_data
