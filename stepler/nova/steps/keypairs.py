"""
-------------
Keypair steps
-------------
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
from stepler.third_party.steps_checker import step

__all__ = [
    'KeypairSteps'
]


class KeypairSteps(BaseSteps):
    """Keypair steps."""

    @step
    def create_keypair(self, keypair_name, check=True):
        """Step to create keypair."""
        keypair = self._client.create(keypair_name)

        if check:
            self.check_keypair_presence(keypair)

        return keypair

    @step
    def delete_keypair(self, keypair, check=True):
        """Step to delete keypair."""
        self._client.delete(keypair.id)

        if check:
            self.check_keypair_presence(keypair, present=False)

    @step
    def check_keypair_presence(self, keypair, present=True, timeout=0):
        """Verify step to check keypair is present."""
        def predicate():
            try:
                self._client.get(keypair.id)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)
