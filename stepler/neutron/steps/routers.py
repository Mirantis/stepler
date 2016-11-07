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

import waiting

from stepler import base
from stepler.third_party import steps_checker

__all__ = ["RouterSteps"]


class RouterSteps(base.BaseSteps):
    """Router steps."""

    @steps_checker.step
    def create(self, router_name, distributed=False, check=True, **kwargs):
        """Step to create router.

        Args:
            router_name (str): router name
            distributed (bool): should router be distributed
            check (bool): flag whether to check step or not
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
            self.check_presence(router, present=False)

    @steps_checker.step
    def check_presence(self, router, present=True, timeout=0):
        """Verify step to check router is present.

        Args:
            router (dict): router to check presence status
            presented (bool): flag whether router should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        def predicate():
            exists = bool(self._client.find_all(id=router['id']))
            return exists == present

        waiting.wait(predicate, timeout_seconds=timeout)

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
            self.check_gateway_presence(router, present=False)

    @steps_checker.step
    def check_gateway_presence(self, router, present=True, timeout=0):
        """Verify step to check router gateway is present.

        Args:
            router (dict): router to check gateway presence status
            presented (bool): flag whether router should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        router_id = router['id']

        def predicate():
            router = self._client.get(router_id)
            return present == (router['external_gateway_info'] is not None)

        waiting.wait(predicate, timeout_seconds=timeout)

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
            self.check_interface_subnet_presence(router, subnet, present=False)

    @steps_checker.step
    def check_interface_subnet_presence(self,
                                        router,
                                        subnet,
                                        present=True,
                                        timeout=0):
        """Verify step to check subnet is in router interfaces.

        Args:
            router (dict): router to check
            subnet (dict): subnet to find in router interfaces
            presented (bool): flag whether router should contains interface
                to subnet or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        def predicate():
            subnet_ids = self._client.get_interfaces_subnets_ids(router['id'])
            return present == (subnet['id'] in subnet_ids)

        waiting.wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def get_by_name(self, name, **kwargs):
        """Step to get router by name.

        Args:
            name (str): router name

        Returns:
            dict: router

        Raises:
            LookupError: if zero or more than one routers found
        """
        return self._client.find(name=name, **kwargs)
