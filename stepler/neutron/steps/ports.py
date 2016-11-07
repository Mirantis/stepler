"""
----------
Port steps
----------
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

import waiting

from stepler import base
from stepler.third_party import steps_checker

__all__ = ["PortSteps"]


class PortSteps(base.BaseSteps):
    """Port steps."""

    @steps_checker.step
    def create(self, network, check=True):
        """Step to create port.

        Args:
            network (dict): network to create port on
            check (bool): flag whether to check step or not

        Returns:
            dict: port
        """
        port = self._client.create(network_id=network['id'])
        if check:
            self.check_presence(port)
        return port

    @steps_checker.step
    def delete(self, port, check=True):
        """Step to create port.

        Args:
            port (dict): port to delete
            check (bool): flag whether to check step or not
        """
        self._client.delete(port['id'])
        if check:
            self.check_presence(port, present=False)

    @steps_checker.step
    def check_presence(self, port, present=True, timeout=0):
        """Verify step to check port is present.

        Args:
            port (dict): neutron port to check presence status
            present (bool): flag whether port should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was triggered to an error after timeout
        """

        def predicate():
            exists = bool(self._client.find_all(id=port['id']))
            return exists == present

        waiting.wait(predicate, timeout_seconds=timeout)
