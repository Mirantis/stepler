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
    step_classes = []

    import stepler
    for _, pkg_name, is_pkg in pkgutil.iter_modules(stepler.__path__):

        if not is_pkg:
            continue

        try:
            steps_module = importlib.import_module(
                stepler.__name__ + '.' + pkg_name + '.steps')
        except ImportError:
            continue

        for obj_name in steps_module.__all__:
            obj = getattr(steps_module, obj_name)

            if inspect.isclass(obj):
                step_classes.append(obj)

    for step_cls in step_classes:
        for attr_name in dir(step_cls):

            if attr_name.startswith('_'):
                continue

            step_func = getattr(step_cls, attr_name).im_func
            step_func = get_orig_func(step_func)

            check_docstring(step_func)

            if step_func.__name__.startswith('get_'):
                if 'check' in inspect.getargspec(step_func).args:
                    check_check(inspect.getargspec(step_func))
                step_last_line = inspect.getsourcelines(
                    step_func)[0][-1].strip()
                assert step_last_line.startswith('return')
                assert not step_last_line.endswith('return')
                assert not step_last_line.endswith('None')

            elif step_func.__name__.startswith('check_'):
                check_timeout(inspect.getargspec(step_func))
                step_last_line = inspect.getsourcelines(
                    step_func)[0][-1].strip()
                assert not step_last_line.startswith('return')
                for word in ('assert_that', 'wait', 'raise', 'assert'):
                    if step_last_line.startswith(word):
                        break
                else:
                    assert False

            else:
                check_check(step_func)
                check_check_usage(step_func)

    import ipdb; ipdb.set_trace()


def check_check_usage(func):

    last_line = inspect.getsourcelines(func)[0][-1].rstrip()
    lines = iter([line.rstrip() for line in inspect.getsourcelines(func)[0]
                  if line.rstrip()])

    DOCSTRING_PRESENCE = 0
    ACTION_PRESENCE = 1
    IF_CHECK_PRESENCE = 2
    RAISE_PRESENCE = 3
    LAST_LINE_CHECK = 4

    func_location = get_func_location(func)
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
            line = lines.next()
        except StopIteration:
            raise SyntaxError(stage_errors[stage])

        if stage == DOCSTRING_PRESENCE:
            if line.endswith('"""'):
                stage = ACTION_PRESENCE
                continue

        if stage == ACTION_PRESENCE:
            line = line.strip()
            if line.startswith('if') and 'check' in line:
                raise SyntaxError(stage_errors[stage])
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
                raise_words = ('assert_that',
                               'wait',
                               'raise',
                               'assert',
                               'check_')
                for word in raise_words:
                    if word in sline:
                        stage = LAST_LINE_CHECK
                        break

        if stage == LAST_LINE_CHECK:
            if line == last_line:
                sline = line.strip()
                line_indent = len(line) - len(sline)

                if line_indent > if_check_indent:
                    assert not sline.startswith('return')
                else:
                    assert sline.startswith('return')
                    assert not sline.endswith('return')
                    assert not sline.endswith('None')

                break


def get_func_location(func):
    return " in function: {!r}, module: {!r}.".format(func.__name__,
                                                      func.__module__)


def check_docstring(func):
    for line in inspect.getsourcelines(func)[0]:
        line = line.strip()
        if line.startswith('"""'):
            break
    else:
        raise Exception('No docstring in step')


def check_check(step_func):
    """Check ``check=True`` argument."""
    argspec = inspect.getargspec(step_func)
    func_location = get_func_location(step_func)
    assert 'check' in argspec.args, func_location
    args = argspec.args
    defaults = argspec.defaults
    assert defaults, func_location
    len_def = len(defaults)
    kwgs = args[-len_def:]
    kwgs = dict(zip(kwgs, defaults))
    assert kwgs['check'], func_location


def check_timeout(argspec):
    """Check ``check=True`` argument."""
    assert 'timeout' in argspec.args
    args = argspec.args
    defaults = argspec.defaults
    assert defaults
    len_def = len(defaults)
    kwgs = args[-len_def:]
    kwgs = dict(zip(kwgs, defaults))
    assert kwgs['timeout'] == 0


def get_orig_func(func):
    if func.__name__ != func.func_code.co_name:
        for cell in func.func_closure:
            obj = cell.cell_contents
            if inspect.isfunction(obj):
                if func.__name__ == obj.func_code.co_name:
                    return obj
                else:
                    return get_orig_func(obj)
    return func
