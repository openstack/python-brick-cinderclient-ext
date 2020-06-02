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

import cinderclient
from cinderclient import api_versions
from cinderclient import exceptions
from os_brick.initiator import connector
from oslo_utils import uuidutils
from pbr import version as pbr_version

from brick_cinderclient_ext import brick_utils
from brick_cinderclient_ext import volume_actions as actions


class Client(object):
    """Python client for os-brick

    Version history:

        1.0.0 - Initial version
        1.1.0 - Query volume paths implementation
        1.2.0 - Add --nic attribute to get-connector
        1.3.0 - Added new v3 attach/detach workflow support

    """

    version = '1.3.0'

    # Use the legacy attach/detach workflow?
    _use_legacy_attach = True

    def __init__(self, volumes_client=None):
        self.volumes_client = volumes_client

        # Test to see if we have a version of the cinderclient
        # that can do the new volume attach/detach API
        version_want = pbr_version.SemanticVersion(major=2)
        current_version = cinderclient.version_info.semantic_version()
        if (self.volumes_client and current_version >= version_want):
            # We have a recent enough client to test the microversion we need.
            required_version = api_versions.APIVersion("3.44")
            if self.volumes_client.api_version.matches(required_version):
                # we can use the new attach/detach API
                self._use_legacy_attach = False

    def _brick_get_connector(self, protocol, driver=None,
                             execute=None,
                             use_multipath=False,
                             device_scan_attempts=3,
                             *args, **kwargs):
        """Wrapper to get a brick connector object.

        This automatically populates the required protocol as well
        as the root_helper needed to execute commands.
        """
        return connector.InitiatorConnector.factory(
            protocol,
            brick_utils.get_root_helper(),
            driver=driver,
            execute=execute,
            use_multipath=use_multipath,
            device_scan_attempts=device_scan_attempts,
            *args, **kwargs)

    def get_connector(self, multipath=False, enforce_multipath=False,
                      nic=None):
        conn_prop = connector.get_connector_properties(
            brick_utils.get_root_helper(),
            brick_utils.get_ip(nic),
            multipath=multipath,
            enforce_multipath=(enforce_multipath),
            execute=None)
        return conn_prop

    def attach(self, volume_id, hostname, mountpoint=None, mode='rw',
               multipath=False, enforce_multipath=False, nic=None):
        """Main entry point for trying to attach a volume.

        If the cinderclient has a recent version that can do the new attach
        workflow, lets try that.  Otherwise we revert to the older attach
        workflow.
        """
        if self._use_legacy_attach:
            return self._legacy_attach(volume_id, hostname,
                                       mountpoint=mountpoint,
                                       mode=mode, multipath=multipath,
                                       enforce_multipath=enforce_multipath,
                                       nic=nic)
        else:
            return self._attach(volume_id, hostname,
                                mountpoint=mountpoint,
                                mode=mode, multipath=multipath,
                                enforce_multipath=enforce_multipath,
                                nic=nic)

    def _legacy_attach(self, volume_id, hostname, mountpoint=None, mode='rw',
                       multipath=False, enforce_multipath=False, nic=None):
        """The original/legacy attach workflow."""
        # Reserve volume before attachment
        with actions.Reserve(self.volumes_client, volume_id) as cmd:
            cmd.reserve()

        with actions.InitializeConnection(
                self.volumes_client, volume_id) as cmd:
            connection = cmd.initialize(self, multipath, enforce_multipath,
                                        nic)

        with actions.VerifyProtocol(self.volumes_client, volume_id) as cmd:
            cmd.verify(connection['driver_volume_type'])

        with actions.ConnectVolume(self.volumes_client, volume_id) as cmd:
            brick_connector = self._brick_get_connector(
                connection['driver_volume_type'], do_local_attach=True)
            device_info = cmd.connect(brick_connector,
                                      connection['data'],
                                      mountpoint, mode, hostname)
            return device_info

    def _attach(self, volume_id, hostname, mountpoint=None, mode='rw',
                multipath=False, enforce_multipath=False, nic=None):
        """Attempt to use the v3 API for attach workflow.

        If the cinder API microversion is good enough, we will use the new
        attach workflow, otherwise we resort back to the old workflow.
        """
        # We can use the new attach/detach workflow
        connector_properties = self.get_connector(
            multipath=multipath,
            enforce_multipath=enforce_multipath,
            nic=nic
        )

        instance_id = uuidutils.generate_uuid()

        info = self.volumes_client.attachments.create(
            volume_id, connector_properties, instance_id)

        connection = info['connection_info']
        with actions.VerifyProtocol(self.volumes_client, volume_id) as cmd:
            cmd.verify(connection['driver_volume_type'])

        brick_connector = self._brick_get_connector(
            connection['driver_volume_type'],
            do_local_attach=True,
            use_multipath=multipath,
        )
        device_info = brick_connector.connect_volume(connection)
        # MV 3.44 requires this step to move the volume to 'in-use'.
        self.volumes_client.attachments.complete(
            info['connection_info']['attachment_id'])
        return device_info

    def detach(self, volume_id, attachment_uuid=None, multipath=False,
               enforce_multipath=False, device_info=None, nic=None):

        if self._use_legacy_attach:
            self._legacy_detach(volume_id,
                                attachment_uuid=attachment_uuid,
                                multipath=multipath,
                                enforce_multipath=enforce_multipath,
                                device_info=device_info, nic=nic)
        else:
            self._detach(volume_id,
                         attachment_uuid=attachment_uuid,
                         multipath=multipath,
                         enforce_multipath=enforce_multipath,
                         device_info=device_info, nic=nic)

    def _legacy_detach(self, volume_id, attachment_uuid=None, multipath=False,
                       enforce_multipath=False, device_info=None, nic=None):
        """The original/legacy detach workflow."""
        with actions.BeginDetach(self.volumes_client, volume_id) as cmd:
            cmd.reserve()

        with actions.InitializeConnectionForDetach(
                self.volumes_client, volume_id) as cmd:
            connection = cmd.initialize(self, multipath, enforce_multipath,
                                        nic)

        brick_connector = self._brick_get_connector(
            connection['driver_volume_type'],
            do_local_attach=True,
            use_multipath=multipath,
        )

        with actions.DisconnectVolume(self.volumes_client, volume_id) as cmd:
            cmd.disconnect(brick_connector, connection['data'], device_info)

        with actions.DetachVolume(self.volumes_client, volume_id) as cmd:
            cmd.detach(self, attachment_uuid, multipath, enforce_multipath)

    def _detach(self, volume_id, attachment_uuid=None, multipath=False,
                enforce_multipath=False, device_info=None, nic=None):
        if not attachment_uuid:
            # We need the specific attachment uuid to know which one to detach.
            # if None was passed in we can only work if there is one and only
            # one attachment for the volume.
            # Get the list of attachments for the volume.
            search_opts = {'volume_id': volume_id}
            attachments = self.volumes_client.attachments.list(
                search_opts=search_opts)

            if len(attachments) == 0:
                raise exceptions.NoAttachmentsFound(volume_id=volume_id)
            if len(attachments) == 1:
                attachment_uuid = attachments[0].id
            else:
                # We have more than 1 attachment and we don't know which to use
                raise exceptions.NeedAttachmentUUID(volume_id=volume_id)

        attachment = self.volumes_client.attachments.show(attachment_uuid)

        brick_connector = self._brick_get_connector(
            attachment.connection_info['driver_volume_type'],
            do_local_attach=True,
            use_multipath=multipath,
        )

        with actions.DisconnectVolume(self.volumes_client, volume_id) as cmd:
            cmd.disconnect(brick_connector,
                           attachment.connection_info,
                           device_info)

        self.volumes_client.attachments.delete(attachment_uuid)

    def get_volume_paths(self, volume_id, use_multipath=False):
        """Gets volume paths on the system for a specific volume."""
        conn_props = self.get_connector(multipath=use_multipath)
        vols = self.volumes_client.volumes.list()
        vol_in_use = False
        vol_found = False
        for vol in vols:
            if (volume_id == vol.id or volume_id == vol.name):
                vol_found = True
                if vol.status == "in-use":
                    vol_in_use = True
                    # Make sure the volume ID is used and not the name
                    volume_id = vol.id
                break

        if not vol_found:
            msg = "No volume with a name or ID of '%s' exists." % volume_id
            raise exceptions.CommandError(msg)

        paths = []
        if vol_in_use:
            conn_info = self.volumes_client.volumes.initialize_connection(
                volume_id, conn_props)
            protocol = conn_info['driver_volume_type']
            conn = self._brick_get_connector(protocol,
                                             use_multipath=use_multipath)
            paths = conn.get_volume_paths(conn_info['data'])

        return paths

    def get_all_volume_paths(self, protocol, use_multipath=False):
        """Gets all volume paths on the system for a given protocol."""
        conn = self._brick_get_connector(protocol, use_multipath=use_multipath)
        paths = conn.get_all_available_volumes()

        return paths
