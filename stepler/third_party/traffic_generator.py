"""
-----------------
Traffic generator
-----------------
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
import threading


class TrafficGenerator(object):
    """Traffic generator context manager.

    Generates TCP traffic to specified ip and port.
    """

    def __init__(self, ip, port, block_size=1024**2, socket_timeout=5):
        """Constructor.

        Args:
            ip (str): ip address to send traffic to
            port (int): port to send traffic to
            block_size (int): size of data chunk
            socket_timeout (int): socket timeout
        """
        self._ip = ip
        self._port = port
        self._payload = bytearray(['0'] * block_size)
        self._socket_timeout = socket_timeout
        self.is_started = False

    def _connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self._socket_timeout)
        sock.connect((self._ip, self._port))
        return sock

    def start(self):
        """Start traffic generator."""
        assert not self.is_started, "Traffic generator is started already"

        def _generate_traffic(sock, stop_ev):
            while not stop_ev.is_set():
                sock.send(self._payload)
            sock.close()

        self.is_started = True
        sock = self._connect()
        self.stop_ev = threading.Event()
        self._t = threading.Thread(
            target=_generate_traffic, args=(sock, self.stop_ev))
        self._t.start()

    def stop(self):
        """Stop traffic generator."""
        assert self.is_started, "Traffic generator isn't started yet"

        self.stop_ev.set()
        self._t.join()
        self.is_started = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, ext_type, ext_val, ext_tb):
        self.stop()
