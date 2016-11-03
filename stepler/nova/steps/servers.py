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
import time

from hamcrest import (assert_that, calling, empty, equal_to, has_entries,
                      has_item, has_properties, is_not, is_in,
                      less_than_or_equal_to, raises)  # noqa H301

from novaclient import exceptions as nova_exceptions
import paramiko
from waiting import wait

from stepler import base
from stepler import config
from stepler.third_party import chunk_serializer
from stepler.third_party.matchers import expect_that
from stepler.third_party import ping
from stepler.third_party import ssh
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = [
    'ServerSteps'
]


class ServerSteps(base.BaseSteps):
    """Nova steps."""

    @steps_checker.step
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
        meta = chunk_serializer.dump(credentials, config.CREDENTIALS_PREFIX)
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
            self.check_server_status(server, config.STATUS_ACTIVE,
                                     timeout=config.SERVER_ACTIVE_TIMEOUT)

        return server

    @steps_checker.step
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
                self.check_server_status(server, config.STATUS_ACTIVE,
                                         timeout=config.SERVER_ACTIVE_TIMEOUT)

        return servers

    @steps_checker.step
    def delete_server(self, server, soft=False, check=True):
        """Step to delete server.

        Args:
            server (object): nova server
            force (bool): delete option
            soft (bool): indicator that server is expected soft-deleted
            check (bool): flag whether to check step or not
        """
        if soft:
            self._soft_delete_server(server, check)
        else:
            self._hard_delete_server(server, check)

    @steps_checker.step
    def delete_servers(self, servers, soft=False, check=True):
        """Step to delete servers."""
        for server in servers:
            self.delete_server(server, soft=soft, check=False)

        if check:
            for server in servers:
                self.check_server_presence(
                    server, present=False,
                    timeout=config.SERVER_DELETE_TIMEOUT)

    @steps_checker.step
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
                       if (server.name or '').startswith(name_prefix)]

        if check:
            assert_that(servers, is_not(empty()))

        return servers

    @steps_checker.step
    def get_server(self, check=True, **kwargs):
        """Step to retrieve server from nova with filter.

        Args:
            check (bool): flag whether to check step or not
            kwargs: Additional filters to pass

        Returns:
            obj: server object
        """
        server = self._client.find(**kwargs)

        if check:
            assert_that(server, has_properties(kwargs))

        return server

    @steps_checker.step
    def check_server_presence(self, server, present=True, by_name=False,
                              timeout=0):
        """Check-step to check server presence.

        Args:
            server (object): nova server
            present (bool): flag to check is server present or absent
            by_name (bool): indicator of check method - by id or by name
                            in server list. For soft-deleted servers,
                            result = False for by_name=True, else True)
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was failed after timeout
        """
        if by_name:
            def predicate():
                names = [s.name for s in self._client.list()]
                return present == (server.name in names)
        else:
            def predicate():
                try:
                    self._client.get(server.id)
                    return present
                except nova_exceptions.NotFound:
                    return not present

        wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def check_server_status(self,
                            server,
                            status,
                            transit_statuses=[config.STATUS_BUILD],
                            timeout=0):
        """Verify step to check server status.

        Args:
            server (object): nova instance to ping its floating ip
            status (str): expected server status
            transit_statuses (iterable): allowed transit statuses
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was failed after timeout
        """

        def predicate():
            server.get()
            return server.status.lower() not in transit_statuses

        wait(predicate, timeout_seconds=timeout)
        assert_that(server.status.lower(), equal_to(status.lower()))

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
            TimeoutExpired: if check was failed after timeout
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

    @steps_checker.step
    def check_server_ssh_connect(self, server_ssh, timeout=0):
        """Step to check ssh connect to server.

        Args:
            server_ssh (ssh.SshClient): ssh client to server ip
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was failed after timeout
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

    @steps_checker.step
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

    @steps_checker.step
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

    @steps_checker.step
    def attach_fixed_ip(self, server, network_id, check=True):
        """Step to attach fixed IP from provided network to provided server.

        Args:
            server (object): nova instance to ping its floating ip
            network_id (str): the ID of the network the IP should be on
            check (bool): flag whether to check step or not

        Returns:
            str:  IF check=True, returns new fixed IP address
            None: IF check=False

        Raises:
            TimeoutExpired: if check was failed after timeout
        """
        ips_before_attach = self.get_ips(server, 'fixed').keys()
        server.add_fixed_ip(network_id)

        if check:
            def _check_fixed_ip_attached():
                server.get()
                ips_after_attach = self.get_ips(server, 'fixed').keys()
                return expect_that(len(ips_after_attach),
                                   equal_to(len(ips_before_attach) + 1))

            waiter.wait(_check_fixed_ip_attached,
                        timeout_seconds=config.SERVER_UPDATE_TIMEOUT)

            ips_after_attach = self.get_ips(server, 'fixed').keys()
            return (set(ips_after_attach) - set(ips_before_attach)).pop()

    @steps_checker.step
    def detach_fixed_ip(self, server, fixed_ip=None, check=True):
        """Step to detach provided fixed IP from provided server.

        Args:
            server (object): nova instance to delete fixed ip
            fixed_ip (str): Fixed IP address
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check was failed after timeout
        """
        if not fixed_ip:
            fixed_ip = self.get_ips(server, 'fixed').keys()[0]

        self._client.remove_fixed_ip(server.id, fixed_ip)

        if check:

            def _check_detach_fixed_ip():
                server.get()
                fixed_ips = self.get_ips(server, 'fixed').keys()
                return expect_that(fixed_ip, is_not(is_in(fixed_ips)))

            waiter.wait(_check_detach_fixed_ip,
                        timeout_seconds=config.SERVER_UPDATE_TIMEOUT)

    @steps_checker.step
    def check_server_doesnot_detach_unattached_fixed_ip(
            self, server, unattached_fixed_ip):
        """Step to check that server will raise exception if we try to detach
            not attached to it fixed IP.

        Args:
            server (object): nova instance to delete fixed ip
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

    @steps_checker.step
    def check_ping_for_ip(self,
                          ip_to_ping,
                          remote_from=None,
                          ping_count=3,
                          timeout=0):
        """Verify step to check ping for ip from remote or local host.

        Args:
            ip_to_ping (str): nova instance to ping its floating ip
            remote_from (object|None): instance of
                stepler.third_party.ssh.SshClient. If None - ping executing
                from local host.
            timeout (int): seconds to wait for success ping

        Raises:
            TimeoutExpired: if check was False after timeout
        """

        def predicate():
            result = ping.Pinger(
                ip_to_ping, remote=remote_from).ping(count=ping_count)
            return result.loss == 0

        wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def check_ping_to_server_floating(self, server, timeout=0):
        """Verify step to check ping to server floating ip address.

        Each instance has a private, fixed IP address and can also have
        a public, or floating IP address. Private IP addresses are used for
        communication between instances, and public addresses are used for
        communication with networks outside the cloud, including the Internet.

        Args:
            server (object): nova instance to ping its floating ip
            timeout (int): seconds to wait for result of check

        Raises:
            TimeoutExpired: if check was False after timeout
        """
        floating_ip = self.get_ips(server, 'floating').keys()[0]
        self.check_ping_for_ip(floating_ip, timeout=timeout)

    def _get_ping_plan(self, servers):
        """Get dict which contains ip list to ping for each server"""
        ping_plan = {}
        for server1 in servers:
            ping_plan[server1] = []
            for server2 in servers:
                if server1 != server2:
                    for ip in self.get_ips(server2).keys():
                        ping_plan[server1].append(ip)
        return ping_plan

    @steps_checker.step
    def check_ping_between_servers_via_floating(self,
                                                servers,
                                                timeout=0):
        """Step to check ping from each server to all other servers.

        Args:
            servers (list): nova instances to check ping between
            timeout (int): seconds to wait for result of check

        Raises:
            TimeoutExpired: if check was False after timeout
        """
        ping_plan = self._get_ping_plan(servers)
        for server, ips in ping_plan.items():
            floating_ip = self.get_ips(server, 'floating').keys()[0]

            with self.get_server_ssh(server, ip=floating_ip) as server_ssh:
                    for ip in ips:
                        self.check_ping_for_ip(ip, remote_from=server_ssh,
                                               timeout=timeout)

    @steps_checker.step
    def check_ping_between_servers(
            self, servers_ssh, ips, timeout=0):
        """Step to ping every provided IP from every provided server

        Args:
            servers_ssh (list): ssh.SshClient client to server
            ips (list): IP addresses to ping
            timeout (int): seconds to wait for result of check

        Raises:
            TimeoutExpired: if check was False after timeout
        """
        for server_ssh in servers_ssh:
            self.check_server_ssh_connect(server_ssh)
            for ip in ips:
                with server_ssh:
                    self.check_ping_for_ip(
                        ip_to_ping=ip,
                        remote_from=server_ssh,
                        timeout=timeout)

    @steps_checker.step
    def live_migrate(self, server, host=None, block_migration=True,
                     check=True):
        """Step to live migrate nova server.

        Args:
            server (object): nova instance to migrate
            host (str): hypervisor's hostname to migrate to
            block_migration (bool): should nova use block or true live
                migration
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check was False after timeout
        """
        server.get()
        current_host = getattr(server, 'OS-EXT-SRV-ATTR:host')
        server.live_migrate(host=host, block_migration=block_migration)
        if check:
            self.check_server_status(
                server,
                config.STATUS_ACTIVE,
                transit_statuses=[config.STATUS_MIGRATING],
                timeout=config.LIVE_MIGRATE_TIMEOUT)
            if host is not None:
                self.check_instance_hypervisor_hostname(server, host)
            else:
                self.check_instance_hypervisor_hostname(
                    server, current_host, equal=False)

    @steps_checker.step
    def migrate_servers(self, servers, check=True):
        """Step to migrate servers

        Args:
            servers (list): servers to migrate
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check was False after timeout
        """
        old_hosts = {}
        for server in servers:
            server.get()
            old_hosts[server.id] = getattr(server, 'OS-EXT-SRV-ATTR:host')
            server.migrate()
        if check:
            for server in servers:
                self.check_server_status(
                    server, config.STATUS_VERIFY_RESIZE,
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
            servers (list): servers to confirm resize
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check was False after timeout
        """
        for server in servers:
            server.confirm_resize()
        if check:
            for server in servers:
                self.check_server_status(
                    server, config.STATUS_ACTIVE,
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
            server (object): nova instance to check hypervisor hostname
            host (str): name of hypervisor hostname to compare with
                server's hypervisor
            equal (bool): flag whether servers's hypervisor hostname should be
                equal to `hostname` or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was failed after timeout
        """

        def predicate():
            server.get()
            server_host = getattr(server, 'OS-EXT-SRV-ATTR:host')
            return equal == (server_host == host)

        wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
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
            Exception: if commmand exit code is not 0
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
            Exception: if commmand exit code is not 0
        """
        # To aviod inifine loop, count of workers to stress is limited to 3.
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
            remote.check_process_present('cpulimit')

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
            server (object): nova instance to ping its floating ip
            substring (str): substring to match
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was failed after timeout
        """

        def predicate():
            server.get()
            console = server.get_console_output()
            return substring in console

        wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
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
                    root_ts_file=config.ROOT_DISK_TIMESTAMP_FILE,
                    ephemeral_ts_file=config.EPHEMERAL_DISK_TIMESTAMP_FILE))
        if check:
            self.check_timestamps_on_root_and_ephemeral_disks(server_ssh,
                                                              timestamp)

    @steps_checker.step
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
                root_ts_file=config.ROOT_DISK_TIMESTAMP_FILE))

            ephemeral_result = server_ssh.check_call(
                'cat "{ephemeral_ts_file}"'.format(
                    ephemeral_ts_file=config.EPHEMERAL_DISK_TIMESTAMP_FILE))

        assert_that(root_result.stdout, equal_to(ephemeral_result.stdout))
        assert_that(timestamp, equal_to(root_result.stdout))

    @steps_checker.step
    def restore_server(self, server, check=True):
        """Step to restore soft-deleted server.

        Args:
            server (object): nova instance
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
            server (object): nova instance object
            custom_meta (dict): data, which presence should be checked in
                                server's metadata.
                                Like: {'key': 'stepler_test'}
            present (bool): flag to check if provided data should OR
                             should NOT present in server's metadata.
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was failed after timeout
        """
        matcher = has_entries(custom_meta)
        if not present:
            matcher = is_not(matcher)

        def predicate():
            server.get()
            return expect_that(server.metadata, matcher)

        waiter.wait(predicate, timeout_seconds=timeout)

    def _soft_delete_server(self, server, check):
        # it doesn't delete server really, just hides server and marks it as
        # trash for nova garbage collection after reclaim timeout.
        server.delete()

        if check:
            self.check_server_presence(
                server, present=False, by_name=True,
                timeout=config.SOFT_DELETED_TIMEOUT)
            self.check_server_status(server, config.STATUS_SOFT_DELETED)

    def _hard_delete_server(self, server, check):
        server.force_delete()  # delete server really

        if check:
            self.check_server_presence(
                server, present=False,
                timeout=config.SERVER_DELETE_TIMEOUT)
