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

from hamcrest import assert_that, equal_to  # noqa
from ironicclient import exceptions

from stepler.base import BaseSteps
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = [
    'IronicChassisSteps'
]


class IronicChassisSteps(BaseSteps):
    """Chassis steps."""

    @steps_checker.step
    def create_ironic_chassis(self, check=True):
        """Step to create a ironic chassis.

        Args:
            check (str): For checking chassis presence

        Raises:
             TimeoutExpired: if check was triggered to False after timeout

        Returns:
            object: UUID of the created chassis or None in case of exception,
            and an exception, if it appears.
        """
        chassis = self._client.chassis.create()
        if check:
            self.check_ironic_chassis_presence(chassis)

        return chassis

    @steps_checker.step
    def delete_ironic_chassis(self, chassis, check=True):
        """Step to delete chassis.

        Args:
            chassis (object): ironic chassis
            check (bool): flag whether to check step or not
        """
        self._client.chassis.delete(chassis.uuid)

        if check:
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
                self._client.chassis.get(chassis.uuid)
                is_present = True
            except exceptions.NotFound:
                is_present = False

            return expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_ironic_chassis_presence, timeout_seconds=timeout)
