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
from hamcrest import assert_that, only_contains, any_of, has_entries  # noqa
from novaclient import exceptions as nova_exceptions
import waiting

from stepler import base
from stepler import config
from stepler.third_party import steps_checker

__all__ = [
    'AvailabilityZoneSteps'
]


class AvailabilityZoneSteps(base.BaseSteps):
    """Availability zone steps."""

    @steps_checker.step
    def check_all_active_nova_compute_hosts_are_available(self):
        """Checks that all active nova computes are available.

        Raises:
            AssertionError: if not all hosts are active
            TimeoutExpired: if there is no fresh data for hosts
        """

        def _get_hosts():
            zone = waiting.wait(
                lambda: self._client.find(zoneName="nova"),
                timeout_seconds=config.NOVA_AVAILABILITY_TIMEOUT,
                expected_exceptions=nova_exceptions.ClientException)
            hosts = [x for y in zone.hosts.values() for x in y.values()]
            for host in hosts:
                host['updated_at'] = parser.parse(host['updated_at'])
            return hosts

        def _predicate():
            return all([x['updated_at'] > last_updated for x in _get_hosts()])

        last_updated = max([x['updated_at'] for x in _get_hosts()])

        waiting.wait(
            _predicate,
            timeout_seconds=config.NOVA_AVAILABILITY_TIMEOUT,
            sleep_seconds=10)
        assert_that(
            _get_hosts(),
            only_contains(
                any_of(
                    has_entries(
                        active=True, available=True),
                    has_entries(active=False))))
