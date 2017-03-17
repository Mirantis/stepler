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

from stepler import config
from stepler.cli_clients.steps import base
from stepler.third_party import steps_checker


class CliSwiftSteps(base.BaseCliSteps):
    """CLI object storage client steps."""

    def execute_command(self,
                        cmd,
                        use_openrc=True,
                        environ=None,
                        **kwargs):
        """Execute swift cli command in shell.

        Swift can't determine keystone version, so we set ``OS_AUTH_URL``
        to point to correct keystone endpoint.

        Args:
            cmd (str): client command to execute
            use_openrc (bool): add 'source openrc' before `cmd` executing
            environ (dict): shell environment variables to set before `cmd`
                executing. By default it not set any variable
            **kwargs: base class arguments

        Returns:
            tuple: (exit_code, stdout, stderr) - result of command execution

        Raises:
            AssertionError: if result check was failed
        """
        environ = environ or {}
        environ['OS_AUTH_URL'] = config.AUTH_URL
        return super(CliSwiftSteps, self).execute_command(cmd, use_openrc, environ, **kwargs)

    @steps_checker.step
    def create(self, container_name, check=True):
        """Step to create swift container.

        Args:
            container_name (str): name of created container
            check (bool): flag whether to check result or not

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        cmd = 'swift post '
        cmd += moves.shlex_quote(container_name)
        self.execute_command(cmd, check=check)

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
    def upload(self, container_name, object_name, check=True):
        """Step to upload object to container.

        Args:
            container_name (str): object storage container
            object_name (str): name of object to upload
            check (bool): flag whether to check result or not

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        cmd = 'swift upload '
        cmd += '{} {}'.format(moves.shlex_quote(container_name),
                              moves.shlex_quote(object_name))
        cmd_to_create_object = 'dd if=/dev/zero of={} bs=1M count=1'.format(
            object_name)
        self.execute_command(cmd_to_create_object)
        exit_code, stdout, stderr = self.execute_command(cmd, check=check)
        if check:
            assert_that(object_name, equal_to(stdout))
        cmd_to_delete_object = 'rm {}'.format(object_name)
        self.execute_command(cmd_to_delete_object)

    @steps_checker.step
    def delete(self, container_name, check=True):
        """Step to delete swift container.

        Args:
            container_name (str): object storage container
            check (bool): flag whether to check result or not

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        cmd = 'swift delete '
        cmd += moves.shlex_quote(container_name)
        self.execute_command(cmd, check=check)

    @steps_checker.step
    def check_container_presence(self, container_name, must_present=True):
        """Step to check that container is in container list.

        Args:
            container_name (str): object storage container
            must_present (bool): flag whether container should present or not

        Raises:
            AssertionError: check failed if container exists/doesn't exist in
            containers list
        """
        containers_list = self.list()
        if must_present:
            assert_that(containers_list, is_not(empty()))
            assert_that(container_name, is_in(containers_list))
        else:
            assert_that(container_name, is_not(is_in(containers_list)))

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
        objects_in_container = self.list(container_name=container_name)
        assert_that(object_name, is_in(objects_in_container))
