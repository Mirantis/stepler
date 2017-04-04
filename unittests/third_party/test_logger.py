"""
-----------------------
logger helper unittests
-----------------------
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

from functools import wraps

import pytest

from stepler.third_party import logger


def dec(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def fn1():
    return


def fn2(arg1, arg2, kwarg=None):
    return


@dec
def fn3(arg1, arg2, kwarg=None):
    return


class Foo(object):
    def meth1(self):
        return

    def meth2(self, arg1, arg2, kwarg=None):
        return

    @dec
    def meth3(self, arg1, arg2, kwarg=None):
        return


obj = Foo()


@pytest.mark.parametrize(['fn', 'args', 'kwargs', 'msg'], [
    (
        fn1,
        (),
        {},
        "Function 'fn1' starts with args () and kwgs {}"
    ),
    (
        fn2,
        (1, 'foo'),
        {'kwarg': 'bar'},
        "Function 'fn2' starts with args (1, 'foo') and kwgs {'kwarg': 'bar'}"
    ),
    (
        fn3,
        (1, 'foo'),
        {'kwarg': 'bar'},
        "Function 'fn3' starts with args (1, 'foo') and kwgs {'kwarg': 'bar'}"
    ),
    (
        obj.meth1,
        (),
        {},
        "Function 'meth1' starts with args () and kwgs {}"
    ),
    (
        obj.meth2,
        (1, 'foo'),
        {'kwarg': 'bar'},
        "Function 'meth2' starts with args (1, 'foo') "
        "and kwgs {'kwarg': 'bar'}"
    ),
    (
        obj.meth3,
        (1, 'foo'),
        {'kwarg': 'bar'},
        "Function 'meth3' starts with args (1, 'foo') "
        "and kwgs {'kwarg': 'bar'}"
    )
])  # yapf: disable
def test_log_function_name_and_args(caplog, fn, args, kwargs, msg):
    fn = logger.log(fn)
    fn(*args, **kwargs)
    assert msg in caplog.text
