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

from cinderclient import exceptions
from oslotest import base

import brick_cinderclient_ext


class TestBrickClientCLI(base.BaseTestCase):
    def setUp(self):
        super(TestBrickClientCLI, self).setUp()

    @mock.patch('os.getuid')
    def test_get_connector_non_root(self, mock_getuid):
        mock_getuid.return_value = 1
        self.assertRaises(exceptions.CommandError,
                          brick_cinderclient_ext.do_get_connector, None, None)
