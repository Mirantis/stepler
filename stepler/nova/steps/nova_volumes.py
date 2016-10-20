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

from waiting import wait

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = [
    'NovaVolumeSteps'
]


class NovaVolumeSteps(BaseSteps):
    """Server volumes steps."""

    @step
    def attach_volume_to_server(self, server, volume, device='/dev/vdb',
                                check=True):
        """Step to attach volume to server

        Args:
            server (object): nova server
            volume (object): cinder volume
            device (str): device name
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        self._client.create_server_volume(server.id, volume.id, device=device)

        if check:
            self.check_volume_to_server_attachment_status(
                server, volume, is_attached=True, timeout=180)

    @step
    def detach_volume_from_server(self, server, volume, check=True):
        """Step to detach volume from server

        Args:
            server (object): nova server
            volume (object): cinder volume
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        self._client.delete_server_volume(server.id, volume.id)

        if check:
            self.check_volume_to_server_attachment_status(
                server, volume, is_attached=False, timeout=180)

    @step
    def check_volume_to_server_attachment_status(self, server, volume,
                                                 is_attached=True, timeout=0):
        """Verify step to check status of server volume.

        Args:
            server (object): nova server
            volume (object): cinder volume
            is_attached: expected state - True (present) or False (missing)
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        def predicate():
            try:
                server.get()
                volume.get()
                self._client.get_server_volume(server.id, volume.id)
                return is_attached
            except Exception:
                return not is_attached

        wait(predicate, timeout_seconds=timeout)
