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

from hamcrest import assert_that, empty, is_not  # noqa

from stepler import base
from stepler.third_party import steps_checker

__all__ = ["AgentSteps"]


class AgentSteps(base.BaseSteps):
    """Agent steps."""

    @steps_checker.step
    def get_agents(self, name=None, host_name=None, alive=None, check=True):
        """Step to get neutron agents using filters.

        Args:
            name (str|None): agent name, ex: neutron-l3-agent
            host_name (str|None): host name
            alive (bool|None): agent state (alive or not)
            check (bool): flag whether to check step or not

        Returns:
            list: list of agents data (dict - binary, host, alive etc.)

        Raises:
            AssertionError: if agent list is empty
        """
        agents = self._client.list_agents(name=name)

        if host_name:
            agents = [agent for agent in agents if agent['host'] == host_name]

        if alive is not None:
            agents = [agent for agent in agents if agent['alive'] == alive]

        if check:
            assert_that(agents, is_not(empty()))

        return agents
