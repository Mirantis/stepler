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

import logging

from hamcrest import assert_that, is_not  # noqa
import pytest

from stepler import config
from stepler.nova import steps
from stepler.third_party import context
from stepler.third_party import utils

__all__ = [
    'create_server_context',
    'create_servers_context',
    'get_server_steps',
    'get_ssh_proxy_cmd',
    'server',
    'server_steps',
    'live_migration_server',
    'live_migration_servers',
    'live_migration_servers_with_volumes',
    'servers_cleanup',
    'unexpected_servers_cleanup',
]

LOGGER = logging.getLogger(__name__)
# servers which should be missed, when unexpected servers will be removed
SKIPPED_SERVERS = []


@pytest.yield_fixture
def unexpected_servers_cleanup():
    """Callable function fixture to clear unexpected servers.

    It provides cleanup before and after test. Cleanup before test is callable
    with injecton of server steps. Should be called before returning of
    instantiated server steps.
    """
    _server_steps = [None]

    def _servers_cleanup(server_steps):
        assert_that(server_steps, is_not(None))
        _server_steps[0] = server_steps  # inject server steps for finalizer
        # check=False because in best case no servers will be present
        servers = server_steps.get_servers(name_prefix=config.STEPLER_PREFIX,
                                           check=False)
        if SKIPPED_SERVERS:
            server_names = [server.name for server in SKIPPED_SERVERS]

            LOGGER.debug(
                "SKIPPED_SERVERS contains servers {!r}. They will not be "
                "removed in cleanup procedure.".format(server_names))

            servers = [server for server in servers
                       if server not in SKIPPED_SERVERS]
        if servers:
            server_steps.delete_servers(servers)

    yield _servers_cleanup

    _servers_cleanup(_server_steps[0])


@pytest.fixture(scope='session')
def get_server_steps(request, get_nova_client):
    """Callable session fixture to get server steps.

    Args:
        get_nova_client (function): function to get nova client.

    Returns:
        function: function to get server steps.
    """
    def _get_server_steps():
        return steps.ServerSteps(get_nova_client().servers)

    return _get_server_steps


@pytest.fixture
def server_steps(get_server_steps, servers_cleanup):
    """Function fixture to get server steps.

    Args:
        get_server_steps (function): function to get server steps
        servers_cleanup (function): function to cleanup servers after test

    Yields:
        ServerSteps: instantiated server steps
    """
    _server_steps = get_server_steps()
    with servers_cleanup(_server_steps):
        yield _server_steps


@pytest.fixture
def servers_cleanup(uncleanable):
    """Callable function fixture to cleanup servers after test.

    Args:
        uncleanable (AttrDict): data structure with skipped resources

    Returns:
        function: function to cleanup servers
    """
    @context.context
    def _servers_cleanup(server_steps):

        def _get_servers():
            # check=False because in best case no servers will be retrieved
            return server_steps.get_servers(
                name_prefix=config.STEPLER_PREFIX, check=False)

        server_ids_before = [server.id for server in _get_servers()]

        yield

        deleting_servers = []
        for server in _get_servers():

            if server.id not in uncleanable.server_ids:
                if server.id not in server_ids_before:

                    deleting_servers.append(server)

        server_steps.delete_servers(deleting_servers)

    return _servers_cleanup


@pytest.fixture
def create_servers_context(server_steps):
    """Function fixture to create servers inside context.

    It guarantees servers deletion after context exit.
    It should be used when ``servers`` must be deleted inside a test, and their
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
    @context.context
    def _create_servers_context(server_names, *args, **kwgs):
        servers = server_steps.create_servers(server_names=server_names,
                                              *args, **kwgs)
        yield servers
        server_steps.delete_servers(servers)

    return _create_servers_context


@pytest.fixture
def create_server_context(create_servers_context):
    """Function fixture to create server inside context.

    It guarantees server deletion after context exit.
    It should be used when ``server`` must be deleted inside a test, and its
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
    @context.context
    def _create_server_context(server_name, *args, **kwgs):
        with create_servers_context([server_name], *args, **kwgs) as servers:
            yield servers[0]

    return _create_server_context


@pytest.fixture
def server(cirros_image,
           flavor,
           security_group,
           net_subnet_router,
           server_steps):
    """Function fixture to create server with default options before test.

    Args:
        cirros_image (object): cirros image from glance
        flavor (object): nova flavor
        security_group (obj): nova security group
        net_subnet_router (tuple): neutron network, subnet, router
        server_steps (ServerSteps): instantiated server steps

    Returns:
        object: nova server
    """
    network, _, _ = net_subnet_router
    return server_steps.create_servers(image=cirros_image,
                                       flavor=flavor,
                                       networks=[network],
                                       security_groups=[security_group],
                                       username=config.CIRROS_USERNAME,
                                       password=config.CIRROS_PASSWORD)[0]


# TODO(schipiga): this fixture is rudiment of MOS. Will be changed in future.
@pytest.fixture
def get_ssh_proxy_cmd(admin_ssh_key_path,
                      ip_by_host,
                      network_steps,
                      server_steps):
    """Callable function fixture to get ssh proxy data of server.

    Args:
        admin_ssh_key_path (str): path to admin ssh key
        ip_by_host (function): function to get IP by host
        network_steps (NetworkSteps): instantiated network steps
        server_steps (ServerSteps): instantiated server steps

    Returns:
        function: function to get ssh proxy command
    """
    def _get_ssh_proxy_cmd(server, ip=None):
        # proxy command is actual for fixed IP only
        server_ips = server_steps.get_ips(server, 'fixed')
        ip_info = server_ips[ip] if ip else server_ips.values()[0]
        server_ip = ip_info['ip']
        server_mac = ip_info['mac']
        net_id = network_steps.get_network_id_by_mac(server_mac)
        dhcp_netns = "qdhcp-{}".format(net_id)
        dhcp_host = network_steps.get_dhcp_host_by_network(net_id)
        dhcp_server_ip = ip_by_host(dhcp_host)
        proxy_cmd = 'ssh -i {} root@{} ip netns exec {} netcat {} 22'.format(
            admin_ssh_key_path, dhcp_server_ip, dhcp_netns, server_ip)

        return proxy_cmd

    return _get_ssh_proxy_cmd


@pytest.fixture
def live_migration_servers(request,
                           keypair,
                           flavor,
                           security_group,
                           ubuntu_image,
                           net_subnet_router,
                           sorted_hypervisors,
                           current_project,
                           nova_create_floating_ip,
                           cinder_quota_steps,
                           hypervisor_steps,
                           volume_steps,
                           server_steps):
    """Fixture to create servers for live migration tests.

    This fixture creates max allowed count of servers and adds floating ip to
    each. It can boot servers from ubuntu image or volume with parametrization.
    Default is boot from image.

    All created resources will be deleted after test.

    Example:
        @pytest.mark.parametrized('live_migration_servers', [
                {'boot_from_volume': True},
                {'boot_from_volume': False}
            ], indirect=True)
        def test_foo(live_migration_servers):
            pass

    Args:
        request (obj): pytest SubRequest instance
        keypair (obj): keypair
        flavor (obj): flavor
        security_group (obj): security group
        ubuntu_image (obj): ubuntu image
        net_subnet_router (tuple): neutron network, subnet and router
        sorted_hypervisors (list): nova hypervisors list
        current_project (obj): current project
        nova_create_floating_ip (function): function to create floating IP
        cinder_quota_steps (obj): instantiated cinder quota steps
        hypervisor_steps (obj): instantiated hypervisor steps
        volume_steps (obj): instantiated volume steps
        server_steps (obj): instantiated server steps

    Returns:
        list: nova servers
    """
    params = getattr(request, "param", {})
    boot_from_volume = params.get('boot_from_volume', False)
    attach_volume = params.get('attach_volume', False)

    network, _, _ = net_subnet_router

    hypervisor = sorted_hypervisors[1]
    servers_count = hypervisor_steps.get_hypervisor_capacity(hypervisor,
                                                             flavor)
    volumes_quota = cinder_quota_steps.get_volumes_quota(current_project)
    if attach_volume or boot_from_volume:
        servers_count = min(servers_count, volumes_quota)
    if attach_volume and boot_from_volume:
        servers_count //= 2

    if servers_count == 0:
        pytest.skip('No valid hosts found for flavor {}'.format(flavor))

    kwargs_list = []
    if boot_from_volume:
        volume_names = utils.generate_ids(count=servers_count)
        volumes = volume_steps.create_volumes(size=5,
                                              image=ubuntu_image,
                                              names=volume_names)
        for volume in volumes:
            block_device_mapping = {'vda': volume.id}
            kwargs_list.append(
                dict(
                    image=None, block_device_mapping=block_device_mapping))
    else:
        kwargs_list = [dict(image=ubuntu_image)] * servers_count

    servers = []
    for kwargs in kwargs_list:
        server = server_steps.create_servers(
            flavor=flavor,
            keypair=keypair,
            networks=[network],
            security_groups=[security_group],
            userdata=config.INSTALL_LM_WORKLOAD_USERDATA,
            username=config.UBUNTU_USERNAME,
            availability_zone='nova:{}'.format(hypervisor.hypervisor_hostname),
            check=False,
            **kwargs)[0]
        servers.append(server)

    for server in servers:
        server_steps.check_server_status(
            server,
            expected_statuses=[config.STATUS_ACTIVE],
            transit_statuses=[config.STATUS_BUILD],
            timeout=config.SERVER_ACTIVE_TIMEOUT)

        server_steps.check_server_log_contains_record(
            server,
            config.USERDATA_DONE_MARKER,
            timeout=config.USERDATA_EXECUTING_TIMEOUT)
        server_steps.attach_floating_ip(server, nova_create_floating_ip())
    return servers


@pytest.fixture
def live_migration_servers_with_volumes(
        live_migration_servers,
        attach_volume_to_server,
        detach_volume_from_server,
        volume_steps):
    """Function fixture to create servers with volumes for LM tests.

    Args:
        live_migration_servers (ilst): list of nova servers
        attach_volume_to_server (function): function to attach volume to server
        detach_volume_from_server (function): function to detach volume from
            server
        volume_steps (obj): instantiated volume steps

    Yields:
        list: nova servers
    """
    volume_names = utils.generate_ids(count=len(live_migration_servers))
    volumes = volume_steps.create_volumes(size=1, names=volume_names)
    for server, volume in zip(live_migration_servers, volumes):
        attach_volume_to_server(server, volume)

    yield live_migration_servers

    for server, volume in zip(live_migration_servers, volumes):
        detach_volume_from_server(server, volume)


@pytest.fixture
def live_migration_server(request,
                          keypair,
                          flavor,
                          security_group,
                          nova_floating_ip,
                          ubuntu_image,
                          net_subnet_router,
                          volume_steps,
                          server_steps):
    """Fixture to create server for live migration tests.

    This fixture create server and add floating ip to it.
    It can boot server from ubuntu image or volume with parametrization.
    Default is boot from image.

    Example:
        @pytest.mark.parametrized('live_migration_server', [
                {'boot_from_volume': True},
                {'boot_from_volume': False}
            ], indirect=True)
        def test_foo(live_migration_server):
            pass

    Args:
        request (obj): pytest SubRequest instance
        keypair (obj): keypair
        flavor (obj): flavor
        security_group (obj): security group
        nova_floating_ip (obj): nova floating ip
        ubuntu_image (obj): ubuntu image
        net_subnet_router (tuple): neutron network, subnet and router
        volume_steps (obj): instantiated volume steps
        server_steps (obj): instance of ServerSteps

    Returns:
        object: nova server instance
    """
    network, _, _ = net_subnet_router

    params = getattr(request, "param", {})
    boot_from_volume = params.get('boot_from_volume', False)

    if boot_from_volume:
        volume = volume_steps.create_volumes(size=5, image=ubuntu_image)[0]

        block_device_mapping = {'vda': volume.id}
        kwargs = dict(image=None, block_device_mapping=block_device_mapping)
    else:
        kwargs = dict(image=ubuntu_image)

    server = server_steps.create_servers(
        flavor=flavor,
        keypair=keypair,
        networks=[network],
        security_groups=[security_group],
        userdata=config.INSTALL_LM_WORKLOAD_USERDATA,
        username=config.UBUNTU_USERNAME,
        **kwargs)[0]

    server_steps.check_server_log_contains_record(
        server,
        config.USERDATA_DONE_MARKER,
        timeout=config.USERDATA_EXECUTING_TIMEOUT)
    server_steps.attach_floating_ip(server, nova_floating_ip)
    return server
