"""
------------
Flavor steps
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

from novaclient import exceptions
from waiting import wait

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = [
    'FlavorSteps'
]


class FlavorSteps(BaseSteps):
    """Flavor steps."""

    @step
    def create_flavor(self, flavor_name, ram, vcpus, disk, flavorid='auto',
                      ephemeral=0, swap=0, rxtx_factor=1.0, is_public=True,
                      check=True):
        """Step to create flavor.

        Args:
            flavor_name (str): Descriptive name of the flavor
            ram (int): Memory in MB for the flavor
            vcpus (int): Number of VCPUs for the flavor
            disk (int): Size of local disk in GB
            flavorid (str): ID for the flavor (optional). You can use the
                            reserved value ``"auto"`` to have Nova generate a
                            UUID for the flavor in cases where you cannot
                            simply pass ``None``.
            ephemeral (int): Ephemeral space in MB
            swap (int): Swap space in MB
            rxtx_factor (float): RX/TX factor
            is_public (bool): flag whether flavor should be public or not
            check (bool): flag whether to check step or not
        Retuns:
            object: flavor object
        """
        flavor = self._client.create(flavor_name,
                                     ram=ram,
                                     vcpus=vcpus,
                                     disk=disk,
                                     flavorid=flavorid,
                                     ephemeral=ephemeral,
                                     swap=swap,
                                     rxtx_factor=rxtx_factor,
                                     is_public=is_public)

        if check:
            self.check_flavor_presence(flavor)

        return flavor

    @step
    def delete_flavor(self, flavor, check=True):
        """Step to delete flavor.

        Args:
            flavor (object): nova flavor
            check (bool): flag whether to check step or not
        """
        self._client.delete(flavor.id)

        if check:
            self.check_flavor_presence(flavor, present=False)

    @step
    def check_flavor_presence(self, flavor, present=True, timeout=0):
        """Verify step to check flavor is present.

        Args:
            flavor (object): nova flavor to check presence status
            present (bool): flag whether flavor should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was triggered to False after timeout
        """
        def predicate():
            try:
                # After deleting flavor `get` method still return object,
                # so it was changed to find
                self._client.find(id=flavor.id)
                return present
            except exceptions.NotFound:
                return not present

        wait(predicate, timeout_seconds=timeout)

    @step
    def get_flavor(self, *args, **kwgs):
        """Step to find a single item with attributes matching **kwargs.

        Parameters:
            flavor_name (str): Descriptive name of the flavor
            ram (int): Memory in MB for the flavor
            vcpus (int): Number of VCPUs for the flavor
            disk (int): Size of local disk in GB
            flavorid (str): ID for the flavor (optional). You can use the
                            reserved value ``"auto"`` to have Nova generate a
                            UUID for the flavor in cases where you cannot
                            simply pass ``None``.
            ephemeral (int): Ephemeral space in MB
            swap (int): Swap space in MB
            rxtx_factor (float): RX/TX factor
            is_public (bool): flag whether flavor should be public or not
            check (bool): flag whether to check step or not

        Returns:
            object: nova flavor
        """
        return self._client.find(*args, **kwgs)
