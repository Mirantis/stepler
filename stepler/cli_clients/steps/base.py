"""
---------------------
Base CLI client steps
---------------------
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
import shlex
import sys

from hamcrest import assert_that, is_not, empty  # noqa

from stepler import config

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

os.environ['OS_PROJECT_DOMAIN_NAME'] = config.PROJECT_DOMAIN_NAME
os.environ['OS_USER_DOMAIN_NAME'] = config.USER_DOMAIN_NAME
os.environ['OS_PROJECT_NAME'] = config.PROJECT_NAME
os.environ['OS_USERNAME'] = config.USERNAME
os.environ['OS_PASSWORD'] = config.PASSWORD
os.environ['OS_AUTH_URL'] = config.AUTH_URL or ''  # env var can't be None


class BaseCliSteps(object):
    """Base CLI client steps."""

    def execute_command(self, cmd, timeout=0, check=True):
        """Execute client command in shell.

        Args:
            cmd (str): client command to execute
            timeout (int): seconds to wait command executed
            check (bool): flag whether to check result or not

        Returns:
            str: result of command execution

        Raises:
            AssertionError: if result check was failed
            CalledProcessError: if command was failed
            TimeoutExpired: if command isn't finished during timeout
        """
        result = subprocess.check_output(shlex.split(cmd), timeout=timeout)
        if check:
            assert_that(result, is_not(empty()))
        return result
