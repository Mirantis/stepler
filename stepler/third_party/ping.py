"""
----------------------
Pings checking helpers
----------------------
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
import os
import re
import signal
import sys
import tempfile

import waiting

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess


class PingResult(object):
    """Ping result class.

    Useful for object-oriented access to results of ping (such as transmitted,
    received, loss counts)
    """
    _transmitted_count_re = r'(?P<count>\d+)(?: packets transmitted)'
    _received_count_re = r'(?P<count>\d+)(?:( packets)? received)'

    def __init__(self):
        self.stdout = ''

    @property
    def transmitted(self):
        result = re.search(self._transmitted_count_re, self.stdout)
        if result is None:
            raise ValueError('There is no transmitted count in `{}`'.format(
                self.stdout))
        return int(result.group('count'))

    @property
    def received(self):
        result = re.search(self._received_count_re, self.stdout)
        if result is None:
            raise ValueError('There is no received count in `{}`'.format(
                self.stdout))
        return int(result.group('count'))

    @property
    def loss(self):
        return self.transmitted - self.received


class Pinger(object):
    """Pinger class to call ping and return result.

    Can be used directly (as Pinger.ping) and as non-blocking context manager.

    Example:
        >>> with Pinger('10.109.8.2') as result:
        ...     some_action()
        >>> print(result.loss)
        0

        >>> result = Pinger('10.0.0.1', remote=remote).ping(count=3)
        >>> print(result.loss)
        0

    """

    def __init__(self, ip_to_ping, remote=None):
        """Pinger constructor.

        Args:
            ip_to_ping (str): ip address to ping
            remote (object): instance of stepler.third_party.ssh.SshClient
        """
        self.remote = remote
        self.ip_to_ping = ip_to_ping
        if remote is not None:
            self.executor = self._remote_ping
        else:
            self.executor = self._local_ping

    def _prepare_cmd(self, count=None):
        cmd = ['ping']
        if count:
            cmd.append('-c{}'.format(count))
        cmd.append(self.ip_to_ping)
        return cmd

    # TODO(schipiga): seems, refactoring is required
    @contextlib.contextmanager
    def _remote_ping(self, count):
        cmd = ' '.join(self._prepare_cmd(count))
        output_file = tempfile.mktemp()
        pid = self.remote.background_call(cmd, stdout=output_file)
        result = PingResult()
        yield result
        if count:
            waiting.wait(
                lambda: not self.remote.execute('ps -o pid | grep {}'.format(
                    pid)).is_ok,
                timeout_seconds=count * 10)
        self.remote.execute('kill -SIGINT {}'.format(pid))
        result.stdout = self.remote.check_call("cat {}".format(
            output_file)).stdout
        self.remote.execute('rm {}'.format(output_file))

    # TODO(schipiga): seems, refactoring is required
    @contextlib.contextmanager
    def _local_ping(self, count):
        cmd = self._prepare_cmd(count)
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        # check that process is alive
        if p.poll() is not None:
            stdout, stderr = p.communicate()
            raise Exception(
                'Command {!r} unexpectedly exit with message {}'.format(
                    cmd, stdout, stderr))
        result = PingResult()
        yield result
        if count:
            p.wait()
        # Check if process still alive
        elif p.poll() is None:
            p.send_signal(signal.SIGINT)
        stdout, stderr = p.communicate()
        result.stdout = stdout

    def ping(self, count=1):
        """Start ping command and return result.

        Args:
            count (int): count of pings to send
        Returns:
            object: instance of PingResult
        """
        with self.executor(count=count) as result:
            return result

    def __enter__(self):
        self.cm = self.executor(count=None)
        return self.cm.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        self.cm.__exit__(exc_type, exc_value, traceback)
