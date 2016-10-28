"""
-----------------
Floating IP steps
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

from waiting import wait

from stepler.base import BaseSteps
from stepler.third_party import steps_checker

__all__ = [
    'FloatingIpSteps'
]


class FloatingIpSteps(BaseSteps):
    """Floating IP steps."""

    @steps_checker.step
    def create_floating_ip(self, check=True):
        """Step to create floating IP."""
        floating_ip_pools = self._client.floating_ip_pools.list()
        assert floating_ip_pools

        floating_ip = self._client.floating_ips.create(
            pool=floating_ip_pools[0].name)

        if check:
            self.check_floating_ip_presence(floating_ip)

        return floating_ip

    @steps_checker.step
    def delete_floating_ip(self, floating_ip, check=True):
        """Step to delete floating IP."""
        self._client.floating_ips.delete(floating_ip)

        if check:
            self.check_floating_ip_presence(floating_ip, present=False)

    @steps_checker.step
    def check_floating_ip_presence(self, floating_ip, present=True, timeout=0):
        """Verify step to check floating IP is present."""
        def predicate():
            try:
                self._client.floating_ips.get(floating_ip.id)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)
