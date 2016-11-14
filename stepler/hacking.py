"""
--------------------
Some hacks for tests
--------------------
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
import types


def settimeout(self, timeout):
    """Wrapper to prevent ability change default timeout to None.

    Note:
        This is workaround for https://github.com/kennethreitz/requests/blob/5524472cc76ea00d64181505f1fbb7f93f11cc2b/requests/packages/urllib3/connectionpool.py#L381  # noqa

    Args:
        timeout (int): Seconds timeout for socket.
    """
    if self.gettimeout() and timeout is None:
        return
    settimeout_func(self, timeout)


settimeout_func = socket.socket.settimeout.im_func
settimeout.__doc__ = settimeout_func.__doc__
socket.socket.settimeout = types.MethodType(settimeout, None, socket.socket)
