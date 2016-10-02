"""
Security group steps.

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

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = [
    'SecurityGroupSteps'
]


class SecurityGroupSteps(BaseSteps):
    """Security group steps."""

    @step
    def create_group(self, group_name, description='', check=True):
        """Step to create security group."""
        group = self._client.security_groups.create(group_name, description)

        if check:
            self.check_group_presence(group)

        return group

    @step
    def add_group_rules(self, group, rules, check=True):
        """Step to add rules to security group."""
        for rule in rules:
            self._client.security_group_rules.create(group.id, **rule)

        if check:
            for rule in rules:
                self.check_rule_presence(group, rule)

    @step
    def delete_group(self, group, check=True):
        """Step to delete security group."""
        self._client.security_groups.delete(group)

        if check:
            self.check_group_presence(group, present=False)

    @step
    def check_group_presence(self, group, present=True, timeout=0):
        """Verify step to check security group is present."""
        def predicate():
            try:
                self._client.security_groups.get(group.id)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)

    @step
    def check_rule_presence(self, group, rule, present=True, timeout=0):
        """Verify step to check security group is present."""
        def predicate():
            try:
                self._client.security_group_rules.get(group, rule)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)
