"""
SSH client.

@author: schipiga@mirantis.com
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

import paramiko
import six

__all__ = [
    'SshClient'
]


class SshClient(object):
    """SSH client."""

    def __init__(self, host, port=22, username=None, password=None, pkey=None,
                 timeout=None, proxy_cmd=None):
        """Constructor."""
        self._host = host
        self._port = port
        self._pkey = paramiko.RSAKey.from_private_key(six.StringIO(pkey))
        self._timeout = timeout
        self._username = username
        self._password = password
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._proxy_cmd = proxy_cmd

    def connect(self):
        """Connect to ssh server."""
        sock = paramiko.ProxyCommand(self._proxy_cmd) \
            if self._proxy_cmd else None

        self._ssh.connect(self._host, self._port, pkey=self._pkey,
                          timeout=self._timeout, banner_timeout=self._timeout,
                          username=self._username, password=self._password,
                          sock=sock)

    def close(self):
        """Close ssh connection."""
        self._ssh.close()
