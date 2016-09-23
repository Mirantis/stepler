"""
Horizon steps for api access.

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

import os

import pom
from waiting import wait

from .base import BaseSteps


class ApiAccessSteps(BaseSteps):
    """Api access steps."""

    def tab_api_access(self):
        """Open api access page if it isn't opened."""
        access_page = self._open(self.app.page_access)
        access_page.label_api_access.click()
        return access_page.tab_api_access

    @pom.timeit('Step')
    def download_rc_v2(self, check=True):
        """Step to download v2 file."""
        self._remove_rc_file()

        tab_api_access = self.tab_api_access()
        tab_api_access.button_download_v2_file.click()

        if check:
            self._wait_rc_file_downloaded()
            content = open(self._rc_path).read()

            assert 'OS_AUTH_URL={}'.format(self._auth_url) in content
            assert 'OS_USERNAME="{}"'.format(self._username) in content
            assert 'OS_TENANT_NAME="{}"'.format(self._project_name) in content
            assert 'OS_TENANT_ID={}'.format(self._project_id) in content

    @pom.timeit('Step')
    def download_rc_v3(self, check=True):
        """Step to download v3 file."""
        self._remove_rc_file()

        tab_api_access = self.tab_api_access()
        tab_api_access.button_download_v3_file.click()

        if check:
            self._wait_rc_file_downloaded()
            content = open(self._rc_path).read()

            _v3_url = self._auth_url.split('/v')[0] + '/v3'  # FIXME(schipiga)
            assert 'OS_AUTH_URL={}'.format(_v3_url) in content
            assert 'OS_USERNAME="{}"'.format(self._username) in content
            assert 'OS_PROJECT_NAME="{}"'.format(self._project_name) in content
            assert 'OS_PROJECT_ID={}'.format(self._project_id) in content

    @pom.timeit('Step')
    def view_credentials(self, check=True):
        """Step to view credentials."""
        tab_api_access = self.tab_api_access()
        tab_api_access.button_view_credentials.click()

        with tab_api_access.form_user_credentials as form:
            if check:
                assert form.field_username.value == self._username
                assert form.field_project_name.value == self._project_name
                assert form.field_project_id.value == self._project_id
                assert form.field_auth_url.value == self._auth_url

            form.cancel()

    @property
    def _rc_path(self):
        return os.path.join(self.app.download_dir,
                            self._project_name + '-openrc.sh')

    def _remove_rc_file(self):
        if os.path.exists(self._rc_path):
            os.remove(self._rc_path)

    @property
    def _username(self):
        return self.app.current_username

    @property
    def _project_name(self):
        return self.app.current_project

    @property
    def _project_id(self):
        return self.app.page_access.tab_api_access \
            .label_volume.value.split('/')[-1]

    @property
    def _auth_url(self):
        return self.app.page_access.tab_api_access.label_identity.value

    def _wait_rc_file_downloaded(self):

        def predicate():
            try:
                if (os.path.basename(self._rc_path) in
                        os.listdir(self.app.download_dir)):

                    with open(self._rc_path) as f:
                        return bool(f.read(1))
                else:
                    return False
            except IOError:
                return False

        wait(predicate,
             timeout_seconds=30, sleep_seconds=0.1)
