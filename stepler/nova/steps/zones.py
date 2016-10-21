"""
------------
Zones steps
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

from hamcrest import assert_that, empty, is_not, has_entries  # noqa

from stepler.base import BaseSteps
from stepler.third_party import steps_checker

__all__ = [
    'ZoneSteps'
]


class ZoneSteps(BaseSteps):
    """Zone steps."""

    @steps_checker.step
    def get_zones(self, check=True, **kwargs):
        """Step to find all zones matching **kwargs.

        Args:
            check (bool): flag whether to check step or not
            **kwargs: like: {'zoneName': 'nova'}

        Returns:
            list: nova zones
        """
        zones = self._client.findall(**kwargs)

        if check:
            assert_that(zones, is_not(empty()))
            for zone in zones:
                assert_that(zone.to_dict(), has_entries(kwargs))

        return zones

    @steps_checker.step
    def get_zone(self, check=True, **kwargs):
        """Step to find one zone matching **kwargs.

        Args:
            check (bool): flag whether to check step or not
            **kwargs: like: {'zoneName': 'nova'}

        Returns:
            object: nova zone
        """
        zones = self.get_zones(check=check, **kwargs)
        return zones[0]
