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
    def create(self, router_name, distributed=False, check=True):
        """Step to create router.

        Args:
            router_name (str): router name
            distributed (bool): should router be distributed
            check (bool): flag whether to check step or not
        Returns:
            dict: router
        """
        router = self._client.create(name=router_name, distributed=distributed)

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
        self._client._neutron_client.add_gateway_router(
            router['id'], {'network_id': network['id']})

        if check:
            self.check_gateway_presence(router)

    @steps_checker.step
    def clear_gateway(self, router, check=True):
        """Step to clear router gateway.

        Args:
            router (dict): router
        """
        self._client._neutron_client.remove_gateway_router(router['id'])

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
    def add_interface(self, router, subnet=None, port=None, check=True):
        """Step to add router to subnet interface.

        Args:
            router (dict): router
            subnet (dict): subnet
        """
        body = self._get_interface_body(subnet, port)
        self._client._neutron_client.add_interface_router(router['id'], body)

        if check:
            self.check_interface_presence(router, subnet, port)

    @steps_checker.step
    def remove_interface(self, router, subnet=None, port=None, check=True):
        """Step to remove router to subnet interface.

        Args:
            router (dict): router
            subnet (dict): subnet
        """
        body = self._get_interface_body(subnet, port)
        self._client._neutron_client.remove_interface_router(router['id'],
                                                             body)
        if check:
            self.check_interface_presence(router, subnet, port, present=False)

    @steps_checker.step
    def check_interface_presence(self, router, subnet=None, port=None,
                                 present=True, timeout=0):
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
            ports = self._client.find_all(
                device_owner='network:router_interface',
                device_id=router['id'])

            if subnet is not None:
                resource_id = subnet['id']
                resource_ids = [fixed_ip['subnet_id'] for port in ports
                                for fixed_ip in port['fixed_ips']]
            elif port is not None:
                resource_id = port['id']
                resource_ids = [port['id'] for port in ports]

            return present == (resource_id in resource_ids)

        waiting.wait(predicate, timeout_seconds=timeout)

    @staticmethod
    def _get_interface_body(subnet=None, port=None):
        body = {}
        if subnet is not None:
            body['subnet_id'] = subnet['id']
        elif port is not None:
            body['port_id'] = port['id']
        else:
            raise ValueError("subnet_id or port_id must be indicated.")
        return body
