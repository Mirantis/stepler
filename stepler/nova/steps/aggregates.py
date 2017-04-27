"""
---------------
Aggregate steps
---------------
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

from hamcrest import (assert_that, equal_to, has_entries, has_item,
                      is_not)  # noqa
from novaclient import exceptions

from stepler import base
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

__all__ = [
    'AggregateSteps'
]


class AggregateSteps(base.BaseSteps):
    """Aggregate steps."""

    @steps_checker.step
    def create_aggregate(self, aggregate_name=None, availability_zone='nova',
                         check=True):
        """Step to create nova aggregate.

        Args:
            aggregate_name (str): name of nova aggregate
            availability_zone (str): availability zone
            check (bool): flag whether to check step or not

        Retuns:
            object: nova aggregate

        Raises:
            TimeoutExpired: if aggregate is not created
        """
        if aggregate_name is None:
            aggregate_name = next(utils.generate_ids())
        aggregate = self._client.create(aggregate_name, availability_zone)

        if check:
            self.check_aggregate_presence(aggregate)

        return aggregate

    @steps_checker.step
    def delete_aggregate(self, aggregate, check=True):
        """Step to delete aggregate.

        Args:
            aggregate (object): nova aggregate
            check (bool): flag whether to check step or not
        """
        self._client.delete(aggregate.id)

        if check:
            self.check_aggregate_presence(aggregate, must_present=False)

    @steps_checker.step
    def check_aggregate_presence(self, aggregate, must_present=True,
                                 timeout=0):
        """Verify step to check aggregate is present or not.

        Args:
            aggregate (object): nova aggregate to check presence status
            must_present (bool): flag whether aggregate should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was triggered to False after timeout
        """
        err_msg = "Invalid presence status of aggregate {}".format(
            aggregate.id)
        if timeout:
            err_msg += " after {} second(s) of waiting".format(timeout)

        def _check_aggregate_presence():
            try:
                # After deleting aggregate `get` method still returns object,
                # so 'find' method is used
                self._client.find(id=aggregate.id)
                is_present = True
            except exceptions.NotFound:
                is_present = False
            return waiter.expect_that(
                is_present, equal_to(must_present), err_msg)

        waiter.wait(_check_aggregate_presence, timeout_seconds=timeout)

    @steps_checker.step
    def set_metadata(self, aggregate, metadata, check=True):
        """Step to set metadata on an aggregate.

        Args:
            aggregate (object): nova aggregate
            metadata (dict): key/value pairs to be set
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        aggregate.set_metadata(metadata)
        aggregate.get()

        if check:
            err_msg = "Aggregate {0} doesn't have metadata {1}".format(
                aggregate.id, metadata)
            assert_that(aggregate.metadata, has_entries(metadata), err_msg)

    @steps_checker.step
    def add_host(self, aggregate, host_name, check=True):
        """Step to add host to an aggregate.

        Args:
            aggregate (object): nova aggregate
            host_name (str): host name
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        aggregate.add_host(host_name)
        aggregate.get()

        if check:
            err_msg = "Aggregate {0} doesn't have host {1}".format(
                aggregate.id, host_name)
            assert_that(aggregate.hosts, has_item(host_name), err_msg)

    @steps_checker.step
    def remove_host(self, aggregate, host_name, check=True):
        """Step to remove host from an aggregate.

        Args:
            aggregate (object): nova aggregate
            host_name (dict): key/value pairs to be set
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        aggregate.remove_host(host_name)
        aggregate.get()

        if check:
            err_msg = "Aggregate {0} still has host {1}".format(
                aggregate.id, host_name)
            assert_that(aggregate.hosts, is_not(has_item(host_name)), err_msg)
