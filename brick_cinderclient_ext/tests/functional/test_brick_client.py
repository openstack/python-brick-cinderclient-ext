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

import configparser
import os

from cinderclient import client as c_client
from oslotest import base


from brick_cinderclient_ext import client


_CREDS_FILE = 'functional_creds.conf'


def credentials():
    """Retrieves credentials to run functional tests

    Credentials are either read from the environment or from a config file
    ('functional_creds.conf'). Environment variables override those from the
    config file.

    The 'functional_creds.conf' file is the clean and new way to use (by
    default tox 2.0 does not pass environment variables).
    """

    username = os.environ.get('OS_USERNAME')
    password = os.environ.get('OS_PASSWORD')
    tenant_name = os.environ.get('OS_TENANT_NAME')
    auth_url = os.environ.get('OS_AUTH_URL')

    config = configparser.RawConfigParser()
    if config.read(_CREDS_FILE):
        username = username or config.get('admin', 'user')
        password = password or config.get('admin', 'pass')
        tenant_name = tenant_name or config.get('admin', 'tenant_name')
        auth_url = auth_url or config.get('auth', 'uri')

    return {
        'username': username,
        'password': password,
        'tenant_name': tenant_name,
        'uri': auth_url
    }


class BrickClientTests(base.BaseTestCase):
    def setUp(self):
        super(BrickClientTests, self).setUp()
        creds = credentials()
        self.cinder_client = c_client.Client(3,
                                             creds['username'],
                                             creds['password'],
                                             creds['tenant_name'],
                                             creds['uri'])

        self.client = client.Client(self.cinder_client)

    def test_get_connector(self):
        connector = self.client.get_connector()
        for prop in ['ip', 'host', 'multipath', 'platform', 'os_type']:
            self.assertIn(prop, connector)
