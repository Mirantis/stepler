"""
--------------------------
Security group rules steps
--------------------------
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

from hamcrest import (assert_that, calling, empty, equal_to, has_entries,
                      is_not, raises)  # noqa H301
from neutronclient.common import exceptions

from stepler import base
from stepler import config
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = ["NeutronSecurityGroupRuleSteps"]


class NeutronSecurityGroupRuleSteps(base.BaseSteps):
    """Security group rules steps."""

    @steps_checker.step
    def get_rules(self, check=True, **kwargs):
        """Step to get security group rules.

        Args:
            check (bool): flag whether to check step or not
            **kwargs: params to list security group rules

        Returns:
            list: security group rules

        Raises:
            AssertionError: if no rules found or rule belongs to unexpected
                security group
        """
        rules = self._client.find_all(**kwargs)

        if check:
            assert_that(rules, is_not(empty()))
            if kwargs:
                for rule in rules:
                    assert_that(rule, has_entries(kwargs))

        return rules

    @steps_checker.step
    def delete_rule_from_group(self, rule_id, group_id, check=True):
        """Step to delete rule from security group.

        Args:
            rule_id (str): id of security group rule
            group_id (str): id of security group
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        self._client.delete(rule_id)
        if check:
            self.check_rule_presence(rule_id, group_id, must_present=False)

    @steps_checker.step
    def check_rule_presence(self, rule_id, group_id, must_present=True):
        """Step to check rule presence for security group.

        Args:
            rule_id (str): id of security group rule
            group_id (str): id of security group
            must_present (bool): flag whether rule must present or not

        Raises:
            AssertionError: if check failed after timeout
        """
        def _check_presence():
            is_present = bool(self._client.find_all(
                security_group_id=group_id,
                id=rule_id))
            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(
            _check_presence,
            timeout_seconds=config.NEUTRON_UPDATE_SEC_GROUP_RULES_TIMEOUT)

    @steps_checker.step
    def add_rule_to_group(self, group_id, check=True, **rule_params):
        """Step to add rule to security group.

        Args:
            group_id (str): id of security group
            check (bool): flag whether to check step or not
            **rule_params (dict, optional): could be:

                * direction (str): 'egress' or 'ingress'
                * security_group_id (str): id or name of security group
                * ethertype (str): 'IPv4' or 'IPv6'
                * protocol (str): icmp, icmpv6, tcp, udp
                * port_range_min (int|None): starting port range
                * port_range_max (int|None): ending port range
                * remote_ip_prefix (str): cidr
                * remote-group-id (str): id or name of the remote security
                    group

        Raises:
            AssertionError: if check failed
        """
        rule = self._client.create(**rule_params)

        if check:
            self.check_rule_presence(rule['id'], group_id)
            assert_that(rule, has_entries(rule_params))

        return rule

    @steps_checker.step
    def check_negative_create_extra_group_rule(self, group_id, **rule_params):
        """Step to check that unable to add group rules more than quota allows.

        Args:
            group_id (str): id of security group
            **rule_params (dict, optional): rule parameters

        Raises:
            AssertionError: if no OverQuotaClient exception occurs or exception
                message is not expected
        """
        exception_message = "Quota exceeded for resources"
        assert_that(calling(self.add_rule_to_group).with_args(group_id,
                                                              check=False,
                                                              **rule_params),
                    raises(exceptions.OverQuotaClient, exception_message))
