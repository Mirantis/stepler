"""
---------------
os_faults steps
---------------
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

from hamcrest import assert_that, is_not, empty  # noqa

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = [
    'OsFaultsSteps'
]


class OsFaultsSteps(BaseSteps):
    """os faults steps."""

    @step
    def get_nodes(self, check=True):
        """Step to get nodes.

        Args:
            check (bool): flag whether to check step or not

        Returns:
            list of nodes
        """
        nodes = self._client.get_nodes()

        if check:
            assert_that(nodes, is_not(empty()))

        return nodes

    @step
    def restart_service(self, name, check=True):
        """Step to restart a service.

        Args:
            name (str): service name
            check (bool): flag whether to check step or not
        """
        service = self._client.get_service(name=name)
        service.restart()

        if check:
            # TODO(ssokolov) replace by real check
            assert_that([service], is_not(empty()))
