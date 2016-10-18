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
from hamcrest import (assert_that, is_not, empty)
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
        """Step to create port based on a kwargs dictionary of attributes.

        Parameters:
            :param address: MAC address for this port
            :param node_uuid: UUID of a node the ports should be associated with
            :param check: For checking port presence
            :param kwargs: Optional. A dictionary containing the attributes
            of the resource that will be created.
               extra - Extra node parameters
               local_link_connection - Contains the port binding profile
               pxe_enabled - Indicates whether PXE is enabled for the port
               uuid - The uuid of the port

        Return:
            object: ironic port
        """
        port = self._client.port.create(address=address,
                                            node_uuid=node_uuid,
                                            **kwargs)
        if check:
            self.check_port_presence(port.uuid)
        return port

    @step
    def check_port_presence(self, port_uuid, present=True, timeout=0):
        """Verify step to check node is present."""
        def predicate():
            try:
                self._client.port.get(port_uuid)
                return present
            except exceptions.NotFound:
                return not present
        wait(predicate, timeout_seconds=timeout)

    @step
    def delete_port(self, port_uuid, check=True):
        """Step to delete port."""
        self._client.port.delete(port_uuid)
        if check:
            self.check_port_presence(port_uuid, present=False)

    @step
    def get_ports(self, check=True):
        """Step to get port."""
        ports = self._client.port.list()
        if check:
            assert_that(ports, is_not(empty()))
        return ports
