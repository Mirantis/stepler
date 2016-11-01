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

from hamcrest import (assert_that, empty, has_item, has_properties, is_not,
                      only_contains)  # noqa

from stepler import base
from stepler import config
from stepler.third_party import steps_checker
from stepler.third_party import utils

__all__ = ['OsFaultsSteps']


class OsFaultsSteps(base.BaseSteps):
    """os-faults steps."""

    @steps_checker.step
    def get_nodes(self, fqdns=None, service_names=None, check=True):
        """Step to get nodes.

        Args:
            fqdns (list): nodes hostnames to filter
            service_names (list): names of services to filter nodes with
            check (bool): flag whether check step or not

        Returns:
            list of nodes
        """
        if service_names:
            service_fqdns = set()
            for service_name in service_names:
                nodes = self._client.get_service(service_name).get_nodes()
                for host in nodes.hosts:
                    service_fqdns.add(host.fqdn)
            if not fqdns:
                fqdns = service_fqdns
            else:
                fqdns = set(fqdns)
                fqdns &= service_fqdns
        nodes = self._client.get_nodes(fqdns=fqdns)

        if check:
            assert_that(nodes, is_not(empty()))

        return nodes

    @steps_checker.step
    def get_node(self, fqdns=None, service_names=None, check=True):
        """Step to get one node.

        Args:
            fqdns (list): nodes hostnames to filter
            service_names (list): names of services to filter nodes with
            check (bool): flag whether check step or not

        Returns:
            FuelNodeCollection: one node
        """
        nodes = self.get_nodes(
            fqdns=fqdns, service_names=service_names, check=check)
        return nodes.pick()

    @steps_checker.step
    def get_service(self, name, check=True):
        """Step to get services.

        Args:
            name (str): service name
            check (bool): flag whether check step or not

        Returns:
            object: service
        """
        service = self._client.get_service(name=name)

        if check:
            assert_that(service, is_not(None))

        return service

    @steps_checker.step
    def restart_services(self, names, check=True):
        """Step to restart a services.

        Args:
            name (str): service name
            check (bool): flag whether to check step or not

        Raises:
            ServiceError: if wrong service name or other errors
        """
        for name in names:
            # TODO(ssokolov) add check of service names
            service = self._client.get_service(name=name)
            # TODO(ssokolov) add check of exceptions
            service.restart()

            if check:
                # TODO(ssokolov) replace by real check
                assert_that([service], is_not(empty()))

    @steps_checker.step
    def download_file(self, node, file_path, check=True):
        """Step to download file from remote host to tempfile.

        Args:
            node (obj): node to fetch file from
            file_path (str): path to file on remote host
            check (bool): flag whether check step or not

        Returns:
            str: path to destination file

        Raises:
            ValueError: if destination file is not a regular file
            AssertionError: if file is empty
        """
        dest = tempfile.mktemp()
        task = {
            'fetch': {
                'src': file_path,
                'dest': dest,
                'flat': True,
            }
        }
        node.run_task(task)
        if check:
            if not os.path.isfile(dest):
                raise ValueError('{!r} is not a regular file'.format(dest))
            file_stat = os.stat(dest)
            assert_that(file_stat.st_size, is_not(0))
        return dest

    @steps_checker.step
    def upload_file(self, node, local_path, remote_path=None, check=True):
        """Step to upload file from local host to remote nodes.

        Args:
            node (obj): node to upload file to
            local_path (str): path to file on local host
            remote_path (str, optional): path to file on remote host. Will be
                generated if omitted.
            check (bool): flag whether check step or not

        Returns:
            str: path to remote file

        Raises:
            AssertionError: if file not exists on remote node after uploading
        """
        if not remote_path:
            remote_path = '/tmp/{}'.format(next(utils.generate_ids('file')))
        task = {
            'copy': {
                'src': local_path,
                'dest': remote_path,
            }
        }
        node.run_task(task)
        if check:
            self.check_file_exists(node, remote_path)

        return remote_path

    @steps_checker.step
    def check_file_contains_line(self, nodes, file_path, line, all=True):
        """Step to check that remote file contains line.

        Args:
            nodes (obj): nodes to check file on them
            file_path (str): path to file on remote hosts
            line (str): line to search in files
            all (bool): presents on all node / any node
        Raises:
            AssertioError: if any of files doesn't contains `line`
        """
        task = {
            'command': 'grep "{line}" "{path}"'.format(
                line=line, path=file_path)
        }
        result = nodes.run_task(task, raise_on_error=all)
        if all:
            assert_that(result,
                        only_contains(has_properties(status=config.STATUS_OK)))
        else:
            assert_that(result,
                        has_item(has_properties(status=config.STATUS_OK)))

    @steps_checker.step
    def make_backup(self, nodes, file_path, suffix=None, check=True):
        """Step to make backup of file with `path`.

        This step makes a copy of file to new file with `suffix` in same
            folder.

        Args:
            nodes (obj): nodes to backup file on them
            file_path (str): path to file on remote hosts
            suffix (str): suffix to append to original file name
            check (bool): flag whether check step or not

        Raises:
            AssertionError: if backup file not exists after step.

        Returns:
            str: path to backup file
        """
        suffix = suffix or utils.generate_ids('backup', length=30)
        backup_path = "{}.{}".format(file_path, suffix)

        task = {
            'command': 'cp "{path}" "{backup_path}"'.format(
                path=file_path, backup_path=backup_path)
        }
        nodes.run_task(task)

        if check:
            self.check_file_exists(nodes, backup_path)

        return backup_path

    @steps_checker.step
    def restore_backup(self, nodes, file_path, backup_path, check=True):
        """Step to restore file with `path` from backup.

        This step restore file from backup with `suffix` placed in same folder.

        Args:
            nodes (obj): nodes to restore file on them
            file_path (str): path to file on remote hosts
            backup_path (str): path to backup
            suffix (str): suffix to make backup file name
            check (bool): flag whether check step or not

        Raises:
            AssertionError: if backup file exists after step.
        """
        task = {
            'command': 'mv "{backup_path}" "{path}"'.format(
                backup_path=backup_path, path=file_path)
        }
        nodes.run_task(task)

        if check:
            self.check_file_exists(nodes, backup_path, present=False)

    @steps_checker.step
    def check_file_exists(self, nodes, file_path, present=True):
        """Step to check that remote file exists.

        Args:
            nodes (obj): nodes to check file on them
            file_path (str): path to file on remote hosts
            present (bool): should file be present or not

        Raises:
            AssertionError: if any of nodes doesn't contains file
        """
        command = 'ls "{path}"'.format(path=file_path)
        if not present:
            command = '! ' + command
        task = {'shell': command}
        result = nodes.run_task(task)
        assert_that(result, only_contains(has_properties(status='OK')))

    @steps_checker.step
    def patch_ini_file(self, nodes, file_path, option, value,
                       section=None, check=True):
        """Step to patch INI like file.

        Args:
            nodes (obj): nodes hostnames to patch file on it
            file_path (str): path to ini file on remote host
            option (str): name of option to add/override
            value (str): value to add/override
            section (str): name of section to process. 'DEFAULT' will be used
                if `section` is None
            check (bool): flag whether check step or not

        Returns:
            str: path to original file
        """
        backup_path = self.make_backup(nodes, file_path)
        task = {
            'ini_file': {
                'backup': False,
                'dest': file_path,
                'section': section or 'DEFAULT',
                'option': option,
                'value': value,
            }
        }
        nodes.run_task(task)
        if check:
            self.check_file_contains_line(
                nodes, file_path, "{} = {}".format(option, value))
        return backup_path

    @steps_checker.step
    def execute_cmd(self, nodes, cmd, check=True):
        """Execute provided bash command on nodes.

        Args:
            nodes (obj): nodes to backup file on them
            cmd (str): bash command to execute
            check (bool): flag whether check step or not

        Raises:
            AssertionError|AnsibleExecutionException: if command execution
                failed in case of check=True

        Returns:
            list: AnsibleExecutionRecord(s)
        """
        task = {'shell': cmd}
        result = nodes.run_task(task, raise_on_error=check)

        if check:
            assert_that(
                result, only_contains(has_properties(status=config.STATUS_OK)))

        return result

    @steps_checker.step
    def check_no_nova_server_artifacts(self, server):
        """Step to check that compute doesn't contain server's artifacts.

        Args:
            server (obj): nova server

        Raises:
            AssertionError: if compute contains server's artifacts
        """
        compute = self.get_nodes(
            fqdns=[getattr(server, 'OS-EXT-SRV-ATTR:hypervisor_hostname')])
        cmd = "ls {} | grep {}".format(config.NOVA_INSTANCES_PATH, server.id)
        result = self.execute_cmd(compute, cmd, check=False)
        assert_that(
            result, only_contains(has_properties(status=config.STATUS_FAILED)))
