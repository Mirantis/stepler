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

import contextlib
import socket

from hamcrest import (assert_that, is_not, has_item, equal_to, empty,
                      less_than_or_equal_to)  # noqa
import paramiko
from waiting import wait

from stepler.base import BaseSteps
from stepler import config
from stepler.third_party import chunk_serializer
from stepler.third_party import ping
from stepler.third_party import ssh
from stepler.third_party.steps_checker import step

__all__ = [
    'ServerSteps'
]

CREDENTIALS_PREFIX = 'stepler_credentials_'
ROOT_DISK_TIMESTAMP_FILE = '/timestamp.txt'
EPHEMERAL_DISK_TIMESTAMP_FILE = '/mnt/timestamp.txt'


class ServerSteps(BaseSteps):
    """Nova steps."""

    @step
    def create_server(self,
                      server_name,
                      image,
                      flavor,
                      networks=(),
                      ports=(),
                      keypair=None,
                      security_groups=None,
                      availability_zone='nova',
                      block_device_mapping=None,
                      username=None,
                      password=None,
                      userdata=None,
                      check=True):
        """Step to create server.

        Args:
            server_name (str): name of created server
            image (object|None): image or None (to use volume)
            flavor (object): flavor
            networks (list): networks objects
            ports (list): ports objects
            keypair (object): keypair
            security_groups (list|tuple): security groups
            availability_zone (str): name of availability zone
            block_device_mapping (dict|None): block device mapping for server
            username (str): username to store with server metadata
            password (str): password to store with server metadata
            userdata (str): userdata (script) to execute on instance after boot
            check (bool): flag whether to check step or not

        Returns:
            object: nova server
        """
        sec_groups = [s.id for s in security_groups or []]
        image_id = None if image is None else image.id
        keypair_id = None if keypair is None else keypair.id
        nics = []
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
        meta = chunk_serializer.dump(credentials, CREDENTIALS_PREFIX)
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
        if check:
            self.check_server_status(server, 'active', timeout=180)

        return server

    @step
    def create_servers(self,
                       server_names,
                       image,
                       flavor,
                       networks=(),
                       ports=(),
                       keypair=None,
                       security_groups=None,
                       availability_zone='nova',
                       block_device_mapping=None,
                       username=None,
                       password=None,
                       userdata=None,
                       check=True):
        """Step to create servers.

        Args:
            server_names (list): names of created servers
            image (object|None): image or None (to use volume)
            flavor (object): flavor
            networks (list): networks objects
            ports (list): ports objects
            keypair (object): keypair
            security_groups (list|tuple): security groups
            availability_zone (str): name of availability zone
            block_device_mapping (dict|None): block device mapping for servers
            username (str): username to store with server metadata
            password (str): password to store with server metadata
            userdata (str): userdata (script) to execute on instance after boot
            check (bool): flag whether to check step or not

        Returns:
            list: nova servers
        """
        servers = []
        for server_name in server_names:
            server = self.create_server(
                server_name,
                image=image,
                flavor=flavor,
                networks=networks,
                ports=ports,
                keypair=keypair,
                security_groups=security_groups,
                availability_zone=availability_zone,
                block_device_mapping=block_device_mapping,
                userdata=userdata,
                username=username,
                password=password,
                check=False)
            servers.append(server)

        if check:
            for server in servers:
                self.check_server_status(server, 'active', timeout=180)

        return servers

    @step
    def delete_server(self, server, check=True):
        """Step to delete server."""
        server.force_delete()

        if check:
            self.check_server_presence(server, present=False, timeout=180)

    @step
    def delete_servers(self, servers, check=True):
        """Step to delete servers."""
        for server in servers:
            self.delete_server(server, check=False)

        if check:
            for server in servers:
                self.check_server_presence(server, present=False, timeout=180)

    @step
    def get_servers(self, name_prefix=None, check=True):
        """Step to retrieve servers from nova.

        Args:
            check (bool): flag whether to check step or not
        Returns:
            list: server list
        """
        servers = self._client.list()

        if name_prefix:
            servers = [server for server in servers
                       if server.name.startswith(name_prefix)]

        if check:
            assert_that(servers, is_not(empty()))

        return servers

    @step
    def check_server_presence(self, server, present=True, timeout=0):
        """Check-step to check server presence.

        Args:
            server (object): nova server
            present (bool): flag to check is server present or absent
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        def predicate():
            try:
                self._client.get(server.id)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)

    @step
    def check_server_status(self,
                            server,
                            status,
                            transit_statuses=('build',),
                            timeout=0):
        """Verify step to check server status.

        Args:
            server (object): nova instance to ping its floating ip
            status (str): expected server status
            transit_statuses (iterable): allowed transit statuses
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        def predicate():
            server.get()
            return server.status.lower() not in transit_statuses

        wait(predicate, timeout_seconds=timeout)
        assert_that(server.status.lower(), equal_to(status.lower()))

    @step
    def get_server_credentials(self, server):
        """Step to retrieve server credentials.

        Args:
            server (object): nova server object
        Returns:
            dict: dict with username, password and (optionally) private_key
        """
        server.get()
        meta = server.metadata
        return chunk_serializer.load(meta, CREDENTIALS_PREFIX)

    @step
    def get_server_ssh(self, server, ip=None, proxy_cmd=None,
                       ssh_timeout=config.SSH_CLIENT_TIMEOUT, check=True):
        """Step to get SSH connect to server.

        Args:
            server (object): nova server
            ip (str): ip of server
            proxy_cmd (str): ssh client proxy command
            ssh_timeout (int): timeout to establish ssh connection
            check (bool): flag whether to check step or not

        Returns:
            ssh.SshClient: instantiated ssh client to server ip

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        if not ip:
            if not proxy_cmd:  # server is available via floating IP directly
                ip = self.get_ips(server, 'floating').keys()[0]
            else:
                ip = self.get_ips(server, 'fixed').keys()[0]

        credentials = self.get_server_credentials(server)

        server_ssh = ssh.SshClient(ip,
                                   pkey=credentials.get('private_key'),
                                   username=credentials.get('username'),
                                   password=credentials.get('password'),
                                   timeout=ssh_timeout,
                                   proxy_cmd=proxy_cmd)
        if check:
            self.check_server_ssh_connect(server_ssh,
                                          config.SSH_CONNECT_TIMEOUT)

        return server_ssh

    @step
    def check_server_ssh_connect(self, server_ssh, timeout=0):
        """Step to check ssh connect to server.

        Args:
            server_ssh (ssh.SshClient): ssh client to server ip
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        def predicate():
            try:
                server_ssh.connect()
                return True
            except (paramiko.SSHException, socket.error):
                return False
            finally:
                server_ssh.close()

        wait(predicate, timeout_seconds=timeout)

    @step
    def attach_floating_ip(self, server, floating_ip, check=True):
        # TODO(schipiga): expand documentation
        """Step to attach floating IP to server."""
        self._client.add_floating_ip(server, floating_ip)

        if check:
            server.get()
            floating_ips = self.get_ips(server, 'floating').keys()
            assert_that(floating_ips,
                        has_item(floating_ip.ip),
                        "Floating IP not in a list of server's IPs.")

    @step
    def detach_floating_ip(self, server, floating_ip, check=True):
        # TODO(schipiga): expand documentation
        """Step to detach floating IP from server."""
        self._client.remove_floating_ip(server, floating_ip)

        if check:
            server.get()
            floating_ips = self.get_ips(server, 'floating').keys()
            assert_that(floating_ips,
                        is_not(has_item(floating_ip.ip)),
                        "Floating IP still in a list of server's IPs.")

    @step
    def get_ips(self, server, ip_type=None):
        # TODO(schipiga): expand documentation
        """Step to get server IPs."""
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
        return ips

    @step
    def check_ping_to_server_floating(self, server, timeout=0):
        """Verify step to check ping to server floating ip address.

        Each instance has a private, fixed IP address and can also have
        a public, or floating IP address. Private IP addresses are used for
        communication between instances, and public addresses are used for
        communication with networks outside the cloud, including the Internet.

        Args:
            server (object): nova instance to ping its floating ip
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        floating_ip = self.get_ips(server, 'floating').keys()[0]

        def predicate():
            result = ping.Pinger(floating_ip).ping(count=1)
            return result.loss == 0

        wait(predicate, timeout_seconds=timeout)

    @step
    def live_migrate(self, server, host=None, block_migration=True,
                     check=True):
        """Step to live migrate nova server.

        Args:
            server (object): nova instance to migrate
            host (str): hypervisor's hostname to migrate to
            block_migration (bool): should nova use block or true live
                migration
            check (bool): flag whether to check step or not
        """
        server.get()
        current_host = getattr(server, 'OS-EXT-SRV-ATTR:host')
        server.live_migrate(host=host, block_migration=block_migration)
        if check:
            if host is not None:
                self.check_instance_hypervisor_hostname(
                    server, host, timeout=config.LIVE_MIGRATE_TIMEOUT)
            else:
                self.check_instance_hypervisor_hostname(
                    server,
                    current_host,
                    equal=False,
                    timeout=config.LIVE_MIGRATE_TIMEOUT)
            self.check_server_status(
                server,
                'active',
                transit_statuses=('migrating',),
                timeout=config.LIVE_MIGRATE_TIMEOUT)

    @step
    def check_instance_hypervisor_hostname(self,
                                           server,
                                           host,
                                           equal=True,
                                           timeout=0):
        """Verify step to check that server's hypervisor hostname.

        Args:
            server (object): nova instance to check hypervisor hostname
            host (str): name of hypervisor hostname to compare with
                server's hypervisor
            equal (bool): flag whether servers's hypervisor hostname should be
                equal to `hostname` or not
            timeout (int): seconds to wait a result of check
        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        def predicate():
            server.get()
            server_host = getattr(server, 'OS-EXT-SRV-ATTR:host')
            return equal == (server_host == host)

        wait(predicate, timeout_seconds=timeout)

    @step
    @contextlib.contextmanager
    def check_ping_loss_context(self, ip_to_ping, max_loss=0):
        """Context manager step to check that ping losses inside CM is less
            than max_loss.

        Args:
            ip_to_ping (str): ip address to ping
            max_loss (int): maximum allowed pings loss

        Raises:
            AssertionError: if ping loss is greater than `max_loss`
        """
        with ping.Pinger(ip_to_ping) as result:
            yield
        assert_that(result.loss, less_than_or_equal_to(max_loss))

    @step
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

    @step
    def check_server_log_contains_record(self, server, substring, timeout=0):
        """Verify step to check server log contains substring.

        Args:
            server (object): nova instance to ping its floating ip
            substring (str): substring to match
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        def predicate():
            server.get()
            console = server.get_console_output()
            return substring in console

        wait(predicate, timeout_seconds=timeout)

    @step
    def create_timestamps_on_root_and_ephemeral_disks(self,
                                                      server_ssh,
                                                      timestamp,
                                                      check=True):
        """Step to create timestamp on root and ephemeral disks

        Args:
            server_ssh (object): instance of stepler.third_party.ssh.SshClient
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
                    root_ts_file=ROOT_DISK_TIMESTAMP_FILE,
                    ephemeral_ts_file=EPHEMERAL_DISK_TIMESTAMP_FILE))
        if check:
            self.check_timestamps_on_root_and_ephemeral_disks(server_ssh,
                                                              timestamp)

    @step
    def check_timestamps_on_root_and_ephemeral_disks(self, server_ssh,
                                                     timestamp):
        """Verify step to check timestamp on root and ephemeral disks

        Args:
            server_ssh (object): instance of stepler.third_party.ssh.SshClient
            timestamp (str): timestamp to check
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if timestamp on root and ephemeral are not equal
        """
        with server_ssh.sudo():
            root_result = server_ssh.check_call('cat "{root_ts_file}"'.format(
                root_ts_file=ROOT_DISK_TIMESTAMP_FILE))
            ephemeral_result = server_ssh.check_call(
                'cat "{ephemeral_ts_file}"'.format(
                    ephemeral_ts_file=EPHEMERAL_DISK_TIMESTAMP_FILE))
        assert_that(root_result.stdout, equal_to(ephemeral_result.stdout))
        assert_that(timestamp, equal_to(root_result.stdout))
