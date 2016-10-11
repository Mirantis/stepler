"""
------------
Domain steps
------------
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
    'DomainSteps'
]


class DomainSteps(BaseSteps):
    """Domain steps."""

    @step
    def create_domain(self, domain_name, check=True):
        """Step to create domain."""
        domain = self._client.create(domain_name)

        if check:
            self.check_domain_presence(domain)

        return domain

    @step
    def delete_domain(self, domain, check=True):
        """Step to delete domain."""
        self._client.update(domain, enabled=False)
        self._client.delete(domain.id)

        if check:
            self.check_domain_presence(domain, present=False)

    @step
    def check_domain_presence(self, domain, present=True, timeout=0):
        """Verify step to check domain is present."""
        def predicate():
            try:
                self._client.get(domain.id)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)
