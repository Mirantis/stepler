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
import time

from hamcrest import (assert_that, is_not, has_item, equal_to, empty,
                      less_than_or_equal_to)  # noqa
from waiting import wait

from stepler.base import BaseSteps
from stepler import config
from stepler.third_party import chunk_serializer
from stepler.third_party import ping
from stepler.third_party.ssh import SshClient
from stepler.third_party.steps_checker import step

__all__ = [
    'ServerSteps'
]

CREDENTIALS_PREFIX = 'stepler_credentials_'


class ServerSteps(BaseSteps):
    """Nova steps."""

    @step
    def create_server(self, server_name, image, flavor, networks=(), ports=(),
                      keypair=None, security_groups=None,
                      availability_zone='nova', block_device_mapping=None,
                      username=None, password=None, userdata=None, check=True):
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
        server = self._client.create(name=server_name,
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
    def create_servers(self, server_names, image, flavor, networks=(),
                       ports=(), keypair=None, security_groups=None,
                       availability_zone='nova', block_device_mapping=None,
                       username=None, password=None, userdata=None,
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
        server.delete()

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
    def get_servers(self, check=True):
        """Step to retrieve servers from nova.

        Args:
            check (bool): flag whether to check step or not
        Returns:
            list: server list
        """
        servers = self._client.list()
        if check:
            assert_that(servers, is_not(empty()))
        return servers

    @step
    def check_server_presence(self, server, present=True, timeout=0):
        """Verify step to check server is present."""

        def predicate():
            try:
                self._client.get(server.id)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)

    @step
    def check_server_status(self, server, status, transit_statuses=('build', ),
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
    def check_ssh_connect(self, server, ip=None, proxy_cmd=None,
                          ssh_timeout=60, timeout=0):
        """Verify step to check ssh connect to server."""
        if not ip:
            if not proxy_cmd:
                ip = self.get_ips(server, 'floating').keys()[0]
            else:
                ip = self.get_ips(server, 'fixed').keys()[0]

        credentials = self.get_server_credentials(server)
        ssh_client = SshClient(ip,
                               pkey=credentials.get('private_key'),
                               username=credentials.get('username'),
                               password=credentials.get('password'),
                               timeout=ssh_timeout,
                               proxy_cmd=proxy_cmd)

        def predicate():
            try:
                ssh_client.connect()
                return True
            except Exception:
                return False
            finally:
                ssh_client.close()

        wait(predicate, timeout_seconds=timeout)

    @step
    def attach_floating_ip(self, server, floating_ip, check=True):
        """Step to attach floating IP to server."""
        self._client.add_floating_ip(server, floating_ip)

        if check:
            server.get()
            floating_ips = self.get_ips(server, 'floating').keys()
            assert_that(floating_ips, has_item(floating_ip.ip),
                        "Floating IP not in a list of server's IPs.")

    @step
    def detach_floating_ip(self, server, floating_ip, check=True):
        """Step to detach floating IP from server."""
        self._client.remove_floating_ip(server, floating_ip)

        if check:
            server.get()
            floating_ips = self.get_ips(server, 'floating').keys()
            assert_that(floating_ips, is_not(has_item(floating_ip.ip)),
                        "Floating IP still in a list of server's IPs.")

    @step
    def get_ips(self, server, ip_type=None):
        """Step to get server IPs."""
        ips = {}
        for net_name, net_info in server.addresses.items():
            for net in net_info:
                ips[net['addr']] = {'type': net['OS-EXT-IPS:type'],
                                    'mac': net['OS-EXT-IPS-MAC:mac_addr'],
                                    'net': net_name,
                                    'ip': net['addr']}
        if ip_type:
            ips = {key: val for key, val in ips.items()
                   if val['type'] == ip_type}
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
            self.check_server_status(
                server,
                'active',
                transit_statuses=('migrating',),
                timeout=config.LIVE_MIGRATE_TIMEOUT)
            if host is not None:
                self.check_instance_hypervisor_hostname(server, host)
            else:
                self.check_instance_hypervisor_hostname(
                    server, current_host, equal=False)

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
    def server_mem_workload(self, remote, check=True):
        """Step to start server memory workload.

        Args:
            remote (object): instance of stepler.third_party.ssh.SshClient
            check (bool): flag whether to check step or not
        """
        pid = remote.background_call('stress --vm-bytes 5M --vm-keep -m 1')
        if check:
            assert_that(pid, is_not(None))

    @step
    def server_cpu_workload(self, remote, check=True):
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

    @step
    def server_disk_workload(self, remote, check=True):
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

    @step
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

    @step
    def check_server_log(self, server, substring, timeout=0):
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
    def create_timestamps_on_root_and_ephemeral(self, remote, check=True):
        """Step to create timestamp on root and ephemeral disks

        Args:
            remote (object): instance of stepler.third_party.ssh.SshClient
            check (bool): flag whether to check step or not
        """
        with remote.sudo():
            remote.check_call('date | tee /timestamp.txt /mnt/timestamp.txt')
        if check:
            self.check_timestamps_on_root_and_ephemeral(remote)

    @step
    def check_timestamps_on_root_and_ephemeral(self, remote):
        """Verify step to check timestamp on root and ephemeral disks

        Args:
            remote (object): instance of stepler.third_party.ssh.SshClient
            check (bool): flag whether to check step or not
        """
        with remote.sudo():
            root_result = remote.check_call('cat /timestamp.txt')
            ephemeral_result = remote.check_call('cat /mnt/timestamp.txt')
        assert_that(root_result.stdout, equal_to(ephemeral_result.stdout))

    @step
    def resize(self, server, flavor, check=True):
        """Step to resize server.

        Args:
            server (object): nova instance
            flavor (object): flavor instance
            check (bool): flag whether to check step or not
        """
        self._client.resize(server, flavor)

        if check:
            self.check_server_status(server, 'verify_resize',
                                     transit_statuses=('resize',),
                                     timeout=config.VERIFY_RESIZE_TIMEOUT)
