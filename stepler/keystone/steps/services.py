"""
-------------
Service steps
-------------
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

from hamcrest import (assert_that, empty, equal_to, is_not)  # noqa
from keystoneclient import exceptions

from stepler.base import BaseSteps
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = [
    'ServiceSteps'
]


class ServiceSteps(BaseSteps):
    """Services steps."""

    @steps_checker.step
    def create_service(self, service_name, service_type=None, enabled=True,
                       description=None, check=True):
        """Step to create service.

        Args:
            service_name (str): service name
            service_type (str): service type
            enabled (bool): whether the service appears in the catalog
            description (str): the description of the service
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check failed

        Returns:
            object: service
        """
        service = self._client.create(
            name=service_name,
            type=service_type,
            enabled=enabled,
            description=description)

        if check:
            self.check_service_presence(service)
            assert_that(service.name, equal_to(service_name))
            assert_that(service.type, equal_to(service_type))
            assert_that(service.enabled, equal_to(enabled))
            if description:
                assert_that(service.description, equal_to(description))
            if hasattr(service, 'id'):
                domain_id = service.id
            else:
                domain_id = service
            assert_that(service.domain_id, equal_to(domain_id))

        return service

    @steps_checker.step
    def delete_service(self, service, check=True):
        """Step to delete service.

        Args:
            service (object): openstack service
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        self._client.delete(service.id)

        if check:
            self.check_service_presence(service, must_present=False,
                                        timeout=30)

    @steps_checker.step
    def check_service_presence(self, service, must_present=True, timeout=0):
        """Step to check that service is present.

        Args:
            service (object): openstack service to check presence status
            must_present (bool): flag whether service should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_service_presence():
            try:
                self._client.get(service.id)
                is_present = True
            except exceptions.NotFound:
                is_present = False

            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_service_presence, timeout_seconds=timeout)

    @steps_checker.step
    def get_services(self, check=True):
        """Step to get services.

        Args:
            check (bool): flag whether to check step or not

        Returns:
            list: services

        Raises:
            AssertionError: if no services are found
        """
        services = list(self._client.list())
        if check:
            assert_that(services, is_not(empty()))

        return services

    @steps_checker.step
    def get_service(self, service_name):
        """Step to get service by name.

        Args:
            service_name (str): openstack service name to find

        Returns:
            obj: service

        Raises:
            LookupError: if no services are found
        """
        try:
            service = self._client.find(name=service_name)
        except exceptions.NotFound:
            raise LookupError("Service {} isn't found".format(service_name))

        return service
