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

from waiting import wait

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = [
    'IronicNodeSteps'
]


class IronicNodeSteps(BaseSteps):
    """Node steps."""

    @step
    def create_ironic_node(self, driver='fake', check=True, **kwargs):
        """Step to create a ironic node.

        Parameters:
            :param driver: The name or UUID of the driver.
            :param check: For checking node presence
            :param kwargs: Optional. A dictionary containing the attributes
            of the resource that will be created:
                chassis_uuid - The uuid of the chassis
                driver_info - The driver info
                extra - Extra node parameters
                uuid - The uuid of the node
                properties - Node properties
                name - The name of the node
                network_interface - The network interface of the node
                resource_class - The resource class of the node

        Returns:
            object: ironic node
        """
        node = self._client.node.create(driver=driver, **kwargs)

        if check:
            self.check_ironic_node_presence(node)

        return node

    @step
    def delete_ironic_node(self, node, check=True):
        """Step to delete node."""
        self._client.node.delete(node.uuid)

        if check:
            self.check_ironic_node_presence(node, present=False)

    @step
    def check_ironic_node_presence(self, node, present=True, timeout=0):
        """Verify step to check ironic node is present."""
        def predicate():
            try:
                self._client.node.get(node.uuid)
                return present
            except exceptions.NotFound:
                return not present

        wait(predicate, timeout_seconds=timeout)
