"""
-------------------------------
Object Storage CLI client steps
-------------------------------
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

from hamcrest import assert_that, empty, equal_to, is_in, is_not  # noqa H301
from six import moves

from stepler.cli_clients.steps import base
from stepler.third_party import steps_checker


class CliSwiftSteps(base.BaseCliSteps):
    """CLI object storage client steps."""

    @steps_checker.step
    def create(self, container_name=None, check=True):
        """Step to create swift container.

        Args:
            container_name (str|None): name of created container
            check (bool): flag whether to check result or not

        Returns:
            tuple: execution result (image dict, exit_code, stdout, stderr)

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        cmd = 'swift post '
        if container_name:
            cmd += moves.shlex_quote(container_name)
        exit_code, stdout, stderr = self.execute_command(cmd, check=check)
        return exit_code

    @steps_checker.step
    def list(self, container_name=None, check=True):
        """Step to get swift list.

        Args:
            container_name (str): object storage container
            check (bool): flag whether to check result or not

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        cmd = 'swift list '
        if container_name:
            cmd += moves.shlex_quote(container_name)
        exit_code, stdout, stderr = self.execute_command(cmd, check=check)
        return stdout

    @steps_checker.step
    def upload(self, container_name=None, object_name=None, check=True):
        """Step to upload object to container.

        Args:
            container_name (str): object storage container
            object_name (str): name of object to upload
            check (bool): flag whether to check result or not

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        cmd_to_create_object = 'dd if=/dev/zero of={} bs=1M count=1'.format(
            object_name)
        cmd = 'swift upload '
        if container_name:
            cmd += '{} '.format(moves.shlex_quote(container_name))
        if object_name:
            cmd += moves.shlex_quote(object_name)
        self.execute_command(cmd_to_create_object)
        exit_code, stdout, stderr = self.execute_command(cmd, check=check)
        if check:
            assert_that(object_name, equal_to(stdout))
        cmd_to_delete_object = 'rm {}'.format(object_name)
        self.execute_command(cmd_to_delete_object)

    @steps_checker.step
    def check_container_created_with_exit_code_zero(self, container_name):
        """Step to check that container created with exit code = 0.

        Args:
            container_name (str): object storage container

        Raises:
            AssertionError: check failed if container created with exit code
            different from 0
        """
        exit_code = self.create(container_name=container_name)
        assert_that(exit_code, equal_to(0))

    @steps_checker.step
    def check_containers_list_contains(self, container_name):
        """Step to check that container is in container list.

        Args:
            container_name (str): object storage container

        Raises:
            AssertionError: check failed if container is not present in
            containers list
        """
        containers_list = self.list()
        assert_that(containers_list, is_not(empty()))
        assert_that(container_name, is_in(containers_list))

    @steps_checker.step
    def check_object_in_container(self, container_name, object_name):
        """Step to check if object presents into container objects list.

        Args:
            container_name (str): object storage container
            object_name (str): name of object to upload

        Raises:
            AssertionError: check failed if object does not present in
            container objects list
        """
        self.upload(container_name=container_name, object_name=object_name)
        objects_in_container = self.list(container_name=container_name)
        assert_that(object_name, is_in(objects_in_container))
