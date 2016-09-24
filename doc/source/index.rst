.. stepler documentation master file, created by
   sphinx-quickstart on Fri Sep 23 18:01:17 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====================================
stepler: test openstack step by step
====================================

----------
Annotation
----------

Stepler framework is intended to provide the community with a testing framework that is capable of perform advanced scenario and destructive test cases, like batch instances launching, instances migration, services restarts and different HA-specific cases.

This solution is not intended for OpenStack API validation, but provides simple tool for creation tests to check advanced end-user scenarios.

Stepler's architecture is based on STEPS-methodology.

-----------------
Deep to structure
-----------------

.. toctree::
   :maxdepth: 1

   common_fixtures
   glance
   horizon
   keystone
   neutron
   nova

----------------
How to run tests
----------------

Stepler uses ``py.test`` as test runner (``tox`` is used for routine operations too). If you know how to launch test with pytest, you may skip this section. Let's view typical commands to launch test in different ways.

If you want to launch all tests (``-v`` is used to show full name and status of each test)::

   py.test stepler -v

For ex, you write the test ``test_upload_image`` and want to launch it only::

   py.test stepler -k test_upload_image

If your test was failed and you want to debug it, you should disable stdout capture::

   py.test stepler -k test_upload_image -s

Full information about ``py.test`` is obtainable with::

   py.test -h

------------------
How to debug tests
------------------

We recommended to use ``ipdb`` to set up break points inside code. Just put next chunk before code line where you want to debug (don't forget about ``-s`` to disable  ``py.test`` stdout capture):

.. code:: python

   import ipdb; ipdb.set_trace()
