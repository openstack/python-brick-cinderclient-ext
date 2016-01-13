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

* open-iscsi - for volume attachment via iSCSI
* ceph-common - for volume attachment via iSCSI (Ceph)
* nfs-common - for volume attachment using NFS protocol

For any other information, refer to the parent projects, Cinder and
python-cinderclient::

*  https://git.openstack.org/cgit/openstack/cinder
*  https://git.openstack.org/cgit/openstack/python-cinderclient

* License: Apache License, Version 2.0
* Documentation: http://docs.openstack.org/developer/python-brick-cinderclient-ext
* Source: http://git.openstack.org/cgit/openstack/python-brick-cinderclient-ext
* Bugs: http://bugs.launchpad.net/python-cinderclient
