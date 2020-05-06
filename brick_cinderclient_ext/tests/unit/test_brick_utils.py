# Copyright 2017 Mirantis.Inc
#
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

from unittest import mock

import ddt

import netifaces
from oslotest import base

from brick_cinderclient_ext import brick_utils
from brick_cinderclient_ext import exceptions as exc


@ddt.ddt
class TestBrickUtils(base.BaseTestCase):
    @mock.patch('netifaces.ifaddresses',
                return_value={netifaces.AF_INET: [{'addr': '127.0.0.1'}]})
    @mock.patch('netifaces.interfaces', return_value=['eth1'])
    @mock.patch('brick_cinderclient_ext.brick_utils.get_my_ip',
                return_value='1.0.0.0')
    @ddt.data((None, '1.0.0.0'),
              ('eth1', '127.0.0.1'))
    @ddt.unpack
    def test_get_ip(self, nic, expected,
                    _fake_my_ip, _fake_interfaces,
                    _fake_ifaddresses):
        """Test getting ip address using interface name.

        Test cases:
            1. Getting address from existing interface;
            2. Getting default value when network-iface param is missing;
        """
        self.assertEqual(expected, brick_utils.get_ip(nic))

    @mock.patch('netifaces.interfaces', return_value=[])
    def test_get_ip_failed_interface(self, _fake_interfaces):
        """Test getting ip from nonexistent interface."""
        nic = 'fake_nic'
        self.assertRaises(exc.NicNotFound, brick_utils.get_ip,
                          nic)

    @mock.patch('netifaces.ifaddresses', return_value={})
    @mock.patch('netifaces.interfaces', return_value=['without_addr'])
    def test_get_ip_non_addr_in_iface(self, _fake_interfaces,
                                      _fake_ifaddresses):
        """Test getting ip using nic that doesn't have ipv4 address."""
        nic = 'without_addr'
        self.assertRaises(exc.IncorrectNic, brick_utils.get_ip, nic)
