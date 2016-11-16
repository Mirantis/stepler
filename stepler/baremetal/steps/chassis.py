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
        chassis = self._client.create()
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
        self._client.delete(chassis.uuid)

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
                self._client.get(chassis.uuid)
                is_present = True
            except exceptions.NotFound:
                is_present = False

            return expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_ironic_chassis_presence, timeout_seconds=timeout)

    @steps_checker.step
    def get_ironic_chassis(self,
                    marker=None,
                    limit=None,
                    sort_key=None,
                    sort_dir=None,
                    detail=False,
                    fields=None,
                    check=True):
        """List all the chassis for a given chassis.

        Args:
            marker (str, optional): the UUID of a node, eg the last node from
                a previous result set. Return the next result set.
            limit (int): The maximum number of results to return per
                request, if:
                   1) limit > 0, the maximum number of chassis to return.
                   2) limit == 0, return the entire list of chassis.
                   3) limit param is NOT specified (None), the number of items
                      returned respect the maximum imposed by the Ironic API
                      (see Ironic's api.max_limit option).
            sort_key (str, optional): field used for sorting.
            sort_dir (str, optional): direction of sorting, either 'asc' (the
                default) or 'desc'.
            detail (str, optional): boolean whether to return detailed
                information about chassis.
            fields (str, optional): a list with a specified set of fields
                of the resource to be returned. Can not be used when `detail`
                is set.
            check (bool, optional): Flag whether to check step or not.

        Returns:
            list of objects: A list of chassis.

        Raises:
            AssertionError: If chassis collection is empty.
        """
        chassis = self._client.list(marker=marker,
                                            limit=limit,
                                            sort_key=sort_key,
                                            sort_dir=sort_dir,
                                            detail=detail,
                                            fields=fields)
        if marker:
            pass
        if limit:
            pass
        if sort_key:
            pass
        if sort_dir:
            pass
        if detail:
            pass
        if fields:
            pass

        if check:
            assert_that(chassis, is_not(empty()))

        return chassis