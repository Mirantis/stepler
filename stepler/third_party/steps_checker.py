"""
Pytest plugin to check only steps and fixtures are called inside test.

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

import importlib
import inspect
import pkgutil
import re

import stepler

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


def step(func):
    """Decorator to append step name to storage."""
    STEPS.append(func.__name__)
    return func


def pytest_collection_modifyitems(config, items):
    """Hook to detect forbidden calls inside test."""
    errors = []
    for item in items:
        fixtures = item.funcargnames
        permitted_calls = STEPS + fixtures

        test_name = item.function.__name__
        file_name = inspect.getsourcefile(item.function)
        source_lines = inspect.getsourcelines(item.function)[0]

        while source_lines:
            def_line = source_lines.pop(0).strip()
            if def_line.startswith('def '):
                break

        for line in source_lines:
            line = line.strip()
            if line.startswith('#'):
                continue

            result = REGEX_CALL.search(line)
            if not result:
                continue

            call_name = result.group(1)
            if call_name not in permitted_calls:

                error = 'Calling {!r} in test {!r} in file {!r}'.format(
                    call_name, test_name, file_name)
                errors.append(error)

    if errors:
        raise SystemError(
            "Only steps and fixtures must be called in test!\n{}".format(
                '\n'.join(errors)))


def pytest_configure(config):
    """Hook to check steps consistency."""
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
            else:  # set step to change a resource
                _validate_set_step(step_func)

    import ipdb; ipdb.set_trace()


def _validate_get_step(func):
    func_location = _get_func_location(func)
    if 'check' in inspect.getargspec(func).args:
        _check_arg(func, 'check', True)

    step_last_line = inspect.getsourcelines(func)[0][-1].strip()
    assert step_last_line.startswith('return'), \
        'Last line must be "return some_var"' + func_location
    assert not step_last_line.endswith('return'), \
        'Last line must be "return some_var"' + func_location
    assert not step_last_line.endswith('None'), \
        'Last line must be "return some_var"' + func_location


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


def _validate_set_step(func):
    _check_arg(func, 'check', True)
    _check_set_step_format(func)


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


def _check_set_step_format(func):
    func_lines = inspect.getsourcelines(func)[0]
    last_line = func_lines[-1].rstrip()
    func_lines = iter([line.rstrip() for line in func_lines if line.rstrip()])

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
    return " in function: {!r}, module: {!r}.".format(func.__name__,
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
            "Arg {!r} value must be {!r}".format(arg_name, arg_val) + \
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
