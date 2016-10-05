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

import importlib
import inspect
import pkgutil
import re

import hamcrest

import stepler

__all__ = [
    'pytest_addoption',
    'pytest_collection_modifyitems',
    'pytest_configure',
    'step'
]

REGEX_CALL = re.compile('\W*(\w+)\(')

# predefined permitted calls
STEPS = [
    'list',
    'next',
    'put',  # TODO (schipiga): update attrdict method
    'range',
    'sorted',
    'set_trace'
]

# register hamcrest matchers
STEPS += [method_name for method_name in dir(hamcrest)
          if not method_name.startswith('_')]

# methods which raise exception
RAISE_WORDS = ('assert_that',
               'check_',
               'raise',
               'wait')

# step validation stages
ACTION_PRESENCE = 1
IF_CHECK_PRESENCE = 2
RAISE_PRESENCE = 3
RETURN_CHECK = 4

DEFAULT_VALUE = object()

DOC_LINK = ' See http://stepler.readthedocs.io/steps_concept.html'


def step(func):
    """
    Decorator to append step method name to permitted calls.

    Args:
        func (function): function to add its name to list with permitted calls

    Returns:
        function: the same function
    """
    STEPS.append(func.__name__)
    return func


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
        fixtures = item.funcargnames
        permitted_calls = STEPS + fixtures

        test_name = item.function.__name__
        file_name = item.function.__module__
        func_lines = _get_func_lines(item.function, check=False)

        for line in func_lines:
            line = line.strip()

            result = REGEX_CALL.search(line)
            if not result:
                continue

            call_name = result.group(1)
            if call_name not in permitted_calls:

                error = ("Calling {!r} isn't allowed in test {!r}, "
                         "module {!r}. {}".format(call_name, test_name,
                                                  file_name, DOC_LINK))
                errors.append(error)

    if errors:
        raise SystemError(
            "Only steps and fixtures must be called in test!\n{}".format(
                '\n'.join(errors)))


def pytest_configure(config):
    """Hook to check steps consistency."""
    if config.option.disable_steps_checker:
        config.warn('P1', 'Step consistency checker is disabled!')
        return

    for step_cls in _get_step_classes():
        for attr_name in dir(step_cls):

            if attr_name.startswith('_'):
                continue

            step_func = getattr(step_cls, attr_name).im_func
            step_func = _get_orig_func(step_func)

            _check_docstring(step_func)

            if step_func.__name__.startswith('get_'):
                _validate_get_step(step_func)

            elif step_func.__name__.startswith('check_'):
                _validate_check_step(step_func)

            else:  # change step
                _validate_change_step(step_func)


def _validate_get_step(func):
    func_location = _get_func_location(func)
    if 'check' in inspect.getargspec(func).args:
        _check_arg(func, 'check', True)

    internal_def = False
    func_lines = _get_func_lines(func)
    for line in func_lines:
        sline = line.strip()

        if sline.startswith('def '):
            internal_def = True

        if internal_def or sline.startswith('return'):
            break
    else:
        raise AssertionError(
            'Step must return something' + func_location + DOC_LINK)

    step_last_line = func_lines[-1].strip()
    assert not step_last_line.endswith('return'), \
        'Step must return something' + func_location + DOC_LINK
    assert not step_last_line.endswith('None'), \
        'Step must return something' + func_location + DOC_LINK


def _validate_check_step(func):
    func_location = _get_func_location(func)
    func_lines = _get_func_lines(func)

    internal_def = False
    for line in func_lines:
        sline = line.strip()

        if sline.startswith('def '):
            internal_def = True

        if not internal_def and sline.startswith('return'):
            raise AssertionError(
                'Step must not return anything' + func_location + DOC_LINK)

    for line in func_lines:
        for word in RAISE_WORDS:
            if word in line:
                return
    else:
        raise AssertionError(
            "No call of method to raise exception" + func_location + DOC_LINK)


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
    func_lines = _get_func_lines(func)

    last_line = func_lines[-1].rstrip()
    func_lines = iter(func_lines)

    func_location = _get_func_location(func)
    stage_errors = {
        ACTION_PRESENCE: "No action before 'if check:'" + func_location +
                         DOC_LINK,
        IF_CHECK_PRESENCE: "No 'if check:'" + func_location + DOC_LINK,
        RAISE_PRESENCE: "No call of method to raise exception under "
                        "'if check:'" + func_location + DOC_LINK,
        RETURN_CHECK: "Can't find line " + last_line + func_location
    }
    stage = ACTION_PRESENCE
    if_check_indent = None
    line_indent = None
    internal_def = False

    while True:
        try:
            line = func_lines.next()
        except StopIteration:
            raise AssertionError(stage_errors[stage])

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
                        stage = RETURN_CHECK
                        break

        if stage == RETURN_CHECK:
            sline = line.strip()
            if sline.startswith('def '):
                internal_def = True

            line_indent = len(line) - len(sline)

            if line_indent > if_check_indent:
                if not internal_def:
                    assert not sline.startswith('return'), \
                        ('Step must not return anything under "if check:"' +
                         func_location + DOC_LINK)
            else:
                assert sline.startswith('return'), \
                    'Step must return something' + func_location + DOC_LINK
                assert not sline.endswith('return'), \
                    'Step must return something' + func_location + DOC_LINK
                assert not sline.endswith('None'), \
                    'Step must return something' + func_location + DOC_LINK

            if line == last_line:
                break


def _get_func_lines(func, check=True):
    func_lines = inspect.getsourcelines(func)[0]
    func_lines = [line.rstrip() for line in func_lines
                  if line.rstrip() and not line.strip().startswith('#')]

    while func_lines:  # loop until end of docstring
        line = func_lines.pop(0).strip()
        if line.endswith('"""'):
            break

    if check:
        assert func_lines, "No code" + _get_func_location(func)
    return func_lines


def _get_func_location(func):
    return " in function {!r}, module {!r}.".format(func.__name__,
                                                    func.__module__)


def _check_docstring(func):
    for line in inspect.getsourcelines(func)[0]:
        line = line.strip()
        if line.startswith('"""'):
            break
    else:
        raise AssertionError('No docstring' + _get_func_location(func))


def _check_arg(func, arg_name, arg_val=DEFAULT_VALUE):
    argspec = inspect.getargspec(func)
    func_location = _get_func_location(func)
    args = argspec.args
    assert arg_name in args, "No arg {!r}".format(arg_name) + func_location

    if arg_val != DEFAULT_VALUE:
        defaults = argspec.defaults
        assert defaults, "No default value for arg {!r}".format(arg_name) + \
            func_location

        kwgs = dict(zip(args[-len(defaults):], defaults))
        assert kwgs[arg_name] == arg_val, \
            "Arg {!r} value must be '{}'".format(arg_name, arg_val) + \
            func_location


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
