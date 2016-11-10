"""
--------------------
Skip autouse fixture
--------------------
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

import pytest

__all__ = [
    'skip_test',
]


@pytest.fixture(autouse=True)
def skip_test(request):
    """Autouse function fixture to skip test by predicate.

    Usage:
        .. code:: python

           @pytest.mark.requires("ceph_enabled")
           @pytest.mark.requires("more_computes_than(4)")
           @pytest.mark.requires("more_computes_than(2) and ceph_enabled")

        Supported logical operations ``and``, ``or``, ``not`` and their
        combinations.

    Args:
        request (object): pytest request
    """
    requires = request.node.get_marker('requires')
    if not requires:
        return

    # TODO(schipiga): configure with real env config, when will be possible
    Predicates.configure(None)

    expr = ast.parse(requires, '<ast>', 'eval')
    expr.body = substitute(expr.body)
    need_skip = eval(compile(expr, '<ast>', 'eval'))

    if need_skip:
        pytest.skip(
            'Skipped due to a mismatch to condition: {!r}'.format(requires))


class Predicates(object):
    """Namespace for predicates to skip a test."""

    _env = None

    @classmethod
    def configure(cls, env):
        """Configure."""
        cls._env = env

    @classmethod
    def more_computes_than(cls, count):
        """Define whether computes enough."""

    @classmethod
    def ceph_enabled(cls):
        """Define whether CEPH enabled."""


def substitute(node):
    """Substitude predicates with their results."""
    def execute(name, args=()):
        boolean = getattr(Predicates, name)(*args)
        return ast.Name(
            id=str(boolean), ctx=ast.Load(), lineno=0, col_offset=0)

    if isinstance(node, ast.BoolOp):
        values = node.values
    else:
        values = [node]
    new_values = []

    for value in values:
        if isinstance(value, ast.BoolOp):
            new_values.append(substitute(value))
            continue

        if isinstance(value, ast.Name):
            new_values.append(execute(value.id))
            continue

        if isinstance(value, ast.Call):
            args = []
            for arg in value.args:
                arg_value = eval(
                    compile(ast.Expression(body=arg), '<ast>', 'eval'))
                args.append(arg_value)

            new_values.append(execute(value.func.id, args))
            continue

        raise SyntaxError('Unexpected node type {!r}'.format(value.__class__))

    if isinstance(node, ast.BoolOp):
        node.values[:] = new_values
    else:
        node = new_values[0]
    return node
