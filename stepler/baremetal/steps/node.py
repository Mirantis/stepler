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

from waiting import wait

from stepler.base import BaseSteps
from stepler.third_party.steps_checker import step

__all__ = [
    'NodeSteps'
]


class NodeSteps(BaseSteps):
    """Node steps."""

    @step
    def create_node(self, driver='fake', check=True):
        """Step to create node."""

        import ipdb; ipdb.set_trace()

        node = self._client.node.create(driver)

        if check:
            self.check_node_presence(node)

        return node

    @step
    def delete_node(self, node, check=True):
        """Step to delete node."""
        self._client.delete(node)

        if check:
            self.check_node_presence(node, present=False)

    @step
    def check_node_presence(self, node, present=True, timeout=0):
        """Verify step to check node is present."""
        def predicate():
            try:
                self._client.get(node)
                return present
            except Exception:
                return not present

        wait(predicate, timeout_seconds=timeout)

    @step
    def get_node(self, *args, **kwgs):
        """Step to get node."""
        return self._client.get(*args, **kwgs)
