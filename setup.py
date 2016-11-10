"""
-------------
Setup stepler
-------------
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

import sys

import pip
from setuptools import setup  # noqa

setup(
    setup_requires=['pbr==1.8'],
    pbr=True
)

# TODO (schipiga): workaround to install requirements from additional file.
# Due to weird logic pbr allows to use only one requirements file.
sys.exit(pip.main(['install', '-r', 'c-requirements.txt']))
