"""
--------------
Network checks
--------------
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

import socket


def check_tcp_connect(ip, port=22, timeout=1):
    """Check whether TCP connection to ``ip`` with ``port``.

    Args:
        ip (str): ip to establish connect to
        port (int, optional): TCP port
        timeout (int, optional): socket timeout to wait connection.

    Returns:
        bool: is connection can be established or not
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((ip, port))
        return True
    except socket.error:
        return False
