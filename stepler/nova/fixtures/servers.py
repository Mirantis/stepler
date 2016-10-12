"""
---------------
Server fixtures
---------------
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
from stepler.third_party.context import context
from stepler.third_party import ssh
from stepler.third_party.utils import generate_ids

__all__ = [
    'create_server',
    'create_server_context',
    'create_servers',
    'create_servers_context',
    'server',
    'server_steps',
    'ssh_proxy_data',
    'ssh_to_instance',
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
def create_servers_context(server_steps):
    """Fixture to create servers inside context to guarantee their deletion
    after context exit.

    Should be used when ``servers`` must be deleted inside a test, and their
    deletion can't be delegated to fixture finalization. Can be called several
    times during a test.

    Example:
        .. code:: python

           def test_something(create_servers_context):
               for i in sequence:  # sequence can't be calculated outside test
                   with create_servers_context(*args, **kwgs) as servers:
                       [server.do_something() for server in servers]

    Args:
        server_steps (stepler.nova.steps.ServerSteps): instantiated steps
            object to manipulate with ``server`` resource.

    Returns:
        function: function to use as context manager to create servers
    """
    @context
    def _create_servers_context(server_names, *args, **kwgs):
        servers = server_steps.create_servers(server_names, *args, **kwgs)
        yield servers
        server_steps.delete_servers(servers)

    return _create_servers_context


@pytest.fixture
def create_server_context(create_servers_context):
    """Fixture to create server inside context to guarantee its deletion after
    context exit.

    Should be used when ``server`` must be deleted inside a test, and its
    deletion can't be delegated to fixture finalization. Can be called several
    times during a test.

    Example:
        .. code:: python

           def test_something(create_server_context):
               for i in sequence:  # sequence can't be calculated outside test
                   with create_server_context(*args, **kwgs) as server:
                       server.do_something()

    Args:
        create_servers_context (function): context manager to create servers

    Returns:
        function: function to use as context manager to create server
    """
    @context
    def _create_server_context(server_name, *args, **kwgs):
        with create_servers_context([server_name], *args, **kwgs) as servers:
            yield servers[0]

    return _create_server_context


@pytest.fixture
def server(create_server, image):
    """Fixture to create server with default options before test."""
    server_name = next(generate_ids('server'))
    return create_server(server_name, image)


@pytest.fixture
def ssh_proxy_data(request, network_steps, server_steps):
    """Fixture to get ssh proxy data of server."""
    def _ssh_proxy_data(server, ip=None):
        server_ips = server_steps.get_ips(server)
        if ip is not None:
            try:
                ip_info = server_ips[ip]
            except KeyError:
                raise ValueError('Passed IP {!r} is not in server {!r} '
                                 'addresses ({!r})'.format(ip, server,
                                                           server_ips.keys()))
        else:
            ip_info = next(v for k, v in server_ips if v['type'] == 'fixed')
        server_ip = ip_info['ip']
        if ip_info['type'] == 'floating':
            cmd = None
        else:
            server_mac = ip_info['mac']
            net_id = network_steps.get_network_id_by_mac(server_mac)
            dhcp_netns = "qdhcp-{}".format(net_id)
            dhcp_host = network_steps.get_dhcp_host_by_network(net_id)
            ip_by_host = request.getfixturevalue('ip_by_host')
            admin_ssh_key_path = request.getfixturevalue('admin_ssh_key_path')
            dhcp_server_ip = ip_by_host(dhcp_host)
            cmd = 'ssh -i {} root@{} ip netns exec {} netcat {} 22'.format(
                admin_ssh_key_path, dhcp_server_ip, dhcp_netns, server_ip)

        return cmd, server_ip

    return _ssh_proxy_data


@pytest.fixture
def ssh_to_instance(ssh_proxy_data, server_steps):
    def _ssh_to_instance(server, ip=None):
        proxy_cmd, ip = ssh_proxy_data(server, ip)
        server_steps.check_ssh_connect(server,
                                       ip=ip,
                                       proxy_cmd=proxy_cmd,
                                       timeout=60 * 5)
        credentials = server_steps.get_server_creadentials(server)
        ssh_client = ssh.SshClient(ip,
                                   pkey=credentials.get('private_key'),
                                   username=credentials.get('username'),
                                   password=credentials.get('password'),
                                   proxy_cmd=proxy_cmd)
        return ssh_client

    return _ssh_to_instance
