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
from hamcrest import assert_that, is_not, empty  # noqa
from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step
from waiting import wait

__all__ = [
    'IronicPortSteps'
]


class IronicPortSteps(BaseSteps):
    """Ironic port steps."""

    @step
    def create_port(self, address, node_uuid, check=True, **kwargs):
        """Step to create ironic port based on a kwargs dictionary
        of attributes.

        Args:
            address (str): MAC address for this port
            node_uuid (str): UUID of a node the ports should be associated with
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
        """
        port = self._client.port.create(address=address,
                                        node_uuid=node_uuid,
                                        **kwargs)
        if check:
            self.check_port_presence(port)
        return port

    @step
    def check_port_presence(self, port, present=True, timeout=0):
        """Verify step to check port is present.

        Args:
            port (object): ironic port
            present (bool): flag whether port should present or no
            timeout (int): seconds to wait a result of check
        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        def predicate():
            try:
                self._client.port.get(port.uuid)
                return present
            except exceptions.NotFound:
                return not present
        wait(predicate, timeout_seconds=timeout)

    @step
    def delete_port(self, port, check=True):
        """Step to delete port.

        Args:
            port (object): ironic port
            check (bool): flag whether to check step or not
        """
        self._client.port.delete(port.uuid)
        if check:
            self.check_port_presence(port, present=False)

    @step
    def get_ports(self, check=True):
        """Step to get ports.

        Args:
            check (bool): flag whether to check step or not
        Returns:
            ports (list): list of ironic ports
        """
        ports = self._client.port.list()
        if check:
            assert_that(ports, is_not(empty()))
        return ports
