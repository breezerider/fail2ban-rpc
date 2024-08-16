========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|

    * - build
      - |github-actions| |codecov|

    * - package
      - | |license| |version| |wheel| |supported-versions|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/fail2ban-rpc/badge/?style=flat
    :target: https://fail2ban-rpc.readthedocs.io/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/breezerider/fail2ban-rpc/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/breezerider/fail2ban-rpc/actions

.. |codecov| image:: https://codecov.io/gh/breezerider/fail2ban-rpc/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://app.codecov.io/github/breezerider/fail2ban-rpc

.. |license| image:: https://img.shields.io/badge/license-BSD-green?style=flat
    :alt: PyPI Package license
    :target: https://test.pypi.org/project/fail2ban-rpc

.. |version| image:: https://img.shields.io/badge/test.pypi-v0.0.0-informational?style=flat
    :alt: PyPI Package latest release
    :target: https://test.pypi.org/project/fail2ban-rpc

.. |wheel| image:: https://img.shields.io/badge/wheel-yes-success?style=flat
    :alt: PyPI Wheel
    :target: https://test.pypi.org/project/fail2ban-rpc

.. |supported-versions| image:: https://img.shields.io/badge/python-3.8_|_3.9_|_3.10|_3.11-informational?style=flat
    :alt: Supported Python versions
    :target: https://test.pypi.org/project/fail2ban-rpc

.. |commits-since| image:: https://img.shields.io/github/commits-since/breezerider/fail2ban-rpc/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/breezerider/fail2ban-rpc/compare/v0.0.0...main

.. end-badges

RPC forwarder for fail2ban client to run a specific command on a remote server.
Package is comprised of two parts:

* a server part that is run as a daemon on the remote machine and performs the call to fail2ban client using arguments provided with the input message from the RPC client;
* an RPC client to be called with same arguments as the local fail2ban client.

It depends on other common packages:

* python-daemon
.. * fail2ban
.. * pyzmq
* click

Installation
============

Get latest released version from `PyPI <https://pypi.org/>`_::

    pip install fail2ban-rpc

You can also install the in-development version with::

    pip install https://github.com/breezerider/fail2ban-rpc/archive/main.zip


Documentation
=============


https://fail2ban-rpc.readthedocs.io/


License
=======

- Source code: `BSD-3-Clause <https://choosealicense.com/licenses/bsd-3-clause/>`_ license unless noted otherwise in individual files/directories
- Documentation: `Creative Commons Attribution-ShareAlike 4.0 <https://creativecommons.org/licenses/by-sa/4.0/>`_ license


Development
===========

To run all the tests issue this command in a terminal::

    tox
