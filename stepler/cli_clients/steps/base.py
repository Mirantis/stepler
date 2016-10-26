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

from hamcrest import assert_that, is_  # noqa


class BaseCliSteps(object):
    """Base CLI client steps."""

    def __init__(self, executor):
        """Base CLI steps executor.

        Args:
            executor (callable): function to execute command and returns tuple:
                (exit_code, stdout, stderr)

        """
        self._executor = executor

    def execute_command(self, cmd, timeout=0, check=True):
        """Execute client command in shell.

        Args:
            cmd (str): client command to execute
            timeout (int): seconds to wait command executed
            check (bool): flag whether to check result or not

        Returns:
            tuple: (exit_code, stdout, stderr) - result of command execution

        Raises:
            AssertionError: if result check was failed
        """
        result = self._executor(cmd, timeout=timeout)
        if check:
            assert_that(result[0], is_(0))
        return result
