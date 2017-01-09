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
import re
import signal
import subprocess
import sys
import time

import pytest

from stepler import config


__all__ = [
    'generate_os_workload',
]


@pytest.yield_fixture
def generate_os_workload(cirros_image):
    """Fixture to generate openstack workload.

    This fixture launches a script which creates and deletes networks, subnets
    and servers cyclically.
    Finally, the signal is sent to the script, and it provides correct
    deletion of objects created before.
    """

    child_processes = []

    def _generate_os_workload():

        module_location = sys.modules['stepler.third_party']
        # ex: < module 'stepler.third_party' from
        # '/home/ubuntu/stepler/stepler/third_party/__init__.pyc' >
        third_party_path = re.findall("from \'(/.+third_party/)",
                                      str(module_location))[0]

        cmd = third_party_path + "os_load_generator.py"
        # ex: /home/ubuntu/stepler/stepler/third_party/os_load_generator.py
        child_process = subprocess.Popen(['python', cmd])
        child_processes.append(child_process)

        # sleep to finish init and start main loop
        time.sleep(config.DELAY_AFTER_OS_WORKLOAD_START)

    yield _generate_os_workload

    for child_process in child_processes:
        os.kill(child_process.pid, signal.SIGTERM)
        child_process.wait()
