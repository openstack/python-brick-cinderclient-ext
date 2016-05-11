# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock

from oslotest import base

from brick_cinderclient_ext import client


class TestBrickClient(base.BaseTestCase):
    def setUp(self):
        super(TestBrickClient, self).setUp()
        self.volume_id = '3d96b134-75bd-492b-8372-330455cae38f'
        self.hostname = 'hostname'
        self.client = client.Client()

    @mock.patch('brick_cinderclient_ext.brick_utils.get_my_ip')
    @mock.patch('brick_cinderclient_ext.brick_utils.get_root_helper')
    @mock.patch('os_brick.initiator.connector.get_connector_properties')
    def test_get_connector(self, mock_connector, mock_root_helper,
                           mock_my_ip):
        mock_root_helper.return_value = 'root-helper'
        mock_my_ip.return_value = '1.0.0.0'

        self.client.get_connector()
        mock_connector.assert_called_with('root-helper', '1.0.0.0',
                                          enforce_multipath=False,
                                          multipath=False)

    @mock.patch('brick_cinderclient_ext.brick_utils.get_my_ip')
    @mock.patch('brick_cinderclient_ext.brick_utils.get_root_helper')
    @mock.patch('os_brick.initiator.connector.get_connector_properties')
    def test_get_connector_with_multipath(self, mock_connector,
                                          mock_root_helper, mock_my_ip):
        mock_root_helper.return_value = 'root-helper'
        mock_my_ip.return_value = '1.0.0.0'

        self.client.get_connector(True, True)
        mock_connector.assert_called_with('root-helper', '1.0.0.0',
                                          enforce_multipath=True,
                                          multipath=True)
