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

from hamcrest import assert_that, is_not, has_item, equal_to  # noqa
from waiting import wait

from stepler.base import BaseSteps
from stepler.third_party.ssh import SshClient
from stepler.third_party.steps_checker import step

__all__ = [
    'ServerSteps'
]


class ServerSteps(BaseSteps):
    """Nova steps."""

    @step
    def create_server(self, server_name, image, flavor, network, keypair,
                      security_groups=None, availability_zone='nova',
                      check=True):
        """Step to create server."""
        sec_groups = [s.id for s in security_groups or []]
        server = self._client.create(name=server_name,
                                     image=image.id,
                                     flavor=flavor.id,
                                     nics=[{'net-id': network['id']}],
                                     key_name=keypair.id,
                                     availability_zone=availability_zone,
                                     security_groups=sec_groups)
        if check:
            self.check_server_status(server, 'active', timeout=180)

        return server

    @step
    def create_servers(self, server_names, image, flavor, network, keypair,
                       security_groups=None, availability_zone='nova',
                       check=True):
        """Step to create servers."""
        servers = []
        for server_name in server_names:
            server = self.create_server(server_name, image, flavor, network,
                                        keypair, security_groups,
                                        availability_zone, check=False)
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
    def check_server_status(self, server, status, timeout=0):
        """Verify step to check server status."""
        transit_statuses = ('build',)

        def predicate():
            server.get()
            return server.status.lower() not in transit_statuses

        wait(predicate, timeout_seconds=timeout)
        assert_that(server.status.lower(), equal_to(status.lower()))

    @step
    def check_ssh_connect(self, server, keypair, username=None, password=None,
                          ip=None, proxy_cmd=None, ssh_timeout=60, timeout=0):
        """Verify step to check ssh connect to server."""
        if not ip:
            if not proxy_cmd:
                ip = self.get_ips(server, 'floating').keys()[0]
            else:
                ip = self.get_ips(server, 'fixed').keys()[0]

        ssh_client = SshClient(ip, pkey=keypair.private_key, username=username,
                               password=password, timeout=ssh_timeout,
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
