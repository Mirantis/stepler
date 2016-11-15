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
from stepler.third_party import waiter

__all__ = [
    'IronicPortSteps'
]


class IronicPortSteps(base.BaseSteps):
    """Ironic port steps."""

    @steps_checker.step
    def create_port(self, address, node, check=True, **kwargs):
        """Step to create ironic port based on a kwargs dictionary
        of attributes.

        Args:
            address (str): MAC address for this port
            node (object): node of the ports should be associated with
            check (bool): For checking port presence
            kwargs: Optional. A dictionary containing the attributes
            of the resource that will be created:
               extra (dictionary)- Extra node parameters
               local_link_connection (dictionary)-
                    Contains the port binding profile
               pxe_enabled (bool)- Indicates whether
                    PXE is enabled for the port
               uuid (str)- The uuid of the port

        Return:
            port (object): ironic port

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        port = self._client.port.create(address=address,
                                        node_uuid=node.uuid,
                                        **kwargs)
        if check:
            self.check_port_presence(port)
            assert_that(port.address, equal_to(address))
            assert_that(port.node_uuid, equal_to(node.uuid))

        return port

    @steps_checker.step
    def check_port_presence(self, port, must_present=True, timeout=0):
        """Verify step to check port is present.

        Args:
            port (object): ironic port
            must_present (bool): flag whether port should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_port_presence():
            try:
                self._client.port.get(port.uuid)
                is_present = True
            except exceptions.NotFound:
                is_present = False

            return expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_port_presence, timeout_seconds=timeout)

    @steps_checker.step
    def delete_port(self, port, check=True):
        """Step to delete port.

        Args:
            port (object): ironic port
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        self._client.port.delete(port.uuid)
        if check:
            self.check_port_presence(port, must_present=False)

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
