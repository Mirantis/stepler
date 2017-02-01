"""
------------
Server steps
------------
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

import collections
import contextlib
import itertools
import os
import time

from hamcrest import (assert_that, calling, empty, equal_to, has_entries,
                      has_item, is_, is_in, is_not, less_than_or_equal_to,
                      raises, greater_than, has_key)  # noqa H301

from keystoneclient import exceptions as keystone_exceptions
from novaclient import exceptions as nova_exceptions
import paramiko

from stepler import base
from stepler import config
from stepler.third_party import arping
from stepler.third_party import chunk_serializer
from stepler.third_party import iperf
from stepler.third_party import ping
from stepler.third_party import ssh
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

__all__ = [
    'ServerSteps'
]


class ServerSteps(base.BaseSteps):
    """Nova server steps."""

    @steps_checker.step
    def create_servers(self,
                       image,
                       flavor,
                       server_names=None,
                       count=1,
                       networks=(),
                       ports=(),
                       keypair=None,
                       security_groups=None,
                       availability_zone='nova',
                       block_device_mapping=None,
                       username=None,
                       password=None,
                       userdata=None,
                       nics=None,
                       check=True):
        """Step to create servers.

        Args:
            image (object|None): image or None (to use volume)
            flavor (object): flavor
            server_names (list): names of created servers
            count (int): count of created servers, it's ignored if server_names
                is specified; one server is created if both args are missing
            networks (list): networks objects
            ports (list): ports objects
            keypair (object): keypair
            security_groups (list|tuple): security groups
            availability_zone (str): name of availability zone
            block_device_mapping (dict|None): block device mapping for servers
            username (str): username to store with server metadata
            password (str): password to store with server metadata
            userdata (str): userdata (script) to execute on instance after boot
            nics (list, optional): An ordered list of nics (dicts) to be added
                to this servers, with information about connected networks,
                fixed IPs, port etc.
            check (bool): flag whether to check step or not

        Returns:
            list: nova servers
        """
        server_names = server_names or utils.generate_ids(count=count)
        sec_groups = [s.id for s in security_groups or []]
        image_id = None if image is None else image.id
        keypair_id = None if keypair is None else keypair.id
        nics = nics or []
        for network in networks:
            nics.append({'net-id': network['id']})
        for port in ports:
            nics.append({'port-id': port['id']})

        # Store credentials to server metadata
        private_key = None if keypair is None else keypair.private_key
        credentials = {
            'username': username,
            'password': password,
            'private_key': private_key
        }
        meta = chunk_serializer.dump(credentials, config.CREDENTIALS_PREFIX)

        servers = []
        for server_name in server_names:
            server = self._client.create(
                name=server_name,
                image=image_id,
                flavor=flavor.id,
                nics=nics,
                key_name=keypair_id,
                availability_zone=availability_zone,
                security_groups=sec_groups,
                block_device_mapping=block_device_mapping,
                userdata=userdata,
                meta=meta)
            servers.append(server)

        if check:
            for server in servers:

                self.check_server_status(
                    server,
                    expected_statuses=[config.STATUS_ACTIVE],
                    transit_statuses=[config.STATUS_BUILD],
                    timeout=config.SERVER_ACTIVE_TIMEOUT)

        return servers

    @steps_checker.step
    def delete_servers(self, servers, force=False, check=True):
        """Step to delete servers.

        Args:
            servers (obj): nova servers' list
            force (bool, optional): flag whetever to run force or soft deleting
            check (bool, optional): flag whether to check step or not
        """
        if force:
            self._hard_delete_servers(servers, check)
        else:
            self._soft_delete_servers(servers, check)

    @steps_checker.step
    def get_servers(self, name_prefix=None, check=True):
        """Step to retrieve servers from nova.

        Args:
            name_prefix (str): prefix of server names to get
            check (bool): flag whether to check step or not
        Returns:
            list: server list
        """
        servers = self._client.list()

        if name_prefix:
            servers = [server for server in servers
                       if (server.name or '').startswith(name_prefix)]

        if check:
            assert_that(servers, is_not(empty()))

        return servers

    @steps_checker.step
    def check_server_presence(self, server, present=True, timeout=0):
        """Check-step to check server presence.

        Args:
            server (object): nova server
            present (bool): flag to check is server present or absent
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """

        def predicate():
            try:
                server.get()
                return present
            except nova_exceptions.NotFound:
                return not present

        waiter.wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def check_server_status(self,
                            server,
                            expected_statuses,
                            transit_statuses=(),
                            timeout=0):
        """Verify step to check server status.

        Args:
            server (object): nova server to check its status
            expected_statuses (list): expected server statuses
            transit_statuses (iterable): allowed transit statuses
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_server_status():
            server.get()
            return waiter.expect_that(server.status.lower(),
                                      is_not(is_in(transit_statuses)))

        waiter.wait(_check_server_status, timeout_seconds=timeout)
        err_msg = self._error_message(server)
        assert_that(server.status.lower(), is_in(expected_statuses), err_msg)

    @steps_checker.step
    def get_server_credentials(self, server):
        """Step to retrieve server credentials.

        Args:
            server (object): nova server object
        Returns:
            dict: dict with username, password and (optionally) private_key
        """
        server.get()
        meta = server.metadata
        return chunk_serializer.load(meta, config.CREDENTIALS_PREFIX)

    @steps_checker.step
    def get_server_ssh(self, server, ip=None, proxy_cmd=None, credentials=None,
                       ssh_timeout=config.SSH_CLIENT_TIMEOUT, check=True):
        """Step to get SSH connect to server.

        Args:
            server (object): nova server
            ip (str): ip of server
            proxy_cmd (str): ssh client proxy command
            credentials (dict): dict with username, password and private_key
            ssh_timeout (int): timeout to establish ssh connection
            check (bool): flag whether to check step or not

        Returns:
            ssh.SshClient: instantiated ssh client to server ip

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        if not ip:
            if not proxy_cmd:  # server is available via floating IP directly
                ip = self.get_ips(server, 'floating').keys()[0]
            else:
                ip = self.get_ips(server, 'fixed').keys()[0]

        if credentials is None:
            credentials = self.get_server_credentials(server)

        server_ssh = ssh.SshClient(ip,
                                   pkey=credentials.get('private_key'),
                                   username=credentials.get('username'),
                                   password=credentials.get('password'),
                                   timeout=ssh_timeout,
                                   proxy_cmd=proxy_cmd)
        if check:
            self.check_ssh_connection_establishment(
                server_ssh, timeout=config.SSH_CONNECT_TIMEOUT)

        return server_ssh

    @steps_checker.step
    def check_ssh_connection_establishment(self, server_ssh, must_work=True,
                                           timeout=0):
        """Step to check that ssh connection can be established.

        Args:
            server_ssh (ssh.SshClient): ssh connection
            must_work (bool, optional): flag whether 'server_ssh' should be
                able to connect or not
            timeout (int, optional): seconds to wait a result of check

        Raises:
            RuntimeError: if `server_ssh` is not closed
            TimeoutExpired: if check failed after timeout
        """
        err_msg = "Invalid SSH connection status to {}".format(server_ssh)
        if timeout:
            err_msg += " during polling time {} second(s)".format(timeout)

        def _check_ssh_connection_establishment():
            return waiter.expect_that(
                server_ssh.check(), equal_to(must_work), err_msg)

        waiter.wait(_check_ssh_connection_establishment,
                    timeout_seconds=timeout)

    @steps_checker.step
    def check_active_ssh_connection(self, server_ssh, must_operable=True,
                                    timeout=0):
        """Step to check active ssh connection.

        Args:
            server_ssh (ssh.SshClient): ssh connection
            must_operable (bool, optional): flag whether `server_ssh` should be
                operable or not
            timeout (int): seconds to wait a result of check

        Raises:
            RuntimeError: if `server_ssh` is closed
            TimeoutExpired: if check failed after timeout
        """
        if server_ssh.closed:
            raise RuntimeError('`server_ssh` passed to check is closed.')

        def _check_active_ssh_connection():
            try:
                server_ssh.execute('hostname', timeout=timeout)
                operable = True
            except paramiko.SSHException:
                operable = False
            return waiter.expect_that(operable, equal_to(must_operable))

        waiter.wait(_check_active_ssh_connection, timeout_seconds=timeout)

    @steps_checker.step
    def execute_commands(self,
                         server,
                         commands,
                         with_sudo=False,
                         command_timeout=config.SSH_COMMAND_TIMEOUT,
                         check=True):
        """Step to execute commands on server via SSH.

        Args:
            server (object): nova server
            commands (list): sequence of commands to execute on server
            with_sudo (bool, optional): flag whether to execute commands
                with sudo or not
            command_timeout (int): seconds to wait executing command will be
                finished
            check (bool, optional): flag whether to check step or not

        Raises:
            RuntimeError: if check failed

        Returns:
            str: result of last command from sequence
        """
        with self.get_server_ssh(server) as server_ssh:
            for command in commands:

                if with_sudo:
                    with server_ssh.sudo():
                        result = server_ssh.execute(command,
                                                    timeout=command_timeout)
                else:
                    result = server_ssh.execute(command,
                                                timeout=command_timeout)
                if check:
                    result.check_exit_code()

        return result.stdout

    @steps_checker.step
    def attach_floating_ip(self, server, floating_ip, check=True):
        """Step to attach floating IP to server.

        Args:
            server (object): nova server
            floating_ip (object): floating IP
            check (bool, optional): flag whether to check step or not

        Raises:
            AssertionError: if floating IP is not attached to a server
        """
        self._client.add_floating_ip(server, floating_ip)

        if check:
            server.get()
            floating_ips = self.get_ips(server, 'floating').keys()
            assert_that(floating_ips,
                        has_item(floating_ip.ip),
                        "Floating IP not in a list of server's IPs.")

    @steps_checker.step
    def detach_floating_ip(self, server, floating_ip, check=True):
        """Step to detach floating IP from server.

        Args:
            server (object): nova server
            floating_ip (object): floating IP
            check (bool, optional): flag whether to check step or not

        Raises:
            AssertionError: if floating IP is still attached to a server
        """
        self._client.remove_floating_ip(server, floating_ip)

        if check:
            server.get()
            floating_ips = self.get_ips(server, 'floating', check=False).keys()
            assert_that(floating_ips,
                        is_not(has_item(floating_ip.ip)),
                        "Floating IP still in a list of server's IPs.")

    @steps_checker.step
    def attach_fixed_ip(self, server, network_id, check=True):
        """Step to attach fixed IP from provided network to provided server.

        Args:
            server (object): nova server to attach fixed ip
            network_id (str): the ID of the network the IP should be on
            check (bool): flag whether to check step or not

        Returns:
            str:  IF check=True, returns new fixed IP address
            None: IF check=False

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        ips_before_attach = self.get_ips(server, 'fixed', check=False).keys()
        server.add_fixed_ip(network_id)

        if check:
            def _check_fixed_ip_attached():
                server.get()
                ips_after_attach = self.get_ips(server, 'fixed').keys()
                return waiter.expect_that(len(ips_after_attach),
                                          equal_to(len(ips_before_attach) + 1))

            waiter.wait(_check_fixed_ip_attached,
                        timeout_seconds=config.SERVER_UPDATE_TIMEOUT)

            ips_after_attach = self.get_ips(server, 'fixed').keys()
            return (set(ips_after_attach) - set(ips_before_attach)).pop()

    @steps_checker.step
    def detach_fixed_ip(self, server, fixed_ip=None, check=True):
        """Step to detach provided fixed IP from provided server.

        Args:
            server (object): nova server to delete fixed ip
            fixed_ip (str): Fixed IP address
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        if not fixed_ip:
            fixed_ip = self.get_ips(server, 'fixed').keys()[0]

        self._client.remove_fixed_ip(server.id, fixed_ip)

        if check:

            def _check_detach_fixed_ip():
                server.get()
                fixed_ips = self.get_ips(server, 'fixed').keys()
                return waiter.expect_that(fixed_ip, is_not(is_in(fixed_ips)))

            waiter.wait(_check_detach_fixed_ip,
                        timeout_seconds=config.SERVER_UPDATE_TIMEOUT)

    @steps_checker.step
    def check_server_doesnot_detach_unattached_fixed_ip(
            self, server, unattached_fixed_ip):
        """Step to check that server will raise exception if we try to detach
            not attached to it fixed IP.

        Args:
            server (object): nova server to delete fixed ip
            unattached_fixed_ip (str): Unattached Fixed IP address

        Raises:
            AssertionError: if error didn't raise
        """
        # TODO(akoryaging): Fill when error will be implemented in Bug
        # https://bugs.launchpad.net/nova/+bug/1534186
        exception_message = ''

        # TODO(akoryaging): Specify Nova exception when it will be implemented
        assert_that(
            calling(self.detach_fixed_ip).with_args(
                server=server, fixed_ip=unattached_fixed_ip, check=False),
            raises(Exception, exception_message))

    @steps_checker.step
    def get_ips(self, server, ip_type=None, check=True):
        """Step to get server IPs.

        Args:
            server (object): nova server
            ip_type (str, optional): type of IP to filter IPs
            check (bool, optional): flag whether to check step or not

        Returns:
            dict: Retrieved IPs.

        Raises:
            AssertionError: If no retrieved IPs.
        """
        server.get()
        ips = {}
        for net_name, net_info in server.addresses.items():
            for net in net_info:
                ips[net['addr']] = {
                    'type': net['OS-EXT-IPS:type'],
                    'mac': net['OS-EXT-IPS-MAC:mac_addr'],
                    'net': net_name,
                    'ip': net['addr']
                }
        if ip_type:
            ips = {
                key: val
                for key, val in ips.items() if val['type'] == ip_type
            }

        if check:
            assert_that(ips, is_not(empty()))

        return ips

    @steps_checker.step
    def check_server_ip(self, server, ip, must_present=True, timeout=0):
        """Step to check that server has (or not) IP address.

        Args:
            server (object): nova server
            ip (str): ip address
            must_present (bool, optional): flag whether server should contain
                ip or not
            timeout (int, optional): seconds to wait result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_server_ip():
            matcher = has_key(ip)
            if not must_present:
                matcher = is_not(matcher)
            return waiter.expect_that(self.get_ips(server, check=False),
                                      matcher)

        waiter.wait(_check_server_ip, timeout_seconds=timeout)

    @steps_checker.step
    def get_fixed_ip(self, server, check=True):
        """Step to get one server fixed IP for the server.

        Args:
            server (object): nova server
            check (bool, optional): flag whether to check step or not

        Returns:
            str: retrieved fixed IP

        Raises:
            AssertionError: if no retrieved IPs
        """
        ip = next(iter(self.get_ips(server, config.FIXED_IP, check=check)))
        return ip

    @steps_checker.step
    def get_floating_ip(self, server, check=True):
        """Step to get one server floating IP for the server.

        Args:
            server (object): nova server
            check (bool, optional): flag whether to check step or not

        Returns:
            str: retrieved floating IP

        Raises:
            AssertionError: if no retrieved IPs
        """
        ip = next(iter(self.get_ips(server, config.FLOATING_IP, check=check)))
        return ip

    @steps_checker.step
    def check_dhcp_on_cirros_server(self, cirros_server):
        """Step to check DHCP on cirros server.

        Args:
            cirros_server (object): nova server

        Raises:
            TimeoutExpired: if check failed after ssh timeout
        """
        cmd = "sudo -i cirros-dhcpc up eth0"

        with self.get_server_ssh(cirros_server) as server_ssh:
            server_ssh.check_call(cmd)

    @steps_checker.step
    def check_ping_for_ip(self,
                          ip_to_ping,
                          remote_from=None,
                          ping_count=3,
                          timeout=0):
        """Verify step to check ping for ip from remote or local host.

        Args:
            ip_to_ping (str): nova server to ping its floating ip
            remote_from (object|None): instance of
                stepler.third_party.ssh.SshClient. If None - ping executing
                from local host.
            ping_count (int): count of attempts to ping
            timeout (int): seconds to wait for success ping

        Raises:
            TimeoutExpired: if check failed after timeout
        """

        def predicate():
            result = ping.Pinger(
                ip_to_ping, remote=remote_from).ping(count=ping_count)
            return result.loss == 0

        waiter.wait(predicate, timeout_seconds=timeout,
                    expected_exceptions=EOFError)

    @steps_checker.step
    def check_ping_to_server_floating(self, server, timeout=0):
        """Verify step to check ping to server floating ip address.

        Each instance has a private, fixed IP address and can also have
        a public, or floating IP address. Private IP addresses are used for
        communication between instances, and public addresses are used for
        communication with networks outside the cloud, including the Internet.

        Args:
            server (object): nova server to ping its floating ip
            timeout (int): seconds to wait for result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        floating_ip = self.get_ips(server, 'floating').keys()[0]
        self.check_ping_for_ip(floating_ip, timeout=timeout)

    def _parse_ping_plan(self, ping_plan):
        """Parse ping plan dict.

        This function replaces servers to be pinged with required ips
        in ping plan dictionary.
        Example of ping plan dict parameter:
            {
                server1: ['8.8.8.8', (server2, config.FLOATING_IP),
                          server3]
                server2: [(server1, config.FLOATING_IP),
                          (server3, config.FLOATING_IP)]
                server3: ['8.8.8.8', (server2, config.FLOATING_IP),
                          server1]
            }

        Args:
            ping_plan (dict): servers and lists of
                ips/tuples(server, type)/servers to ping

        Returns:
            dict: servers and lists of ips to ping
        """
        parsed_ping_plan = {}
        for server_from, objects_to_ping in ping_plan.items():
            ips_list = []
            for object_to_ping in objects_to_ping:
                if isinstance(object_to_ping, (list, tuple)):
                    server_to_ping, ip_type = object_to_ping
                    ips = self.get_ips(server_to_ping, ip_type=ip_type)
                    ips_list.extend(ips)
                elif hasattr(object_to_ping, 'addresses'):
                    server_to_ping = object_to_ping
                    ips = self.get_ips(server_to_ping)
                    ips_list.extend(ips)
                else:
                    ips_list.append(object_to_ping)
            parsed_ping_plan[server_from] = ips_list
        return parsed_ping_plan

    @steps_checker.step
    def check_ping_by_plan(self, ping_plan, timeout=0):
        """Step to check ping using ping plan dict.

        Args:
            ping_plan (dict): servers and lists of
                ips/tuples(server, ip_type)/servers to ping
            timeout (int): seconds to wait for result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        parsed_ping_plan = self._parse_ping_plan(ping_plan)
        for server, ips in parsed_ping_plan.items():
            floating_ip = self.get_ips(server, config.FLOATING_IP).keys()[0]

            with self.get_server_ssh(server, ip=floating_ip) as server_ssh:
                for ip in ips:
                    self.check_ping_for_ip(ip,
                                           remote_from=server_ssh,
                                           timeout=timeout)

    def _get_ping_plan_for_servers(self, servers, ip_types):
        """Get dict which contains ip list to ping for all servers"""
        ping_plan = collections.defaultdict(list)
        for server1, server2 in itertools.permutations(servers, 2):
            for ip_type in ip_types:
                ips = self.get_ips(server2, ip_type=ip_type)
                ping_plan[server1].extend(ips)
        return ping_plan

    @steps_checker.step
    def check_ping_between_servers_via_floating(self,
                                                servers,
                                                ip_types=(config.FLOATING_IP,
                                                          config.FIXED_IP),
                                                timeout=0):
        """Step to check ping from each server to all other servers.

        This function uses floating ips of servers to connect to them
        and then send pings to other servers according to 'ip_types'
        parameter.

        Args:
            servers (list): nova servers to check ping between them
            ip_types (tuple): types of ip addresses which should be pinged
            timeout (int): seconds to wait for result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        ping_plan = self._get_ping_plan_for_servers(servers, ip_types)
        self.check_ping_by_plan(ping_plan, timeout=timeout)

    @steps_checker.step
    def live_migrate(self, servers, host=None, block_migration=True,
                     check=True):
        """Step to live migrate nova servers.

        Args:
            servers (list): nova servers to migrate
            host (str): hypervisor's hostname to migrate to
            block_migration (bool): should nova use block or true live
                migration
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        old_hosts = []
        for server in servers:
            server.get()
            old_hosts.append(getattr(server, 'OS-EXT-SRV-ATTR:host'))
            server.live_migrate(host=host, block_migration=block_migration)

        if check:
            for server, old_host in zip(servers, old_hosts):
                self.check_server_status(
                    server,
                    expected_statuses=[config.STATUS_ACTIVE],
                    transit_statuses=[config.STATUS_MIGRATING],
                    timeout=config.LIVE_MIGRATE_TIMEOUT)
                if host is not None:
                    self.check_instance_hypervisor_hostname(server, host)
                else:
                    self.check_instance_hypervisor_hostname(
                        server, old_host, equal=False)

    @steps_checker.step
    def migrate_servers(self, servers, check=True):
        """Step to migrate servers

        Args:
            servers (list): nova servers to migrate
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        old_hosts = {}
        for server in servers:
            server.get()
            old_hosts[server.id] = getattr(server, 'OS-EXT-SRV-ATTR:host')
            server.migrate()

        if check:
            for server in servers:

                self.check_server_status(
                    server,
                    expected_statuses=[config.STATUS_VERIFY_RESIZE],
                    transit_statuses=[config.STATUS_RESIZE],
                    timeout=config.VERIFY_RESIZE_TIMEOUT)

                self.check_instance_hypervisor_hostname(
                    server,
                    old_hosts[server.id],
                    equal=False,
                    timeout=config.LIVE_MIGRATE_TIMEOUT)

    @steps_checker.step
    def confirm_resize_servers(self, servers, check=True):
        """Step to confirm resize for servers

        Args:
            servers (list): nova servers to confirm resize
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        for server in servers:
            server.confirm_resize()

        if check:
            for server in servers:

                self.check_server_status(
                    server,
                    expected_statuses=[config.STATUS_ACTIVE],
                    transit_statuses=[config.STATUS_VERIFY_RESIZE],
                    timeout=config.SERVER_ACTIVE_TIMEOUT)

    @steps_checker.step
    def check_instance_hypervisor_hostname(self,
                                           server,
                                           host,
                                           equal=True,
                                           timeout=0):
        """Verify step to check that server's hypervisor hostname.

        Args:
            server (object): nova server to check hypervisor hostname
            host (str): name of hypervisor hostname to compare with
                server's hypervisor
            equal (bool): flag whether servers's hypervisor hostname should be
                equal to `hostname` or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """

        def predicate():
            server.get()
            server_host = getattr(server, 'OS-EXT-SRV-ATTR:host')
            return equal == (server_host == host)

        waiter.wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    @contextlib.contextmanager
    def check_ping_loss_context(self, ip_to_ping, max_loss=0, server_ssh=None,
                                connect_restore_timeout=0):
        """Step to check that ping losses inside CM is less than max_loss.

        Args:
            ip_to_ping (str): ip address to ping
            max_loss (int): maximum allowed pings loss
            server_ssh (obj, optional): instance of
                stepler.third_party.ssh.SshClient. If None - ping will be run
                from local machine
            connect_restore_timeout (int, optional): time in seconds to wait
                for connection to be restored before CM exit

        No Longer Raises:
            AssertionError: if ping loss is greater than `max_loss`
        """
        with ping.Pinger(ip_to_ping, remote=server_ssh) as result:
            yield
            self.check_ping_for_ip(ip_to_ping, remote_from=server_ssh,
                                   timeout=connect_restore_timeout)
        assert_that(result.loss, less_than_or_equal_to(max_loss))

    @steps_checker.step
    @contextlib.contextmanager
    def check_no_ping_context(self, ip_to_ping, server_ssh=None):
        """Step to check that ping is not success inside CM.

        Args:
            ip_to_ping (str): ip address to ping
            server_ssh (obj, optional): instance of
                stepler.third_party.ssh.SshClient. If None - ping will be run
                from local machine

        Raises:
            AssertionError: if ping received is not equal to 0
        """
        with ping.Pinger(ip_to_ping, remote=server_ssh) as result:
            yield
        assert_that(result.received, equal_to(0))

    @steps_checker.step
    @contextlib.contextmanager
    def check_fixed_id_ping_loss_context(self,
                                         ip_to_ping,
                                         icmp_id,
                                         server,
                                         max_loss=0):
        """Step to check that ping losses inside CM is less than max_loss.

        Note:
            This method required ping binary which supports icmp_id parameter.

        Args:
            ip_to_ping (str): ip address to ping
            icmp_id (int): desired id of icmp packets
            server (obj): nova server
            max_loss (int): maximum allowed pings loss

        Raises:
            AssertionError: if ping loss is greater than `max_loss`
        """
        with self.get_server_ssh(server) as server_ssh:
            with ping.FixedIDPinger(
                    ip_to_ping,
                    remote=server_ssh,
                    icmp_id=icmp_id,
                    command_path=config.CUSTOM_PING_COMMAND_PATH) as result:
                yield

        assert_that(result.loss, less_than_or_equal_to(max_loss))

    @steps_checker.step
    @contextlib.contextmanager
    def check_no_fixed_id_ping_context(self, ip_to_ping, icmp_id, server):
        """Step to check that ping is not success inside CM.

        Note:
            This method required ping binary which supports icmp_id parameter.

        Args:
            ip_to_ping (str): ip address to ping
            icmp_id (int): desired id of icmp packets
            server (obj): nova server

        Raises:
            AssertionError: if ping received is not equal to 0
        """
        with self.get_server_ssh(server) as server_ssh:
            with ping.FixedIDPinger(
                    ip_to_ping,
                    remote=server_ssh,
                    icmp_id=icmp_id,
                    command_path=config.CUSTOM_PING_COMMAND_PATH) as result:
                yield
        assert_that(result.received, equal_to(0))

    @steps_checker.step
    def check_no_arping_for_ip(self, server_ssh, ip, iface="eth0", count=1):
        """Verify step to check arping for ip.

        Args:
            server_ssh (SshClient): instance of ssh client
            ip (str): ip address to ping
            iface (str, optional): name of interface to arping
            count (int, optional): count of packets to send

        Raises:
            AssertionError: if some of packets are unperlied
        """
        with arping.arping(ip, iface=iface,
                           remote=server_ssh, count=count) as result:
            pass
        assert_that(result, has_entries(sent=greater_than(0), received=0))

    @steps_checker.step
    @contextlib.contextmanager
    def check_arping_loss_context(self, server_ssh, ip, iface='eth0',
                                  max_loss=0):
        """Step to check that arping losses inside CM is less than max_loss.

        Args:
            server_ssh (SshClient): instance of ssh client
            ip (str): ip address to ping
            iface (str, optional): name of interface to arping
            max_loss (int): maximum allowed pings loss

        Raises:
            AssertionError: if ping loss is greater than `max_loss`
        """
        with arping.arping(ip, iface=iface, remote=server_ssh) as result:
            yield
        assert_that(result['sent'] - result['received'],
                    less_than_or_equal_to(max_loss))

    @steps_checker.step
    def generate_server_memory_workload(self,
                                        remote,
                                        vm_bytes='5M',
                                        check=True):
        """Step to start server memory workload.

        Args:
            remote (object): instance of stepler.third_party.ssh.SshClient
            vm_bytes (str): malloc `vm_bytes` bytes per vm worker
            check (bool): flag whether to check step or not
        """
        pid = remote.background_call(
            'stress --vm-bytes {} --vm-keep -m 1'.format(vm_bytes))
        if check:
            assert_that(pid, is_not(None))

    @steps_checker.step
    def generate_server_cpu_workload(self, remote, check=True):
        """Step to start server CPU workload.

        Args:
            remote (object): instance of stepler.third_party.ssh.SshClient
            check (bool): flag whether to check step or not
        Raises:
            Exception: if command exit code is not 0
        """
        remote.check_call('cpulimit -b -l 50 -- gzip -9 '
                          '< /dev/urandom > /dev/null')
        if check:
            remote.check_process_present('cpulimit')

    @steps_checker.step
    def generate_server_disk_workload(self, remote, check=True):
        """Step to start server disk workload.

        This step makes about 95% load on disk.

        Args:
            remote (object): instance of stepler.third_party.ssh.SshClient
            check (bool): flag whether to check step or not
        Raises:
            Exception: if command exit code is not 0
        """
        # To avoid infinite loop, count of workers to stress is limited to 3.
        # This value is suitable for most cases.
        for i in range(1, 4):
            remote.kill_process('stress')
            remote.background_call('stress --hdd {}'.format(i))
            # Sleep to make iostat data updated
            time.sleep(5)
            result = remote.check_call(
                "iostat -d -x -y 5 1 | grep -m1 '[hsv]d[abc]' | "
                "awk '{print $14}'")
            if float(result.stdout) > 95:
                break

        if check:
            remote.check_process_present('stress')

    @steps_checker.step
    def server_network_listen(self, remote, port=5010, check=True):
        """Step to start server TCP connection listening.

        Args:
            remote (object): instance of stepler.third_party.ssh.SshClient
            port (int): port to send traffic
            check (bool): flag whether to check step or not
        """
        pid = remote.background_call('nc -k -l {}'.format(port))

        if check:
            assert_that(pid, is_not(None))

    @steps_checker.step
    def check_server_log_contains_record(self, server, substring, timeout=0):
        """Verify step to check server log contains substring.

        Args:
            server (object): nova server
            substring (str): substring to match
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """

        def predicate():
            server.get()
            console = server.get_console_output()
            return substring in console

        waiter.wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def create_timestamps_on_root_and_ephemeral_disks(self,
                                                      server_ssh,
                                                      timestamp,
                                                      check=True):
        """Step to create timestamp on root and ephemeral disks

        Args:
            server_ssh (ssh.SshClient): ssh connection to nova server
            timestamp (str): timestamp to store on files
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if timestamp on root and ephemeral are not equal
        """
        with server_ssh.sudo():
            server_ssh.check_call(
                'echo "{timestamp}" | '
                'tee "{root_ts_file}" "{ephemeral_ts_file}"'.format(
                    timestamp=timestamp,
                    root_ts_file=config.DISK_TIMESTAMP_FILE,
                    ephemeral_ts_file=config.DISK_TIMESTAMP_FILE_FULL_PATH))
        if check:
            self.check_timestamps_on_root_and_ephemeral_disks(server_ssh,
                                                              timestamp)

    @steps_checker.step
    def check_timestamps_on_root_and_ephemeral_disks(self, server_ssh,
                                                     timestamp):
        """Verify step to check timestamp on root and ephemeral disks

        Args:
            server_ssh (ssh.SshClient): ssh connection to nova server
            timestamp (str): timestamp to check

        Raises:
            AssertionError: if timestamp on root and ephemeral are not equal
        """
        with server_ssh.sudo():
            root_result = server_ssh.check_call('cat "{root_ts_file}"'.format(
                root_ts_file=config.DISK_TIMESTAMP_FILE))

            ephemeral_result = server_ssh.check_call(
                'cat "{ephemeral_ts_file}"'.format(
                    ephemeral_ts_file=config.DISK_TIMESTAMP_FILE_FULL_PATH))

        assert_that(root_result.stdout, equal_to(ephemeral_result.stdout))
        assert_that(timestamp, equal_to(root_result.stdout))

    @steps_checker.step
    def create_empty_file_on_server(self, server_ssh, file_dir, check=True):
        """Step to create empty file on the server.

        Args:
            server_ssh (ssh.SshClient): ssh connection to nova server
            file_dir (str): directory to create file
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        file_path = os.path.join(file_dir, next(utils.generate_ids()))
        with server_ssh.sudo():
            server_ssh.check_call('touch ' + file_path)

        if check:
            self.check_files_presence_for_fs(server_ssh, file_dir)

    @steps_checker.step
    def get_block_device_by_mount(self, server_ssh, fs_path, check=True):
        """Step to retrieve block device which is mounted to the path.

        Args:
            server_ssh (ssh.SshClient): ssh connection to nova server
            fs_path (str): fs path to find block device
            check (bool): flag whether to check step or not

        Returns:
            str: device for fs_path

        Raises:
            AssertionError: if check failed
        """
        with server_ssh.sudo():
            cmd_result = server_ssh.check_call('cat /proc/mounts')

        fs_dev = None
        for row in cmd_result.stdout.split('\n'):
            cells = row.split()
            dev, mount_point = cells[:2]
            if mount_point == fs_path and dev.startswith('/dev'):
                fs_dev = dev
                break

        if check:
            assert_that(fs_dev, is_not(None))

        return fs_dev

    @steps_checker.step
    def unmount_fs_for_server(self, server_ssh, fs_path, check=True):
        """Step to unmount fs for server.

        Args:
            server_ssh (ssh.SshClient): ssh connection to nova server
            fs_path (str): fs path to unmount
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        fs_dev = self.get_block_device_by_mount(server_ssh, fs_path)
        with server_ssh.sudo():
            cmd = 'umount ' + fs_dev
            server_ssh.check_call(cmd)

        if check:
            device = self.get_block_device_by_mount(server_ssh, fs_path,
                                                    check=False)
            assert_that(device, is_(None))

    @steps_checker.step
    def create_qcow_image_for_server(self, server_ssh, eph_dev,
                                     root_dev, image_size, check=True):
        """Step to create qcow image for server.

        Args:
            server_ssh (ssh.SshClient): ssh connection to nova server
            eph_dev (str): ephemeral device
            root_dev (str): root device
            image_size (str): image size
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        with server_ssh.sudo():
            cmd = ('qemu-img create -f qcow2'
                   ' -o backing_file={host_dev},backing_fmt=raw '
                   '{eph_dev} {size}').format(eph_dev=eph_dev,
                                              host_dev=root_dev,
                                              size=image_size)
            server_ssh.check_call(cmd)

        if check:
            self.check_qcow_image_for_server(server_ssh, eph_dev)

    @steps_checker.step
    def check_qcow_image_for_server(self, server_ssh, filename):
        """Step to check that qcow image exists.

        Args:
            server_ssh (ssh.SshClient): ssh connection to nova server
            filename (str): name of image to check

        Raises:
            AssertionError: if check failed
        """
        with server_ssh.sudo():
            cmd = 'qemu-img info -f qcow2 {0}'.format(filename)
            cmd_result = server_ssh.check_call(cmd)

        assert_that('image: ' + filename, is_in(cmd_result.stdout))

    @steps_checker.step
    def check_files_presence_for_fs(self, server_ssh, fs_path,
                                    must_present=True):
        """Verify step to check that fs doesn't contain any files.

        Args:
            server_ssh (ssh.SshClient): ssh connection to nova server
            fs_path (str): fs path to check
            must_present (bool): flag whether fs should have any files or not

        Raises:
            AssertionError: if check failed
        """
        with server_ssh.sudo():
            cmd_result = server_ssh.check_call('ls ' + fs_path)

        if must_present:
            assert_that(cmd_result.stdout, is_not(empty()))
        else:
            assert_that(cmd_result.stdout, is_(empty()))

    @steps_checker.step
    def restore_server(self, server, check=True):
        """Step to restore soft-deleted server.

        Args:
            server (object): nova server
            check (bool): flag whether to check step or not
        """
        server.restore()

        if check:
            self.check_server_presence(server, present=True, timeout=180)

    @steps_checker.step
    def check_metadata_presence(
            self, server, custom_meta, present=True, timeout=0):
        """Step to check if server's metadata contains OR NOT contains
        provided values.

        Args:
            server (object): nova server
            custom_meta (dict): data, which presence should be checked in
                                server's metadata.
                                Like: {'key': 'stepler_test'}
            present (bool): flag to check if provided data should OR
                             should NOT present in server's metadata.
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        matcher = has_entries(custom_meta)
        if not present:
            matcher = is_not(matcher)

        def predicate():
            server.get()
            return waiter.expect_that(server.metadata, matcher)

        waiter.wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def pause_server(self, server, check=True):
        """Step to pause nova server.

        Args:
            server (object): nova server to pause
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        server.pause()

        if check:
            self.check_server_status(
                server,
                expected_statuses=[config.STATUS_PAUSED],
                transit_statuses=[config.STATUS_ACTIVE,
                                  config.STATUS_PAUSING],
                timeout=config.SERVER_UPDATE_TIMEOUT)

    @steps_checker.step
    def rebuild_server(self, server, image, check=True, **kwargs):
        """Step to rebuild nova server.

        Args:
            server (object): nova server to rebuild
            image (object): image used for server rebuild
            check (bool): flag whether to check step or not
            kwargs: Additional filters to pass

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        server.rebuild(image, **kwargs)

        if check:
            self.check_server_status(
                server,
                expected_statuses=[config.STATUS_ACTIVE],
                transit_statuses=[config.STATUS_REBUILD,
                                  config.STATUS_REBUILDING,
                                  config.STATUS_REBUILD_SPAWNING],
                timeout=config.SERVER_ACTIVE_TIMEOUT)

    @steps_checker.step
    def rescue_server(self, server, check=True):
        """Step to rescue nova server.

        Args:
            server (object): nova server to rescue
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        server.rescue()

        if check:
            self.check_server_status(
                server,
                expected_statuses=[config.STATUS_RESCUE],
                transit_statuses=[config.STATUS_ACTIVE,
                                  config.STATUS_RESCUING],
                timeout=config.SERVER_UPDATE_TIMEOUT)

    @steps_checker.step
    def check_server_not_rebuilt_in_paused_state(self, paused_server, image):
        """Step to check server will not be rebuilt in Paused state.

        Args:
            paused_server (obj): server to be set to Paused state
            image (object): image used for instance rebuild

        Raises:
            AssertionError: if check failed
        """
        exception_message = ("Cannot 'rebuild' instance " + paused_server.id +
                             " while it is in vm_state paused")
        assert_that(
            calling(self.rebuild_server).with_args(
                paused_server, image, check=False),
            raises(nova_exceptions.Conflict, exception_message))

    @steps_checker.step
    def check_server_not_rebuilt_in_rescue_state(self, rescue_server, image):
        """Step to check server will not be rebuilt in Rescue state.

        Args:
            rescue_server (obj): server to be set to Rescue state
            image (object): image used for instance rebuild

        Raises:
            AssertionError: if check failed
        """
        exception_message = ("Cannot 'rebuild' instance " + rescue_server.id +
                             " while it is in vm_state rescue")
        assert_that(
            calling(self.rebuild_server).with_args(
                rescue_server, image, check=False),
            raises(nova_exceptions.Conflict, exception_message))

    def _soft_delete_servers(self, servers, check):
        # it doesn't delete server really, just hides server and marks it as
        # trash for nova garbage collection after reclaim timeout.
        for server in servers:
            server.delete()

        if check:
            for server in servers:
                self.check_server_presence(
                    server,
                    present=False,
                    timeout=config.SERVER_DELETE_TIMEOUT)

    def _hard_delete_servers(self, servers, check):
        for server in servers:
            server.force_delete()  # delete server really

        if check:
            for server in servers:
                self.check_server_presence(
                    server,
                    present=False,
                    timeout=config.SERVER_DELETE_TIMEOUT)

    @steps_checker.step
    def resize(self, server, flavor, check=True):
        """Step to resize server.

        Args:
            server (object): nova server
            flavor (object): flavor object
            check (bool): flag whether check step or not
        """
        server.resize(flavor)

        if check:
            self.check_server_status(
                server,
                expected_statuses=[config.STATUS_VERIFY_RESIZE],
                transit_statuses=[config.STATUS_RESIZE],
                timeout=config.VERIFY_RESIZE_TIMEOUT)

    @steps_checker.step
    def reboot_server(self,
                      server,
                      reboot_type=config.REBOOT_SOFT,
                      check=True):
        """Step to reboot nova server.

        Args:
            server (obj): nova server
            reboot_type (str): `REBOOT_SOFT` for a software-level
                reboot, or `REBOOT_HARD` for a virtual power cycle hard reboot
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        server.reboot(reboot_type=reboot_type)

        if check:
            self.check_server_status(
                server,
                expected_statuses=[config.STATUS_ACTIVE],
                transit_statuses=[config.STATUS_REBOOT,
                                  config.STATUS_HARD_REBOOT],
                timeout=config.SERVER_ACTIVE_TIMEOUT)

    @steps_checker.step
    def stop_server(self, server, check=True):
        """Step to stop server.

        Args:
            server (obj): nova server
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        server.stop()

        if check:
            self.check_server_status(server,
                                     expected_statuses=[config.STATUS_SHUTOFF],
                                     transit_statuses=[config.STATUS_ACTIVE],
                                     timeout=config.SERVER_SHUTOFF_TIMEOUT)

    @steps_checker.step
    def start_server(self, server, check=True):
        """Step to start server.

        Args:
            server (obj): nova server
            check (bool): flag whether to check step or not

        Raises:
             TimeoutExpired: if check failed after timeout
        """
        server.start()

        if check:
            self.check_server_status(server,
                                     expected_statuses=[config.STATUS_ACTIVE],
                                     transit_statuses=[config.STATUS_SHUTOFF],
                                     timeout=config.SERVER_ACTIVE_TIMEOUT)

    @steps_checker.step
    def shelve_server(self, server, check=True):
        """Step to shelve server.

        Args:
            server (obj): nova server to shelve
            check (bool): flag whether to check step or not

        Raises:
             TimeoutExpired: if check failed after timeout
        """
        server.shelve()

        if check:
            self.check_server_status(server,
                                     expected_statuses=[
                                         config.STATUS_SHELVED,
                                         config.STATUS_SHELVED_OFFLOADED
                                     ],
                                     transit_statuses=[config.STATUS_ACTIVE],
                                     timeout=config.SERVER_SHELVE_TIMEOUT)

    @steps_checker.step
    def lock_server(self, server, check=True):
        """Step to lock server.

        Args:
            server (obj): nova server to lock
            check (bool): flag whether to check step or not

        Raises:
             TimeoutExpired: if check failed after timeout
        """
        server.lock()

        if check:
            self.check_server_status(server,
                                     expected_statuses=[config.STATUS_ACTIVE],
                                     timeout=config.SERVER_ACTIVE_TIMEOUT)

            self.check_server_attribute(server,
                                        attr=config.SERVER_ATTR_LOCKED,
                                        value=True,
                                        timeout=config.SERVER_UPDATE_TIMEOUT)

    @steps_checker.step
    @contextlib.contextmanager
    def check_iperf_loss_context(self, server_ssh, ip, port, time=60,
                                 max_loss=0):
        """Step to check that iperf loss inside CM is less than max_loss.

        Note:
            This step requires to iperf server will be launched with listening
            for UDP protocol.

        Args:
            server_ssh (obj): instance of stepler.third_party.ssh.SshClient
            ip (str): iperf server ip address
            port (int): iperf server port
            time (int, optional): time to generate traffic
            max_loss (float): maximum allowed datagramm loss in percents

        Raises:
            AssertionError: if iperf loss is greater than `max_loss`
        """
        with iperf.iperf(
                remote=server_ssh, ip=ip, time=time, port=port,
                udp=True) as result:
            yield
        assert_that(result['summary']['error_percent'],
                    less_than_or_equal_to(max_loss))

    def _error_message(self, server):
        fault = getattr(server, 'fault', {})
        if not fault:
            fault_msg = "No information"
        else:
            fault_msg = '\n'.join(("{}:\n{}".format(k, v)
                                   for k, v in fault.items()))
        return "Server fault:\n{}".format(fault_msg)

    @steps_checker.step
    def check_server_attribute(self,
                               server,
                               attr,
                               value,
                               equal=True,
                               timeout=0):
        """Verify step to check that server's attribute has an expected value.

        Args:
            server (object): nova server to check its attribute defined in
                arguments
            attr (str): name of server's attribute
            value (str) expected value of server's attribute
            equal (bool): flag whether servers's attribute should be
                equal to `value` or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """

        if equal:
            matcher = is_(value)
        else:
            matcher = is_not(value)

        def predicate():
            server.get()
            server_attr = getattr(server, attr)
            return waiter.expect_that(server_attr, matcher)

        waiter.wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def evacuate_servers(self, servers, host=None, check=True):
        """Step to evacuate servers from failed host

        Args:
            servers (obj): servers to evacuate
            host (str): target host
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        failed_host = {}
        for server in servers:
            server.get()
            failed_host[server.id] = getattr(server, config.SERVER_ATTR_HOST)
            server.evacuate(host)

        if check:
            for server in servers:

                self.check_server_status(
                    server,
                    expected_statuses=[config.STATUS_ACTIVE],
                    transit_statuses=[config.STATUS_REBUILD,
                                      config.STATUS_REBUILDING,
                                      config.STATUS_REBUILD_SPAWNING],
                    timeout=config.SERVER_ACTIVE_TIMEOUT)

                self.check_instance_hypervisor_hostname(
                    server,
                    failed_host[server.id],
                    equal=False,
                    timeout=config.EVACUATE_TIMEOUT)

    @steps_checker.step
    def check_servers_not_evacuated_in_rescue_state(self, rescue_servers):
        """Step to check servers will not be evacuated in Rescue state.

        Args:
            rescue_servers (list): servers to be set to Rescue state

        Raises:
            AssertionError: if check failed
        """
        exception_message = ("Cannot 'evacuate' instance " +
                             (rescue_servers[0].id or rescue_servers[1].id) +
                             " while it is in vm_state rescue")
        assert_that(
            calling(self.evacuate_servers).with_args(
                rescue_servers, check=False),
            raises(nova_exceptions.Conflict, exception_message))

    @steps_checker.step
    def check_servers_not_evacuated_in_shelved_state(self, shelved_servers):
        """Step to check servers will not be evacuated in Shelved state.

        Args:
            shelved_servers (list): servers to be set to Shelved state

        Raises:
            AssertionError: if check failed
        """
        exception_message = ("The target host can't be the same one.")
        assert_that(
            calling(self.evacuate_servers).with_args(
                shelved_servers, check=False),
            raises(nova_exceptions.BadRequest, exception_message))

    @steps_checker.step
    def check_servers_not_evacuated_in_paused_state(self, paused_servers):
        """Step to check servers will not be evacuated in Paused state.

        Args:
            paused_servers (list): servers to be set to Paused state

        Raises:
            AssertionError: if check failed
        """
        exception_message = ("Cannot 'evacuate' instance " +
                             (paused_servers[0].id or paused_servers[1].id) +
                             " while it is in vm_state paused")
        assert_that(
            calling(self.evacuate_servers).with_args(
                paused_servers, check=False),
            raises(nova_exceptions.Conflict, exception_message))

    @steps_checker.step
    def check_servers_not_evacuated_in_resized_state(self, resized_servers):
        """Step to check servers will not be evacuated in Resized state.

        Args:
            resized_servers (list): servers to be set to Resized state

        Raises:
            AssertionError: if check failed
        """
        exception_message = ("Cannot 'evacuate' instance " +
                             (resized_servers[0].id or resized_servers[1].id) +
                             " while it is in vm_state resized")
        assert_that(
            calling(self.evacuate_servers).with_args(
                resized_servers, check=False),
            raises(nova_exceptions.Conflict, exception_message))

    @steps_checker.step
    def check_servers_not_evacuated_to_initial_compute(self,
                                                       servers_to_evacuate,
                                                       host):
        """Step to check servers will not be evacuated to initial compute.

        Args:
            servers_to_evacuate (list): servers to be evacuated
            host (str): target host, must be equal to failed compute's hostname

        Raises:
            AssertionError: if check failed
        """
        exception_message = ("The target host can't be the same one.")
        assert_that(
            calling(self.evacuate_servers).with_args(
                servers_to_evacuate, host, check=False),
            raises(nova_exceptions.BadRequest, exception_message))

    @steps_checker.step
    def check_servers_actions_not_available(self, get_server_steps):
        """Step to check servers actions if no free space on controller.

        Args:
            get_server_steps (function): function to get server steps

        Raises:
            TimeoutExpired: if no GatewayTimeout exception occurs after timeout
        """
        def _is_servers_action_unavailable():
            try:
                get_server_steps()
                is_available = True
            except keystone_exceptions.GatewayTimeout:
                is_available = False
            return waiter.expect_that(is_available, equal_to(False))

        waiter.wait(_is_servers_action_unavailable,
                    timeout_seconds=config.GALERA_CLUSTER_DOWN_TIMEOUT)
