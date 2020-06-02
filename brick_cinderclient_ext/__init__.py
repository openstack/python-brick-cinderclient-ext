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


"""Command-line interface to the os-brick."""

import json
import socket

from cinderclient import utils
import pbr.version

from brick_cinderclient_ext import brick_utils
from brick_cinderclient_ext import client as brick_client


__version__ = pbr.version.VersionInfo(
    'python-brick-cinderclient-ext').version_string()


VOLUME_ID_HELP_MESSAGE = 'Name or other Identifier for existing volume'
MULTIPATH_HELP_MESSAGE = ('Set True if connector wants to use multipath.'
                          'Default value is False.')
ENFORCE_MULTIPATH_HELP_MESSAGE = (
    'If enforce_multipath=True is specified too, an exception is thrown when '
    'multipathd is not running. Otherwise, it falls back to multipath=False '
    'and only the first path shown up is used.')
NETWORK_INTERFACE_HELP_MESSAGE = ('Use a specific network interface to '
                                  'determine IP address.')
LOCAL_ATTACH_NIC_HELP_MESSAGE = ('Use a specific network interface for '
                                 'connector during attach operation.')


@utils.arg('--multipath',
           metavar='<multipath>',
           default=False,
           help=MULTIPATH_HELP_MESSAGE)
@utils.arg('--enforce_multipath',
           metavar='<enforce_multipath>',
           default=False,
           help=ENFORCE_MULTIPATH_HELP_MESSAGE)
@utils.arg('--nic',
           metavar='<nic>',
           default=None,
           help=NETWORK_INTERFACE_HELP_MESSAGE)
@brick_utils.require_root
def do_get_connector(client, args):
    """Get the connection properties for all protocols."""
    brickclient = brick_client.Client(client)
    connector = brickclient.get_connector(args.multipath,
                                          args.enforce_multipath,
                                          args.nic)
    utils.print_dict(connector)


@utils.arg('identifier',
           metavar='<identifier>',
           help=VOLUME_ID_HELP_MESSAGE)
@utils.arg('--hostname',
           metavar='<hostname>',
           default=socket.gethostname(),
           help='hostname')
@utils.arg('--mountpoint',
           metavar='<mountpoint>',
           default=None,
           help='mountpoint')
@utils.arg('--mode',
           metavar='<mode>',
           default='rw',
           help='mode')
@utils.arg('--multipath',
           metavar='<multipath>',
           default=False,
           help=MULTIPATH_HELP_MESSAGE)
@utils.arg('--enforce_multipath',
           metavar='<enforce_multipath>',
           default=False,
           help=ENFORCE_MULTIPATH_HELP_MESSAGE)
@utils.arg('--nic',
           metavar='<nic>',
           default=None,
           help=LOCAL_ATTACH_NIC_HELP_MESSAGE)
@brick_utils.require_root
def do_local_attach(client, args):
    hostname = args.hostname
    volume = args.identifier
    brickclient = brick_client.Client(client)
    device_info = brickclient.attach(volume,
                                     hostname,
                                     args.mountpoint,
                                     args.mode,
                                     args.multipath,
                                     args.enforce_multipath,
                                     args.nic)
    utils.print_dict(device_info)


@utils.arg('identifier',
           metavar='<identifier>',
           help=VOLUME_ID_HELP_MESSAGE)
@utils.arg('--attachment_uuid',
           metavar='<attachment_uuid>',
           default=None,
           help='The uuid of the volume attachment.')
@utils.arg('--multipath',
           metavar='<multipath>',
           default=False,
           help=MULTIPATH_HELP_MESSAGE)
@utils.arg('--enforce_multipath',
           metavar='<enforce_multipath>',
           default=False,
           help=ENFORCE_MULTIPATH_HELP_MESSAGE)
@utils.arg('--device_info',
           metavar='<device_info>',
           default=None,
           help='The device_info is returned from connect_volume.')
@brick_utils.require_root
def do_local_detach(client, args):
    volume = args.identifier
    brickclient = brick_client.Client(client)
    device_info = None
    if args.device_info:
        device_info = json.loads(args.device_info)

    brickclient.detach(volume, args.attachment_uuid, args.multipath,
                       args.enforce_multipath, device_info)


@utils.arg('identifier',
           metavar='<identifier>',
           help=VOLUME_ID_HELP_MESSAGE)
@utils.arg('--multipath',
           metavar='<multipath>',
           default=False,
           help=MULTIPATH_HELP_MESSAGE)
@brick_utils.require_root
def do_get_volume_paths(client, args):
    """Get volume paths for a volume."""
    volume = args.identifier
    brickclient = brick_client.Client(client)

    paths = brickclient.get_volume_paths(volume, args.multipath)
    if paths:
        print('\n'.join(paths))


@utils.arg('--multipath',
           metavar='<multipath>',
           default=False,
           help=MULTIPATH_HELP_MESSAGE)
@utils.arg('--protocol',
           metavar='<protocol>',
           default='ISCSI',
           help='Connection protocol. ISCSI, FIBRE_CHANNEL, etc.')
@brick_utils.require_root
def do_get_all_volume_paths(client, args):
    """Get all volume paths for a protocol."""
    brickclient = brick_client.Client(client)

    paths = brickclient.get_all_volume_paths(args.protocol, args.multipath)
    if paths:
        print('\n'.join(paths))


manager_class = brick_client.Client
name = 'brick_local_volume_management'
