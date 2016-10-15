"""
-----------------------------------------------
Pytest plugin to dispatch destructive scenarios
-----------------------------------------------

In destructive scenarios we skip all fixture finalizations because we revert
environment to original state.
Destructive scenarios are marked via decorator ``@pytest.mark.destructive``.
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

__all__ = [
    'pytest_runtest_teardown',
    'revert_environment',
]


def pytest_runtest_teardown(item, nextitem):
    """Pytest hook to dispatch destructive scenarios."""
    if not item.get_marker('destructive'):
        return

    item_finalizers = item._pyfuncitem.session._setupstate._finalizers[item]

    for fixture_name in item.funcargnames:
        for finalizer in item_finalizers:

            # There are finalizers in the form of lambda function without name.
            # That looks as internal pytest specifics. We should skip them.
            fixture_def = getattr(finalizer, 'im_self', None)

            if fixture_def and fixture_def.argname == fixture_name:
                fixture_def._finalizer[:] = []  # clear fixture finalizer
                break

    revert_environment()


def revert_environment():
    """Revert environment to original state."""
    pass  # TODO(schipiga): should implement revert mechanism
