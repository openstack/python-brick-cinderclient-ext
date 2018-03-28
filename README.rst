========================
Team and repository tags
========================

.. image:: https://governance.openstack.org/tc/badges/python-brick-cinderclient-ext.svg
    :target: https://governance.openstack.org/tc/reference/tags/index.html

.. Change things from this point on

=============================
python-brick-cinderclient-ext
=============================

OpenStack Cinder Brick client for local volume attachement

Features
--------

* Get volume connector information


Dependencies
------------

Requires dependency::

* python-cinderclient

Optional dependencies based on Cinder driver's protocol::

* open-iscsi, udev - for volume attachment via iSCSI

NOTE (e0ne): current version is tested only on Linux hosts

For any other information, refer to the parent projects, Cinder and
python-cinderclient::

*  https://git.openstack.org/cgit/openstack/cinder
*  https://git.openstack.org/cgit/openstack/python-cinderclient

* License: Apache License, Version 2.0
* Documentation: https://docs.openstack.org/python-brick-cinderclient-ext/latest/
* Source: https://git.openstack.org/cgit/openstack/python-brick-cinderclient-ext
* Bugs: https://bugs.launchpad.net/python-cinderclient
