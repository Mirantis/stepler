"""
------------
Router steps
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

from hamcrest import (assert_that, empty, equal_to,
                      has_entries, is_not)  # noqa H301

from stepler import base
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = ["RouterSteps"]


class RouterSteps(base.BaseSteps):
    """Router steps."""

    @steps_checker.step
    def create(self, router_name, distributed=None, check=True, **kwargs):
        """Step to create router.

        Args:
            router_name (str): router name
            distributed (bool): should router be distributed
            check (bool): flag whether to check step or not
            **kwargs: other arguments to pass to API

        Returns:
            dict: router
        """
        router = self._client.create(name=router_name, distributed=distributed,
                                     **kwargs)

        if check:
            self.check_presence(router)

        return router

    @steps_checker.step
    def delete(self, router, check=True):
        """Step to delete router.

        Args:
            router (dict): router
            check (bool): flag whether to check step or not
        """
        self._client.delete(router['id'])

        if check:
            self.check_presence(router, must_present=False)

    @steps_checker.step
    def check_presence(self, router, must_present=True, timeout=0):
        """Verify step to check router is present.

        Args:
            router (dict): router to check presence status
            must_present (bool): flag whether router must present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_router_presence():
            is_present = bool(self._client.find_all(id=router['id']))
            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_router_presence, timeout_seconds=timeout)

    @steps_checker.step
    def set_gateway(self, router, network, check=True):
        """Step to set router gateway.

        Args:
            router (dict): router
            network (dict): network
        """
        self._client.set_gateway(router_id=router['id'],
                                 network_id=network['id'])
        if check:
            self.check_gateway_presence(router)

    @steps_checker.step
    def clear_gateway(self, router, check=True):
        """Step to clear router gateway.

        Args:
            router (dict): router
        """
        self._client.clear_gateway(router_id=router['id'])
        if check:
            self.check_gateway_presence(router, must_present=False)

    @steps_checker.step
    def check_gateway_presence(self, router, must_present=True, timeout=0):
        """Verify step to check router gateway is present.

        Args:
            router (dict): router to check gateway presence status
            must_present (bool): flag whether router must present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        router_id = router['id']

        def _check_gateway_presence():
            router = self._client.get(router_id)
            is_present = router['external_gateway_info'] is not None
            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_gateway_presence, timeout_seconds=timeout)

    @steps_checker.step
    def add_subnet_interface(self, router, subnet, check=True):
        """Step to add router to subnet interface.

        Args:
            router (dict): router
            subnet (dict): subnet
        """
        self._client.add_subnet_interface(router_id=router['id'],
                                          subnet_id=subnet['id'])
        if check:
            self.check_interface_subnet_presence(router, subnet)

    @steps_checker.step
    def remove_subnet_interface(self, router, subnet, check=True):
        """Step to remove router to subnet interface.

        Args:
            router (dict): router
            subnet (dict): subnet
        """
        self._client.remove_subnet_interface(router_id=router['id'],
                                             subnet_id=subnet['id'])
        if check:
            self.check_interface_subnet_presence(
                router, subnet, must_present=False)

    @steps_checker.step
    def check_interface_subnet_presence(self,
                                        router,
                                        subnet,
                                        must_present=True,
                                        timeout=0):
        """Verify step to check subnet is in router interfaces.

        Args:
            router (dict): router to check
            subnet (dict): subnet to find in router interfaces
            must_present (bool): flag whether router should contains interface
                to subnet or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_interface_subnet_presence():
            subnet_ids = self._client.get_interfaces_subnets_ids(router['id'])
            is_present = subnet['id'] in subnet_ids
            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_interface_subnet_presence, timeout_seconds=timeout)

    @steps_checker.step
    def get_router(self, **kwargs):
        """Step to get router.

        Args:
            **kwargs: filter to match router

        Returns:
            dict: router

        Raises:
            LookupError: if zero or more than one routers found
        """
        return self._client.find(**kwargs)

    @steps_checker.step
    def get_routers(self, check=True):
        """Step to retrieve all routers in current project.

        Args:
            check (bool): flag whether to check step or not

        Returns:
            list: list of retrieved routers
        """
        routers = self._client.list()

        if check:
            assert_that(routers, is_not(empty()))

        return routers

    @steps_checker.step
    def check_router_attrs(self, name, expected_attr_values=None):
        """Step to check whether router has expected attributes or not.

        Args:
            name (str): name of the router
            expected_attr_values (dict|None): expected attribute values.
                If None, only check that elements of router output are
                not empty.

        Raises:
            AssertionError: if check failed
        """
        router_attr = self.get_router(name=name)
        expected_attr_values = expected_attr_values or {}

        assert_that(router_attr, is_not(empty()))
        if expected_attr_values:
            assert_that(router_attr,
                        has_entries(**expected_attr_values))
