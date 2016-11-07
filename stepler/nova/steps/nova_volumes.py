"""
-------------------
Server volume steps
-------------------
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

from novaclient import exceptions as nova_exceptions
from waiting import wait

from stepler import base
from stepler import config
from stepler.third_party import steps_checker

__all__ = [
    'NovaVolumeSteps'
]


class NovaVolumeSteps(base.BaseSteps):
    """Server volumes steps."""

    @steps_checker.step
    def attach_volume_to_server(self, server, volume, device='/dev/vdb',
                                check=True):
        """Step to attach volume to server

        Args:
            server (object): nova server
            volume (object): cinder volume
            device (str): device name
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        self._client.create_server_volume(server.id, volume.id, device=device)

        if check:
            self.check_volume_to_server_attachment_status(
                server, volume, is_attached=True,
                timeout=config.VOLUME_ATTACH_TIMEOUT)

    @steps_checker.step
    def detach_volume_from_server(self, server, volume, check=True):
        """Step to detach volume from server

        Args:
            server (object): nova server
            volume (object): cinder volume
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        self._client.delete_server_volume(server.id, volume.id)

        if check:
            self.check_volume_to_server_attachment_status(
                server, volume, is_attached=False,
                timeout=config.VOLUME_ATTACH_TIMEOUT)

    @steps_checker.step
    def check_volume_to_server_attachment_status(self, server, volume,
                                                 is_attached=True, timeout=0):
        """Verify step to check status of server volume.

        Args:
            server (object): nova server
            volume (object): cinder volume
            is_attached: expected state - True (present) or False (missing)
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def predicate():
            server.get()
            volume.get()
            try:
                self._client.get_server_volume(server.id, volume.id)
                return is_attached
            except nova_exceptions.NotFound:
                return not is_attached

        wait(predicate, timeout_seconds=timeout)
