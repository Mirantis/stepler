"""
-----------------
Ironic port steps
-----------------
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


from ironicclient import exceptions
from hamcrest import assert_that, is_not, empty, equal_to  # noqa
from stepler import base
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

__all__ = [
    'IronicPortSteps'
]


class IronicPortSteps(base.BaseSteps):
    """Ironic port steps."""

    @steps_checker.step
    def create_ports(self,
                     node,
                     addresses=None,
                     count=1,
                     check=True,
                     **kwargs):
        """Step to create ironic ports based on a kwargs dictionary
        of attributes.

        Args:
            addresses (list): MAC addresses for ports
            node (object): node of the ports should be associated with
            count (int): count of created ports
            check (bool): For checking ports were created correct
                with correct addresses
            kwargs: Optional. A dictionary containing the attributes
            of the resource that will be created:
               extra (dictionary)- Extra node parameters
               local_link_connection (dictionary)-
                    Contains the port binding profile
               pxe_enabled (bool)- Indicates whether
                    PXE is enabled for the port
               uuid (str)- The uuid of the port

        Return:
            ports (list): list of created ironic ports

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        addresses = addresses or utils.generate_mac_addresses(count=count)
        ports = []
        _port_addresses = {}

        for address in addresses:
            port = self._client.port.create(address=address,
                                            node_uuid=node.uuid,
                                            **kwargs)
            _port_addresses[port.uuid] = address
            ports.append(port)

        if check:
            self.check_ports_presence(ports)
            for port in ports:
                assert_that(_port_addresses[port.uuid],
                            equal_to(port.address))

        return ports

    @steps_checker.step
    def check_ports_presence(self, ports, must_present=True, port_timeout=0):
        """Step to check ports is present.

        Args:
            ports (list): list of ironic ports
            must_present (bool): flag whether ports should be present or not
            port_timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        expected_presence = {port.uuid: must_present for port in ports}

        def _check_ports_presence():
            actual_presence = {}

            for port in ports:
                try:
                    self._client.port.get(port.uuid)
                    actual_presence[port.uuid] = True
                except exceptions.NotFound:
                    actual_presence[port.uuid] = False

            return expect_that(actual_presence, equal_to(expected_presence))

        timeout = len(ports) * port_timeout
        waiter.wait(_check_ports_presence, timeout_seconds=timeout)

    @steps_checker.step
    def delete_ports(self, ports, check=True):
        """Step to delete ports.

        Args:
            ports (list): list of ironic ports
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        for port in ports:
            self._client.port.delete(port.uuid)

        if check:
            self.check_ports_presence(ports, must_present=False)

    @steps_checker.step
    def get_ports(self, check=True):
        """Step to get ports.

        Args:
            check (bool): flag whether to check step or not

        Returns:
            ports (list): list of ironic ports

        Raises:
            AssertionError: if check failed
        """
        ports = self._client.port.list()
        if check:
            assert_that(ports, is_not(empty()))
        return ports
