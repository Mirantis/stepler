# -*- coding: utf-8 -*-

"""
------------------------------------
Fixtures to manipulate with projects
------------------------------------
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

import pytest

from stepler.horizon import steps
from stepler.third_party import utils

__all__ = [
    'projects_steps_ui',
    'project_name_non_ascii'
]


@pytest.fixture
def projects_steps_ui(login, horizon):
    """Fixture to get projects steps.

    Args:
        login (None): should log in horizon before steps using
        horizon (Horizon): instantiated horizon web application

    Returns:
        stepler.horizon.steps.ProjectsSteps: instantiated UI projects steps
    """
    return steps.ProjectsSteps(horizon)


@pytest.fixture
def project_name_non_ascii(projects_steps_ui,
                           admin_project_resources):
    """Fixture to create project with non ascii name and switch to it."""
    project_name = projects_steps_ui.create_project(
        next(utils.generate_ids(use_unicode=True)),
        check=False).encode('utf-8')
    projects_steps_ui.manage_project_members(
        project_name,
        admin_project_resources)
    projects_steps_ui.switch_project(project_name, check=False)

    yield project_name

    projects_steps_ui.switch_project(admin_project_resources["project"].name)
    projects_steps_ui.delete_project(project_name)
