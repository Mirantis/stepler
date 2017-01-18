"""
---------------------------
Openstack workload fixtures
---------------------------
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
import subprocess
import time

import pytest

from stepler import config


__all__ = [
    'generate_os_workload',
]


@pytest.yield_fixture
def generate_os_workload(cirros_image):
    """Fixture to generate openstack workload.

    This fixture launches a script which generates Openstack workload, ex:
    creates and deletes networks, subnets and servers cyclically.
    Finally, the signal is sent to the script, and it provides correct
    deletion of objects created before.
    For correct execution of generation scripts, it's supposed that
    at least one image exists.

    Returns:
        function: function to generate openstack workload
    """
    child_processes = []

    def _generate_os_workload(file):

        script_path = os.path.join(config.OS_LOAD_SCRIPTS_DIR, file)
        child_process = subprocess.Popen(script_path)
        child_processes.append(child_process)

        # sleep to finish init and start main loop
        time.sleep(config.DELAY_AFTER_OS_WORKLOAD_START)

    yield _generate_os_workload

    for child_process in child_processes:
        child_process.terminate()
        child_process.wait()
