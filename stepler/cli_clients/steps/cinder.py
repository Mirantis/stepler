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

from stepler.cli_clients.steps import base
from stepler import config
from stepler.third_party import output_parser
from stepler.third_party import steps_checker


class CliCinderSteps(base.BaseCliSteps):
    """CLI cinder client steps."""

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
        if description:
            cmd += ' --description ' + description
        if container:
            cmd += ' --container ' + container

        cmd += ' ' + volume.id

        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.BACKUP_AVAILABLE_TIMEOUT, check=check)

        backup_table = output_parser.table(stdout)
        backup = {key: value for key, value in backup_table['values']}

        return backup

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
        if description:
            cmd += ' --description ' + description

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
