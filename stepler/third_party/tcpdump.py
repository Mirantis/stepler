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

import dpkt
from hamcrest import assert_that, is_in  # noqa H301

_ip_protocols = {
    'icmp': dpkt.ip.IP_PROTO_ICMP,
    'tcp': dpkt.ip.IP_PROTO_TCP,
    'udp': dpkt.ip.IP_PROTO_UDP,
}


def parse_pcap(content, proto=None):
    """Parse pcap file and yields pairs of timestamp and ip packets.

    Args:
        content (obj): file-like object
        proto (str, optional): protocol name to filter packets. By default
            yields all packets.

    Yields:
        tuple: timestamp and ip packet
    """
    if proto:
        proto = _ip_protocols[proto]
    for ts, pkt in dpkt.pcap.Reader(content):
        eth = dpkt.ethernet.Ethernet(pkt)
        if eth.type != dpkt.ethernet.ETH_TYPE_IP:
            continue

        ip = eth.data

        if proto and ip.p != proto:
            continue

        yield ts, ip


@contextlib.contextmanager
def tcpdump(remote, args='', prefix=None, proto=None, latency=2):
    """Non-blocking context manager for run tcpdump on backgroud.

    It yields as result list of pairs - (timestamp, dpkt.ip.IP instance).

    Args:
        remote (SshClient): instance of ssh client
        args (str, optional): additional ``tcpdump`` args
        prefix (str, optional): prefix for command. It can be useful for
            executing tcpdump on ip namespace.
        proto (str, optional): protocol to filter packets. By default all
            packets will be returned

    Yields:
        list: list of timestamps and ip packets
    """
    if proto is not None:
        assert_that(proto, is_in(_ip_protocols))
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

    result = []

    yield result

    # wait some time to allow tcpdump to process all packets
    time.sleep(latency)
    with remote.sudo():
        remote.execute('kill -SIGINT {}'.format(pid))
        # Wait tcpdump to done
        remote.execute('while kill -0 {pid} 2> /dev/null; '
                       'do sleep 1; done;'.format(pid=pid))
        with remote.open(pcap_file) as f:
            result.extend(parse_pcap(f, proto))
        remote.execute('rm {}'.format(pcap_file))


def get_last_ping_reply_ts(packets):
    """Returns last ICMP echo response timestamp.

    If there are no replies in packets - it returns None.

    Args:
        packets (list): list of tuples (timestamp, packet)

    Returns:
        float|None: last ICMP reply timestamp or None
    """
    last_replied_ts = None
    for ts, ip in packets:
        if ip.p != dpkt.ip.IP_PROTO_ICMP:
            continue
        if ip.icmp.type == dpkt.icmp.ICMP_ECHOREPLY:
            last_replied_ts = max(last_replied_ts, ts)
    return last_replied_ts
