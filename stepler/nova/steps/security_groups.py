"""
--------------------
Security group steps
--------------------
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

from hamcrest import assert_that, has_item, has_entries  # noqa
from waiting import wait

from stepler.base import BaseSteps
from stepler.third_party import steps_checker

__all__ = [
    'SecurityGroupSteps'
]


class SecurityGroupSteps(BaseSteps):
    """Security group steps."""

    @steps_checker.step
    def create_group(self, group_name=None, description='description',
                     check=True):
        """Step to create security group.

        Args:
            group_name (str): security group name
            description (str, optional): security group description
            check (bool, optional): flag whether to check this step or not

        Returns:
            obj: security group

        Raises:
            AssertionError: if check failed
        """
        group = self._client.security_groups.create(group_name, description)

        if check:
            self.check_group_presence(group)

        return group

    @steps_checker.step
    def add_group_rules(self, group, rules, check=True):
        """Step to add rules to security group."""
        rule_objects = []
        for rule in rules:
            rule = self._client.security_group_rules.create(group.id, **rule)
            rule_objects.append(rule)

        if check:
            for rule in rules:
                self.check_rule_presence(group, rule)

        return rule_objects

    @steps_checker.step
    def remove_group_rules(self, group, rules, check=True):
        """Step to remove rule from security group."""
        for rule in rules:
            self._client.security_group_rules.delete(rule)

        if check:
            for rule in rules:
                self.check_rule_presence(group, rule, present=False)

    @steps_checker.step
    def delete_group(self, group, check=True):
        """Step to delete security group."""
        self._client.security_groups.delete(group)

        if check:
            self.check_group_presence(group, present=False)

    @steps_checker.step
    def check_group_presence(self, group, present=True, timeout=0):
        """Verify step to check security group is present."""
        def predicate():
            try:
                self._client.security_groups.get(group.id)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def check_rule_presence(self, group, rule, present=True, timeout=0):
        """Verify step to check security group rule is present."""

        group_id = group.id
        if hasattr(rule, 'id'):
            rule_to_check = {'to_port': rule.to_port,
                             'from_port': rule.from_port,
                             'ip_protocol': rule.ip_protocol,
                             'ip_range': rule.ip_range}
        else:
            rule_to_check = rule.copy()
            cidr = rule_to_check.pop('cidr')
            rule_to_check['ip_range'] = {'cidr': cidr}

        def predicate():
            try:
                group = self._client.security_groups.get(group_id)
                assert_that(group.rules, has_item(has_entries(rule_to_check)))
                return present
            except AssertionError:
                return not present

        wait(predicate, timeout_seconds=timeout)
