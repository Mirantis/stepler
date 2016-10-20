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
    'ServerVolumeSteps'
]


class ServerVolumeSteps(BaseSteps):
    """Server volumes steps."""

    @step
    def create_server_volume(self, server, volume, device=None, check=True):
        """Step to attach volume to server

        Args:
            server (object): nova server
            volume (object): cinder volume
            device (str): device name
            check (bool): flag whether to check step or not

        Returns:
            object: tuple (server.id, volume.id)
        """
        self._client.create_server_volume(server.id, volume.id, device=device)
        server_volume = (server.id, volume.id)

        if check:
            self.check_server_volume_presence(server_volume, present=True,
                                              timeout=180)

        return server_volume

    @step
    def delete_server_volume(self, server_volume, check=True):
        """Step to delete server volume

        Args:
            server_volume (object): server volume data
            check (bool): flag whether to check step or not
        """
        server_id, volume_id = server_volume
        self._client.delete_server_volume(server_id, volume_id)

        if check:
            self.check_server_volume_presence(server_volume, present=False,
                                              timeout=180)

    @step
    def check_server_volume_presence(self, server_volume,
                                     present=True, timeout=0):
        """Verify step to check server volume is present.

        Args:
            server_volume (object): server volume data
            present: expected state - True (present) or False (missing)
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """
        server_id, volume_id = server_volume

        def predicate():
            try:
                self._client.get_server_volume(server_id, volume_id)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)
