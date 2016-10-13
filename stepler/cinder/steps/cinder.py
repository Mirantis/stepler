"""
------------
Cinder steps
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

from cinderclient import exceptions
import waiting

from stepler import base
from stepler import config
from stepler.third_party import steps_checker

__all__ = ['CinderSteps']


class CinderSteps(base.BaseSteps):
    """Cinder steps."""

    @steps_checker.step
    def create_volume(self,
                      name,
                      size=1,
                      image=None,
                      volume_type=None,
                      description=None,
                      check=True):
        """Step to create volume.

        Args:
            name (str): name of created volume
            size (int): size of created volume (in GB)
            image (object): glance image to create volume from
            volume_type (str): type of volume
            description (str): description
            check (bool): flag whether check step or not

        Returns:
            object: cinder volume
        """
        image_id = None if image is None else image.id
        volume = self._client.volumes.create(size,
                                             name=name,
                                             imageRef=image_id,
                                             volume_type=volume_type,
                                             description=description)

        if check:
            self.check_volume_status(volume,
                                     'available',
                                     timeout=config.VOLUME_AVAILABLE_TIMEOUT)

        return volume

    @steps_checker.step
    def create_volumes(self,
                       names,
                       size=1,
                       image=None,
                       volume_type=None,
                       description=None,
                       check=True):
        """Step to create volumes.

        Args:
            name (str): name of created volume
            size (int): size of created volume (in GB)
            image (object): glance image to create volume from
            volume_type (str): type of volume
            description (str): description
            check (bool): flag whether check step or not

        Returns:
            list: cinder volumes
        """
        volumes = []
        for name in names:
            volume = self.create_volume(name=name,
                                        size=size,
                                        image=image,
                                        volume_type=volume_type,
                                        description=description,
                                        check=False)
            volumes.append(volume)

        if check:

            for volume in volumes:
                self.check_volume_status(
                    volume,
                    'available',
                    timeout=config.VOLUME_AVAILABLE_TIMEOUT)

        return volumes

    @steps_checker.step
    def delete_volume(self, volume, check=True):
        """Step to delete volume.

        Args:
            volume (object): cinder volume
            check (bool): flag whether check step or not
        """
        self._client.volumes.delete(volume.id)

        if check:
            self.check_volume_presence(volume,
                                       present=False,
                                       timeout=config.VOLUME_DELETE_TIMEOUT)

    @steps_checker.step
    def delete_volumes(self, volumes, check=True):
        """Step to delete volumes.

        Args:
            volumes (list): cinder volumes
            check (bool): flag whether check step or not
        """
        for volume in volumes:
            self.delete_volume(volume, check=False)

        if check:
            for volume in volumes:
                self.check_volume_presence(
                    volume,
                    present=False,
                    timeout=config.VOLUME_DELETE_TIMEOUT)

    @steps_checker.step
    def check_volume_presence(self, volume, present=True, timeout=0):
        """Check step volume presence status.

        Args:
            volume (object): cinder volume to check presence status
            presented (bool): flag whether volume should present or no
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        def predicate():
            try:
                self._client.volumes.get(volume.id)
                return present
            except exceptions.NotFound:
                return not present

        waiting.wait(predicate, timeout_seconds=timeout)

    @steps_checker.step
    def check_volume_status(self, volume, status, timeout=0):
        """Check step volume status.

        Args:
            volume (object): cinder volume to check status
            status (str): volume status name to check
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check was falsed after timeout
        """

        def predicate():
            volume.get()
            return volume.status.lower() == status.lower()

        waiting.wait(predicate, timeout_seconds=timeout)
