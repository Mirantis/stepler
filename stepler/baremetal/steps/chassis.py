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
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

__all__ = [
    'IronicChassisSteps'
]


class IronicChassisSteps(BaseSteps):
    """Chassis steps."""

    @steps_checker.step
    def create_ironic_chassis(self, descriptions=None, check=True):
        """Step to create a ironic chassis.

        Args:
            descriptions (list): descriptions of created chassis, if not
                specified one chassis description will be generate
            check (str): For checking chassis presence

        Raises:
             TimeoutExpired: if check was triggered to False after timeout

        Returns:
            list: list of the created chassis or None in case of exception,
            and an exception, if it appears.
        """
        descriptions = descriptions or utils.generate_ids('test')
        chassis_list = []
        _chassis_descriptions = {}

        for description in descriptions:
            chassis = self._client.create(description=description)

            _chassis_descriptions[chassis.uuid] = description
            chassis_list.append(chassis)

        if check:
            for chassis, description in zip(chassis_list, descriptions):
                self.check_ironic_chassis_presence(chassis)
                assert_that(chassis.description, equal_to(description))

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
            for chassis in chassis_list:
                self.check_ironic_chassis_presence(chassis, must_present=False)

    @steps_checker.step
    def check_ironic_chassis_presence(self,
                                      chassis,
                                      must_present=True,
                                      timeout=0):
        """Verify step to check ironic chassis is present.

        Args:
            chassis (object): ironic chassis to check presence status
            must_present (bool): flag whether chassis should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """

        def _check_ironic_chassis_presence():
            try:
                self._client.get(chassis.uuid)
                is_present = True
            except exceptions.NotFound:
                is_present = False

            return expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_ironic_chassis_presence, timeout_seconds=timeout)

    @steps_checker.step
    def get_ironic_chassis(self, check=True):
        """List all the chassis for a given chassis.

        Returns:
            list of objects: List of chassis.

        Raises:
            AssertionError: If chassis collection is empty.
        """
        chassis_list = self._client.list()

        if check:
            assert_that(chassis_list, is_not(empty()))

        return chassis_list
