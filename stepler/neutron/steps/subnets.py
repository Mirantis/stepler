"""
------------
Subnet steps
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

import ipaddress

from hamcrest import assert_that, calling, equal_to, raises  # noqa
from neutronclient.common import exceptions

from stepler import base
from stepler import config
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

__all__ = ["SubnetSteps"]


class SubnetSteps(base.BaseSteps):
    """Subnet steps."""

    @steps_checker.step
    def create(self, subnet_name, network, cidr, check=True, **kwargs):
        """Step to create subnet.

        Args:
            subnet_name (str): subnet name
            network (dict): network to create subnet on
            cidr (str): cidr for subnet (like 192.168.1.0/24"")
            check (bool): flag whether to check step or not
            **kwargs: other arguments to pass to API

        Returns:
            dict: subnet
        """
        subnet = self._client.create(name=subnet_name,
                                     network_id=network['id'],
                                     cidr=cidr,
                                     **kwargs)

        if check:
            self.check_presence(subnet)

        return subnet

    @steps_checker.step
    def delete(self, subnet, check=True):
        """Step to delete subnet.

        Args:
            subnet (dict): subnet
            check (bool): flag whether to check step or not
        """
        self._client.delete(subnet['id'])

        if check:
            self.check_presence(subnet, must_present=False)

    @steps_checker.step
    def check_presence(self, subnet, must_present=True, timeout=0):
        """Verify step to check subnet is present.

        Args:
            subnet (dict): subnet to check presence status
            must_present (bool): flag whether subnet must present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_subnet_presence():
            is_present = bool(self._client.find_all(id=subnet['id']))
            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_subnet_presence, timeout_seconds=timeout)

    @steps_checker.step
    def check_negative_create_extra_subnet(self, network):
        """Step to check that unable to create subnets more than quota.

        Args:
            network (obj): network

        Raises:
            AssertionError: if no OverQuotaClient exception occurs or exception
                message is not expected
        """
        exception_message = "Quota exceeded for resources"
        assert_that(
            calling(self.create).with_args(
                subnet_name=next(utils.generate_ids()),
                network=network,
                cidr=config.LOCAL_CIDR,
                check=False),
            raises(exceptions.OverQuotaClient, exception_message),
            "Subnet for network with ID {!r} has been created though it "
            "exceeds the quota or OverQuotaClient exception with expected "
            "error message has not been appeared".format(network['id']))

    def get_available_fixed_ips(self, subnet):
        """Step to get available fixed ips from subnet.

        Args:
            subnet (obj): subnet

        Yields:
            str: available ip address

        Raises:
            StopIteration: if there are no free ip addresses on subnet
        """
        used_ips = list(self._client.get_fixed_ips(subnet['id']))
        for allocation_pool in subnet['allocation_pools']:
            start = ipaddress.ip_address(allocation_pool['start'])
            end = ipaddress.ip_address(allocation_pool['end'])
            for net in ipaddress.summarize_address_range(start, end):
                for host in net.hosts():
                    if str(host) not in used_ips:
                        yield str(host)
