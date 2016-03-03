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


"""
Command-line interface to the os-brick.
"""

from __future__ import print_function
import logging

import pbr.version

from brick_cinderclient_ext import brick_utils
from brick_cinderclient_ext import client as brick_client
from cinderclient import utils


__version__ = pbr.version.VersionInfo(
    'brick-python-cinderclient-ext').version_string()


VOLUME_ID_HELP_MESSAGE = 'Name or other Identifier for existing volume'
MULTIPATH_HELP_MESSAGE = ('Set True if connector wants to use multipath.'
                          'Default value is False.')
ENFORCE_MULTIPATH_HELP_MESSAGE = (
    'If enforce_multipath=True is specified too, an exception is thrown when '
    'multipathd is not running. Otherwise, it falls back to multipath=False '
    'and only the first path shown up is used.')

logging.basicConfig()
logger = logging.getLogger(__name__)


@utils.arg('--multipath',
           metavar='<multipath>',
           default=False,
           help=MULTIPATH_HELP_MESSAGE)
@utils.arg('--enforce_multipath',
           metavar='<enforce_multipath>',
           default=False,
           help=ENFORCE_MULTIPATH_HELP_MESSAGE)
@brick_utils.require_root
def do_get_connector(client, args):
    """Get the connection properties for all protocols."""
    brickclient = brick_client.Client(client)
    connector = brickclient.get_connector(args.multipath,
                                          args.enforce_multipath)
    utils.print_dict(connector)


@utils.arg('identifier',
           metavar='<identifier>',
           help=VOLUME_ID_HELP_MESSAGE)
@utils.arg('--multipath',
           metavar='<multipath>',
           default=False,
           help=MULTIPATH_HELP_MESSAGE)
@utils.service_type('volumev2')
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
@utils.service_type('volumev2')
@brick_utils.require_root
def do_get_all_volume_paths(client, args):
    """Get all volume paths for a protocol."""
    brickclient = brick_client.Client(client)

    paths = brickclient.get_all_volume_paths(args.protocol, args.multipath)
    if paths:
        print('\n'.join(paths))

manager_class = brick_client.Client
name = 'brick_local_volume_management'
