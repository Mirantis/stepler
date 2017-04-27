"""
--------------------
Ironic chassis steps
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

from hamcrest import assert_that, equal_to, is_not, empty  # noqa
from ironicclient import exceptions

from stepler.base import BaseSteps
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

__all__ = [
    'IronicChassisSteps'
]


class IronicChassisSteps(BaseSteps):
    """Chassis steps."""

    @steps_checker.step
    def create_ironic_chassis(self, descriptions=None, count=1, check=True):
        """Step to create a ironic chassis.

        Args:
            descriptions (list): descriptions of created chassis, if not
                specified one chassis description will be generate
            count (int): count of created chassis, it's ignored if
                chassis_descriptions are specified; one chassis is created if
                both args are missing
            check (str): flag for checking chassis presence

        Raises:
             TimeoutExpired: if check was triggered to False after timeout

        Returns:
            list: list of the created chassis or None in case of exception,
            and an exception, if it appears.
        """
        descriptions = descriptions or list(utils.generate_ids(count=count))
        chassis_list = []
        _chassis_descriptions = {}

        for description in descriptions:
            chassis = self._client.create(description=description)

            _chassis_descriptions[chassis.uuid] = description
            chassis_list.append(chassis)

        if check:
            self.check_ironic_chassis_presence(chassis_list)
            for chassis in chassis_list:
                assert_that(chassis.description,
                            equal_to(_chassis_descriptions[chassis.uuid]))

        return chassis_list

    @steps_checker.step
    def delete_ironic_chassis(self, chassis_list, check=True):
        """Step to delete chassis.

        Args:
            chassis_list (list): list of ironic chassis
            check (bool): flag whether to check step or not
        """
        for chassis in chassis_list:
            self._client.delete(chassis.uuid)

        if check:
            self.check_ironic_chassis_presence(chassis_list,
                                               must_present=False)

    @steps_checker.step
    def check_ironic_chassis_presence(self,
                                      chassis_list,
                                      must_present=True,
                                      chassis_timeout=0):
        """Verify step to check ironic chassis is present.

        Args:
            chassis_list (list): list of ironic chassis to check presence
                status
            must_present (bool): flag whether chassis should present or not
            chassis_timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        expected_presence = {chassis.uuid: must_present
                             for chassis in chassis_list}

        def _check_chassis_presence():
            actual_presence = {}

            for chassis in chassis_list:
                try:
                    self._client.get(chassis.uuid)
                    actual_presence[chassis.uuid] = True
                except exceptions.NotFound:
                    actual_presence[chassis.uuid] = False

            return waiter.expect_that(actual_presence,
                                      equal_to(expected_presence))

        timeout = len(chassis_list) * chassis_timeout
        waiter.wait(_check_chassis_presence, timeout_seconds=timeout)

    @steps_checker.step
    def get_ironic_chassis(self, check=True):
        """Step to retrieve chassis.

        Returns:
            list of objects: list of chassis.

        Raises:
            AssertionError: if chassis collection is empty.
        """
        chassis_list = self._client.list()

        if check:
            assert_that(chassis_list, is_not(empty()))

        return chassis_list
