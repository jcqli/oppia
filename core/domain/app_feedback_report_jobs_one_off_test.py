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

"""Tests for one-off jobs related to app feedback reports."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

import datetime

from core.domain import app_feedback_report_jobs_one_off
from core.platform import models
from core.tests import test_utils
import feconf

(app_feedback_report_models,) = models.Registry.import_models([
    models.NAMES.app_feedback_report])


class ScrubAppFeedbackReportsOneOffJobTests(test_utils.GenericTestBase):
    PLATFORM_ANDROID = 'android'
    PLATFORM_WEB = 'web'
    # Timestamp in sec since epoch for Dec 28 2020 23:02:16 GMT.
    REPORT_SUBMITTED_TIMESTAMP = datetime.datetime.fromtimestamp(1609196540)
    TIMESTAMP_AT_MAX_DAYS = (
        datetime.datetime.utcnow() - datetime.timedelta(
            days=feconf.APP_FEEDBACK_REPORT_MAX_NUMBER_OF_DAYS))
    TIMESTAMP_OVER_MAX_DAYS = (
        datetime.datetime.utcnow() - datetime.timedelta(
            days=feconf.APP_FEEDBACK_REPORT_MAX_NUMBER_OF_DAYS + 10))
    # Timestamp in sec since epoch for Mar 19 2021 17:10:36 UTC.
    TICKET_CREATION_TIMESTAMP = datetime.datetime.fromtimestamp(1616173836)
    TICKET_ID = '%s.%s.%s' % (
        'random_hash', TICKET_CREATION_TIMESTAMP.second, '16CharString1234')
    USER_ID = 'user_1'
    REPORT_TYPE_SUGGESTION = 'suggestion'
    CATEGORY_OTHER = 'other'
    PLATFORM_VERSION = '0.1-alpha-abcdef1234'
    DEVICE_COUNTRY_LOCALE_CODE_INDIA = 'in'
    ANDROID_DEVICE_MODEL = 'Pixel 4a'
    ANDROID_SDK_VERSION = 22
    ENTRY_POINT_NAVIGATION_DRAWER = 'navigation_drawer'
    TEXT_LANGUAGE_CODE_ENGLISH = 'en'
    AUDIO_LANGUAGE_CODE_ENGLISH = 'en'
    ANDROID_REPORT_INFO = {
        'user_feedback_other_text_input': 'add an admin',
        'event_logs': ['event1', 'event2'],
        'logcat_logs': ['logcat1', 'logcat2'],
        'package_version_code': 1,
        'language_locale_code': 'en',
        'entry_point_info': {
            'entry_point_name': 'crash',
        },
        'text_size': 'MEDIUM_TEXT_SIZE',
        'download_and_update_only_on_wifi': True,
        'automatically_update_topics': False,
        'is_admin': False
    }
    WEB_REPORT_INFO = {
        'user_feedback_other_text_input': 'add an admin'
    }
    ANDROID_REPORT_INFO_SCHEMA_VERSION = 1
    WEB_REPORT_INFO_SCHEMA_VERSION = 1

    REPORT_ID_AT_MAX_DAYS = '%s.%s.%s' % (
        PLATFORM_ANDROID, REPORT_SUBMITTED_TIMESTAMP.second,
        'AtMaxDaysxxx')
    SCRUBBED_REPORT_ID= '%s.%s.%s' % (
        PLATFORM_ANDROID, REPORT_SUBMITTED_TIMESTAMP.second,
        'ScrubbedDone')
    ANDROID_REPORT_ID_OVER_MAX_DAYS = '%s.%s.%s' % (
        PLATFORM_ANDROID, REPORT_SUBMITTED_TIMESTAMP.second,
        'OverMaxDaysx')
    WEB_REPORT_ID_OVER_MAX_DAYS = '%s.%s.%s' % (
        PLATFORM_WEB, REPORT_SUBMITTED_TIMESTAMP.second,
        'OverMaxDaysx')
    
    def setUp(self):
        super(ScrubAppFeedbackReportsOneOffJobTests, self).setUp()
        self.job_class = (
            app_feedback_report_jobs_one_off.ScrubAppFeedbackReportsOneOffJob)

    def test_job_reduce_passes_with_no_op(self):
        self.assertIsNone(self.job_class.reduce('key', 'values'))

    def test_job_on_current_and_expired_reports_only_scrubs_expired(self):
        self._add_current_reports()
        self._add_expiring_android_report()
        self._run_one_off_job()

        scrubbed_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.ANDROID_REPORT_ID_OVER_MAX_DAYS))
        current_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.REPORT_ID_AT_MAX_DAYS))

        self._verify_report_is_scrubbed(
            scrubbed_model, feconf.APP_FEEDBACK_REPORT_SCRUBBER_BOT_ID)
        self._verify_report_is_not_scrubbed(current_model)

    def test_job_with_no_reports_in_storage_does_not_scrub_storage(self):
        current_models_query = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_all())
        current_models = current_models_query.fetch()
        self.assertEqual(len(current_models), 0)
        self._run_one_off_job()

        stored_models_query = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_all())
        stored_models = stored_models_query.fetch()
        self.assertEqual(len(stored_models), 0)

    def test_job_on_no_models_does_not_scrub_models(self):
        self._add_current_reports()
        self._run_one_off_job()

        current_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.REPORT_ID_AT_MAX_DAYS))
        self._verify_report_is_not_scrubbed(current_model)

    def test_job_on_all_expired_models_updates_all_models(self):
        self._add_expiring_android_report()
        self._add_expiring_web_report()
        self._run_one_off_job()

        android_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.ANDROID_REPORT_ID_OVER_MAX_DAYS))
        web_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.WEB_REPORT_ID_OVER_MAX_DAYS))

        self._verify_report_is_scrubbed(
            android_model, feconf.APP_FEEDBACK_REPORT_SCRUBBER_BOT_ID)
        self._verify_report_is_scrubbed(
            web_model, feconf.APP_FEEDBACK_REPORT_SCRUBBER_BOT_ID)

    def test_job_on_already_scrubbed_models_does_not_scrub_models(self):
        self._add_scrubbed_report()
        self._run_one_off_job()

        scrubbed_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.SCRUBBED_REPORT_ID))

        self._verify_report_is_scrubbed(scrubbed_model, 'scrubber_user')

    def test_job_runs_again_scrubs_newly_added_expired_models(self):
        self._add_expiring_android_report()
        self._run_one_off_job()
        scrubbed_android_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.ANDROID_REPORT_ID_OVER_MAX_DAYS))
        self._verify_report_is_scrubbed(
            scrubbed_android_model, feconf.APP_FEEDBACK_REPORT_SCRUBBER_BOT_ID)

        self._add_expiring_web_report()
        self._run_one_off_job()

        scrubbed_web_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.WEB_REPORT_ID_OVER_MAX_DAYS))
        self._verify_report_is_scrubbed(
            scrubbed_web_model, feconf.APP_FEEDBACK_REPORT_SCRUBBER_BOT_ID)
        # Check that the originally-scrubbed model is still valid.
        self._verify_report_is_scrubbed(
            scrubbed_android_model, feconf.APP_FEEDBACK_REPORT_SCRUBBER_BOT_ID)

    def _run_one_off_job(self):
        # Helper function to create, enqueue, and process a new job instance.
        job_id = self.job_class.create_new()
        self.job_class.enqueue(job_id)
        self.process_and_flush_pending_mapreduce_tasks()

        output = self.job_class.get_output(job_id)
        self.assertEqual(output, [])

    def _verify_report_is_scrubbed(self, model_entity, scrubber):
        self.assertIsNotNone(model_entity)
        self.assertEqual(
            model_entity.scrubbed_by, scrubber)

    def _verify_report_is_not_scrubbed(self, model_entity):
        self.assertIsNotNone(model_entity)
        self.assertIsNone(model_entity.scrubbed_by)

    def _add_current_reports(self):
        """Adds reports to the model that should not be scrubbed."""
        current_feedback_report_model = (
            app_feedback_report_models.AppFeedbackReportModel(
                id=self.REPORT_ID_AT_MAX_DAYS,
                platform=self.PLATFORM_ANDROID,
                ticket_id='%s.%s.%s' % (
                    'random_hash', self.TICKET_CREATION_TIMESTAMP.second,
                    '16CharString1234'),
                submitted_on=self.REPORT_SUBMITTED_TIMESTAMP,
                report_type=self.REPORT_TYPE_SUGGESTION,
                category=self.CATEGORY_OTHER,
                platform_version=self.PLATFORM_VERSION,
                android_device_country_locale_code=(
                    self.DEVICE_COUNTRY_LOCALE_CODE_INDIA),
                android_device_model=self.ANDROID_DEVICE_MODEL,
                android_sdk_version=self.ANDROID_SDK_VERSION,
                entry_point=self.ENTRY_POINT_NAVIGATION_DRAWER,
                text_language_code=self.TEXT_LANGUAGE_CODE_ENGLISH,
                audio_language_code=self.AUDIO_LANGUAGE_CODE_ENGLISH,
                android_report_info=self.ANDROID_REPORT_INFO,
                android_report_info_schema_version=(
                    self.ANDROID_REPORT_INFO_SCHEMA_VERSION)))
        current_feedback_report_model.created_on = self.TIMESTAMP_AT_MAX_DAYS
        current_feedback_report_model.put()

    def _add_expiring_android_report(self):
        """Adds reports to the model that should be scrubbed."""
        expiring_android_report_model = (
            app_feedback_report_models.AppFeedbackReportModel(
                id=self.ANDROID_REPORT_ID_OVER_MAX_DAYS,
                platform=self.PLATFORM_ANDROID,
                ticket_id='%s.%s.%s' % (
                    'random_hash', self.TICKET_CREATION_TIMESTAMP.second,
                    '16CharString1234'),
                submitted_on=self.REPORT_SUBMITTED_TIMESTAMP,
                report_type=self.REPORT_TYPE_SUGGESTION,
                category=self.CATEGORY_OTHER,
                platform_version=self.PLATFORM_VERSION,
                android_device_country_locale_code=(
                    self.DEVICE_COUNTRY_LOCALE_CODE_INDIA),
                android_device_model=self.ANDROID_DEVICE_MODEL,
                android_sdk_version=self.ANDROID_SDK_VERSION,
                entry_point=self.ENTRY_POINT_NAVIGATION_DRAWER,
                text_language_code=self.TEXT_LANGUAGE_CODE_ENGLISH,
                audio_language_code=self.AUDIO_LANGUAGE_CODE_ENGLISH,
                android_report_info=self.ANDROID_REPORT_INFO,
                android_report_info_schema_version=(
                    self.ANDROID_REPORT_INFO_SCHEMA_VERSION)))
        expiring_android_report_model.created_on = self.TIMESTAMP_OVER_MAX_DAYS
        expiring_android_report_model.put()

    def _add_expiring_web_report(self):
        expiring_web_report_model = (
            app_feedback_report_models.AppFeedbackReportModel(
                id=self.WEB_REPORT_ID_OVER_MAX_DAYS,
                platform=self.PLATFORM_WEB,
                ticket_id='%s.%s.%s' % (
                    'random_hash', self.TICKET_CREATION_TIMESTAMP.second,
                    '16CharString1234'),
                submitted_on=self.REPORT_SUBMITTED_TIMESTAMP,
                report_type=self.REPORT_TYPE_SUGGESTION,
                category=self.CATEGORY_OTHER,
                platform_version=self.PLATFORM_VERSION,
                android_device_country_locale_code=(
                    self.DEVICE_COUNTRY_LOCALE_CODE_INDIA),
                android_device_model=self.ANDROID_DEVICE_MODEL,
                android_sdk_version=self.ANDROID_SDK_VERSION,
                entry_point=self.ENTRY_POINT_NAVIGATION_DRAWER,
                text_language_code=self.TEXT_LANGUAGE_CODE_ENGLISH,
                audio_language_code=self.AUDIO_LANGUAGE_CODE_ENGLISH,
                web_report_info=self.WEB_REPORT_INFO,
                web_report_info_schema_version=(
                    self.WEB_REPORT_INFO_SCHEMA_VERSION)))
        expiring_web_report_model.created_on = self.TIMESTAMP_OVER_MAX_DAYS
        expiring_web_report_model.put()

    def _add_scrubbed_report(self):
        """Add an already-scrubbed report to the model."""
        expiring_android_report_model = (
            app_feedback_report_models.AppFeedbackReportModel(
                id=self.SCRUBBED_REPORT_ID,
                platform=self.PLATFORM_ANDROID,
                scrubbed_by='scrubber_user',
                ticket_id='%s.%s.%s' % (
                    'random_hash', self.TICKET_CREATION_TIMESTAMP.second,
                    '16CharString1234'),
                submitted_on=self.REPORT_SUBMITTED_TIMESTAMP,
                report_type=self.REPORT_TYPE_SUGGESTION,
                category=self.CATEGORY_OTHER,
                platform_version=self.PLATFORM_VERSION,
                android_device_country_locale_code=(
                    self.DEVICE_COUNTRY_LOCALE_CODE_INDIA),
                android_device_model=self.ANDROID_DEVICE_MODEL,
                android_sdk_version=self.ANDROID_SDK_VERSION,
                entry_point=self.ENTRY_POINT_NAVIGATION_DRAWER,
                text_language_code=self.TEXT_LANGUAGE_CODE_ENGLISH,
                audio_language_code=self.AUDIO_LANGUAGE_CODE_ENGLISH,
                android_report_info=self.ANDROID_REPORT_INFO,
                android_report_info_schema_version=(
                    self.ANDROID_REPORT_INFO_SCHEMA_VERSION)))
        expiring_android_report_model.created_on = self.TIMESTAMP_OVER_MAX_DAYS
        expiring_android_report_model.put()
