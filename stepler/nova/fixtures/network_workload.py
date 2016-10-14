"""
-------------------------
Network workload fixtures
-------------------------
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


from multiprocessing import dummy as mp
import socket

import pytest


__all__ = [
    'make_traffic',
]


@pytest.yield_fixture
def make_traffic():
    """Fixture to generate traffic to server.

    Can be called several time during test. Simplest listener can be started
    with `nc -k -l <port>`.
    """

    threads = []

    def _send(pipe, s):
        mbyte = bytearray(['0'] * 1024**2)
        while True:
            s.send(mbyte)
            if pipe.poll():
                break
        s.close()

    def _make_traffic(ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((ip, port))
        parent_conn, child_conn = mp.Pipe()
        thread = mp.Process(target=_send, args=(child_conn, s))
        threads.append((thread, parent_conn))
        thread.start()

    yield _make_traffic

    for thread, pipe in threads:
        pipe.send(True)
        pipe.close()
        thread.join()
