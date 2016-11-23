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

from hamcrest import equal_to, assert_that, is_not, empty  # noqa
from ironicclient import exceptions

from stepler.base import BaseSteps
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

__all__ = [
    'IronicNodeSteps'
]


class IronicNodeSteps(BaseSteps):
    """Node steps."""

    @steps_checker.step
    def create_ironic_nodes(self,
                            driver='fake',
                            nodes_names=None,
                            count=1,
                            check=True,
                            **kwargs):
        """Step to create a ironic node.

        Args:
            driver (str): The name or UUID of the driver.
            nodes_names (list): names of created images, if not specified
                one image name will be generated
            count (int): count of created chassis, it's ignored if
                chassis_descriptions are specified; one chassis is created if
                both args are missing
            check (str): For checking node presence
            **kwargs (optional): A dictionary containing the attributes
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
             TimeoutExpired: if check failed after timeout

        Returns:
            object: ironic node
        """
        nodes_names = nodes_names or utils.generate_ids(count=count)
        nodes_list = []
        _nodes_names = {}

        for name in nodes_names:
            node = self._client.node.create(driver=driver, name=name, **kwargs)

            _nodes_names[node.uuid] = name
            nodes_list.append(node)

        if check:
            self.check_ironic_nodes_presence(nodes_list)
            for node in nodes_list:
                assert_that(_nodes_names[node.uuid], equal_to(name))

        return nodes_list

    @steps_checker.step
    def delete_ironic_nodes(self, nodes, check=True):
        """Step to delete node.

        Args:
            nodes (list): list of ironic nodes
            check (bool): flag whether to check step or not
        """
        for node in nodes:
            self._client.node.delete(node.uuid)

        if check:
            self.check_ironic_nodes_presence(nodes, must_present=False)

    @steps_checker.step
    def check_ironic_nodes_presence(self,
                                    nodes,
                                    must_present=True,
                                    node_timeout=0):
        """Verify step to check ironic node is present.

        Args:
            nodes (list): list of ironic nodes
            must_present (bool): flag whether node should present or not
            node_timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        expected_presence = {node.uuid: must_present for node in nodes}

        def _check_ironic_nodes_presence():
            actual_presence = {}

            for node in nodes:
                try:
                    self._client.node.get(node.uuid)
                    actual_presence[node.uuid] = True
                except exceptions.NotFound:
                    actual_presence[node.uuid] = False

            return expect_that(actual_presence, equal_to(expected_presence))

        timeout = len(nodes) * node_timeout
        waiter.wait(_check_ironic_nodes_presence, timeout_seconds=timeout)

    @steps_checker.step
    def set_ironic_nodes_maintenance(self,
                                     nodes,
                                     state,
                                     reason=None,
                                     check=True):
        """Set the maintenance mode for the nodes.

        Args:
            nodes (list): The list of ironic nodes.
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
        for node in nodes:
            self._client.node.set_maintenance(node_id=node.uuid,
                                              state=state,
                                              maint_reason=reason)
        if check:
            self.check_ironic_nodes_maintenance(nodes=nodes, state=state)

    @steps_checker.step
    def check_ironic_nodes_maintenance(self,
                                       nodes,
                                       state,
                                       node_timeout=0):
        """Check ironic node maintenance was changed.

        Args:
            nodes (list): The list of ironic nodes.
            state (Bool): the maintenance mode; either a Boolean or a string
                representation of a Boolean (eg, 'true', 'on', 'false',
                'off'). True to put the node in maintenance mode; False
                to take the node out of maintenance mode.
            node_timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        expected_maintenance = {node.maintenance: state for node in nodes}

        def _check_ironic_node_maintenance():
            actual_maintenance = {}
            for node in nodes:
                try:
                    self._client.node.get(node.maintenance)
                    actual_maintenance[node.maintenance] = True
                except exceptions.NotFound:
                    actual_maintenance[node.maintenance] = False

            return expect_that(actual_maintenance,
                               equal_to(expected_maintenance))

        timeout = len(nodes) * node_timeout
        waiter.wait(_check_ironic_node_maintenance, timeout_seconds=timeout)

    @steps_checker.step
    def set_ironic_node_power_state(self, node, state, check=True):
        """Set the power state for the node.

        Args:
            node (str): The ironic node.
            state (str): the power state mode; `on` to put the node in power
                state mode on; `off` to put the node in power state mode off;
                `reboot` to reboot the node
            check (bool): flag whether to check step or not

        Raises:
            InvalidAttribute: if state is an invalid string
        """
        self._client.node.set_power_state(node_id=node.uuid, state=state)

        if check:
            self.check_ironic_node_power_state(node=node, state=state)

    @steps_checker.step
    def check_ironic_node_power_state(self,
                                      node,
                                      state,
                                      timeout=0):
        """Check ironic node power state was changed.

        Args:
            node (str): The ironic node.
            state (str): the power state mode; `on` to put the node in power
                state mode on; `off` to put the node in power state mode off;
                `reboot` to reboot the node
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_ironic_node_power_state():
            self._get_node(node)

            if state == 'reboot':
                power_state = 'power on'
            else:
                power_state = 'power ' + state

            return expect_that(node.power_state, equal_to(power_state))

        waiter.wait(_check_ironic_node_power_state, timeout_seconds=timeout)

    def _get_node(self, node):
        node._info.update(self._client.node.get(node.uuid)._info)
        node.__dict__.update(node._info)

    @steps_checker.step
    def get_ironic_nodes(self, check=True):
        """Step to retrieve nodes.

        Returns:
            list of objects: list of nodes.

        Raises:
            AssertionError: if nodes collection is empty.
        """
        nodes_list = self._client.node.list()

        if check:
            assert_that(nodes_list, is_not(empty()))

        return nodes_list
