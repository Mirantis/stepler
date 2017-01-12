"""
------------------------------------------------------
Pytest plugin to output fixtures order on failed tests
------------------------------------------------------

Output example::

    test_something
    +-> fix_c (autouse)
    |   +-> fix_a
    +-> fix_b
    |   +-> fix_a
    +-> fix_a

Fixtures are displayed as many times as involved. It's useful, because
it's easy to read and understand full topology.

Fixtures output can be disabled with option ``--disable-output-fixtures``.
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

import pytest

__all__ = [
    'pytest_addoption',
    'pytest_runtest_makereport',
]


def pytest_addoption(parser):
    """Add option ``--disable-output-fixtures`` to pytest."""
    parser.addoption(
        "--disable-output-fixtures", action="store_true",
        help="Suppress involved fixtures output if test is failed.")


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item):
    """Output involved fixtures order."""
    report = (yield).get_result()
    if (item.session.config.option.disable_output_fixtures or
            not report.failed or not report.longrepr):
        return

    # define fixtures with all scope types
    finalizers = [fin for fins in item.session._setupstate._finalizers.values()
                  for fin in fins]
    # Some internal pytest finalizers can be lambda functions, must avoid them.
    all_fixtures = {fin.im_self for fin in finalizers
                    if hasattr(fin, 'im_self')}

    fixtures = []
    # `item.fixturenames` order corresponds to fixtures involving order. So
    # after filtering fixtures will sorted according it's involving.
    for fix_name in item.fixturenames:
        for fix in all_fixtures:
            if fix_name == fix.argname:
                fixtures.append(fix)  # separate fixtures for current test only

    fixturenames = set(item.fixturenames)
    argnames = set(item.function.func_code.co_varnames)

    # get fixture names, which are specified via `@pytest.mark.usefixtures`
    if hasattr(item.function, 'usefixtures'):
        usefixtures = set(item.function.usefixtures.args)
    else:
        usefixtures = set()

    item_fixturenames = argnames & fixturenames | usefixtures
    # create a root of fixtures involving tree
    root = FixtureNode(item.name, item_fixturenames)

    for fixture in fixtures:
        fixturenames = list(fixture.argnames)

        if 'request' in fixturenames:
            fixturenames.remove('request')
        # Using of `@pytest.fixture` creates additional attribute of function,
        # which contains fixture attribute values.
        is_autouse = fixture.func.func_dict['_pytestfixturefunction'].autouse

        node = FixtureNode(fixture.argname, fixturenames, autouse=is_autouse)
        root.add_node(node)

    report.longrepr.addsection('Involved fixtures order', root.to_string())


class FixtureNode(object):
    """Node class to organize and output fixtures tree."""

    def __init__(self, name, child_names, autouse=False):
        self.name = name
        self.child_names = list(child_names)
        self.children = []
        self.parents = []
        self.autouse = autouse
        self.usefixtures = False

    def _add_node(self, node, first=False):
        # `set` is not used to provide order of added nodes
        if node not in self.children:
            if first:
                self.children.insert(0, node)
            else:  # add node as last
                self.children.append(node)
            node.parents.append(self)

    def add_node(self, node):
        """Add node to tree.

        Node will be added to all nodes which involve it. It's useful, because
        it's easy to read full topology when fixture is involved.
        """
        for child in self.children:
            child.add_node(node)

        # Not need to check order of node name inside child names, because
        # nodes come according its involving order. Sequence
        # `item.fixturenames` guarantees that.
        if node.name in self.child_names:
            self._add_node(node)

        # Only root node can have no parents. All added nodes have parent(s).
        elif not self.parents:  # self is root
            if node.autouse:
                # Attach autouse fixture to root (to test name) even it's
                # absent among test arguments. Set it in front, because it
                # is executed before explicit fixtures.
                self._add_node(node, first=True)

            elif not node.parents:  # fixture was involved via `usefixtures()`
                node.usefixtures = True
                self._add_node(node)

            # Catch situation when node can't be added to tree. It may be if
            # `item.fixturenames` order doesn't correspond fixtures involving.
            else:
                raise ValueError(
                    "Can't add fixture {!r} to tree. No fixtures, which "
                    "involve this fixture, among added:\n{}".format(
                        node.name, self.to_string()))

    def to_string(self):
        """Represent fixtures tree.

        It represent fixtures with offset of each level in relation to
        previous.

        Example::

            test
            +-> c (autouse)
            |   +-> a
            +-> b
            |   +-> a
            +-> a
        """
        offset = 4
        sep = '\n'
        lines = [self.name + ' (autouse)' * self.autouse +
                 ' (usefixtures)' * self.usefixtures]
        for child in self.children:
            child_lines = []
            for idx, line in enumerate(child.to_string().split(sep)):
                if idx == 0:
                    child_lines.append('+->'.ljust(offset) + line)
                else:
                    child_lines.append('|'.ljust(offset) + line)
            lines.append(sep.join(child_lines))
        return sep.join(lines)
