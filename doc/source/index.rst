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

------------
Architecture
------------

Stepler's architecture is based on STEPS-methodology, that considers a test as a sequence of steps, each of them ends with check, that step was finished correct. It allows to compose plenty of tests, having moderate codebase.

Architecture has following abstraction levels, where code lives (from higher to less):

* **clients** are able to manipulate resources: *users, roles, servers, etc*. For ex: *keystone client, nova client, node client, etc*.
* **steps** are actions, that we want to make over resources via **clients**: *create, delete, update, migrate, etc*. They should end with check, that step was finished correct.
* **fixtures** manage resources *construction, destruction, etc* via **steps**.
* **tests** combine **steps** and **fixtures** according to scenario.

Detailed information about autotests construction is available in `our guideline <http://autotests-guideline.readthedocs.io/>`_.

Sometimes it needs to have code for *ssh connection, proxy server, etc*. They are not related with **clients**, **steps**, **fixtures** and **tests** and are considered as third party helpers and must be implemented based on its purpose with OOP and design principles.

Stepler uses `py.test <http://doc.pytest.org/>`_ as test runner and `tox <https://tox.readthedocs.io/>`_ for routine operations. Be sure you know them.

--------------
How to install
--------------

Make following commands in terminal::

   git clone https://github.com/Mirantis/stepler.git
   cd stepler
   virtualenv .venv
   . .venv/bin/activate
   pip install -U pip
   pip install -r requirements.txt -r c-requirements.txt

----------------
How to run tests
----------------

*If you know how to launch tests with py.test, you may skip this section.*

Before launching you should export some openstack environment variables:

* ``OS_PROJECT_DOMAIN_NAME`` (default value ``'default'``)
* ``OS_USER_DOMAIN_NAME`` (default value ``'default'``)
* ``OS_PROJECT_NAME`` (default value ``'admin'``)
* ``OS_USERNAME`` (default value ``'admin'``)
* ``OS_PASSWORD`` (default value ``'password'``)
* ``OS_AUTH_URL`` (keystone auth url should be defined explicitly:
  **v3** - ``http://keystone/url/v3``, **v2** - ``http://keystone/url/v2.0``)

To get details look into ``stepler/config.py``

Let's view typical commands to launch test in different ways:

* If you want to launch all tests (``-v`` is used to show full name and status of each test)::

   py.test stepler -v

* For ex, you write the test ``test_upload_image`` and want to launch it only::

   py.test stepler -k test_upload_image

* If your test was failed and you want to debug it, you should disable stdout capture::

   py.test stepler -k test_upload_image -s

* Full information about ``py.test`` is obtainable with::

   py.test -h

------------------
How to debug tests
------------------

We recommend to use ``ipdb`` to set up break points inside code. Just put following chunk before code line where you want to debug (don't forget about ``-s`` to disable  ``py.test`` stdout capture):

.. code:: python

   import ipdb; ipdb.set_trace()

-----------------
Deep to structure
-----------------

.. toctree::
   :maxdepth: 1

   steps_concept
   common_fixtures
   cinder
   baremetal
   glance
   heat
   horizon
   keystone
   neutron
   nova
   os_faults
   third_party
