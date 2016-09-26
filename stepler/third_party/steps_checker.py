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

import inspect
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
