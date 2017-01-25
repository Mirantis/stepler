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

from stepler.cli_clients.steps import base
from stepler import config
from stepler.third_party import output_parser
from stepler.third_party import steps_checker


class CliSwiftSteps(base.BaseCliSteps):
    """CLI object storage client steps."""

    @steps_checker.step
    def swift_list(self, check=True):
        """Step to get swift list.

        Args:
            check (bool): flag whether to check result or not

        Raises:
            AnsibleExecutionException: if command execution failed
        """
        cmd = 'swift list'
        exit_code, stdout, stderr = self.execute_command(
            cmd, timeout=config.SERVER_LIST_TIMEOUT, check=check)
        if check:
            containers_list = output_parser.listing(stdout)
            return containers_list

    @steps_checker.step
    def check_containers_list_contains(self, container):
        """Step to check that image is in images list.

        Args:
            container (obj): object storage container

        Raises:
            AssertionError: check failed if container is not present in
            containers list
        """
        containers_list = self.swift_list()
        assert_that(containers_list, is_not(empty()))
        assert_that(container, is_in(containers_list))
