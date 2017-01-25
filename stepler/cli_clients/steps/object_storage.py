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

from hamcrest import assert_that, empty, is_in, is_not  # noqa H301
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
        self.execute_command(cmd, check=check)

    @steps_checker.step
    def list(self, check=True):
        """Step to get swift list.

        Args:
            check (bool): flag whether to check result or not

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        cmd = 'swift list'
        exit_code, stdout, stderr = self.execute_command(cmd, check=check)
        return stdout

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
