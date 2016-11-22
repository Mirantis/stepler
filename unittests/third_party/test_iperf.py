"""
----------------------
Iperf helper unittests
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
# limitations under the License.

from hamcrest import assert_that, has_entries, has_length  # noqa H301

from stepler.third_party import iperf

TCP_OUTPUT = """20161122142711,127.0.0.1,36278,127.0.0.1,5001,3,0.0-1.0,1991376896,15931015168
20161122142712,127.0.0.1,36278,127.0.0.1,5001,3,1.0-2.0,1909719040,15277752320
20161122142713,127.0.0.1,36278,127.0.0.1,5001,3,2.0-3.0,1980891136,15847129088
20161122142714,127.0.0.1,36278,127.0.0.1,5001,3,3.0-4.0,1928331264,15426650112
20161122142715,127.0.0.1,36278,127.0.0.1,5001,3,0.0-5.0,9703784448,15525713551"""  # noqa

UDP_OUTPUT = """20161122143037,127.0.0.1,51649,127.0.0.1,5001,3,0.0-1.0,1250970,10007760
20161122143038,127.0.0.1,51649,127.0.0.1,5001,3,1.0-2.0,1249500,9996000
20161122143039,127.0.0.1,51649,127.0.0.1,5001,3,2.0-3.0,1249500,9996000
20161122143040,127.0.0.1,51649,127.0.0.1,5001,3,3.0-4.0,1250970,10007760
20161122143041,127.0.0.1,51649,127.0.0.1,5001,3,4.0-5.0,1249500,9996000
20161122143041,127.0.0.1,51649,127.0.0.1,5001,3,0.0-5.0,6251910,9999814
20161122143041,127.0.0.1,5001,127.0.0.1,51649,3,0.0-5.0,6251910,10000061,0.068,0,4252,0.000,1"""  # noqa


def test_tcp_output_parsing():
    result = iperf._parse(TCP_OUTPUT)
    assert_that(
        result,
        has_entries(
            intervals=has_length(4),
            summary=has_entries(
                bits_per_second=15525713551, jitter=None)))


def test_udp_output_parsing():
    result = iperf._parse(UDP_OUTPUT)
    assert_that(
        result,
        has_entries(
            intervals=has_length(6),
            summary=has_entries(
                bits_per_second=10000061, jitter=0.068, error_percent=0.0)))
