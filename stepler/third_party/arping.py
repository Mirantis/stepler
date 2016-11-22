"""
------------------------
Arpings checking helpers
------------------------
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
# limitations under the License.from functools import wraps

import contextlib
import re
import tempfile


@contextlib.contextmanager
def arping(ip, iface, remote):
    """Non-blocking context manager for run arping on backgroud.

    It yields ping results (dict) and update it with 'sent' and 'received'
    values after CM will be exited.

    Args:
        ip (str): ip to arping
        iface (string): name of interface, like 'eth0'
        remote (obj): instance of stepler.third_party.ssh.SshClient

    Yields:
        dict: arping results
    """
    cmd = "arping -I {iface} {ip}".format(iface=iface, ip=ip)
    output_file = tempfile.mktemp()
    with remote.sudo():
        pid = remote.background_call(cmd, stdout=output_file)
    result = {}
    yield result
    with remote.sudo():
        remote.execute('kill -SIGINT {}'.format(pid))
        stdout = remote.check_call("cat {}".format(output_file)).stdout
        remote.execute('rm {}'.format(output_file))
    search_result = re.search(
        r"Sent (?P<sent>\d+).+?Received (?P<received>\d+)", stdout, re.DOTALL)
    if search_result is not None:
        for key, value in search_result.groupdict().items():
            result[key] = int(value)
