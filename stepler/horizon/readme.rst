==========
Annotation
==========
This repo contains horizon integration UI tests, which work with dashboard as user. They are based on STEPS-methodology to provide scalable, modular and portable code. And under hood they use `POM <https://github.com/sergeychipiga/pom>`_-microframework, which provide the logic to operate with DOM.

====================
Architectural levels
====================

- ``tests`` - (pytest specific) use steps to work with dashboard
- ``fixtures`` - (pytest specific) provide setup and teardown actions
- ``steps`` - (cross platform) actions over page content
- ``pages`` - declarative description of page structure
- ``POM`` - unified methods to manipulate with pages and UI elements.
- ``selenium`` - low level to manipulate with DOM

==========
How to run
==========
``export DASHBOARD_URL=http://horizon/dashboard/`` - should explain to framework where horizon dashboard is located.

``py.test horizon_autotests -v`` - single-threaded mode to launch tests at display

``VIRTUAL_DISPLAY=1 py.test horizon_autotests -v`` - single-threaded mode to launch tests in virtual frame buffer (headless mode)

``VIRTUAL_DISPLAY=1 py.tests horizon_autotests -v -n 4`` - multi-processed mode to launch tests in virtual frame buffers (create 4 parallel processes to launch tests)

============
Test results
============
After tests finishing there will be a directory ``test_reports`` which contains folders named test names, where there are:

- ``video.mp4`` - video capture of test (can be played with browser player)
- ``remote_connection.log`` - log of selenium webdriver requests to browser
- ``timeit.log`` - log of time execution of steps and UI element actions
- ``test.log`` - log of everything else

==================
How to write tests
==================
In progress...

================
Current coverage
================
In progress...