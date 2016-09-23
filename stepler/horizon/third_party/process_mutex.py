"""
Interprocess locker.

@author: schipiga@mirantis.com
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

import fcntl


class Lock(object):
    """Process mutex."""

    def __init__(self, filename):
        """Constructor."""
        self.filename = filename
        # This will create it if it does not exist already
        self.handle = open(self.filename, 'w')

    # Bitwise OR fcntl.LOCK_NB if you need a non-blocking lock
    def acquire(self):
        """Acquire lock."""
        fcntl.flock(self.handle, fcntl.LOCK_EX)

    def release(self):
        """Release lock."""
        fcntl.flock(self.handle, fcntl.LOCK_UN)

    def __enter__(self):
        """Enter to context."""
        self.acquire()
        return self

    def __exit__(self, ext_type, exc_val, exc_tb):
        """Exit from context."""
        self.release()

    def __del__(self):
        """Delete object."""
        self.handle.close()
