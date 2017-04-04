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

from hamcrest import assert_that, is_not  # noqa: H401
import pytest

from stepler import config
from stepler.nova import steps
from stepler.third_party import context
from stepler.third_party import utils

__all__ = [
    'create_server_context',
    'create_servers_context',
    'cirros_server_to_rebuild',
    'get_server_steps',
    'get_ssh_proxy_cmd',
    'server',
    'server_steps',
    'servers_to_evacuate',
    'servers_with_volumes_to_evacuate',
    'live_migration_server',
    'live_migration_servers',
    'live_migration_servers_with_volumes',
    'servers_cleanup',
    'ubuntu_server',
    'ubuntu_server_to_rebuild',
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
def get_server_steps(get_nova_client):
    """Callable session fixture to get server steps.

    Args:
        get_nova_client (function): function to get nova client

    Returns:
        function: function to get server steps
    """
    def _get_server_steps(**credentials):
        return steps.ServerSteps(get_nova_client(**credentials).servers)

    return _get_server_steps


@pytest.fixture
def server_steps(get_server_steps, servers_cleanup):
    """Function fixture to get server steps.

    Args:
        get_server_steps (function): function to get server steps
        servers_cleanup (function): function to cleanup servers after test

    Returns:
        ServerSteps: instantiated server steps
    """
    return get_server_steps()


@pytest.fixture
def servers_cleanup(uncleanable, get_server_steps):
    """Function fixture to cleanup servers after test.

    Args:
        uncleanable (AttrDict): data structure with skipped resources
    """
    server_steps = get_server_steps()

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

    # we should use force deletion as teardown of this fixture can be
    # performed before fixtures which can change config file and
    # restart services
    # as result reclaim_instance_interval can be big and check of
    # ``delete_servers`` step can fail
    server_steps.delete_servers(deleting_servers, force=True)


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


@pytest.fixture
def ubuntu_server(ubuntu_image,
                  flavor,
                  keypair,
                  security_group,
                  net_subnet_router,
                  server_steps):
    """Function fixture to create ubuntu server with default options.

    Args:
        ubuntu_image (object): glance ubuntu image
        flavor (object): nova flavor
        keypair (object): nova keypair
        security_group (obj): nova security group
        net_subnet_router (tuple): neutron network, subnet, router
        server_steps (ServerSteps): instantiated server steps

    Returns:
        object: nova server
    """
    network, _, _ = net_subnet_router
    return server_steps.create_servers(image=ubuntu_image,
                                       flavor=flavor,
                                       networks=[network],
                                       security_groups=[security_group],
                                       username=config.UBUNTU_USERNAME,
                                       keypair=keypair)[0]


@pytest.fixture
def get_ssh_proxy_cmd(network_steps,
                      os_faults_steps,
                      server_steps):
    """Callable function fixture to get ssh proxy data of server.

    Args:
        network_steps (NetworkSteps): instantiated network steps
        os_faults_steps (OsFaultsSteps): initialized os-faults steps
        server_steps (ServerSteps): instantiated server steps

    Returns:
        function: function to get ssh proxy command
    """
    ssh_opts = ('-o UserKnownHostsFile=/dev/null '
                '-o StrictHostKeyChecking=no')
    if os_faults_steps.get_cloud_param_value('driver') == config.TCP_CLOUD:
        ssh_opts += ' -i {}'.format(
            os_faults_steps.get_cloud_param_value('private_key_file'))

    def _get_ssh_proxy_cmd(server, ip=None):
        # proxy command is actual for fixed IP only
        server_ips = server_steps.get_ips(server, 'fixed')
        ip_info = server_ips[ip] if ip else server_ips.values()[0]
        server_ip = ip_info['ip']
        server_mac = ip_info['mac']
        net_id = network_steps.get_network_id_by_mac(server_mac)
        dhcp_netns = "qdhcp-{}".format(net_id)
        dhcp_host = network_steps.get_dhcp_host_by_network(net_id)
        dhcp_fqdn = os_faults_steps.get_fqdn_by_host_name(dhcp_host)
        dhcp_server_ip = [
            node.ip for node in os_faults_steps.get_node(fqdns=[dhcp_fqdn])][0]
        private_key_path = os_faults_steps.get_nodes_private_key_path()
        proxy_cmd = ('ssh {ssh_opts} -i {pkey} root@{dhcp_server_ip} ip netns '
                     'exec {dhcp_netns} netcat {server_ip} 22').format(
            ssh_opts=ssh_opts,
            pkey=private_key_path,
            dhcp_server_ip=dhcp_server_ip,
            dhcp_netns=dhcp_netns,
            server_ip=server_ip)

        return proxy_cmd

    return _get_ssh_proxy_cmd


@pytest.fixture
def live_migration_servers(
        request,
        keypair,
        flavor,
        security_group,
        ubuntu_image,
        net_subnet_router,
        sorted_hypervisors,
        current_project,
        create_floating_ip,
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
        .. code:: python

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
        create_floating_ip (function): function to create floating IP
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
    servers_count = hypervisor_steps.get_hypervisor_capacity(
        hypervisor, flavor, check=False)
    volumes_quota = cinder_quota_steps.get_volumes_quota(current_project)
    if attach_volume or boot_from_volume:
        servers_count = min(servers_count, volumes_quota)
    if attach_volume and boot_from_volume:
        servers_count //= 2

    servers_count = min(servers_count, config.LIVE_MIGRATE_MAX_SERVERS_COUNT)

    if servers_count == 0:
        pytest.skip('No valid hosts found for flavor {}'.format(flavor))

    kwargs_list = []
    if boot_from_volume:
        volume_names = utils.generate_ids(count=servers_count)
        volumes = volume_steps.create_volumes(
            size=5, image=ubuntu_image, names=volume_names)
        for volume in volumes:
            block_device_mapping = {'vda': volume.id}
            kwargs_list.append(
                dict(image=None, block_device_mapping=block_device_mapping))
    else:
        kwargs_list = [dict(image=ubuntu_image)] * servers_count

    servers = []
    for kwargs_group in utils.grouper(kwargs_list,
                                      config.SERVERS_CREATE_CHUNK):
        servers_group = []
        for kwargs in kwargs_group:
            server = server_steps.create_servers(
                flavor=flavor,
                keypair=keypair,
                networks=[network],
                security_groups=[security_group],
                userdata=config.INSTALL_LM_WORKLOAD_USERDATA,
                username=config.UBUNTU_USERNAME,
                availability_zone='nova:{}'.format(hypervisor.service['host']),
                check=False,
                **kwargs)[0]
            servers_group.append(server)

        for server in servers_group:
            server_steps.check_server_status(
                server,
                expected_statuses=[config.STATUS_ACTIVE],
                transit_statuses=[config.STATUS_BUILD],
                timeout=config.SERVER_ACTIVE_TIMEOUT)

        servers.extend(servers_group)

    for server in servers:
        server_steps.check_server_log_contains_record(
            server,
            config.USERDATA_DONE_MARKER,
            timeout=config.USERDATA_EXECUTING_TIMEOUT)
        server_steps.attach_floating_ip(server, create_floating_ip())
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
                          floating_ip,
                          ubuntu_image,
                          net_subnet_router,
                          volume_steps,
                          server_steps):
    """Fixture to create server for live migration tests.

    This fixture create server and add floating ip to it.
    It can boot server from ubuntu image or volume with parametrization.
    Default is boot from image.

    Example:
        .. code:: python

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
        floating_ip (obj): floating ip
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
    server_steps.attach_floating_ip(server, floating_ip)
    return server


@pytest.fixture
def servers_to_evacuate(request,
                        cirros_image,
                        security_group,
                        flavor,
                        net_subnet_router,
                        keypair,
                        create_floating_ip,
                        hypervisor_steps,
                        volume_steps,
                        server_steps):
    """Fixture to create servers for nova evacuate tests.

    This fixture creates amount of servers defined in config file,
    schedules them against dedicated compute node and attaches floating IP to
    every created server. It can boot servers from cirros image or
    cirros-based volume with parametrization. Default is boot from image.
    All created resources will be deleted after test.

    Example:
        .. code:: python

            @pytest.mark.parametrize('servers_to_evacuate', [
                    {'boot_from_volume': True},
                    {'boot_from_volume': False}
                ], indirect=True)
            def test_foo(servers_to_evacuate):
                pass

    Args:
        request (obj): pytest SubRequest instance
        cirros_image (obj): cirros image
        security_group (obj): security group
        flavor (obj): flavor
        net_subnet_router (tuple): neutron network, subnet and router
        keypair (obj): keypair
        create_floating_ip (function): function to create floating IP
        hypervisor_steps (obj): instantiated hypervisor steps
        volume_steps (obj): instantiated volume steps
        server_steps (obj): instantiated server steps

    Returns:
        list: nova servers
    """
    network, _, _ = net_subnet_router

    params = getattr(request, "param", {})
    boot_from_volume = params.get('boot_from_volume', False)

    hypervisor = hypervisor_steps.get_hypervisors()[0]

    kwargs_list = []
    if boot_from_volume:
        volume_names = utils.generate_ids(count=config.EVACUATE_SERVERS_COUNT)
        volumes = volume_steps.create_volumes(size=5,
                                              image=cirros_image,
                                              names=volume_names)
        for volume in volumes:
            block_device_mapping = {'vda': volume.id}
            kwargs_list.append(
                dict(
                    image=None, block_device_mapping=block_device_mapping))
    else:
        kwargs_list = [dict(
            image=cirros_image)] * config.EVACUATE_SERVERS_COUNT

    servers = []
    for kwargs in kwargs_list:
        server = server_steps.create_servers(
            flavor=flavor,
            keypair=keypair,
            networks=[network],
            security_groups=[security_group],
            username=config.CIRROS_USERNAME,
            availability_zone='nova:{}'.format(hypervisor.service['host']),
            **kwargs)[0]
        servers.append(server)

    for server in servers:
        server_steps.attach_floating_ip(server, create_floating_ip())
    return servers


@pytest.fixture
def servers_with_volumes_to_evacuate(servers_to_evacuate,
                                     attach_volume_to_server,
                                     volume_steps):
    """Fixture to create servers with volumes for nova evacuate tests.

    Args:
        servers_to_evacuate (list): list of nova servers
        attach_volume_to_server (function): function to attach volume to server
        volume_steps (obj): instantiated volume steps

    Returns:
        list: nova servers with volumes attached
    """
    volume_names = utils.generate_ids(count=len(servers_to_evacuate))
    volumes = volume_steps.create_volumes(size=1, names=volume_names)
    for server, volume in zip(servers_to_evacuate, volumes):
        attach_volume_to_server(server, volume)

    return servers_to_evacuate, volumes


@pytest.fixture
def cirros_server_to_rebuild(request,
                             keypair,
                             flavor,
                             security_group,
                             cirros_image,
                             net_subnet_router,
                             volume_steps,
                             server_steps):
    """Fixture to create server for nova rebuild tests.

    This fixture creates a server which can be booted from cirros image
    or cirros-based volume with parametrization.
    Default is boot from image.

    Example:
        .. code:: python

            @pytest.mark.parametrized('cirros_server_to_rebuild', [
                    {'boot_from_volume': True},
                    {'boot_from_volume': False}
                ], indirect=True)
            def test_foo(cirros_server_to_rebuild):
                pass

    Args:
        request (obj): pytest SubRequest instance
        keypair (obj): keypair
        flavor (obj): flavor
        security_group (obj): security group
        cirros_image (obj): cirros image
        net_subnet_router (tuple): neutron network, subnet and router
        volume_steps (obj): instantiated volume steps
        server_steps (obj): instantiated server steps

    Returns:
        object: nova server
    """
    network, _, _ = net_subnet_router

    params = getattr(request, "param", {})
    boot_from_volume = params.get('boot_from_volume', False)

    if boot_from_volume:
        volume = volume_steps.create_volumes(size=5, image=cirros_image)[0]

        block_device_mapping = {'vda': volume.id}
        kwargs = dict(image=None, block_device_mapping=block_device_mapping)
    else:
        kwargs = dict(image=cirros_image)

    server = server_steps.create_servers(
        flavor=flavor,
        keypair=keypair,
        networks=[network],
        security_groups=[security_group],
        username=config.CIRROS_USERNAME,
        **kwargs)[0]

    return server


@pytest.fixture
def ubuntu_server_to_rebuild(request,
                             keypair,
                             flavor,
                             security_group,
                             ubuntu_image,
                             net_subnet_router,
                             volume_steps,
                             server_steps):
    """Fixture to create Ubuntu server for nova rebuild tests.

    In some test cases for 'nova rebuild' actions we need a proper cloud-init
    behavior (e.g. file injection operation), which cannot be guaranteed by
    cirros-based images and servers booted from them.
    This fixture creates a server which can be booted from ubuntu image
    or ubuntu-based volume with parametrization.
    Default is boot from image.

    Example:
        .. code:: python

            @pytest.mark.parametrized('ubuntu_server_to_rebuild', [
                    {'boot_from_volume': True},
                    {'boot_from_volume': False}
                ], indirect=True)
            def test_foo(ubuntu_server_to_rebuild):
                pass

    Args:
        request (obj): pytest SubRequest instance
        keypair (obj): keypair
        flavor (obj): flavor
        security_group (obj): security group
        ubuntu_image (obj): ubuntu image
        net_subnet_router (tuple): neutron network, subnet and router
        volume_steps (obj): instantiated volume steps
        server_steps (obj): instantiated server steps

    Returns:
        object: nova server
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
        username=config.UBUNTU_USERNAME,
        **kwargs)[0]

    return server
