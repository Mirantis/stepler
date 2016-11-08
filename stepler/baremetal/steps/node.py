"""
-----------------
Ironic node steps
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

from hamcrest import assert_that, equal_to  # noqa
from ironicclient import exceptions

from stepler.base import BaseSteps
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = [
    'IronicNodeSteps'
]


class IronicNodeSteps(BaseSteps):
    """Node steps."""

    @steps_checker.step
    def create_ironic_node(self, driver='fake', check=True, **kwargs):
        """Step to create a ironic node.

        Args:
            driver (str): The name or UUID of the driver.
            check (str): For checking node presence
            kwargs: Optional. A dictionary containing the attributes
            of the resource that will be created:
                chassis_uuid - The uuid of the chassis
                driver_info - The driver info
                extra - Extra node parameters
                uuid - The uuid of the node
                properties - Node properties
                name - The name of the node
                network_interface - The network interface of the node
                resource_class - The resource class of the node

        Raises:
             TimeoutExpired: if check was triggered to False after timeout

        Returns:
            object: ironic node
        """
        node = self._client.node.create(driver=driver, **kwargs)

        if check:
            self.check_ironic_node_presence(node)

        return node

    @steps_checker.step
    def delete_ironic_node(self, node, check=True):
        """Step to delete node.

        Args:
            node (object): ironic node
            check (bool): flag whether to check step or not
        """
        self._client.node.delete(node.uuid)

        if check:
            self.check_ironic_node_presence(node, must_present=False)

    @steps_checker.step
    def check_ironic_node_presence(self,
                                   node,
                                   must_present=True,
                                   timeout=0):
        """Verify step to check ironic node is present.

        Args:
            node (object): ironic node to check presence status
            must_present (bool): flag whether node should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was triggered to False after timeout
        """
        def predicate():
            try:
                self._client.node.get(node.uuid)
                is_present = True
            except exceptions.NotFound:
                is_present = False

            return expect_that(is_present, equal_to(must_present))

        waiter.wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def set_ironic_node_maintenance(self,
                                    node,
                                    state,
                                    reason=None,
                                    check=True):
        """Set the maintenance mode for the node.

        Args:
            node (str): The ironic node.
            state (Bool): the maintenance mode; either a Boolean or a string
                representation of a Boolean (eg, 'true', 'on', 'false',
                'off'). True to put the node in maintenance mode; False
                to take the node out of maintenance mode.
            reason (str): Optional string. Reason for putting node
                into maintenance mode.
            check (bool): flag whether to check step or not

        Raises:
            InvalidAttribute: if state is an invalid string
        """
        self._client.node.set_maintenance(node_id=node.uuid,
                                          state=state, maint_reason=reason)
        if check:
            self.check_ironic_node_maintenance(node=node, state=state)

    @steps_checker.step
    def check_ironic_node_maintenance(self,
                                      node,
                                      state,
                                      timeout=0):
        """Check ironic node maintenance was changed.

        Args:
            node (str): The ironic node.
            state (Bool): the maintenance mode; either a Boolean or a string
                representation of a Boolean (eg, 'true', 'on', 'false',
                'off'). True to put the node in maintenance mode; False
                to take the node out of maintenance mode.
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was triggered to to an error after timeout
        """
        def predicate():
            node.get()
            return expect_that(node.maintenance, equal_to(state))

        waiter.wait(predicate, timeout_seconds=timeout)
