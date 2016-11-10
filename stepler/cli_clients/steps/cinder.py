"""
-----------------------
Cinder CLI client steps
-----------------------
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

from hamcrest import assert_that, is_  # noqa H301
from six import moves

from stepler.cli_clients.steps import base
from stepler import config
from stepler.third_party import output_parser
from stepler.third_party import steps_checker


class CliCinderSteps(base.BaseCliSteps):
    """CLI cinder client steps."""

    @steps_checker.step
    def rename_volume(self, volume, name=None, description=None, check=True):
        """Step to change volume's name or description using CLI.

        Args:
            volume (object): cinder volume to edit
            name (str): new volume name
            description (str): new volume description
            check (bool): flag whether to check step or not
        """
        err_msg = 'One of `name` or `description` should be passed.'
        assert_that(any([name, description]), is_(True), err_msg)

        cmd = 'cinder rename'
        if description is not None:
            cmd += ' --description ' + moves.shlex_quote(description)
        cmd += ' ' + volume.id
        if name:
            cmd += ' ' + name

        self.execute_command(cmd,
                             timeout=config.VOLUME_AVAILABLE_TIMEOUT,
                             check=check)

    @steps_checker.step
    def create_volume_backup(self, volume, name=None, description=None,
                             container=None, check=True):
        """Step to create volume backup using CLI.

        Args:
            volume (object): cinder volume
            name (str): name of backup to create
            description (str): description
            container (str): name of the backup service container
            check (bool): flag whether to check step or not

        Returns:
            dict: cinder volume backup
        """
        cmd = 'cinder backup-create'
        if name:
            cmd += ' --name ' + name
        if description is not None:
            cmd += ' --description ' + moves.shlex_quote(description)
        if container:
            cmd += ' --container ' + container

        cmd += ' ' + volume.id

        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.BACKUP_AVAILABLE_TIMEOUT, check=check)

        backup_table = output_parser.table(stdout)
        backup = {key: value for key, value in backup_table['values']}

        return backup

    @steps_checker.step
    def show_volume_backup(self, backup, check=True):
        """Step to show volume backup using CLI.

        Args:
            backup (object): cinder volume backup object to show
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        cmd = 'cinder backup-show ' + backup.id

        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.BACKUP_SHOW_TIMEOUT, check=check)

        backup_table = output_parser.table(stdout)
        show_result = {key: value for key, value in backup_table['values']}

        if check:
            # TODO(agromov): add checks when parser can process unicode:
            # 1) show_result['name'] equals backup.name
            # 2) show_result['description'] equals backup.description
            # 3) show_result['container'] equals backup.container
            assert_that(show_result['id'], is_(backup.id))

    @steps_checker.step
    def create_volume_snapshot(self, volume, name=None, description=None,
                               check=True):
        """Step to create volume snapshot using CLI.

        Args:
            volume (object): cinder volume
            name (str): name of snapshot to create
            description (str): snapshot description
            check (bool): flag whether to check step or not

        Returns:
            dict: cinder volume snapshot
        """
        cmd = 'cinder snapshot-create'
        if name:
            cmd += ' --name ' + name
        if description is not None:
            cmd += ' --description ' + moves.shlex_quote(description)

        cmd += ' ' + volume.id

        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.SNAPSHOT_AVAILABLE_TIMEOUT, check=check)

        snapshot_table = output_parser.table(stdout)
        snapshot = {key: value for key, value in snapshot_table['values']}

        return snapshot

    @steps_checker.step
    def create_volume_transfer(self, volume, name=None, check=True):
        """Step to create volume transfer using CLI.

        Args:
            volume (object): cinder volume
            name (str): name of transfer to create
            check (bool): flag whether to check step or not

        Returns:
            dict: cinder volume transfer
        """
        cmd = 'cinder transfer-create'
        if name:
            cmd += ' --name ' + name

        cmd += ' ' + volume.id

        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.TRANSFER_CREATE_TIMEOUT, check=check)

        transfer_table = output_parser.table(stdout)
        transfer = {key: value for key, value in transfer_table['values']}
        return transfer

    @steps_checker.step
    def show_volume_transfer(self, volume_transfer, volume, check=True):
        """Step to show volume transfer using CLI.

        Args:
            volume_transfer (object): cinder volume transfer object to show
            volume (object): related cinder volume
            check (bool): flag whether to check step or not

        Raises:
            AssertionError: if check failed
        """
        cmd = 'cinder transfer-show ' + volume_transfer.id

        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.TRANSFER_SHOW_TIMEOUT, check=check)

        transfer_table = output_parser.table(stdout)
        transfer_dict = {key: value for key, value in transfer_table['values']}

        if check:
            # TODO(aallakhverdieva): add check
            # transfer_dict['name'] equals volume_transfer.name
            assert_that(transfer_dict['id'], is_(volume_transfer.id))
            assert_that(transfer_dict['volume_id'], is_(volume.id))
