"""
----------------------------------
Pytest plugin to check consistency
----------------------------------

- steps and fixtures only are called inside a test

- steps must have format described in
  :ref:`STEPS architecture <steps-architecture>`

Checker can be disabled via ``py.test`` key ``--disable-steps-checker``.

Checker can be disabled with comments:

.. code:: python

    def test_inline():
        foo = 'bar'
        baz = non_permitted_call(
            foo
        )  # checker: disable


    def test_block():
        # checker: disable
        baz = non_permitted_call_1()
        baz = non_permitted_call_2()
        # checker: enable
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
import collections
import functools
import importlib
import inspect
import pkgutil
import re
import tokenize

import pytest
import six

import stepler
from stepler.third_party import logger
from stepler.third_party import utils

try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache

__all__ = [
    'pytest_addoption',
    'pytest_collection_modifyitems',
    'pytest_configure',
    'step',
]

# predefined permitted calls
PERMITTED_CALLS = [
    'append',
    'embed',
    'format',
    'getattr',
    'iter',
    'keys',
    'len',
    'list',
    'min',
    'next',
    'put',  # TODO(schipiga): update attrdict method
    'range',
    'set_trace',
    'sleep',
    'sorted',
    'str',
    'time',
    'dict',
    'set',
    'getfixturevalue',
]

# Py.test decorators
PERMITTED_CALLS += [
    'idempotent_id',
    'requires',
    'parametrize',
    'usefixtures',
]

# register utils
PERMITTED_CALLS += utils.__all__

# registered steps
STEPS = []

# methods which raise exception
RAISE_WORDS = ('assert_that',
               'check_',
               'raise',
               'wait')

# step types
GET = 'get'
CHECK = 'check'
CHANGE = 'change'

DEFAULT_VALUE = object()
DOC_LINK = (' Visit http://stepler.readthedocs.io/steps_concept.html to get'
            ' details.')

DISABLE_COMMENT = 'checker: disable'
ENABLE_COMMENT = 'checker: enable'


def step(func):
    """Decorator to append step method name to permitted calls.

    Args:
        func (function): function to add its name to list with permitted calls

    Returns:
        function: the same function wrapped to log
    """
    STEPS.append(func.__name__)
    return logger.log(func)


def pytest_addoption(parser):
    """Hook to register checker options."""
    parser.addoption(
        "--disable-steps-checker",
        action="store_true",
        help="disable steps checker (warning will be shown)")
    parser.addoption(
        "--steps-check-only",
        action="store_true",
        help="disable steps checker (warning will be shown)")


def pytest_collection_modifyitems(config, items):
    """Hook to detect forbidden calls inside test."""
    if config.option.disable_steps_checker:
        config.warn('P1', 'Permitted calls checker is disabled!')
        return

    errors = []
    for item in items:
        permitted_calls = PERMITTED_CALLS + STEPS + item.funcargnames
        validator = TestValidator(item.function, permitted_calls)
        errors.extend(validator.validate())

    if errors:
        pytest.exit("Only steps and fixtures must be called in test!\n" +
                    '\n'.join(errors))


def pytest_runtestloop(session):
    """Check idempotent id presence."""
    if session.config.option.steps_check_only:
        return True


def pytest_configure(config):
    """Hook to check steps consistency."""
    if config.option.disable_steps_checker:
        config.warn('P1', 'Step consistency checker is disabled!')
        return

    errors = []
    for step_cls in _get_step_classes():
        for attr_name in dir(step_cls):

            if attr_name not in STEPS:
                continue

            step_func = six.get_unbound_function(getattr(step_cls, attr_name))
            step_func = utils.get_unwrapped_func(step_func)

            validator = StepValidator(step_func)

            errors.extend(validator.validate())
    if errors:
        pytest.exit('Some steps are not consistent!\n' + '\n'.join(errors))


class NodeCollectorVisitor(ast.NodeVisitor):
    """Filter nodes by type and returns list of collected nodes."""
    def __init__(self, node_type, bucket=None, *args, **kwargs):
        super(NodeCollectorVisitor, self).__init__(*args, **kwargs)
        self.node_type = node_type
        self.bucket = bucket or []

    def visit(self, node):
        super(NodeCollectorVisitor, self).visit(node)
        if isinstance(node, self.node_type):
            self.bucket.append(node)
        return self.bucket


class NodesEndLineVisitor(ast.NodeVisitor):
    """Add end_lineno to each node (if it has lineno)."""

    def __init__(self, get_end_line, *args, **kwargs):
        super(NodesEndLineVisitor, self).__init__(*args, **kwargs)
        self.get_end_line = get_end_line

    def visit(self, node):
        lineno = getattr(node, 'lineno', None)
        if lineno:
            end_lineno = self.get_end_line(lineno)
            node.end_lineno = end_lineno
        return super(NodesEndLineVisitor, self).visit(node)


class FuncValidator(object):
    """Base function validator class."""
    def __init__(self, func):
        self.func = func

    @lru_cache()
    def _get_source_lines(self):
        """Get function source lines without common indentations.

        Function can be under another function or class and due to that it has
        additional indentation. Its indentation must be deleted before
        ast.parse().
        """
        lines = inspect.getsourcelines(self.func)[0]
        offset = len(lines[0]) - len(lines[0].lstrip())
        pattern = re.compile('^[ ]{{{}}}'.format(offset))
        return [pattern.sub('', line) for line in lines]

    @lru_cache()
    def _get_ast_root(self):
        """Get function AST root node."""
        root = ast.parse(''.join(self._get_source_lines()))
        NodesEndLineVisitor(self._get_end).visit(root)
        return root

    @lru_cache()
    def _get_ast_nodes(self, node, node_type, bucket=None):
        """Get ast nodes with specified ast type.

        Recursive traversal of ast nodes tree to retrieve nodes by defined
        type.
        """
        collector = NodeCollectorVisitor(node_type, bucket)
        nodes = collector.visit(node)
        for node in reversed(nodes):
            for pair in self._get_excluded_lines():
                if node.lineno >= pair[0] and node.end_lineno <= pair[1]:
                    nodes.remove(node)
                    break
        return nodes

    @lru_cache()
    def _get_call_names(self):
        """Get called function names inside function."""
        call_names = set()
        call_nodes = self._get_ast_nodes(self._get_ast_root(), ast.Call)

        for call_node in call_nodes:
            if hasattr(call_node.func, 'attr'):
                call_name = call_node.func.attr

            else:
                call_name = call_node.func.id
            call_names.add(call_name)

        return call_names

    @lru_cache()
    def _get_tokens(self):
        """Get list of tokens from function."""
        lines = iter(self._get_source_lines())
        tokens = tokenize.generate_tokens(functools.partial(six.next, lines))
        return list(tokens)

    @lru_cache()
    def _get_token_table(self):
        """Get table with start lines for each token."""
        token_table = collections.defaultdict(list)
        for i, tok in enumerate(self._get_tokens()):
            token_table[tok[2][0]].append(i)
        return token_table

    def _get_start(self, end):
        """Get expression start line number by end line number."""
        i = self._get_token_table()[end][0]
        tokens = self._get_tokens()
        while tokens[i][0] != tokenize.NEWLINE:
            i -= 1
        return tokens[i + 1][2][0]

    def _get_end(self, start):
        """Get expression end line number by start line number."""
        i = self._get_token_table()[start][-1]
        tokens = self._get_tokens()
        while tokens[i][0] != tokenize.NEWLINE:
            i += 1
        return tokens[i][2][0]

    @lru_cache()
    def _get_excluded_lines(self):
        """Get lines excluded from check with special comments."""
        lines_to_exclude = []
        starts = []
        for toknum, tokval, (start, _), _, line in self._get_tokens():
            if toknum != tokenize.COMMENT:
                continue
            line = line.strip()
            tokval = tokval.strip()
            if tokval == line:
                # Block mode
                tokval = tokval.strip('# ')
                if tokval == DISABLE_COMMENT:
                    starts.append(start)
                elif tokval == ENABLE_COMMENT and starts:
                    lines_to_exclude.append([starts[-1], start])
                    starts = []
            elif line.endswith(tokval):
                # Inline mode
                end = start
                start = self._get_start(end)
                lines_to_exclude.append([start, end])
        return lines_to_exclude

    @lru_cache()
    def _get_func_location(self):
        """Get function location for error message."""
        return " in function {!r}, module {!r}.".format(
            self.func.__name__, self.func.__module__)

    def _verify_docstring_present(self):
        """Rule to verify that function has docstring section."""
        for line in self._get_source_lines():
            if line.strip().startswith('"""'):
                break
        else:
            return 'Step has no docstring' + self._get_func_location()


class StepValidator(FuncValidator):
    """Class to validate step method."""

    def __init__(self, *args, **kwargs):
        super(StepValidator, self).__init__(*args, **kwargs)
        self.func_location = self._get_func_location()
        self.ast_func_def = self._get_ast_root().body[0]

    def _verify_argument_present(self,
                                 arg_name,
                                 arg_val=DEFAULT_VALUE,
                                 step_type=None):
        """Rule to verify that function has defined argument."""
        assert step_type

        argspec = inspect.getargspec(self.func)

        if arg_name not in argspec.args:
            return ("{type}-step must have argument {name!r} "
                    "{loc} {doc}").format(
                        type=step_type,
                        arg=arg_name,
                        loc=self.func_location,
                        doc=DOC_LINK)

        if arg_val == DEFAULT_VALUE:
            return

        if not argspec.defaults:
            return ("{type}-step must have argument {name!r} "
                    "with default value '{val}' {loc} {doc}").format(
                        type=step_type,
                        name=arg_name,
                        val=arg_val,
                        loc=self.func_location,
                        doc=DOC_LINK)

        kwgs = dict(
            zip(argspec.args[-len(argspec.defaults):], argspec.defaults))

        if not kwgs[arg_name] == arg_val:
            return ("{type}-step must have argument {name!r} "
                    "with default value '{val}' {loc} {doc}").format(
                        type=step_type,
                        name=arg_name,
                        val=arg_val,
                        loc=self.func_location,
                        doc=DOC_LINK)

    def _verify_step_has_code(func):
        """Rule to verify that step has code or docstring.

        It used as decorator for other rules.
        """

        @functools.wraps(func)
        def wrapper(self, step_type):
            func_location = self._get_func_location()
            if len(self.ast_func_def.body) <= 1:
                return (step_type + '-step has no code or docstring' +
                        func_location)
            return func(self, step_type)

        return wrapper

    @_verify_step_has_code
    def _verify_step_return_something(self, step_type):
        """Rule to verify that step returns something."""
        ast_returns = self._get_ast_nodes(self.ast_func_def.body[-1],
                                          ast.Return)
        if not ast_returns:
            return (step_type + '-step must return something' +
                    self.func_location + DOC_LINK)

        for ast_return in ast_returns:
            if (not ast_return.value or
                    getattr(ast_return.value, 'id', None) == 'None'):

                return (step_type + '-step must return something' +
                        self.func_location + DOC_LINK)

    @_verify_step_has_code
    def _verify_step_return_nothing(self, step_type):
        """Rule to verify that step returns nothing."""
        ast_returns = self._get_ast_nodes(self.ast_func_def.body[-1],
                                          ast.Return)
        if ast_returns:
            return (step_type + '-step must return nothing' +
                    self.func_location + DOC_LINK)

    def _verify_step_raise_exception(self, step_type):
        """Rule to verify that step raises exception."""
        call_names = self._get_call_names()

        for word in RAISE_WORDS:
            for call_name in call_names:
                if call_name.startswith(word):
                    return
        else:
            return (step_type + '-step must raise error if check is failed' +
                    self.func_location + DOC_LINK)

    @_verify_step_has_code
    def _verify_step_has_action_before_check(self, step_type):
        """Rule to verify that step action over resource before checking."""
        if _is_ast_check(self.ast_func_def.body[1]):
            return (step_type + '-step has no action before check' +
                    self.func_location + DOC_LINK)

    def _verify_step_has_if_check(self, step_type):
        """Rule to verify that step has `if check:` section."""
        ast_ifs = self._get_ast_nodes(self.ast_func_def, ast.If)
        if not ast_ifs:
            return (step_type + '-step has no block "if check:"' +
                    self.func_location + DOC_LINK)

        for ast_if in ast_ifs:
            if _is_ast_check(ast_if):
                return
        else:
            return (step_type + '-step has no block "if check:"' +
                    self.func_location + DOC_LINK)

    def _validate_get_step(self):
        errors = []

        if 'check' in inspect.getargspec(self.func).args:
            error = self._verify_argument_present('check', True, step_type=GET)
            if error:
                errors.append(error)

        error = self._verify_step_return_something(step_type=GET)
        if error:
            errors.append(error)
        return errors

    def _validate_check_step(self):
        errors = []

        error = self._verify_step_raise_exception(step_type=CHECK)
        if error:
            errors.append(error)
        return errors

    def _validate_change_step(self):
        errors = []

        error = self._verify_argument_present('check', True, step_type=CHANGE)
        if error:
            errors.append(error)

        error = self._verify_step_has_action_before_check(step_type=CHANGE)
        if error:
            errors.append(error)
        return errors

    def validate(self):
        """Validate step with default rules."""
        errors = []
        error = self._verify_docstring_present()
        if error:
            errors.append(error)

        if self.func.__name__.startswith('get_'):
            errors.extend(self._validate_get_step())

        elif self.func.__name__.startswith('check_'):
            errors.extend(self._validate_check_step())

        else:  # change step
            errors.extend(self._validate_change_step())

        return errors


class TestValidator(FuncValidator):
    """Test function/method validator class."""

    def __init__(self, func, permitted_calls=None, *args, **kwargs):
        super(TestValidator, self).__init__(func, *args, **kwargs)
        self._permitted_calls = permitted_calls or []

    def _validate_calls(self):
        """Validate that only permitted calls are in the test."""
        errors = []
        for call_name in self._get_call_names():
            if call_name not in self._permitted_calls:

                error = ("Calling {!r} isn't allowed".format(call_name) +
                         self._get_func_location() + DOC_LINK)
                errors.append(error)
        return errors

    def validate(self):
        """Validate test with default rules."""
        return self._validate_calls()


def _get_step_classes():
    """Get classes which contain step-methods."""
    step_classes = []
    for _, pkg_name, is_pkg in pkgutil.iter_modules(stepler.__path__):

        if not is_pkg:
            continue

        steps_module_name = stepler.__name__ + '.' + pkg_name + '.steps'
        try:
            steps_module = importlib.import_module(steps_module_name)
        except ImportError:
            continue

        for obj_name in steps_module.__all__:
            obj = getattr(steps_module, obj_name)

            if inspect.isclass(obj):
                step_classes.append(obj)

    return step_classes


def _is_ast_check(node):
    """Define whether ast_node has `if check:` section or no."""
    if isinstance(node, ast.If):
        if getattr(node.test, 'id', None) == 'check':
            return True
    return False
