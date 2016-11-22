"""
----------------------
Iperf checking helpers
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

import csv
import contextlib
import tempfile


def _transform_values(values_dict, fields, transform):
    for key in fields:
        if values_dict[key] is not None:
            values_dict[key] = transform(values_dict[key])


def _parse(output):
    lines = output.splitlines()
    fields = (
        'timestamp',
        'source_address',
        'source_port',
        'destination_address',
        'destination_port',
        'transfer_id',
        'interval',
        'transferred_bytes',
        'bits_per_second',
        'jitter',
        'err_count',
        'datagramm_count',
        'error_percent',
        'out_of_order_count', )
    int_fields = (
        'source_port',
        'destination_port',
        'transferred_bytes',
        'bits_per_second',
        'err_count',
        'datagramm_count',
        'out_of_order_count', )
    float_fields = (
        'jitter',
        'error_percent', )
    reader = csv.DictReader(lines, fieldnames=fields, delimiter=',')
    results = {'intervals': []}
    for line in reader:
        _transform_values(line, int_fields, int)
        _transform_values(line, float_fields, float)
        results['intervals'].append(line)
    results['summary'] = results['intervals'].pop()
    return results


@contextlib.contextmanager
def iperf(remote, ip, time=80, interval=20, port=5002, udp=False):
    """Non-blocking context manager for run iperf client on backgroud.

    Args:
        remote (obj): instance of stepler.third_party.ssh.SshClient
        ip (str): iperf server ip
        time (int, optional): time in second to transmit traffic for
        interval (int, optional): interval to periodic report
        port (int, optional): iperf server port
        udp (bool, optional): flag whether use TCP or UDP protocol

    Returns:
        dict: iperf parsed result. Contains ``intervals`` list and ``summary``
            dict with iperf results.
    """
    interval = min(interval, time)
    if udp:
        cmd = ('iperf -u -c {ip} -p {port} -y C -t {time} '
               '-i {interval} --bandwidth 10M')
    else:
        cmd = 'iperf -c {ip} -p {port} -y C -t {time} -i {interval}'
    cmd = cmd.format(ip=ip, port=port, time=time, interval=interval)
    stdout_path = tempfile.mktemp()
    stderr_path = tempfile.mktemp()
    pid = remote.background_call(cmd, stdout=stdout_path, stderr=stderr_path)
    result = {}

    yield result

    # Wait iperf to done
    remote.execute('while kill -0 {pid} 2> /dev/null; '
                   'do sleep 1; done;'.format(pid))

    # Check stderr is empty
    stderr = remote.check_call('cat {path})'.format(stderr_path))
    if stderr:
        raise Exception('iperf stderr is not empty:\n{}', format(stderr))

    stdout = remote.check_call('cat {path})'.format(stdout_path))
    result.update(_parse(stdout))
