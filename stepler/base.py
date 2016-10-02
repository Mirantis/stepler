"""
----
Base
----
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

__all__ = [
    'BaseSteps',
]


class BaseSteps(object):
    """Base steps-class.

    Steps-class aggregates steps over one resource. It means there are many
    inherited steps-classes for each resource.

    Note:
        Technically there are three types of steps:

        #. ``get``-steps

           Their goal to retrieve information about resource and return it. If
           information is unavailable, a step should raise exception. Rules to
           code:

           - step method name has prefix ``get_``, for ex: ``get_ips``,
             ``get_projects``, ``get_flavor``, ``get_network``.
           - step should return something in last code line, for ex:
             ``return projects``, ``return network``. It makes easier code
             review and debugging.
           - step can include argument ``check=True``. It's depends on context,
             for ex: step returns collection, but collection can be empty. And
             here ``check=True`` will help to check that collection has items.

        #. ``check``-steps

           Their goal to validate input resource and raise exception if it's
           invalid. Rules to code:

           - step method name has prefix ``check_``, for ex:
             ``check_image_presence``, ``check_project_bind_status``.

           - step should return nothing.
           - step should use code to raise exception: ``assert_that`` from
             hamcrest, ``wait``-methods which raise ``TimeoutError``, ``raise``
             for explicit exception, another ``check_``-steps.

             .. warning::
                We don't use python ``assert``, prefer ``hamcrest`` library.

           - step should include argument ``timeout=0`` to provide check during
             the time.

        #. ``change``-steps

           Their goal to change resource and check that changing is successful.
           Rules to code:

           - step method name starts with a verb denoting the action.
           - step has argument ``check=True``.
           - step makes action over resource before check.
           - inside ``if check:`` step should use code to raise exception:
             ``assert_that`` from hamcrest, ``wait``-methods which raise
             ``TimeoutError``, ``raise`` for explicit exception, or
             ``check_``-step.
           - inside ``if check:`` step should return nothing. Its section is
             for verification only.
           - if step should return something (for ex: ``return image``), it
             should be after ``if check:``.

        Common rules:

        - each step method has docstring, explaining its mission.

    See Also:
        **Why do we make steps with optional verification** ``check=True``?

        Sometimes (may be very rarely) we will need to make step without
        verification. In negative tests, for ex: try to create server
        without name and check that there is error.
        But more often we need positive verification by default to guarantee
        that step of a test was finished successfully and the test can go to
        another step.
    """

    def __init__(self, client):
        """
        Constructor.

        Args:
            client (object): client for resources manipulation.
        """
        self._client = client
