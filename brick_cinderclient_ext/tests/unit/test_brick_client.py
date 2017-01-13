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

    def _init_fake_cinderclient(self, protocol):
        # Init fake cinderclient
        self.mock_vc = mock.Mock()
        conn_data = {'key': 'value'}
        connection = {'driver_volume_type': protocol, 'data': conn_data}
        self.mock_vc.volumes.initialize_connection.return_value = connection
        mock_vol = mock.Mock()
        mock_vol.id = self.volume_id
        mock_vol.name = 'fake-vol'
        mock_vol.status = 'in-use'
        self.mock_vc.volumes.list.return_value = [mock_vol]
        self.client.volumes_client = self.mock_vc
        return connection

    def _init_fake_os_brick(self, mock_conn_prop):
        # Init fakes for os-brick
        conn_props = mock.Mock()
        mock_conn_prop.return_value = conn_props
        mock_connector = mock.Mock()
        mock_connect = mock.Mock()
        mock_connector.return_value = mock_connect
        self.client._brick_get_connector = mock_connector
        mock_connect.connect_volume = mock.Mock()

        return conn_props, mock_connect

    @mock.patch('oslo_concurrency.processutils.execute')
    @mock.patch('brick_cinderclient_ext.brick_utils.get_my_ip')
    @mock.patch('brick_cinderclient_ext.brick_utils.get_root_helper')
    @mock.patch('os_brick.initiator.connector.get_connector_properties')
    def test_get_connector(self, mock_connector, mock_root_helper,
                           mock_my_ip, mock_execute):
        mock_root_helper.return_value = 'root-helper'
        mock_my_ip.return_value = '1.0.0.0'

        self.client.get_connector()
        mock_connector.assert_called_with('root-helper', '1.0.0.0',
                                          enforce_multipath=False,
                                          multipath=False,
                                          execute=mock_execute)

    @mock.patch('oslo_concurrency.processutils.execute')
    @mock.patch('brick_cinderclient_ext.brick_utils.get_my_ip')
    @mock.patch('brick_cinderclient_ext.brick_utils.get_root_helper')
    @mock.patch('os_brick.initiator.connector.get_connector_properties')
    def test_get_connector_with_multipath(self, mock_connector,
                                          mock_root_helper, mock_my_ip,
                                          mock_execute):
        mock_root_helper.return_value = 'root-helper'
        mock_my_ip.return_value = '1.0.0.0'

        self.client.get_connector(True, True)
        mock_connector.assert_called_with('root-helper', '1.0.0.0',
                                          enforce_multipath=True,
                                          multipath=True,
                                          execute=mock_execute)

    @mock.patch('os_brick.initiator.connector.get_connector_properties')
    def test_attach_iscsi(self, mock_conn_prop):
        connection = self._init_fake_cinderclient('iscsi')
        conn_props, mock_connect = self._init_fake_os_brick(mock_conn_prop)

        self.client.attach(self.volume_id, self.hostname)
        self.mock_vc.volumes.initialize_connection.assert_called_with(
            self.volume_id, conn_props)
        mock_connect.connect_volume.assert_called_with(connection['data'])

    @mock.patch('os_brick.initiator.connector.get_connector_properties')
    def test_detach_iscsi(self, mock_conn_prop):
        connection = self._init_fake_cinderclient('iscsi')
        conn_props, m_connect = self._init_fake_os_brick(mock_conn_prop)

        self.client.detach(self.volume_id)
        self.mock_vc.volumes.initialize_connection.assert_called_with(
            self.volume_id, conn_props)
        m_connect.disconnect_volume.assert_called_with(connection['data'], {})

    @mock.patch('os_brick.initiator.connector.get_connector_properties')
    def test_get_volume_paths(self, mock_conn_prop):
        connection = self._init_fake_cinderclient('iscsi')
        conn_props, m_connect = self._init_fake_os_brick(mock_conn_prop)
        self.client.get_volume_paths(self.volume_id, use_multipath=False)
        self.mock_vc.volumes.initialize_connection.assert_called_with(
            self.volume_id, conn_props)
        self.client._brick_get_connector.assert_called_with(
            connection['driver_volume_type'], use_multipath=False)
        m_connect.get_volume_paths.assert_called_with(connection['data'])

    @mock.patch('os_brick.initiator.connector.get_connector_properties')
    def test_get_all_volume_paths(self, mock_conn_prop):
        protocol = 'iscsi'
        conn_props, m_connect = self._init_fake_os_brick(mock_conn_prop)
        self.client.get_all_volume_paths(protocol, use_multipath=False)
        self.client._brick_get_connector.assert_called_with(
            protocol, use_multipath=False)
        m_connect.get_all_available_volumes.assert_called_with()
