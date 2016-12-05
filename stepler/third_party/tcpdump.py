"""
---------------
tcpdump helpers
---------------
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
import tempfile
import time

from hamcrest import assert_that, is_in  # noqa H301
import scapy.all as scapy


TYPE_ICMP_REPLY = 0


def read_pcap(path, lfilter=None):
    """Read pcap file and yields packets.

    Args:
        path (str): path to pcap file
        lfilter (function, optional): function to filter returned packets. By
            default all packets will be returned.

    Yields:
        obj: packet
    """
    with scapy.PcapReader(path) as reader:
        for packet in filter(lfilter, reader):
            yield packet


def filter_icmp(packet):
    """Returns True if packet contains ICMP layer."""
    return scapy.ICMP in packet


def filter_vxlan(packet):
    """Returns True if packet contains VxLAN layer."""
    return scapy.VXLAN in packet


@contextlib.contextmanager
def tcpdump(remote, args='', prefix=None, latency=2, lfilter=None):
    """Non-blocking context manager for run tcpdump on backgroud.

    It yields path to pcap file.

    Args:
        remote (SshClient): instance of ssh client
        args (str, optional): additional ``tcpdump`` args
        prefix (str, optional): prefix for command. It can be useful for
            executing tcpdump on ip namespace.
        latency (int, optional): time to wait after tcpdump's starting and
            before tcpdump's termination to guarantee that all packets will be
            captured
        lfilter (function, optional): function to filter returned packets. By
            default all packets will be returned.

    Yields:
        str: path to pcap file
    """
    pcap_file = tempfile.mktemp()
    stdout_file = tempfile.mktemp()
    cmd = "tcpdump -w{pcap_file} {args}".format(args=args, pcap_file=pcap_file)
    if prefix:
        cmd = "{} {}".format(prefix, cmd)
    with remote.sudo():
        pid = remote.background_call(cmd, stdout=stdout_file)
        # wait tcpdump to start
        remote.execute('while [ ! -f {} ]; do sleep 1; done'.format(pcap_file))
        # tcpdump need some more time to start packets capturing
        time.sleep(latency)

    yield pcap_file

    # wait some time to allow tcpdump to process all packets
    time.sleep(latency)
    with remote.sudo():
        remote.execute('kill -SIGINT {}'.format(pid))
        remote.wait_process_done(pid, timeout=latency)
        with remote.open(pcap_file) as src:
            with open(pcap_file, 'wb') as dst:
                dst.write(src.read())
        remote.execute('rm {}'.format(pcap_file))


def get_last_ping_reply_ts(path):
    """Returns last ICMP echo response timestamp.

    If there are no replies in packets - it returns None.

    Args:
        packets (list): list packets

    Returns:
        float|None: last ICMP reply timestamp or None
    """
    last_replied_ts = None
    for packet in read_pcap(path, lfilter=filter_icmp):
        if not filter_icmp(packet):
            continue
        if packet[scapy.ICMP].type == TYPE_ICMP_REPLY:
            last_replied_ts = max(last_replied_ts, packet.time)
    return last_replied_ts
