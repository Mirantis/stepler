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

import contextlib
import os
import tempfile

from hamcrest import assert_that, is_not, empty, only_contains, has_properties  # noqa

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = ['OsFaultsSteps']


class OsFaultsSteps(BaseSteps):
    """os-faults steps."""

    @step
    def get_nodes(self, fqdns=None, check=True):
        """Step to get nodes.

        Args:
            check (bool): flag whether to check step or not
            fqdns (list): nodes hostnames to filter

        Returns:
            list of nodes
        """
        nodes = self._client.get_nodes(fqdns=fqdns)

        if check:
            assert_that(nodes, is_not(empty()))

        return nodes

    @step
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

    @step
    def download_file(self, fqdn, path, check=True):
        """Copy file from remote host to tempfile.

        Args:
            fqdn (str): node hostname to fetch file from
            path (str): path to file on remote host
        """
        dest = tempfile.mktemp()
        task = {
            'fetch': {
                'src': path,
                'dest': dest,
                'flat': True,
            }
        }
        node = self.get_nodes(fqdns=[fqdn]).pick()
        node.run_task(task)
        if check:
            if not os.path.isfile(dest):
                raise Exception('Destination path is not a regular file')
        return dest

    @step
    def check_file_contains_line(self, fqdns, path, line):
        """Check that remote file contains line.

        Args:
            fqdns (list): nodes hostnames to check file on them
            path (str): path to file on remote hosts
            line (str): line to search in files

        Raises:
            AssertioError: if any of files doesn't contains `line`
        """
        task = {
            'command': 'grep "{line}" "{path}"'.format(
                line=line, path=path)
        }
        nodes = self.get_nodes(fqdns=fqdns)
        result = nodes.run_task(task)
        assert_that(result, only_contains(has_properties(status='OK')))

    @step
    def make_backup(self, fqdns, path, suffix='backup', check=True):
        """Make backup of file with `path`.

        This step makes a copy of file to new file with `suffix` in same
            folder.

        Args:
            fqdns (list): nodes hostnames to backup file on them
            path (str): path to file on remote hosts
            suffix (str): suffix to append to original file name
        Raises:
            AssertionError: if backup file not exists after step.
        """
        task = {
            'command': 'cp "{path}" "{path}.{suffix}"'.format(
                path=path, suffix=suffix)
        }
        nodes = self.get_nodes(fqdns=fqdns)
        nodes.run_task(task)

        if check:
            self.check_file_exists(
                fqdns,
                path='"{path}.{suffix}"'.format(
                    path=path, suffix=suffix))

    @step
    def restore_backup(self, fqdns, path, suffix='backup', check=True):
        """Restore file with `path` from backup.

        This step restore file from backup with `suffix` placed in same folder.

        Args:
            fqdns (list): nodes hostnames to restore file on them
            path (str): path to file on remote hosts
            suffix (str): suffix to make backup file name
        Raises:
            AssertionError: if backup file exists after step.
        """
        task = {
            'command': 'mv "{path}.{suffix}" "{path}"'.format(
                path=path, suffix=suffix)
        }
        nodes = self.get_nodes(fqdns=fqdns)
        nodes.run_task(task)

        if check:
            self.check_file_exists(
                fqdns,
                path='"{path}.{suffix}"'.format(
                    path=path, suffix=suffix),
                present=False)

    @step
    def check_file_exists(self, fqdns, path, present=True):
        """Check that remote file exists.

        Args:
            fqdns (list): nodes hostnames to check file on them
            path (str): path to file on remote hosts
            present (bool): should file be present or not

        Raises:
            AssertionError: if any of nodes doesn't contains file
        """
        command = 'ls "{path}"'.format(path=path)
        if not present:
            command = '! ' + command
        task = {'shell': command}
        nodes = self.get_nodes(fqdns=fqdns)
        nodes.run_task(task)
        result = nodes.run_task(task)
        assert_that(result, only_contains(has_properties(status='OK')))

    @step
    @contextlib.contextmanager
    def patch_ini(self, fqdns, path, option, value, section=None, check=True):
        """Patch INI like file.

        Args:
            fqdns (list): nodes hostnames to patch file on it
            path (str): path to ini file on remote host
            option (str): name of option to add/override
            value (str): value to add/override
            section (str): name of section to process. 'DEFAULT' will be used
                if `section` is None
        """
        self.make_backup(fqdns, path)
        task = {
            'ini_file': {
                'backup': True,
                'dest': path,
                'section': section or 'DEFAULT',
                'option': option,
                'value': value,
            }
        }
        nodes = self.get_nodes(fqdns=fqdns)
        nodes.run_task(task)
        if check:
            self.check_file_contains_line(fqdns, path, "{} = {}".format(option,
                                                                        value))
        yield
        self.restore_backup(fqdns, path)
