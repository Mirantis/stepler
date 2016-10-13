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


from stepler.third_party import traffic_generator
import pytest


__all__ = [
    'generate_traffic',
]


@pytest.yield_fixture
def generate_traffic():
    """Fixture to generate traffic to server.

    Can be called several time during test. Simplest listener can be started
    with `nc -k -l <port>`.
    """

    traffic_generators = []

    def _generate_traffic(ip, port):
        tg = traffic_generator.TrafficGenerator(ip, port)
        tg.start()
        traffic_generators.append(tg)

    yield _generate_traffic

    for tg in traffic_generators:
        tg.stop()
