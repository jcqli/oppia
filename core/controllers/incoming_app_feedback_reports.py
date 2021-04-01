# Copyright 2021 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Controllers for the incoming app feedback reports."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

from core.controllers import acl_decorators
from core.controllers import base
from core.domain import app_feedback_report_domain
from core.domain import app_feedback_report_services

import feconf


class IncomingAndroidFeedbackReportsHandler(base.BaseHandler):
    """Handles incoming feedback reports from the Android app."""

    @acl_decorators.open_access
    def post(self):
        """Handles POST requests.

        Verifies the incoming message based on the request header and stores
        the feedback report.
        """
        if not self._validate_incoming_request(self.request.headers):
            pass

        request_body = json.loads(self.request.body)
        self.values.update({
            'feedback_thread_dicts': (
                [t.to_dict() for t in feedback_services.get_all_threads(
                    feconf.ENTITY_TYPE_EXPLORATION, exploration_id, False)]),
            'suggestion_thread_dicts': (
                [t.to_dict() for t in feedback_services.get_all_threads(
                    feconf.ENTITY_TYPE_EXPLORATION, exploration_id, True)])
        })
        self.render_json(self.values)

    def _validate_incoming_request(self, headers):
        api_key = headers['api_key']
        app_package_name = headers['app_package_name']
        app_version_name = headers['app_version_name']
        app_version_code = headers['app_version_code']
        if api_key != feconf.ANDROID_API_KEY or (
            app_package_name != feconf.ANDROID_APP_PACKAGE_NAME or (
                app_version_name != feconf.ANDROID_APP_PACKAGE_NAME or (
                    app_version_code != feconf.ANDROID_APP_VERSION_CODE))):
            return False
        return True

