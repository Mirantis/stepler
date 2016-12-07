"""
-----------
Agent steps
-----------
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

from hamcrest import (assert_that, empty, is_in, is_not, only_contains,
                      has_entries, has_length)  # noqa H301

from stepler import base
from stepler import config
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = ["AgentSteps"]


class AgentSteps(base.BaseSteps):
    """Agent steps."""

    @steps_checker.step
    def get_agents(self, node=None, check=True, **kwargs):
        """Step to get agents by params in '**kwargs'.

        Args:
            node (obj): NodeCollection instance to get agents. If node
                parameter is defined, 'host' parameter can't be used
                in **kwargs
            check (bool, optional): flag whether to check step or not
            **kwargs: additional arguments to pass to API

        Returns:
            list: neutron agents

        Raises:
            AssertionError: if list of agents is empty
        """
        if node:
            assert_that('host', is_not(is_in(kwargs)))
            kwargs['host'] = node.get_fqdns()[0]

        agents = list(self._client.find_all(**kwargs))
        if check:
            assert_that(agents, is_not(empty()))
        return agents

    @steps_checker.step
    def check_alive(self, agents, must_alive=True, timeout=0):
        """Verify step to check ``agents`` aliveness status.

        Args:
            agents (list): neutron agents to check status
            must_alive (bool, optional): flag whether all agents should be
                alive or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        agents_ids = [agent['id'] for agent in agents]

        def _check_agents_alive():
            agents = [
                agent for agent in self.get_agents()
                if agent['id'] in agents_ids
            ]
            return waiter.expect_that(agents, only_contains(
                has_entries(alive=must_alive)))

        waiter.wait(_check_agents_alive, timeout_seconds=timeout)

    @steps_checker.step
    def get_dhcp_agents_for_net(self, network, filter_attrs=None, check=True):
        """Step to retrieve network DHCP agents dicts list.

        Args:
            network (dict): network to get DHCP agents
            filter_attrs (dict, optional): filter attrs dict to return only
                matched dhcp_agents
            check (bool, optional): flag whether to check step or not

        Returns:
            list: list of DHCP agents dicts for network

        Raises:
            AssertionError: if list of agents is empty
        """
        filter_attrs = filter_attrs or {}
        dhcp_agents = self._client.get_dhcp_agents_for_network(network['id'])
        for key, prop in filter_attrs.items():
            dhcp_agents = [agent for agent in dhcp_agents
                           if agent[key] == prop]
        if check:
            assert_that(dhcp_agents, is_not(empty()))
            if filter_attrs:
                assert_that(dhcp_agents, only_contains(
                    has_entries(**filter_attrs)))

        return dhcp_agents

    @steps_checker.step
    def get_dhcp_agents_not_hosting_net(self, network, check=True):
        """Step to retrieve DHCP agents which are not hosting network.

        Args:
            network (dict): network to get DHCP agents which can't be used
            check (bool, optional): flag whether to check step or not

        Returns:
            list: list of DHCP agents which are not hosting network

        Raises:
            AssertionError: if list of agents is empty
        """
        all_dhcp_agents = self.get_agents(binary=config.NEUTRON_DHCP_SERVICE)

        dhcp_agents = self._client.get_dhcp_agents_for_network(network['id'])
        dhcp_agents_ids = [agent['id'] for agent in dhcp_agents]

        free_agents = [agent for agent in all_dhcp_agents
                       if agent['id'] not in dhcp_agents_ids]

        if check:
            assert_that(free_agents, is_not(empty()))

        return free_agents

    @steps_checker.step
    def check_agents_count_for_net(self, network, expected_count):
        """Step to check DHCP agents count for network.

        Args:
            network (dict): network to check
            expected_count (int): expected DHCP agents count for network

        Raises:
            AssertionError: if check failed
        """
        dhcp_agents = self.get_dhcp_agents_for_net(network, check=False)
        assert_that(dhcp_agents, has_length(expected_count))

    @steps_checker.step
    def check_network_rescheduled(self, network, old_dhcp_agent, timeout=0):
        """Step to check that network was rescheduled.

        Args:
            network (dict): network to check
            old_dhcp_agent (dict): DHCP agent before rescheduling
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_network_rescheduled():
            dhcp_agents = self._client.get_dhcp_agents_for_network(
                network['id'])
            dhcp_agents_ids = [agent['id'] for agent in dhcp_agents]
            return waiter.expect_that(old_dhcp_agent['id'],
                                      is_not(is_in(dhcp_agents_ids)))

        waiter.wait(_check_network_rescheduled, timeout_seconds=timeout)

    @steps_checker.step
    def check_network_is_on_agent(self, network, dhcp_agent, timeout=0):
        """Step to check that network is on DHCP agent.

        Args:
            network (dict): network to check
            dhcp_agent (dict): DHCP agent to check
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_network_is_on_agent():
            dhcp_agents = self._client.get_dhcp_agents_for_network(
                network['id'])
            return waiter.expect_that(dhcp_agent, is_in(dhcp_agents))

        waiter.wait(_check_network_is_on_agent, timeout_seconds=timeout)

    @steps_checker.step
    def get_l3_agents_for_router(self, router, filter_attrs=None, check=True):
        """Step to retrieve router L3 agents dicts list.

        Args:
            router (dict): router to get L3 agents
            filter_attrs (dict, optional): filter attrs dict to return only
                matched l3_agents
            check (bool, optional): flag whether to check step or not

        Returns:
            list: list of L3 agents dicts for router

        Raises:
            AssertionError: if list of agents is empty
        """
        filter_attrs = filter_attrs or {}
        l3_agents = self._client.get_l3_agents_for_router(router['id'])
        for key, prop in filter_attrs.items():
            l3_agents = [agent for agent in l3_agents if agent[key] == prop]
        if check:
            assert_that(l3_agents, is_not(empty()))
            if filter_attrs:
                assert_that(l3_agents, only_contains(
                    has_entries(**filter_attrs)))

        return l3_agents

    @steps_checker.step
    def check_router_rescheduled(self, router, old_l3_agent, timeout=0):
        """Verify step to check that router was rescheduled.

        Args:
            router (dict): router to check
            old_l3_agent (dict): L3 agent before rescheduling
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_router_rescheduled():
            l3_agents = self._client.get_l3_agents_for_router(router['id'])
            return waiter.expect_that(old_l3_agent, is_not(is_in(l3_agents)))

        waiter.wait(_check_router_rescheduled, timeout_seconds=timeout)

    @steps_checker.step
    def check_l3_ha_router_rescheduled(self, router, old_l3_agent, timeout=0):
        """Verify step to check that l3 ha router was rescheduled.

        Args:
            router (obj): router to check
            old_l3_agent (dict): l3 agent before rescheduling
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """

        def _check_router_rescheduled():
            l3_agents = self.get_l3_agents_for_router(
                router, filter_attrs=config.HA_STATE_ACTIVE_ATTRS, check=False)
            waiter.expect_that(l3_agents, is_not(empty()))
            waiter.expect_that(old_l3_agent, is_not(is_in(l3_agents)))
            return l3_agents

        waiter.wait(_check_router_rescheduled, timeout_seconds=timeout)

    @steps_checker.step
    def remove_network_from_dhcp_agent(self, dhcp_agent, network, timeout=0,
                                       check=True):
        """Step to remove network from DHCP agent.

        Args:
            dhcp_agent (dict): DHCP agent to remove network from
            network (dict): network to remove from DHCP agent
            timeout (int): seconds to wait a result of check
            check (bool, optional): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        self._client.remove_network_from_dhcp_agent(dhcp_agent['id'],
                                                    network['id'])
        if check:
            self.check_network_rescheduled(network,
                                           dhcp_agent,
                                           timeout=timeout)

    @steps_checker.step
    def add_network_to_dhcp_agent(self, dhcp_agent, network, timeout=0,
                                  check=True):
        """Step to add network to DHCP agent.

        Args:
            dhcp_agent (dict): DHCP agent to add network to
            network (dict): network to add to DHCP agent
            timeout (int): seconds to wait a result of check
            check (bool, optional): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        self._client.add_network_to_dhcp_agent(dhcp_agent['id'], network['id'])

        if check:
            self.check_network_is_on_agent(network,
                                           dhcp_agent,
                                           timeout=timeout)

    @steps_checker.step
    def reschedule_network_to_dhcp_agent(self,
                                         target_dhcp_agent,
                                         network,
                                         timeout=0,
                                         check=True):
        """Step to reschedule network's active DHCP agent.

        Args:
            target_dhcp_agent (dict): DHCP agent to reschedule network to
            network (dict): network to be rescheduled
            timeout (int): seconds to wait a result of check
            check (bool, optional): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        active_agents = self.get_dhcp_agents_for_net(network)

        if target_dhcp_agent not in active_agents:
            agent_to_remove = active_agents[0]
            self.remove_network_from_dhcp_agent(agent_to_remove,
                                                network,
                                                timeout=timeout,
                                                check=check)
            self.add_network_to_dhcp_agent(target_dhcp_agent,
                                           network,
                                           timeout=timeout,
                                           check=check)

    @steps_checker.step
    def check_router_is_on_agent(self, router, l3_agent, timeout=0):
        """Step to check that router is on L3 agent.

        Args:
            router (dict): router to check
            l3_agent (dict): L3 agent to check
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_router_is_on_agent():
            l3_agents = self.get_l3_agents_for_router(router, check=False)
            return waiter.expect_that(l3_agent, is_in(l3_agents))

        waiter.wait(_check_router_is_on_agent, timeout_seconds=timeout)

    @steps_checker.step
    def remove_router_from_l3_agent(self, l3_agent, router, timeout=0,
                                    check=True):
        """Step to remove router from L3 agent.

        Args:
            l3_agent (dict): L3 agent to remove router from
            router (dict): router to remove from L3 agent
            timeout (int): seconds to wait a result of check
            check (bool, optional): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        self._client.remove_router_from_l3_agent(l3_agent['id'],
                                                 router['id'])
        if check:
            self.check_router_rescheduled(router,
                                          l3_agent,
                                          timeout=timeout)

    @steps_checker.step
    def add_router_to_l3_agent(self, l3_agent, router, timeout=0, check=True):
        """Step to add router to L3 agent.

        Args:
            l3_agent (dict): L3 agent to add router to
            router (dict): router to add to L3 agent
            timeout (int): seconds to wait a result of check
            check (bool, optional): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        self._client.add_router_to_l3_agent(l3_agent['id'], router['id'])

        if check:
            self.check_router_is_on_agent(router,
                                          l3_agent,
                                          timeout=timeout)

    @steps_checker.step
    def reschedule_router_to_l3_agent(self,
                                      target_l3_agent,
                                      router,
                                      timeout=0,
                                      check=True):
        """Step to reschedule router's active L3 agent.

        Args:
            target_l3_agent (dict): L3 agent to reschedule router to
            router (dict): router to be rescheduled
            timeout (int): seconds to wait a result of check
            check (bool, optional): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        active_agents = self.get_l3_agents_for_router(router)

        if target_l3_agent not in active_agents:
            agent_to_remove = active_agents[0]
            self.remove_router_from_l3_agent(agent_to_remove,
                                             router,
                                             timeout=timeout,
                                             check=check)
            self.add_router_to_l3_agent(target_l3_agent,
                                        router,
                                        timeout=timeout,
                                        check=check)
