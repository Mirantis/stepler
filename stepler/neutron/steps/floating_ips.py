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

from hamcrest import assert_that, calling, equal_to, raises  # noqa H301
from neutronclient.common import exceptions

from stepler import base
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = ["FloatingIPSteps"]


class FloatingIPSteps(base.BaseSteps):
    """Floating IP steps."""

    @steps_checker.step
    def create(self, network, port=None, check=True, **kwargs):
        """Step to create floating_ip.

        Args:
            network (dict): external network to create floating_ip on
            port (dict, optional): port to associate floating ip with it. By
                default created floating ip is not associated with any port.
            check (bool): flag whether to check step or not
            **kwargs: other arguments to pass to API

        Returns:
            dict: floating_ip

        Raises:
            AssertionError: if check failed
        """
        port_id = port['id'] if port else None
        floating_ip = self._client.create(network_id=network['id'],
                                          port_id=port_id,
                                          **kwargs)

        if check:
            self.check_presence(floating_ip)

        return floating_ip

    @steps_checker.step
    def delete(self, floating_ip, check=True):
        """Step to delete floating_ip.

        Args:
            floating_ip (dict): floating_ip
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        self._client.delete(floating_ip['id'])

        if check:
            self.check_presence(floating_ip, must_present=False)

    @steps_checker.step
    def check_presence(self, floating_ip, must_present=True, timeout=0):
        """Verify step to check floating_ip is present.

        Args:
            floating_ip (dict): floating_ip to check presence status
            must_present (bool): flag whether floating_ip must present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_floating_ip_presence():
            is_present = bool(self._client.find_all(id=floating_ip['id']))
            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_floating_ip_presence, timeout_seconds=timeout)

    @steps_checker.step
    def attach_floating_ip(self, floating_ip, port, check=True):
        """Step to attach floating IP to server with neutron.

        Args:
            floating_ip (dict): floating ip
            port (dict): server port to attach floating ip to
            check (bool, optional): flag whether to check this step or not

        Raises:
            AssertionError: if check failed
        """
        self._client.update(floating_ip['id'], port_id=port['id'])

        if check:
            new_port_id = self._client.get(floating_ip['id'])['port_id']
            assert_that(new_port_id, equal_to(port['id']))

    @steps_checker.step
    def detach_floating_ip(self, floating_ip, check=True):
        """Step to detach floating IP from server with neutron.

        Args:
            floating_ip (dict): floating ip
            check (bool, optional): flag whether to check this step or not

        Raises:
            AssertionError: if check failed
        """
        self._client.update(floating_ip['id'], port_id=None)

        if check:
            new_port_id = self._client.get(floating_ip['id'])['port_id']
            assert_that(new_port_id, equal_to(None))

    @steps_checker.step
    def check_negative_create_extra_floating_ip(self, network):
        """Step to check that unable to create floating ips more than quota.

        Args:
            network (obj): network

        Raises:
            AssertionError: if no OverQuotaClient exception occurs or exception
                message is not expected
        """
        exception_message = "Quota exceeded for resources"
        assert_that(
            calling(self.create).with_args(network, check=False),
            raises(exceptions.OverQuotaClient, exception_message),
            "Floating IP has been created for network with ID {!r} "
            "though it exceeds the quota or OverQuotaClient exception with "
            "expected message has not been appeared".format(network['id']))
