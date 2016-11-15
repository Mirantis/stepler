"""
-----------------------
Availability zone steps
-----------------------
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

from dateutil import parser
from hamcrest import assert_that, empty, has_entries, is_, is_not, only_contains  # noqa
from novaclient import exceptions as nova_exceptions

from stepler import base
from stepler import config
from stepler.third_party.matchers import expect_that
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = ['AvailabilityZoneSteps']


class AvailabilityZoneSteps(base.BaseSteps):
    """Availability zone steps."""

    @steps_checker.step
    def check_all_active_hosts_available(self, zone_name='nova'):
        """Checks that all active nova hosts for zone are available.

        Nova checks hosts status with some interval. To prevent checking on
        outdated hosts data this method wait for `updated_at` host's attribute
        to be changed.

        Args:
            zone_name (str): zone name

        Raises:
            AssertionError: if not all hosts are active
            TimeoutExpired: if there is no updates for hosts
        """

        def _get_hosts():
            zone = waiter.wait(
                lambda: self._client.find(zoneName=zone_name),
                timeout_seconds=config.NOVA_AVAILABILITY_TIMEOUT,
                expected_exceptions=(nova_exceptions.ClientException,))
            for hosts_dict in zone.hosts.values():
                for host in hosts_dict.values():
                    host['updated_at'] = parser.parse(host['updated_at'])
                    yield host

        last_updated = max([x['updated_at'] for x in _get_hosts()])

        def _check_hosts_updated():
            return expect_that(
                is_(True),
                all([x['updated_at'] > last_updated for x in _get_hosts()]))

        waiter.wait(
            _check_hosts_updated,
            timeout_seconds=config.NOVA_AVAILABILITY_TIMEOUT)

        active_hosts = [x for x in _get_hosts() if x['active']]

        assert_that(active_hosts, only_contains(has_entries(available=True)))

    @steps_checker.step
    def get_zones(self, check=True, **kwargs):
        """Step to find all zones matching **kwargs.

        Args:
            check (bool): flag whether to check step or not
            **kwargs: like: {'zoneName': 'nova'},
                            {'zoneState': {u'available': True}}

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
            **kwargs: like: {'zoneName': 'nova'},
                            {'zoneState': {u'available': True}}

        Returns:
            object: nova zone
        """
        zone = self._client.find(**kwargs)

        if check:
            assert_that(zone.to_dict(), has_entries(kwargs))

        return zone
