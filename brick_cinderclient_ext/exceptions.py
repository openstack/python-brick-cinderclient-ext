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

"""
Exception definitions.
"""
from cinderclient._i18n import _


class BrickInterfaceException(Exception):
    """Base exception for brick-cinderclient."""
    message = _("An unknown exception occurred.")

    def __init__(self, message=None, **kwargs):
        if message:
            self.message = message
        self.message = self.message % kwargs

    def __str__(self):
        return self.message


class NicNotFound(BrickInterfaceException):
    message = _("Could not find network interface %(iface)s.")


class IncorrectNic(BrickInterfaceException):
    # TODO(mdovgal): change message after adding ipv6 support
    message = _("Network interface %(iface)s has not ipv4 address assigned.")


class NoAttachmentsFound(BrickInterfaceException):
    message = _("There were no attachments found for %(volume_id)s")


class NeedAttachmentUUID(BrickInterfaceException):
    message = _("Volume %(volume_id)s has more than one attachment. "
                "Please pass in the attachment_uuid you wish to detach.")
