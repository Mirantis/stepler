"""
Flavor steps.

@author: schipiga@mirantis.com
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

from stepler.steps import BaseSteps, step

__all__ = [
    'FlavorSteps'
]


class FlavorSteps(BaseSteps):
    """Flavor steps."""

    @step
    def create_flavor(self, flavor_name, check=True):
        """Step to create flavor."""
        flavor = self._client.create(flavor_name)

        if check:
            self.check_flavor_presence(flavor)

        return flavor

    @step
    def delete_flavor(self, flavor, check=True):
        """Step to delete flavor."""
        self._client.delete(flavor.id)

        if check:
            self.check_flavor_presence(flavor, present=False)

    @step
    def check_flavor_presence(self, flavor, present=True, timeout=0):
        """Verify step to check flavor is present."""
        def predicate():
            try:
                self._client.get(flavor.id)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)

    @step
    def find(self, *args, **kwgs):
        """Step to find flavor."""
        return self._client.find(*args, **kwgs)
