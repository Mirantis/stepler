"""
---------------
os_faults steps
---------------
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

import os
import tempfile

from hamcrest import assert_that, is_not, empty, only_contains, has_properties  # noqa

from stepler import base
from stepler.third_party import steps_checker
from stepler.third_party import utils

__all__ = ['OsFaultsSteps']


class OsFaultsSteps(base.BaseSteps):
    """os-faults steps."""

    @steps_checker.step
    def get_nodes(self, fqdns=None, check=True):
        """Step to get nodes.

        Args:
            fqdns (list): nodes hostnames to filter
            check (bool): flag whether check step or not

        Returns:
            list of nodes
        """
        nodes = self._client.get_nodes(fqdns=fqdns)

        if check:
            assert_that(nodes, is_not(empty()))

        return nodes

    @steps_checker.step
    def restart_service(self, name, check=True):
        """Step to restart a service.

        Args:
            name (str): service name
            check (bool): flag whether to check step or not
        """
        # TODO(ssokolov) add check of service names
        service = self._client.get_service(name=name)
        # TODO(ssokolov) add check of exceptions
        service.restart()

        if check:
            # TODO(ssokolov) replace by real check
            assert_that([service], is_not(empty()))

    @steps_checker.step
    def download_file(self, node, path, check=True):
        """Copy file from remote host to tempfile.

        Args:
            node (obj): node to fetch file from
            path (str): path to file on remote host
            check (bool): flag whether check step or not

        Returns:
            str: path to destination file

        Raises:
            ValueError: if destination file is not a regular file
        """
        dest = tempfile.mktemp()
        task = {
            'fetch': {
                'src': path,
                'dest': dest,
                'flat': True,
            }
        }
        node.run_task(task)
        if check:
            if not os.path.isfile(dest):
                raise ValueError('Destination path is not a regular file')
        return dest

    @steps_checker.step
    def check_file_contains_line(self, nodes, path, line):
        """Check that remote file contains line.

        Args:
            nodes (obj): nodes to check file on them
            path (str): path to file on remote hosts
            line (str): line to search in files

        Raises:
            AssertioError: if any of files doesn't contains `line`
        """
        task = {
            'command': 'grep "{line}" "{path}"'.format(
                line=line, path=path)
        }
        result = nodes.run_task(task)
        assert_that(result, only_contains(has_properties(status='OK')))

    @steps_checker.step
    def make_backup(self, nodes, path, suffix=None, check=True):
        """Make backup of file with `path`.

        This step makes a copy of file to new file with `suffix` in same
            folder.

        Args:
            nodes (obj): nodes to backup file on them
            path (str): path to file on remote hosts
            suffix (str): suffix to append to original file name
            check (bool): flag whether check step or not

        Raises:
            AssertionError: if backup file not exists after step.

        Returns:
            str: path to backup file
        """
        suffix = suffix or utils.generate_ids('backup', length=30)
        backup_path = "{}.{}".format(path, suffix)

        task = {
            'command': 'cp "{path}" "{backup_path}"'.format(
                path=path, backup_path)
        }
        nodes.run_task(task)

        if check:
            self.check_file_exists(nodes, path=backup_path)

        return backup_path


    @steps_checker.step
    def restore_backup(self, nodes, path, backup_path, check=True):
        """Restore file with `path` from backup.

        This step restore file from backup with `suffix` placed in same folder.

        Args:
            nodes (obj): nodes to restore file on them
            path (str): path to file on remote hosts
            backup_path (str): path to backup
            suffix (str): suffix to make backup file name
            check (bool): flag whether check step or not

        Raises:
            AssertionError: if backup file exists after step.
        """
        task = {
            'command': 'mv "{backup_path}" "{path}"'.format(
                backup_path=backup_path, path=path)
        }
        nodes.run_task(task)

        if check:
            self.check_file_exists(nodes, path=backup_path, present=False)

    @steps_checker.step
    def check_file_exists(self, nodes, path, present=True):
        """Check that remote file exists.

        Args:
            nodes (obj): nodes to check file on them
            path (str): path to file on remote hosts
            present (bool): should file be present or not

        Raises:
            AssertionError: if any of nodes doesn't contains file
        """
        command = 'ls "{path}"'.format(path=path)
        if not present:
            command = '! ' + command
        task = {'shell': command}
        result = nodes.run_task(task)
        assert_that(result, only_contains(has_properties(status='OK')))

    @steps_checker.step
    def patch_ini_file(self, nodes, path, option, value, section=None,
                       check=True):
        """Patch INI like file.

        Args:
            nodes (obj): nodes hostnames to patch file on it
            path (str): path to ini file on remote host
            option (str): name of option to add/override
            value (str): value to add/override
            section (str): name of section to process. 'DEFAULT' will be used
                if `section` is None
            check (bool): flag whether check step or not

        Returns:
            str: path to original file
        """
        backup_path = self.make_backup(nodes, path)
        task = {
            'ini_file': {
                'backup': False,
                'dest': path,
                'section': section or 'DEFAULT',
                'option': option,
                'value': value,
            }
        }
        nodes.run_task(task)
        if check:
            self.check_file_contains_line(nodes, path, "{} = {}".format(option,
                                                                        value))
        return backup_path
