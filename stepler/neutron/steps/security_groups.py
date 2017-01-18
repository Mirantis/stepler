"""
-----------------------------
Neutron security groups steps
-----------------------------
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
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

__all__ = ["NeutronSecurityGroupSteps"]


class NeutronSecurityGroupSteps(base.BaseSteps):
    """Neutron security group steps."""

    @steps_checker.step
    def create(self, group_name=None, description=None, check=True):
        """Step to create security group.

        Args:
            group_name (str): security group name
            description (str): security group description
            check (bool): flag whether to check step or not

        Returns:
            dict: security group
        """
        group_name = group_name or next(utils.generate_ids())
        description = description or ''
        group = self._client.create(name=group_name, description=description)

        if check:
            self.check_presence(group)
            if group_name:
                assert_that(group['name'], equal_to(group_name))
            if description:
                assert_that(group['description'], equal_to(description))

        return group

    @steps_checker.step
    def check_presence(self, group, must_present=True, timeout=0):
        """Verify step to check security group is present.

        Args:
            group (dict): security group to check presence status
            must_present (bool): flag whether group must present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_group_presence():
            is_present = bool(self._client.find_all(id=group['id']))
            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_group_presence, timeout_seconds=timeout)

    @steps_checker.step
    def delete(self, group, check=True):
        """Step to delete security group.

        Args:
            group (dict): security group
            check (bool): flag whether to check step or not
        """
        self._client.delete(group['id'])

        if check:
            self.check_presence(group, must_present=False)

    @steps_checker.step
    def get_security_groups(self, check=True, **kwargs):
        """Step to get all security groups.

        Args:
            check (bool): flag whether to check step or not
            **kwargs: params to list security groups

        Returns:
            list: security groups

        Raises:
            AssertionError: if group list is empty or doesn't correspond to
                given filter
        """
        groups = self._client.find_all(**kwargs)

        if check:
            assert_that(groups, is_not(empty()))
            if kwargs:
                for group in groups:
                    assert_that(group, has_entries(kwargs))

        return groups

    @steps_checker.step
    def check_negative_create_extra_security_group(self):
        """Step to check that unable to create security groups more than quota.

        Raises:
            AssertionError: if no OverQuotaClient exception occurs or exception
                message is not expected
        """
        exception_message = "Quota exceeded for resources"
        assert_that(
            calling(self.create).with_args(check=False),
            raises(exceptions.OverQuotaClient, exception_message),
            "Security group has been created though it exceeds the quota "
            "or OverQuotaClient exception with expected error message "
            "has not been appeared")
