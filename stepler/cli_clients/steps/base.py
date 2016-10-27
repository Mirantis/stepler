import os
import shlex
import sys

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

from hamcrest import assert_that, is_not, empty  # noqa

from stepler import config

os.environ['OS_PROJECT_DOMAIN_NAME'] = config.PROJECT_DOMAIN_NAME
os.environ['OS_USER_DOMAIN_NAME'] = config.USER_DOMAIN_NAME
os.environ['OS_PROJECT_NAME'] = config.PROJECT_NAME
os.environ['OS_USERNAME'] = config.USERNAME
os.environ['OS_PASSWORD'] = config.PASSWORD
os.environ['OS_AUTH_URL'] = config.AUTH_URL


class BaseCliSteps(object):

    def execute_command(self, cmd, timeout=0, check=True):
        result = subprocess.check_output(shlex.split(cmd), timeout=timeout)
        if check:
            assert_that(result, is_not(empty()))
        return result
