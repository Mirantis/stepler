"""
----------
SSH client
----------
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

import contextlib
import logging
import select
import time

import paramiko
import six
from six import moves


__all__ = [
    'SshClient'
]

LOGGER = logging.getLogger(__name__)


class ExecutionTimeout(Exception):
    """Command execution timeout exception."""


class CommandResult(object):
    """Remote command result."""

    def __init__(self, *args, **kwargs):
        super(CommandResult, self).__init__(*args, **kwargs)
        self.command = None
        self.exit_code = None
        self.stdout_bytes = ''
        self.stderr_bytes = ''

    def __repr__(self):
        return (u'`{0.command}` result:\n'
                u'exit code: {0.exit_code}\n'
                u'stdout: {0.stdout}\n'
                u'stderr: {0.stderr}').format(self)

    @property
    def is_ok(self):
        return self.exit_code == 0

    @property
    def stdout(self):
        return self.stdout_bytes.decode('utf-8').strip()

    def append_stdout(self, value):
        self.stdout_bytes += value

    @property
    def stderr(self):
        return self.stderr_bytes.decode('utf-8').strip()

    def append_stderr(self, value):
        self.stderr_bytes += value

    def check_exit_code(self, expected=0):
        """Check that exit_code is 0."""
        if self.exit_code != expected:
            raise Exception('Command {0.command!r} exit code is not 0'.format(
                self))

    def check_stderr(self):
        """Check that stderr is empty."""
        if self.stderr:
            raise Exception('Command {0.command!r} stderr '
                            'is not empty:\n{0.stderr}'.format(self))


class SshClient(object):
    """SSH client."""

    def __init__(self,
                 host,
                 port=22,
                 username=None,
                 password=None,
                 pkey=None,
                 timeout=None,
                 proxy_cmd=None):
        """Constructor.

        Args:
            host (str): ip to connect
            port (int, optional): ssh port
            username (str): username
            password (str, optional): password
            pkey (str, optional): private key content
            timeout (int, optional): connection timeout
            proxy_cmd (str, optional): ssh proxy command
        """
        self._host = host
        self._port = port
        if pkey:
            self._pkey = paramiko.RSAKey.from_private_key(six.StringIO(pkey))
        else:
            self._pkey = None
        self._timeout = timeout
        self._username = username
        self._password = password
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._proxy_cmd = proxy_cmd
        self._sudo = False

    def connect(self):
        """Connect to ssh server."""
        sock = paramiko.ProxyCommand(self._proxy_cmd) \
            if self._proxy_cmd else None

        self._ssh.connect(
            self._host,
            self._port,
            pkey=self._pkey,
            timeout=self._timeout,
            banner_timeout=self._timeout,
            username=self._username,
            password=self._password,
            sock=sock)

    def close(self):
        """Close ssh connection."""
        self._ssh.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @contextlib.contextmanager
    def sudo(self):
        """Context manager to run commmand with sudo."""
        self._sudo = True
        yield self
        self._sudo = False

    def check_call(self, command, verbose=False):
        """Call command and check that exit_code is 0.

        Args:
            command (str): command to execute
            verbose (bool): make log records or not

        Returns:
            object: CommandResult instance

        Raises:
            Exception: if command exit_code is not 0
        """
        result = self.execute(command, verbose)
        result.check_exit_code()
        return result

    def check_stderr(self, command, verbose=False):
        """Call command and check that stderr is empty.

        Args:
            command (str): command to execute
            verbose (bool): make log records or not

        Returns:
            object: CommandResult instance

        Raises:
            Exception: if command stderr is not empty
        """
        result = self.check_call(command, verbose)
        result.check_stderr()
        return result

    def check_process_present(self, name):
        """Check that `name` is present in `ps aux` output.

        Args:
            name (str): command name to search

        Raises:
            Exception: if `name` is not found.
        """
        self.check_call('ps aux | grep {}'.format(name))

    def kill_process(self, name):
        """Kill all processes by `killall <name>`

        Args:
            name (str): command name to search

        Returns:
            object: CommandResult for execute command
        """
        self.execute('killall {}'.format(name))

    def background_call(self, command, stdout='/dev/null', stderr='&1'):
        """Start long-running command in backgroung and return it's pid.

        Args:
            command (str): command to execute
            stdout (str): path to file to redirect command stdout to
            stderr (str, optional): path to file to redirect command stderr to.
                By default stderr combines with stdout.

        Returns:
            str: pid of running command

        Raises:
            AssertionError: if command is not running in background
        """
        bg_command = command + ' <&- >{stdout} 2>{stderr} & echo $!'.format(
            stdout=stdout, stderr=stderr)
        result = self.check_call(bg_command, verbose=False)
        pid = result.stdout
        result = self.execute('ps -o pid | grep {pid}'.format(pid=pid),
                              verbose=False)
        assert result.is_ok, (
            "Can't find `{command}` (PID: {pid}) in "
            "processes".format(command=command, pid=pid))
        return pid

    def wait_process_done(self, pid, timeout=0):
        """Wait until command with `pid` will be done.

        Args:
            pid (int|str): pid
            timeout (int, optional): time to wait for process to be done

        Raises:
            ExecutionTimeout: if process executing after timeout.
        """
        self.execute('while kill -0 {pid} 2> /dev/null; '
                     'do sleep 1; done;'.format(pid=pid), timeout=timeout)

    def execute(self, command, merge_stderr=False, verbose=False,
                timeout=None):
        """Execute command and returns CommandResult instance.

        Args:
            command (str): command to execute
            merge_stderr (bool): merge stderr to stdout
            verbose (bool): make log records or not
            timeout (int, optional): maximum command executing time in seconds

        Returns:
            object: CommandResult instance

        Raises:
            ExecutionTimeout: if command executing more than timeout
        """
        chan, stdin, stdout, stderr = self.execute_async(
            command, merge_stderr=merge_stderr)

        result = CommandResult()
        result.command = command

        start = time.time()
        while not chan.closed or chan.recv_ready() or chan.recv_stderr_ready():
            select.select([chan], [], [chan], 60)

            if chan.recv_ready():
                result.append_stdout(chan.recv(1024))
            if chan.recv_stderr_ready():
                result.append_stderr(chan.recv_stderr(1024))

            if timeout and (time.time() > start + timeout):
                chan.close()
                raise ExecutionTimeout('Executing `{cmd}` is too long '
                                       '(more than {timeout} seconds)'.format(
                                           cmd=command, timeout=timeout))

        result.exit_code = chan.recv_exit_status()
        stdin.close()
        stdout.close()
        stderr.close()
        chan.close()
        if verbose:
            LOGGER.debug("'{0}' exit_code is {1}".format(command,
                                                         result.exit_code))
            if len(result.stdout) > 0:
                LOGGER.debug(u'Stdout:\n{0}'.format(result.stdout))
            if len(result.stderr) > 0:
                LOGGER.debug(u'Stderr:\n{0}'.format(result.stderr))
        return result

    def execute_async(self, command, merge_stderr=False, verbose=False):
        """Start executing command async.

        Args:
            command (str): command to execute
            merge_stderr (bool): merge stderr to stdout
            verbose (bool): make log records or not

        Returns:
            tuple: SSH session, file-like stdin, stdout, stderr
        """
        if verbose:
            LOGGER.debug("Executing command: '%s'" % command.rstrip())
        chan = self._ssh.get_transport().open_session(timeout=self._timeout)
        chan.set_combine_stderr(merge_stderr)
        stdin = chan.makefile('wb')
        stdout = chan.makefile('rb')
        stderr = chan.makefile_stderr('rb')
        if self._sudo:
            command = "sudo -s $SHELL -c " + moves.shlex_quote(command)
        chan.exec_command(command)
        return chan, stdin, stdout, stderr

    @contextlib.contextmanager
    def open(self, path, mode='r'):
        """Open remote file with SFTP.

        Args:
            path (str): path to remote file
            mode (str, optional): file open mode. The arguments are the same
                as for Python's built-in open. Read-only by default.

        Yields:
            obj: an SFTPFile object representing the open file
        """
        with self._ssh.open_sftp() as sftp:
            yield sftp.open(path, mode)
