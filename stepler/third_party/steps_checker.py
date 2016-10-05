"""
----------------------------------
Pytest plugin to check consistency
----------------------------------

- steps and fixtures only are called inside a test

- steps should have format described in
  :ref:`STEPS architecture <steps-architecture>`
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
import importlib
import inspect
import pkgutil

import hamcrest

import stepler
from stepler.third_party import utils


__all__ = [
    'pytest_collection_modifyitems',
    'pytest_configure',
    'step'
]

# predefined permitted calls
PERMITTED_CALLS = [
    'list',
    'next',
    'put',  # TODO(schipiga): update attrdict method
    'range',
    'sorted',
    'set_trace',
    'generate_ids',
    'generate_files'
]

# register hamcrest matchers
PERMITTED_CALLS += [method_name for method_name in dir(hamcrest)
                    if not method_name.startswith('_')]

# registered steps
STEPS = []

# methods which raise exception
RAISE_WORDS = ('assert_that',
               'check_',
               'raise',
               'wait')

# step validation stages
DOCSTRING_PRESENCE = 0
ACTION_PRESENCE = 1
IF_CHECK_PRESENCE = 2
RAISE_PRESENCE = 3
LAST_LINE_CHECK = 4

DEFAULT_VALUE = object()
DOC_LINK = (' Visit http://stepler.readthedocs.io/steps_concept.html to get'
            ' details.')


def step(func):
    """Decorator to append step method name to permitted calls.

    Args:
        func (function): function to add its name to list with permitted calls

    Returns:
        function: the same function
    """
    STEPS.append(func.__name__)
    return func


def pytest_collection_modifyitems(config, items):
    """Hook to detect forbidden calls inside test."""
    errors = []
    for item in items:
        permitted_calls = PERMITTED_CALLS + STEPS + item.funcargnames
        ast_root = ast.parse(_get_source(item.function))

        for call_name in _get_call_names(ast_root):
            if call_name not in permitted_calls:

                error = ("Calling {!r} isn't allowed".format(call_name)
                         + _get_func_location(item.function) + DOC_LINK)
                errors.append(error)

    if errors:
        raise SystemError(
            "Only steps and fixtures must be called in test!\n{}".format(
                '\n'.join(errors)))


def _get_source_lines(func):
    """Get function source without common indentations.

    Function can be under another function or class and due to that it has
    additional indentation. Its indentation should be deleted before ast.parse.
    """
    lines = inspect.getsourcelines(func)[0]
    lines = [l.rstrip() for l in lines if not l.strip().startswith('#')]

    def_line = [l for l in lines if l.strip().startswith('def ')][0]
    def_indent = len(def_line) - len(def_line.strip())

    return [l[def_indent:] for l in lines]


def _get_source(func):
    return '\n'.join(_get_source_lines(func))


def _get_ast_attrs(node):
    """Get attributes of ast node.

    Some attributes are skipped because they are not related to function body
    and just create side effect.
    """
    skip_list = ('args', 'decorator_list')
    attrs = []
    for name in dir(node):
        if not name.startswith('_') and not name in skip_list:
            attrs.append(getattr(node, name))
    return attrs


def _get_call_names(node, call_names=None):
    """Get called function names inside function.

    Recursive traversal of ast nodes tree to retrieve calls.
    """
    call_names = set()
    call_nodes = _get_nodes(node, ast.Call)

    for call_node in call_nodes:
        if hasattr(call_node.func, 'attr'):
            call_name = call_node.func.attr

        else:
            call_name = call_node.func.id
        call_names.add(call_name)

    return call_names


def _get_nodes(node, node_type, bucket=None):
    """Get ast nodes with specifed ast type."""
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
                else:
                    bucket = _get_nodes(elem, node_type, bucket)
    return bucket


def pytest_configure(config):
    """Hook to check steps consistency."""
    for step_cls in _get_step_classes():
        for attr_name in dir(step_cls):

            if attr_name not in STEPS:
                continue

            step_func = getattr(step_cls, attr_name).im_func
            step_func = _get_orig_func(step_func)

            _check_docstring(step_func)

            if step_func.__name__.startswith('get_'):
                _validate_get_step(step_func)

            # elif step_func.__name__.startswith('check_'):
            #     _validate_check_step(ast_root)

            # else:  # change step
            #     _validate_change_step(ast_root)


def _validate_get_step(func):
    func_location = _get_func_location(func)
    if 'check' in inspect.getargspec(func).args:
        _check_arg(func, 'check', True)

    ast_root = ast.parse(_get_source(func))
    func_def = ast_root.body[0]

    assert func_def.body, "No code" + func_location

    ast_rets = _get_nodes(func_def.body[-1], ast.Return)
    assert ast_rets, 'Step should return something' + func_location + DOC_LINK

    for ast_ret in ast_rets:
        if not ast_ret.value or getattr(ast_ret.value, 'id', None) == 'None':
            raise AssertionError(
                'Step should return something' + func_location + DOC_LINK)


def _validate_check_step(func):
    func_location = _get_func_location(func)
    _check_arg(func, 'timeout', 0)

    step_last_line = inspect.getsourcelines(func)[0][-1].strip()
    assert not step_last_line.startswith('return'), \
        'Last line must not contain "return"' + func_location

    for word in RAISE_WORDS:
        if word in step_last_line:
            break
    else:
        raise AssertionError("No raise error" + func_location)


def _validate_change_step(func):
    _check_arg(func, 'check', True)
    _check_change_step_format(func)


def _get_step_classes():
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


def _check_change_step_format(func):
    func_lines = inspect.getsourcelines(func)[0]
    func_lines = [line.rstrip() for line in func_lines
                  if line.rstrip() and not line.strip().startswith('#')]

    last_line = func_lines[-1].rstrip()
    func_lines = iter(func_lines)

    func_location = _get_func_location(func)
    stage_errors = {
        DOCSTRING_PRESENCE: "No docstring" + func_location,
        ACTION_PRESENCE: "No action before 'if check:'" + func_location,
        IF_CHECK_PRESENCE: "No 'if check:'" + func_location,
        RAISE_PRESENCE: "No raise error under 'if check:'" + func_location,
        LAST_LINE_CHECK: "Can't find line " + last_line + func_location
    }
    stage = DOCSTRING_PRESENCE
    if_check_indent = None
    line_indent = None

    while True:
        try:
            line = func_lines.next()
        except StopIteration:
            raise AssertionError(stage_errors[stage])

        if stage == DOCSTRING_PRESENCE:
            if line.endswith('"""'):
                stage = ACTION_PRESENCE
                continue

        if stage == ACTION_PRESENCE:
            line = line.strip()
            if line.startswith('if') and 'check' in line:
                raise AssertionError(stage_errors[stage])
            stage = IF_CHECK_PRESENCE

        if stage == IF_CHECK_PRESENCE:
            sline = line.strip()
            if sline.startswith('if') and 'check' in line:
                if_check_indent = len(line) - len(sline)
                stage = RAISE_PRESENCE

        if stage == RAISE_PRESENCE:
            sline = line.strip()
            line_indent = len(line) - len(sline)
            if line_indent > if_check_indent:
                for word in RAISE_WORDS:
                    if word in sline:
                        stage = LAST_LINE_CHECK
                        break

        if stage == LAST_LINE_CHECK:
            if line == last_line:
                sline = line.strip()
                line_indent = len(line) - len(sline)

                if line_indent > if_check_indent:
                    assert not sline.startswith('return'), \
                        'Last line must not contain "return"' + func_location
                else:
                    assert sline.startswith('return'), \
                        'Last line must be "return some_var"' + func_location
                    assert not sline.endswith('return'), \
                        'Last line must be "return some_var"' + func_location
                    assert not sline.endswith('None'), \
                        'Last line must be "return some_var"' + func_location
                break


def _get_func_location(func):
    """Get function location for error message."""
    return " in function {!r}, module {!r}.".format(func.__name__,
                                                    func.__module__)


def _check_docstring(func):
    for line in _get_source_lines(func):
        line = line.strip()
        if line.startswith('"""'):
            break
    else:
        raise AssertionError(
            'No docstring' + _get_func_location(func) + DOC_LINK)


def _check_arg(func, arg_name, arg_val=DEFAULT_VALUE):
    argspec = inspect.getargspec(func)
    func_location = _get_func_location(func)
    args = argspec.args
    assert arg_name in args, "No arg {!r}".format(arg_name) + func_location

    if arg_val != DEFAULT_VALUE:
        defaults = argspec.defaults
        assert defaults, "No default value for arg {!r}".format(arg_name) + \
            func_location + DOC_LINK

        kwgs = dict(zip(args[-len(defaults):], defaults))
        assert kwgs[arg_name] == arg_val, \
            "Arg {!r} value must be '{}'".format(arg_name, arg_val) + \
            func_location + DOC_LINK


def _get_orig_func(func):
    if func.__name__ != func.func_code.co_name:
        for cell in func.func_closure:
            obj = cell.cell_contents
            if inspect.isfunction(obj):
                if func.__name__ == obj.func_code.co_name:
                    return obj
                else:
                    return _get_orig_func(obj)
    return func
