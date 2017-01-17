=======
Horizon
=======

---------------
Tests launching
---------------

.. code::

   py.test stepler/horizon

Special environment variables:

* ``VIRTUAL_DISPLAY`` says py.test to use `xvfb <https://en.wikipedia.org/wiki/Xvfb>`_.
  Not specified by default.

Required software:

* ``firefox v45 or less`` - modern firefox versions require geckodriver,
  which is unstable still
* ``avconv`` - is used to capture tests video
* ``xvfb`` - optionally, if you are going to use virtual X11 display

.. note::

   It requires X11 display to launch firefox. With server distributive it's
   recommended to use ``xvfb``. Environment variable ``DISPLAY`` should be
   defined and point to actual X11 display. Otherwise tests will be failed.

.. automodule:: stepler.horizon.conftest
   :members:

.. automodule:: stepler.horizon.steps
   :members:

-------------
Horizon tests
-------------

.. automodule:: stepler.horizon.tests.test_auth
   :members:

.. automodule:: stepler.horizon.tests.test_containers
   :members:

.. automodule:: stepler.horizon.tests.test_credentials
   :members:

.. automodule:: stepler.horizon.tests.test_defaults
   :members:

.. automodule:: stepler.horizon.tests.test_flavors
   :members:

.. automodule:: stepler.horizon.tests.test_floatingips
   :members:

.. automodule:: stepler.horizon.tests.test_host_aggregates
   :members:

.. automodule:: stepler.horizon.tests.test_images
   :members:

.. automodule:: stepler.horizon.tests.test_instances
   :members:

.. automodule:: stepler.horizon.tests.test_keypairs
   :members:

.. automodule:: stepler.horizon.tests.test_metadata_definitions
   :members:

.. automodule:: stepler.horizon.tests.test_networks
   :members:

.. automodule:: stepler.horizon.tests.test_projects
   :members:

.. automodule:: stepler.horizon.tests.test_router
   :members:

.. automodule:: stepler.horizon.tests.test_security_groups
   :members:

.. automodule:: stepler.horizon.tests.test_user_settings
   :members:

.. automodule:: stepler.horizon.tests.test_users
   :members:

.. automodule:: stepler.horizon.tests.test_volume_backups
   :members:

.. automodule:: stepler.horizon.tests.test_volume_snapshots
   :members:

.. automodule:: stepler.horizon.tests.test_volume_types
   :members:

.. automodule:: stepler.horizon.tests.test_volumes
   :members:
