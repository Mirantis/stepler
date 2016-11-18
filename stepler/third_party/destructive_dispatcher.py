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

import logging

import pytest

__all__ = [
    'pytest_runtest_teardown',
    'revert_environment',
]

LOG = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption("--snapshot-name", '-S', action="store",
                     help="Libvirt snapshot name")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item, nextitem):
    """Pytest hook to dispatch destructive scenarios."""

    destructor = item._request.getfixturevalue('os_faults_client')

    # Revert only destructive tests
    if not item.get_marker('destructive'):
        return

    snapshot_name = item.session.config.option.snapshot_name

    # Prevent reverting if no snapshot_name passed
    if snapshot_name is None:
        return

    # reject finalizers of all fixture scopes
    for finalizers in item.session._setupstate._finalizers.values():
        for finalizer in finalizers:

            # There are finalizers in the form of lambda function without name.
            # That looks as internal pytest specifics. We should skip them.
            fixture_def = getattr(finalizer, 'im_self', None)
            if fixture_def and not hasattr(fixture_def.func, 'indestructible'):
                LOG.debug('Clear {} finalizers'.format(fixture_def))
                fixture_def._finalizer[:] = []

                # Clear fixture cached result to force fixture with any scope
                # to restart in next test.
                if hasattr(fixture_def, "cached_result"):
                    LOG.debug('Clear {} cache'.format(fixture_def))
                    del fixture_def.cached_result

    outcome = yield

    # Prevent reverting after last test
    if nextitem is None or item.session.shouldstop:
        return

    # Prevent reverting after KeyboardInterrupt
    if outcome.excinfo is not None and outcome.excinfo[0] is KeyboardInterrupt:
        return

    revert_environment(destructor, snapshot_name)


def revert_environment(destructor, snapshot_name):
    """Revert environment to original state."""
    nodes = destructor.get_nodes()
    nodes.revert(snapshot_name)
    nodes.run_task({'command': 'hwclock --hctosys'})
