"""
------------
Volume steps
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

from cinderclient import exceptions
from hamcrest import assert_that, is_not, empty, equal_to  # noqa

from stepler import base
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = ['VolumeTypeSteps']


class VolumeTypeSteps(base.BaseSteps):
    """Cinder volume types steps."""

    @steps_checker.step
    def get_volume_types(self, check=True):
        """Step to retrieve volume types.

        Args:
            check (bool): flag whether to check step or not

        Returns:
            list: volume types list

        Raises:
            AssertionError: if check failed
        """
        volume_types = self._client.list()

        if check:
            assert_that(volume_types, is_not(empty()))
        return volume_types

    @steps_checker.step
    def create_volume_type(self, name, description=None, is_public=True,
                           check=True):
        """Step to create volume type.

        Args:
            name (str): name of created volume type
            description (str): description
            is_public (bool|True): volume type visibility
            check (bool|true): flag whether to check step or not

        Returns:
            object: cinder volume type

        Raises:
            AssertionError: if check failed
        """
        volume_type = self._client.create(name=name,
                                          description=description,
                                          is_public=is_public)

        if check:
            self.check_volume_type_presence(volume_type)

        return volume_type

    @steps_checker.step
    def delete_volume_type(self, volume_type, check=True):
        """Step to delete volume type.

        Args:
            volume_type (obj): volume type object
            check (bool|true): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        self._client.delete(volume_type.id)

        if check:
            self.check_volume_type_presence(volume_type, must_present=False)

    @steps_checker.step
    def check_volume_type_presence(self, volume_type, must_present=True,
                                   timeout=0):
        """Check step volume type presence status.

        Args:
            volume_type (object): cinder volume type to check presence status
            must_present (bool|True): flag whether volume type should present
            or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """

        def _check_volume_type_presence():
            try:
                self._client.get(volume_type.id)
                is_present = True
            except exceptions.NotFound:
                is_present = False
            return expect_that(is_present, equal_to(must_present))

        waiter.wait(
            _check_volume_type_presence, timeout_seconds=timeout,
            waiting_for="Waiting for volume type presence {0}"
            .format(volume_type))
