# coding: utf-8
#
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

"""One-off jobs for app feedback report models."""

from __future__ import absolute_import # pylint: disable=import-only-modules
from __future__ import unicode_literals # pylint: disable=import-only-modules

import datetime

from core import jobs
from core.domain import app_feedback_report_services
from core.platform import models
import feconf

(app_feedback_report_models,) = models.Registry.import_models([
    models.NAMES.app_feedback_report])


class ScrubAppFeedbackReportsOneOffJob(jobs.BaseMapReduceOneOffJobManager):
    """A reusable one-time job that scrubs reports that have been held in
    storage for over 90 days.
    """

    @classmethod
    def entity_classes_to_map_over(cls):
        return [app_feedback_report_models.AppFeedbackReportModel]

    @staticmethod
    def map(item):
        earliest_date = datetime.date.today() - datetime.timedelta(
            days=feconf.APP_FEEDBACK_REPORT_MAX_NUMBER_OF_DAYS)
        if item.created_on.date() < earliest_date and item.scrubbed_by is None:
            app_feedback_report_services.scrub_report(
                item.id, feconf.REPORT_SCRUBBER_BOT_ID)

    @staticmethod
    def reduce(key, values):
        # Scrubbing occurs in the map() function so that nothing is done in the
        # reduce() function.
        pass
