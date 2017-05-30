"""
----------------------------------
Horizon application implementation
----------------------------------
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

from tempfile import mkdtemp

import pom
from pom import ui
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.remote.remote_connection import RemoteConnection

from stepler import config

from .pages import PageBase, pages  # noqa

ui.UI.timeout = config.UI_TIMEOUT
RemoteConnection.set_timeout(config.ACTION_TIMEOUT)
sorted_pages = sorted(pages, key=lambda page: len(page.url))


class Profile(FirefoxProfile):
    """Horizon browser profile."""

    def __init__(self, *args, **kwgs):
        """Constructor."""
        super(Profile, self).__init__(*args, **kwgs)
        self.download_dir = mkdtemp()
        self.set_preference("browser.download.folderList", 2)
        self.set_preference("browser.download.manager.showWhenStarting",
                            False)
        self.set_preference("browser.download.dir", self.download_dir)
        self.set_preference("browser.helperApps.neverAsk.saveToDisk",
                            "application/binary,text/plain,application/zip")
        self.set_preference("browser.download.manager.showAlertOnComplete",
                            False)
        self.set_preference("browser.download.panel.shown", True)


@pom.register_pages(pages)
class Horizon(pom.App):
    """Application to launch horizon in browser."""

    def __init__(self, url, *args, **kwgs):
        """Constructor."""
        self.profile = Profile()
        super(Horizon, self).__init__(
            url, 'firefox', firefox_profile=self.profile, *args, **kwgs)

        self.webdriver.maximize_window()
        self.webdriver.set_window_size(*config.BROWSER_WINDOW_SIZE)
        self.webdriver.set_page_load_timeout(config.ACTION_TIMEOUT)

        self.current_username = None
        self.current_project = None

    @property
    def download_dir(self):
        """Directory with downloaded files."""
        return self.profile.download_dir

    def open(self, page):
        """Open page or url.

        Arguments:
            - page: page class or url string.
        """
        if isinstance(page, str):
            url = page
        else:
            url = page.url
        super(Horizon, self).open(url)

    @property
    def current_page(self):
        """Current page dynamic definition."""
        current_url = self.webdriver.current_url
        for page in sorted_pages:
            url = self.app_url + page.url

            if current_url.startswith(url):
                url_end = current_url.split(url)[-1]

                if not (url_end and url_end[0].isalnum()):
                    return page(self)
        return PageBase(self)

    def flush_session(self):
        """Delete all cookies.

        It forces flushes user session by cookies deleting.
        """
        self.webdriver.delete_all_cookies()
