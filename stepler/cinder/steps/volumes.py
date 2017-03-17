"""
------------
Volume steps
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

import uuid

import attrdict
from cinderclient import exceptions
from hamcrest import (assert_that, calling, empty, equal_to, has_entries,
                      has_properties, has_property, is_not, raises,
                      equal_to_ignoring_case, any_of)  # noqa H301

from stepler import base
from stepler import config
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

__all__ = ['VolumeSteps']


class VolumeSteps(base.BaseSteps):
    """Volume steps."""

    @steps_checker.step
    def check_volume_not_created_with_long_name(self, name):
        """Step to check volume is not created with long name.

        Args:
            name (str): name for volume. Expected long name in argument

        Raises:
            AssertionError: if check triggered an error
        """
        exception_message = ("(Name has more than 255 characters)|"
                             "(Name has \d+ characters, more than 255)")

        assert_that(
            calling(self.create_volumes).with_args(
                names=[name], check=False),
            raises(exceptions.BadRequest, exception_message))

    @steps_checker.step
    def check_volume_not_created_with_non_exist_volume_type(self, image):
        """Step to check volume is not created with non-existed volume type.

        Args:
            image (obj): image for volume creation

        Raises:
            AssertionError: if check triggered an error
        """
        type_name = next(utils.generate_ids('volume_type'))
        exception_message = ("Volume type with name {0} could not be found"
                             .format(type_name))

        assert_that(
            calling(self.create_volumes).with_args(
                names=[None], volume_type=type_name, image=image, check=False),
            raises(exceptions.NotFound, exception_message))

    @steps_checker.step
    def check_volume_not_created_with_wrong_image_id(self):
        """Step to check volume is not created with wrong image id.

        Raises:
            AssertionError: if check triggered an error
        """
        wrong_image = attrdict.AttrDict({'id': next(utils.generate_ids())})
        exception_message = "Invalid image identifier"

        assert_that(
            calling(self.create_volumes).with_args(
                names=[None], image=wrong_image, check=False),
            raises(exceptions.BadRequest, exception_message))

    @steps_checker.step
    def create_volumes(self,
                       names=None,
                       size=1,
                       image=None,
                       volume_type=None,
                       description=None,
                       snapshot_id=None,
                       source_volid=None,
                       metadata=None,
                       check=True):
        """Step to create volumes.

        Args:
            names (list): names of created volume, if not specified
                one volume name will be generated
            size (int): size of created volume (in GB)
            image (object): glance image to create volume from
            volume_type (str): type of volume
            description (str): description
            snapshot_id (str): ID of the snapshot
            source_volid (str): ID of source volume to clone from
            metadata (dict): volume metadata
            check (bool): flag whether to check step or not

        Returns:
            list: cinder volumes

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        names = names or utils.generate_ids()
        image_id = None if image is None else image.id
        volumes = []
        _volume_names = {}

        for name in names:
            volume = self._client.create(size,
                                         name=name,
                                         imageRef=image_id,
                                         volume_type=volume_type,
                                         description=description,
                                         source_volid=source_volid,
                                         snapshot_id=snapshot_id,
                                         metadata=metadata)
            _volume_names[volume.id] = name
            volumes.append(volume)

        if check:
            for volume in volumes:
                self.check_volume_status(
                    volume,
                    [config.STATUS_AVAILABLE],
                    transit_statuses=(config.STATUS_CREATING,
                                      config.STATUS_DOWNLOADING,
                                      config.STATUS_UPLOADING),
                    timeout=config.VOLUME_AVAILABLE_TIMEOUT)

                if snapshot_id:
                    assert_that(volume.snapshot_id, equal_to(snapshot_id))
                if _volume_names[volume.id]:
                    assert_that(volume.name,
                                equal_to(_volume_names[volume.id]))
                if size:
                    assert_that(volume.size, equal_to(size))
                if volume_type:
                    assert_that(volume.volume_type, equal_to(volume_type))
                if description:
                    assert_that(volume.description, equal_to(description))
                if source_volid:
                    assert_that(volume.source_volid, equal_to(source_volid))

        return volumes

    @steps_checker.step
    def delete_volumes(self, volumes, cascade=False, check=True):
        """Step to delete volumes.

        Args:
            volumes (list): cinder volumes
            cascade (bool): flag whether to delete dependent snapshot or not
            check (bool): flag whether to check step or not
        """
        for volume in volumes:
            self.check_volume_status(
                volume,
                statuses=[config.STATUS_AVAILABLE, config.STATUS_ERROR],
                transit_statuses=[
                    config.STATUS_CREATING, config.STATUS_DELETING,
                    config.STATUS_UPDATING
                ],
                timeout=config.VOLUME_IN_USE_TIMEOUT)
            self._client.delete(volume.id, cascade=cascade)

        if check:
            for volume in volumes:
                self.check_volume_presence(
                    volume,
                    must_present=False,
                    timeout=config.VOLUME_DELETE_TIMEOUT)

    @steps_checker.step
    def check_volume_presence(self, volume, must_present=True, timeout=0):
        """Check step volume presence status.

        Args:
            volume (object): cinder volume to check presence status
            must_present (bool): flag whether volume should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_volume_presence():
            try:
                self._client.get(volume.id)
                is_present = True
            except exceptions.NotFound:
                is_present = False
            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_volume_presence, timeout_seconds=timeout)

    @steps_checker.step
    def check_volume_status(self, volume, statuses, transit_statuses=(),
                            timeout=0):
        """Check step volume status.

        Args:
            volume (object|str): cinder volume to check status or its id
            statuses (list): list of statuses to check
            transit_statuses (tuple): possible volume transitional statuses
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired|AssertionError: if check failed after timeout
        """
        transit_matchers = [equal_to_ignoring_case(status)
                            for status in transit_statuses]

        if not hasattr(volume, 'id'):
            volume = self.get_volume_by_id(volume)

        def _check_volume_status():
            volume.get()
            return waiter.expect_that(volume.status,
                                      is_not(any_of(*transit_matchers)))

        waiter.wait(_check_volume_status, timeout_seconds=timeout)
        matchers = [equal_to_ignoring_case(status) for status in statuses]
        assert_that(volume.status, any_of(*matchers))

    @steps_checker.step
    def get_volumes(self,
                    name_prefix=None,
                    metadata=None,
                    search_opts=None,
                    check=True):
        """Step to retrieve volumes.

        Args:
            name_prefix (str, optional): Prefix to filter volumes by name
            metadata (dict, optional): Data to filter volume by metadata
                ``key: value``
            search_opts (dict: optional): API filter options to retrieve
                volumes
            check (bool, optional): Flag whether to check step or not

        Returns:
            list: Volumes collection

        Raises:
            AssertionError: If volumes collection is empty
        """
        volumes = self._client.list(search_opts=search_opts)

        if name_prefix:
            volumes = [volume for volume in volumes
                       if (volume.name or '').startswith(name_prefix)]

        if metadata:
            filtered_volumes = []
            metaset = set(metadata.items())

            for volume in volumes:
                volume_metaset = set(volume.metadata.items())
                if metaset.issubset(volume_metaset):
                    filtered_volumes.append(volume)

            volumes = filtered_volumes

        if check:
            assert_that(volumes, is_not(empty()))

        return volumes

    @steps_checker.step
    def get_volume_by_id(self, volume_id, check=True):
        """Step to get volume object from cinder using volume id.

        Args:
            volume_id (str): volume id
            check (bool): flag whether to check step or not

        Returns:
            object: volume

        Raises:
            exceptions.NotFound: if volume with volume_id doesn't exist
            AssertionError: if check failed
        """
        volume = self._client.get(volume_id)

        if check:
            assert_that(volume.id, equal_to(volume_id))

        return volume

    @steps_checker.step
    def check_volume_properties(self, volume, timeout=0, **properties):
        """Step to check volume's properties.

        Args:
            volume (object): cinder volume
            timeout (int): seconds to wait a result of check
            **properties: volume's properties to check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_volume_properties():
            volume.get()
            return waiter.expect_that(volume, has_properties(properties))

        waiter.wait(_check_volume_properties, timeout_seconds=timeout)

    @steps_checker.step
    def check_volume_size(self, volume, size, timeout=0):
        """Step to check volume size.

        Args:
            volume (object): cinder volume
            size (int): expected volume size
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_volume_size():
            volume.get()
            return waiter.expect_that(volume.size, equal_to(size))

        waiter.wait(_check_volume_size, timeout_seconds=timeout)

    @steps_checker.step
    def get_attached_server_ids(self, volume, check=True):
        """Step to retrieve IDs of servers attached to volume.

        Args:
            volume (object): cinder volume
            check (bool): flag whether to check step or not

        Returns:
            list: attached server ids

        Raises:
            AssertionError: if no attached server IDs
        """
        attached_ids = [attach['server_id'] for attach in volume.attachments]

        if check:
            assert_that(attached_ids, is_not(empty()))

        return attached_ids

    @steps_checker.step
    def check_volume_type(self, volume, volume_type, timeout=0):
        """Step to check volume type.

        Args:
            volume (object): cinder volume
            volume_type (obj): expected volume type
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_volume_type():
            volume.get()
            return waiter.expect_that(volume.volume_type,
                                      equal_to(volume_type.name))

        waiter.wait(_check_volume_type, timeout_seconds=timeout)

    @steps_checker.step
    def check_volume_attachments(self, volume, server_ids=None, timeout=0):
        """Step to check volume attachments.

        Args:
            volume (object): cinder volume
            server_ids (list): list of nova servers ids
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        server_ids = server_ids or []

        def _check_volume_attachments():
            volume.get()
            attached_ids = self.get_attached_server_ids(volume, check=False)
            return waiter.expect_that(set(attached_ids),
                                      equal_to(set(server_ids)))

        waiter.wait(_check_volume_attachments, timeout_seconds=timeout)

    @steps_checker.step
    def check_volume_extend_failed_incorrect_size(self, volume, size):
        """Step to check negative volume extend to incorrect size.

        Args:
            volume (object): cinder volume
            size (int): volume size

        Raises:
            AssertionError: if check failed
        """
        error_message = 'New size for extend must be greater than current size'
        assert_that(
            calling(self.volume_extend).with_args(volume, size, check=False),
            raises(exceptions.BadRequest, error_message))

    @steps_checker.step
    def check_volume_not_created_with_incorrect_size(self, size):
        """Step to check negative volume creation with negative/zero size.

        Args:
            size (int): volume size

        Raises:
            AssertionError: if check failed
        """
        error_message = 'must be an integer.+greater than (?:0|zero)'
        assert_that(
            calling(self.create_volumes).with_args(
                names=[None], size=size, check=False),
            raises(exceptions.BadRequest, error_message))

    @steps_checker.step
    def check_volume_not_created_with_size_more_than_limit(self, size):
        """Step to check negative volume creation with size more than limit.

        Args:
            size (int): volume size in gb

        Raises:
            AssertionError: if check failed
        """
        error_message = (
            "VolumeSizeExceedsLimit: Requested volume size {} is larger "
            "than maximum allowed limit").format(size)
        assert_that(
            calling(self.create_volumes).with_args(
                names=[None], size=size, check=False),
            raises(exceptions.OverLimit, error_message))

    @steps_checker.step
    def check_volume_extend_failed_size_more_than_limit(self, volume, size):
        """Step to check negative volume extend to size more than limit.

        Args:
            volume (object): cinder volume
            size (int): volume size

        Raises:
            AssertionError: if check failed
        """
        error_message = (
            "VolumeSizeExceedsLimit: Requested volume size {} is larger "
            "than maximum allowed limit").format(size)
        assert_that(
            calling(self.volume_extend).with_args(volume, size, check=False),
            raises(exceptions.OverLimit, error_message))

    @steps_checker.step
    def volume_upload_to_image(self,
                               volume,
                               image_name=None,
                               force=False,
                               container_format='bare',
                               disk_format='raw',
                               check=True):
        """Step to upload volume to image.

        Args:
            volume (object): The :class:`Volume` to upload
            image_name (str): The new image name
            force (bool): Enables or disables upload of a volume that is
            attached to an instance
            container_format (str): Container format type
            disk_format (str): Disk format type
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check was triggered to False

        Returns:
            object: image
        """
        image_name = image_name or next(utils.generate_ids())

        response, image = self._client.upload_to_image(
            volume=volume,
            force=force,
            image_name=image_name,
            container_format=container_format,
            disk_format=disk_format)

        if check:
            assert_that(response.status_code, equal_to(202))
            assert_that(image['os-volume_upload_image'], has_entries({
                'container_format': container_format,
                'disk_format': disk_format,
                'image_name': image_name,
                'id': volume.id,
                'size': volume.size
            }))

        return image

    @steps_checker.step
    def volume_extend(self, volume, size, check=True):
        """Step to extend volume to new size.

        Args:
            volume (object): cinder volume
            size (int): The new volume size
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        self._client.extend(volume, size)

        if check:
            self.check_volume_size(volume, size,
                                   timeout=config.VOLUME_AVAILABLE_TIMEOUT)

    @steps_checker.step
    def update_volume(self, volume, new_name=None,
                      new_description=None, check=True):
        """Step to update volume.

        Args:
            volume (object): cinder volume
            new_name (str); new name for volume
            new_description (str): new description for volume
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        update_data = {}
        if new_name:
            update_data['name'] = new_name
        if new_description:
            update_data['description'] = new_description
        self._client.update(volume, **update_data)

        if check:
            volume.get()
            assert_that(volume, has_properties(update_data))

    @steps_checker.step
    def check_volume_update_failed(self, volume, new_name=None,
                                   new_description=None):
        """Step to check negative volume update.

        Args:
            volume (object): cinder volume
            new_name (str): new name for volume
            new_description(str): new description for volume

        Raises:
            BadRequest: if check failed
        """
        assert_that(
            calling(
                self.update_volume).with_args(volume, new_name=new_name,
                                              new_description=new_description,
                                              check=False),
            raises(exceptions.BadRequest))

    @steps_checker.step
    def check_migration_status(self, volume, status, timeout=0):
        """Step to check migration status.

        Args:
            volume (object): cinder volume to check migration status
            status (str): expected migration status
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if migration status is not equal to 'status'
                after timeout
        """

        def _check_migration_status():
            volume.get()
            return waiter.expect_that((volume.migration_status or '').lower(),
                                      equal_to(status.lower()))

        waiter.wait(_check_migration_status, timeout_seconds=timeout)

    @steps_checker.step
    def check_volume_host(self, volume, host, timeout=0):
        """Step to check volume host.

        Args:
            volume (object): cinder volume to check host
            host (str): expected volume host to check
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if volume host is not changed after timeout
        """

        def _check_volume_host():
            volume.get()
            volume_host = getattr(volume, config.VOLUME_HOST_ATTR)
            return waiter.expect_that(volume_host.lower(),
                                      equal_to(host.lower()))

        waiter.wait(_check_volume_host, timeout_seconds=timeout)

    @steps_checker.step
    def set_volume_bootable(self, volume, bootable, check=True):
        """Step to set volume bootable.

        Args:
            volume (object): cinder volume
            bootable (bool): flag whether to set or unset volume bootable
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        if bootable:
            bootable = 'true'
        else:
            bootable = 'false'
        self._client.set_bootable(volume, bootable)

        if check:
            volume.get()
            assert_that(volume, has_property('bootable', bootable))

    @steps_checker.step
    def change_volume_type(self, volume, volume_type, policy, check=True):
        """Step to retype volume.

        Args:
            volume (object): cinder volume
            volume_type (object): cinder volume type
            policy (str): policy for migration during the retype
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        self._client.retype(volume, volume_type.name, policy)

        if check:
            self.check_volume_type(volume, volume_type,
                                   timeout=config.VOLUME_RETYPE_TIMEOUT)

    @steps_checker.step
    def check_volume_deletion_without_cascading_failed(self, volume):
        """Step to check negative volume deletion without cascade option.

        Args:
            volume (object): cinder volume

        Raises:
            BadRequest: if check failed
        """
        assert_that(calling(self.delete_volumes).with_args([volume],
                                                           check=False),
                    raises(exceptions.BadRequest))
        self.check_volume_presence(volume)

    @steps_checker.step
    def check_volume_deletion_with_wrong_id(self):
        """Step to check negative volume deletion with wrong volume id.

        Raises:
            AssertionError: if NotFound exception is not appeared
        """
        assert_that(calling(self._client.delete).with_args(str(uuid.uuid4())),
                    raises(exceptions.NotFound))

    @steps_checker.step
    def migrate_volume(self, volume, host, force_host_copy=False,
                       lock_volume=False, check=True):
        """Step to migrate volume.

        Args:
            volume (object): volume to migrate
            host (str): target host to migrate volume
            force_host_copy (bool): skip driver optimizations
            lock_volume (bool): lock the volume
            check (bool): flag whether to check step or not

        Raises:
            TimeoutExpired: if migration status is not 'success' or
                volume host is not changed after timeout
        """
        self._client.migrate_volume(volume,
                                    host,
                                    force_host_copy=force_host_copy,
                                    lock_volume=lock_volume)
        if check:
            self.check_migration_status(
                volume, status=config.STATUS_SUCCESS,
                timeout=config.VOLUME_AVAILABLE_TIMEOUT)
            self.check_volume_host(volume, host)

    @steps_checker.step
    def get_volume_migrate_host(self, volume, nodes, check=True):
        """Step to get cinder host to migrate volume.

        Arguments:
            volume (str): migrating volume
            nodes (iterable): cinder nodes
            check (bool): flag whether to check step or not

        Returns:
            str: host to volume migrate

        Raises:
            LookupError: if no available hosts to migrate
        """
        current_host = getattr(volume, config.VOLUME_HOST_ATTR)

        for node in nodes:
            if not current_host.startswith(node.fqdn):
                return node.fqdn + config.VOLUME_HOST_POSTFIX

        else:
            if check:
                raise LookupError("No available hosts to migrate volume from "
                                  "host {!r}".format(current_host))

    @steps_checker.step
    def check_cinder_available(self, must_be=True):
        """Step to check cinder availability.

        Args:
            must_be (bool): flag whether cinder must be available or not

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_cinder_available():
            try:
                self.get_volumes(check=False)
                is_available = True
            except exceptions.NotAcceptable:
                is_available = False
            return waiter.expect_that(is_available, equal_to(must_be))

        waiter.wait(_check_cinder_available,
                    timeout_seconds=config.CINDER_AVAILABILITY_TIMEOUT)
