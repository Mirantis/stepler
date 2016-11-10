"""
---------------------------
Skip substitution unittests
---------------------------
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

import ast
from collections import namedtuple

import pytest

from stepler.fixtures import skip


class Predicates(object):
    """Mock predicates."""

    @classmethod
    def ceph_enabled(cls):
        """Define whether ceph enabled."""
        return True

    @classmethod
    def is_ha(cls):
        """Define whether HA cluster."""
        return False

    @classmethod
    def more_nodes_than(cls, count):
        """Define nodes limit."""
        return 3 > count

    @classmethod
    def more_computes_than(cls, count):
        """Define computes limit."""
        return 2 > count


skip.Predicates = Predicates

Case = namedtuple('Case', ('requires', 'expected'))

cases = [
    Case(requires='ceph_enabled', expected=True),
    Case(requires='not ceph_enabled', expected=False),
    Case(requires='is_ha', expected=False),
    Case(requires='not is_ha', expected=True),
    Case(requires='ceph_enabled and is_ha', expected=False),
    Case(requires='ceph_enabled and not is_ha', expected=True),
    Case(requires='more_nodes_than(2)', expected=True),
    Case(requires='more_computes_than(5)', expected=False),
    Case(requires='more_nodes_than(2) and ceph_enabled', expected=True),
    Case(requires='more_nodes_than(1) and (ceph_enabled or is_ha)',
         expected=True),
    Case(requires='more_nodes_than(1) and (ceph_enabled and is_ha)',
         expected=False),
    Case(requires='more_nodes_than(1) and ceph_enabled and is_ha',
         expected=False),
    Case(requires='more_nodes_than(1) and (ceph_enabled and not is_ha)',
         expected=True),
    Case(requires='more_nodes_than(1) and not (ceph_enabled and is_ha)',
         expected=True),
    Case(requires='more_nodes_than(1) and not (ceph_enabled or is_ha)',
         expected=False),
    Case(requires='not more_nodes_than(1) and not (ceph_enabled and is_ha)',
         expected=False),
]


@pytest.mark.parametrize('case', cases)
def test_skip_substitute(case):
    """Test skip value is defined correctly."""
    expr = ast.parse(case.requires, '<ast>', 'eval')
    expr.body = skip.substitute(expr.body)
    assert eval(compile(expr, '<ast>', 'eval')) == case.expected
