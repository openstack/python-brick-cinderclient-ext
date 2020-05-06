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

from unittest import mock

import ddt
import netifaces

from cinderclient import exceptions as cinder_exceptions
from os_brick import exception
from oslotest import base

from brick_cinderclient_ext import volume_actions


@ddt.ddt
class TestVolumeActions(base.BaseTestCase):
    def setUp(self):
        super(TestVolumeActions, self).setUp()
        self.volume_id = '3d96b134-75bd-492b-8372-330455cae38f'
        self.brick_client = mock.Mock()
        self.v_client = mock.Mock()
        self.command_args = [self.v_client, self.volume_id]

    def test_reserve(self):
        with volume_actions.Reserve(*self.command_args) as cmd:
            cmd.reserve()

        self.v_client.volumes.reserve.assert_called_once_with(self.volume_id)

    def test_reserve_failed(self):
        self.v_client.volumes.reserve.side_effect = (
            cinder_exceptions.BadRequest(400))
        try:
            with volume_actions.Reserve(*self.command_args) as cmd:
                cmd.reserve()
        except cinder_exceptions.BadRequest:
            self.v_client.volumes.unreserve.assert_called_once_with(
                self.volume_id)

        self.v_client.volumes.reserve.assert_called_once_with(self.volume_id)

    @mock.patch('netifaces.ifaddresses',
                return_value={netifaces.AF_INET: [{'addr': '127.0.0.1'}]})
    @mock.patch('netifaces.interfaces', return_value=['eth1'])
    @mock.patch('brick_cinderclient_ext.brick_utils.get_my_ip',
                return_value='1.0.0.0')
    @ddt.data((None,  {'ip': '1.0.0.0'}),
              ('eth1', {'ip': '127.0.0.1'}))
    @ddt.unpack
    def test_initialize_connection(self, _nic, _conn_prop,
                                   _fake_my_ip, _fake_interfaces,
                                   _fake_ifaddresses):
        """Test calling initialize_connection with different input params.

        Contains next initialize connection test cases:
        1. Without any additional parameters in request;
        2. Using --nic as a parameter;
        TODO (mdovgal): add other test cases;
        """
        self.brick_client.get_connector.return_value = _conn_prop
        with volume_actions.InitializeConnection(*self.command_args) as cmd:
            cmd.initialize(self.brick_client, False, False, _nic)

        self.brick_client.get_connector.assert_called_once_with(False, False,
                                                                _nic)
        self.v_client.volumes.initialize_connection.assert_called_once_with(
            self.volume_id, _conn_prop)

    @ddt.data('iscsi', 'iSCSI', 'ISCSI', 'rbd', 'RBD')
    def test_verify_protocol(self, protocol):
        with volume_actions.VerifyProtocol(*self.command_args) as cmd:
            # NOTE(e0ne): veryfy that no exception is rased
            cmd.verify(protocol)

    def test_verify_protocol_failed(self):
        try:
            with volume_actions.VerifyProtocol(*self.command_args) as cmd:
                cmd.verify('protocol')
        except exception.ProtocolNotSupported:
            self.v_client.volumes.unreserve.assert_called_once_with(
                self.volume_id)

    def test_connect_volume(self):
        connector = mock.Mock()
        connector.connect_volume.return_value = {'device': 'info'}
        with volume_actions.ConnectVolume(*self.command_args) as cmd:
            cmd.connect(connector,
                        'connection_data', 'mountpoint', 'mode', 'hostname')

        connector.connect_volume.assert_called_once_with('connection_data')
        self.v_client.volumes.attach.assert_called_once_with(
            self.volume_id,
            instance_uuid=None, mountpoint='mountpoint', mode='mode',
            host_name='hostname')

    @ddt.data((None, {}), ('connection_data', 'connection_data'))
    @ddt.unpack
    def test_disconnect_no_device_info(self, command_arg, connector_arg):
        connector = mock.Mock()
        with volume_actions.DisconnectVolume(*self.command_args) as cmd:
            cmd.disconnect(connector, 'connection_data', command_arg)

        connector.disconnect_volume.assert_called_once_with('connection_data',
                                                            connector_arg)

    def test_detach(self):
        brick_client = mock.Mock()
        brick_client.get_connector.return_value = 'connector'
        with volume_actions.DetachVolume(*self.command_args) as cmd:
            cmd.detach(brick_client, 'attachment_uuid',
                       'multipath', 'enforce_multipath')

        brick_client.get_connector.assert_called_once_with('multipath',
                                                           'enforce_multipath')
        self.v_client.volumes.terminate_connection.assert_called_once_with(
            self.volume_id, 'connector')
        self.v_client.volumes.detach.assert_called_once_with(
            self.volume_id, 'attachment_uuid')
