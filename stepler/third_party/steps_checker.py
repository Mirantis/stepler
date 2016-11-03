"""
----------------------------------
Pytest plugin to check consistency
----------------------------------

- steps and fixtures only are called inside a test

- steps must have format described in
  :ref:`STEPS architecture <steps-architecture>`

Checker can be disabled via ``py.test`` key ``--disable-steps-checker``.
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
import functools
import importlib
import inspect
import pkgutil

import hamcrest

import stepler
from stepler.third_party import logger
from stepler.third_party import utils

__all__ = [
    'pytest_addoption',
    'pytest_collection_modifyitems',
    'pytest_configure',
    'step'
]

# predefined permitted calls
PERMITTED_CALLS = [
    'list',
    'next',
    'iter',
    'put',  # TODO(schipiga): update attrdict method
    'range',
    'sorted',
    'set_trace',
    'time',
    'str',
    'embed',
    'format',
    'getattr',
    'len',
    'keys',
]

# register hamcrest matchers
PERMITTED_CALLS += [method_name for method_name in dir(hamcrest)
                    if not method_name.startswith('_')]

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
    parser.addoption("--disable-steps-checker", action="store_true",
                     help="disable steps checker (warning will be shown)")


def pytest_collection_modifyitems(config, items):
    """Hook to detect forbidden calls inside test."""
    if config.option.disable_steps_checker:
        config.warn('P1', 'Permitted calls checker is disabled!')
        return

    errors = []
    for item in items:
        permitted_calls = PERMITTED_CALLS + STEPS + item.funcargnames

        ast_root = ast.parse(_get_source(item.function))
        for call_name in _get_call_names(ast_root):
            if call_name not in permitted_calls:

                error = ("Calling {!r} isn't allowed".format(call_name) +
                         _get_func_location(item.function) + DOC_LINK)
                errors.append(error)

    if errors:
        raise SystemError("Only steps and fixtures must be called in test!\n" +
                          '\n'.join(errors))


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

            step_func = getattr(step_cls, attr_name).im_func
            step_func = utils.get_unwrapped_func(step_func)

            error = _verify_docstring_present(step_func)
            if error:
                errors.append(error)

            if step_func.__name__.startswith('get_'):
                errors.extend(
                    _validate_get_step(step_func))

            elif step_func.__name__.startswith('check_'):
                errors.extend(
                    _validate_check_step(step_func))

            else:  # change step
                errors.extend(
                    _validate_change_step(step_func))
    if errors:
        raise SystemError('Some steps are not consistent!\n' +
                          '\n'.join(errors))


def _validate_get_step(func):
    errors = []

    if 'check' in inspect.getargspec(func).args:
        error = _verify_argument_present(func, 'check', True, step_type=GET)
        if error:
            errors.append(error)

    ast_func_def = ast.parse(_get_source(func)).body[0]
    func_location = _get_func_location(func)

    error = _verify_step_return_something(
        ast_func_def, func_location, step_type=GET)
    if error:
        errors.append(error)
    return errors


def _validate_check_step(func):
    errors = []

    ast_func_def = ast.parse(_get_source(func)).body[0]
    func_location = _get_func_location(func)

    error = _verify_step_raise_exception(
        ast_func_def, func_location, step_type=CHECK)
    if error:
        errors.append(error)
    return errors


def _validate_change_step(func):
    errors = []

    error = _verify_argument_present(func, 'check', True, step_type=CHANGE)
    if error:
        errors.append(error)

    ast_func_def = ast.parse(_get_source(func)).body[0]
    func_location = _get_func_location(func)

    error = _verify_step_has_action_before_check(
        ast_func_def, func_location, step_type=CHANGE)
    if error:
        errors.append(error)
    return errors


def _get_source_lines(func):
    """Get function source lines without common indentations.

    Function can be under another function or class and due to that it has
    additional indentation. Its indentation must be deleted before ast.parse().
    """
    lines = inspect.getsourcelines(func)[0]
    lines = [l.rstrip() for l in lines if not l.strip().startswith('#')]

    def_line = [l for l in lines if l.strip().startswith('def ')][0]
    def_indent = len(def_line) - len(def_line.strip())

    return [l[def_indent:] for l in lines]


def _get_source(func):
    """Get function source lines joined to one."""
    return '\n'.join(_get_source_lines(func))


def _get_ast_attrs(node):
    """Get attributes of ast node.

    Some attributes are skipped because they are not related to function body
    and just create side effect.
    """
    skip_list = ()
    if isinstance(node, ast.FunctionDef):
        skip_list = ('args', 'decorator_list')

    attrs = []
    for name in dir(node):
        if not name.startswith('_') and name not in skip_list:
            attrs.append(getattr(node, name))
    return attrs


def _get_call_names(node):
    """Get called function names inside function."""
    call_names = set()
    call_nodes = _get_ast_nodes(node, ast.Call)

    for call_node in call_nodes:
        if hasattr(call_node.func, 'attr'):
            call_name = call_node.func.attr

        else:
            call_name = call_node.func.id
        call_names.add(call_name)

    return call_names


def _get_ast_nodes(node, node_type, bucket=None):
    """Get ast nodes with specifed ast type.

    Recursive traversal of ast nodes tree to retrieve nodes by defined type.
    """
    bucket = [] if bucket is None else bucket

    if isinstance(node, node_type):
        bucket.append(node)

    for attr in _get_ast_attrs(node):
        if not utils.is_iterable(attr):
            attr = [attr]

        for elem in attr:
            if isinstance(elem, ast.AST):
                if isinstance(elem, node_type):
                    bucket.append(elem)
                bucket = _get_ast_nodes(elem, node_type, bucket)
    return bucket


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


def _get_func_location(func):
    """Get function location for error message."""
    return " in function {!r}, module {!r}.".format(func.__name__,
                                                    func.__module__)


def _get_orig_func(func):
    """Get original unwrapped function under decorator(s)."""
    if func.__name__ != func.func_code.co_name:
        for cell in func.func_closure:
            obj = cell.cell_contents
            if inspect.isfunction(obj):
                if func.__name__ == obj.func_code.co_name:
                    return obj
                else:
                    return _get_orig_func(obj)
    return func


def _is_ast_check(node):
    """Define whether ast_node has `if check:` section or no."""
    if isinstance(node, ast.If):
        if getattr(node.test, 'id', None) == 'check':
            return True
    return False


# =============== SYNTAX RULES ===============


def _verify_docstring_present(func):
    """Rule to verify that function has docstring section."""
    for line in _get_source_lines(func):
        if line.strip().startswith('"""'):
            break
    else:
        return 'Step has no docstring' + _get_func_location(func)


def _verify_argument_present(func, arg_name, arg_val=DEFAULT_VALUE,
                             step_type=None):
    """Rule to verify that function has defined argument."""
    assert step_type

    argspec = inspect.getargspec(func)
    func_location = _get_func_location(func)

    if arg_name not in argspec.args:
        return (
            step_type + "-step must have argument {!r}".format(arg_name) +
            func_location + DOC_LINK)

    if arg_val == DEFAULT_VALUE:
        return

    if not argspec.defaults:
        return (
            step_type + "-step must have argument {!r} with default "
            "value '{}'".format(arg_name, arg_val) + func_location + DOC_LINK)

    kwgs = dict(
        zip(argspec.args[-len(argspec.defaults):],
            argspec.defaults))

    if not kwgs[arg_name] == arg_val:
        return (
            step_type + "-step must have argument {!r} with default "
            "value '{}'".format(arg_name, arg_val) + func_location + DOC_LINK)


def _verify_step_has_code(func):
    """Rule to verify that step has code or docstring.

    It used as decorator for other rules.
    """
    @functools.wraps(func)
    def wrapper(ast_func_def, func_location, step_type):
        if len(ast_func_def.body) <= 1:
            return step_type + '-step has no code or docstring' + func_location
        return func(ast_func_def, func_location, step_type)

    return wrapper


@_verify_step_has_code
def _verify_step_return_something(ast_func_def, func_location, step_type):
    """Rule to verify that step returns something."""
    ast_returns = _get_ast_nodes(ast_func_def.body[-1], ast.Return)
    if not ast_returns:
        return (step_type + '-step must return something' +
                func_location + DOC_LINK)

    for ast_return in ast_returns:
        if (not ast_return.value or
                getattr(ast_return.value, 'id', None) == 'None'):

            return (step_type + '-step must return something' +
                    func_location + DOC_LINK)


@_verify_step_has_code
def _verify_step_return_nothing(ast_func_def, func_location, step_type):
    """Rule to verify that step returns nothing."""
    ast_returns = _get_ast_nodes(ast_func_def.body[-1], ast.Return)
    if ast_returns:
        return (step_type + '-step must return nothing' +
                func_location + DOC_LINK)


def _verify_step_raise_exception(ast_func_def, func_location, step_type):
    """Rule to verify that step raises exception."""
    call_names = _get_call_names(ast_func_def)

    for word in RAISE_WORDS:
        for call_name in call_names:
            if call_name.startswith(word):
                return
    else:
        return (step_type + '-step must raise error if check is failed' +
                func_location + DOC_LINK)


@_verify_step_has_code
def _verify_step_has_action_before_check(ast_func_def, func_location,
                                         step_type):
    """Rule to verify that step action over resource before check result."""
    if _is_ast_check(ast_func_def.body[1]):
        return (step_type + '-step has no action before check' +
                func_location + DOC_LINK)


def _verify_step_has_if_check(ast_func_def, func_location, step_type):
    """Rule to verify that step has `if check:` section."""
    ast_ifs = _get_ast_nodes(ast_func_def, ast.If)
    if not ast_ifs:
        return(step_type + '-step has no block "if check:"' +
               func_location + DOC_LINK)

    for ast_if in ast_ifs:
        if _is_ast_check(ast_if):
            return
    else:
        return (step_type + '-step has no block "if check:"' +
                func_location + DOC_LINK)
