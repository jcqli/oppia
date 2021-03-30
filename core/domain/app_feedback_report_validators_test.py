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

"""Tests for app feedback report validators."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

import datetime

from core.domain import prod_validation_jobs_one_off as prod_validation_jobs
from core.platform import models
from core.tests import test_utils
import feconf

datastore_services = models.Registry.import_datastore_services()

(app_feedback_report_models,) = models.Registry.import_models([
    models.NAMES.app_feedback_report])

# Timestamp in sec since epoch for Mar 1 2021 12:00:00 UTC.
EARLIEST_VALID_DATETIME = datetime.datetime.fromtimestamp(1614556800)


class AppFeedbackReportModelValidatorTests(test_utils.AuditJobsTestBase):

    USER_1_EMAIL = 'some@email.com'
    USER_1_USERNAME = 'username1'
    # The timestamp in sec since epoch for Mar 7 2021 21:17:16 UTC.
    REPORT_SUBMITTED_TIMESTAMP = datetime.datetime.fromtimestamp(1615151836)
    # The timestamp in sec since epoch for Mar 19 2021 17:10:36 UTC.
    TICKET_CREATION_TIMESTAMP = datetime.datetime.fromtimestamp(1616173836)

    PLATFORM_ANDROID = 'android'
    PLATFORM_WEB = 'web'
    TICKET_ID = '%s.%s.%s' % (
        'random_hash', TICKET_CREATION_TIMESTAMP.second, '16CharString1234')
    REPORT_TYPE_SUGGESTION = 'suggestion'
    CATEGORY_OTHER = 'other'
    PLATFORM_VERSION = '0.1-alpha-abcdef1234'
    COUNTRY_LOCALE_CODE_INDIA = 'in'
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
    ANDROID_REPORT_INFO_SCHEMA_VERSION = 1

    def setUp(self):
        super(AppFeedbackReportModelValidatorTests, self).setUp()
        self.signup(self.USER_1_EMAIL, self.USER_1_USERNAME)
        self.user_1_id = self.get_user_id_from_email(self.USER_1_EMAIL)
        self.report_id = (
            app_feedback_report_models.AppFeedbackReportModel.create(
                platform=self.PLATFORM_ANDROID,
                submitted_on=self.REPORT_SUBMITTED_TIMESTAMP,
                report_type=self.REPORT_TYPE_SUGGESTION,
                category=self.CATEGORY_OTHER,
                platform_version=self.PLATFORM_VERSION,
                device_country_locale_code=self.COUNTRY_LOCALE_CODE_INDIA,
                android_sdk_version=self.ANDROID_SDK_VERSION,
                android_device_model=self.ANDROID_DEVICE_MODEL,
                entry_point=self.ENTRY_POINT_NAVIGATION_DRAWER,
                entry_point_topic_id=None,
                entry_point_story_id=None,
                entry_point_exploration_id=None,
                entry_point_subtopic_id=None,
                text_language_code=self.TEXT_LANGUAGE_CODE_ENGLISH,
                audio_language_code=self.AUDIO_LANGUAGE_CODE_ENGLISH,
                android_report_info=self.ANDROID_REPORT_INFO,
                web_report_info=None))

        self.expected_output = [
            u'[u\'fully-validated AppFeedbackReportModel\', 1]']
        self.job_class = (
            prod_validation_jobs.AppFeedbackReportModelAuditOneOffJob)

    def test_standard_model(self):
        self.run_job_and_check_output(
            self.expected_output, sort=False, literal_eval=False)

    def test_model_validation_with_valid_external_references(self):
        model_entity = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.report_id))
        model_entity.ticket_id = self.TICKET_ID
        model_entity.update_timestamps()
        model_entity.put()
        app_feedback_report_models.AppFeedbackReportTicketModel(
            id=self.TICKET_ID, ticket_name='example ticket',
            github_issue_number=None, archived=False,
            newest_report_timestamp=self.REPORT_SUBMITTED_TIMESTAMP,
            report_ids=[self.report_id]).put()

        self.run_job_and_check_output(
            self.expected_output, sort=False, literal_eval=False)

    def test_model_validation_with_invalid_external_references(self):
        model_entity = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.report_id))
        model_entity.ticket_id = 'invalid_ticket_id'
        model_entity.update_timestamps()
        model_entity.put()
        output = [
            (
                u'[u\'failed validation check for ticket_id field check of '
                'AppFeedbackReportModel\', '
                '[u"Entity id %s: based on field ticket_id having value '
                'invalid_ticket_id, expected model AppFeedbackReportTicketModel'
                ' with id invalid_ticket_id but it doesn\'t exist"]]') % (
                    model_entity.id)]

        self.run_job_and_check_output(
            output, sort=False, literal_eval=False)

    def test_model_validation_fails_with_invalid_id(self):
        app_feedback_report_models.AppFeedbackReportModel(
            id='invalid_entity_id',
            platform=self.PLATFORM_ANDROID,
            submitted_on=self.REPORT_SUBMITTED_TIMESTAMP,
            report_type=self.REPORT_TYPE_SUGGESTION,
            category=self.CATEGORY_OTHER,
            platform_version=self.PLATFORM_VERSION,
            device_country_locale_code=self.COUNTRY_LOCALE_CODE_INDIA,
            android_device_model=self.ANDROID_DEVICE_MODEL,
            android_sdk_version=self.ANDROID_SDK_VERSION,
            entry_point=self.ENTRY_POINT_NAVIGATION_DRAWER,
            text_language_code=self.TEXT_LANGUAGE_CODE_ENGLISH,
            audio_language_code=self.AUDIO_LANGUAGE_CODE_ENGLISH,
            android_report_info=self.ANDROID_REPORT_INFO,
            android_report_info_schema_version=(
                self.ANDROID_REPORT_INFO_SCHEMA_VERSION)
        ).put()
        self.expected_output.append(
            u'[u\'failed validation check for model id check of '
            'AppFeedbackReportModel\', '
            '[u\'Entity id invalid_entity_id: Entity id does not match regex '
            'pattern\']]')

        self.run_job_and_check_output(
            self.expected_output, sort=True, literal_eval=False)

    def test_model_with_android_schema_version_greater_than_current_schema(
            self):
        model_entity = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.report_id))
        model_entity.android_report_info_schema_version = 2
        model_entity.update_timestamps()
        model_entity.put()
        output = [
            (
                u'[u\'failed validation check for report schema version check '
                'of AppFeedbackReportModel\', '
                '[u\'Entity id %s: android report schema version %s is greater '
                'than current version %s\']]') % (
                    model_entity.id,
                    model_entity.android_report_info_schema_version,
                    feconf.CURRENT_ANDROID_REPORT_SCHEMA_VERSION)]

        self.run_job_and_check_output(
            output, sort=False, literal_eval=False)

    def test_model_with_web_schema_version_greater_than_current_schema(self):
        web_report_id = (
            app_feedback_report_models.AppFeedbackReportModel.create(
                platform=self.PLATFORM_WEB,
                submitted_on=self.REPORT_SUBMITTED_TIMESTAMP,
                report_type=self.REPORT_TYPE_SUGGESTION,
                category=self.CATEGORY_OTHER,
                platform_version=self.PLATFORM_VERSION,
                device_country_locale_code=self.COUNTRY_LOCALE_CODE_INDIA,
                android_device_model=self.ANDROID_DEVICE_MODEL,
                android_sdk_version=self.ANDROID_SDK_VERSION,
                entry_point=self.ENTRY_POINT_NAVIGATION_DRAWER,
                entry_point_topic_id=None, entry_point_story_id=None,
                entry_point_exploration_id=None, entry_point_subtopic_id=None,
                text_language_code=self.TEXT_LANGUAGE_CODE_ENGLISH,
                audio_language_code=self.AUDIO_LANGUAGE_CODE_ENGLISH,
                android_report_info=None,
                web_report_info={}))
        web_entity = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                web_report_id))
        web_entity.web_report_info_schema_version = 2
        web_entity.update_timestamps()
        web_entity.put()
        self.expected_output.append((
            u'[u\'failed validation check for report schema version check of '
            'AppFeedbackReportModel\', '
            '[u\'Entity id %s: web report schema version %s is greater than'
            ' current version %s\']]') % (
                web_entity.id, web_entity.web_report_info_schema_version,
                feconf.CURRENT_WEB_REPORT_SCHEMA_VERSION))

        self.run_job_and_check_output(
            self.expected_output, sort=True, literal_eval=False)

    def test_model_with_submitted_on_greater_than_current_datetime(self):
        entity_id = (
            app_feedback_report_models.AppFeedbackReportModel.create(
                platform=self.PLATFORM_ANDROID,
                submitted_on=(
                    datetime.datetime.utcnow() + datetime.timedelta(days=2)),
                report_type=self.REPORT_TYPE_SUGGESTION,
                category=self.CATEGORY_OTHER,
                platform_version=self.PLATFORM_VERSION,
                device_country_locale_code=self.COUNTRY_LOCALE_CODE_INDIA,
                android_device_model=self.ANDROID_DEVICE_MODEL,
                android_sdk_version=self.ANDROID_SDK_VERSION,
                entry_point=self.ENTRY_POINT_NAVIGATION_DRAWER,
                entry_point_topic_id=None, entry_point_story_id=None,
                entry_point_exploration_id=None, entry_point_subtopic_id=None,
                text_language_code=self.TEXT_LANGUAGE_CODE_ENGLISH,
                audio_language_code=self.AUDIO_LANGUAGE_CODE_ENGLISH,
                android_report_info={},
                web_report_info=None))
        model_entity = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                entity_id))
        self.expected_output.append(
            (
                u'[u\'failed validation check for submitted_on datetime check '
                'of AppFeedbackReportModel\', '
                '[u\'Entity id %s: The submitted_on field has a value %s which '
                'is greater than the time when the job was run\']]') % (
                    model_entity.id, model_entity.submitted_on))

        self.run_job_and_check_output(
            self.expected_output, sort=True, literal_eval=False)

    def test_model_with_submitted_on_less_than_earliest_valid_datetime(self):
        entity_id = (
            app_feedback_report_models.AppFeedbackReportModel.create(
                platform=self.PLATFORM_ANDROID,
                submitted_on=(
                    EARLIEST_VALID_DATETIME - datetime.timedelta(days=2)),
                report_type=self.REPORT_TYPE_SUGGESTION,
                category=self.CATEGORY_OTHER,
                platform_version=self.PLATFORM_VERSION,
                device_country_locale_code=self.COUNTRY_LOCALE_CODE_INDIA,
                android_device_model=self.ANDROID_DEVICE_MODEL,
                android_sdk_version=self.ANDROID_SDK_VERSION,
                entry_point=self.ENTRY_POINT_NAVIGATION_DRAWER,
                entry_point_topic_id=None, entry_point_story_id=None,
                entry_point_exploration_id=None, entry_point_subtopic_id=None,
                text_language_code=self.TEXT_LANGUAGE_CODE_ENGLISH,
                audio_language_code=self.AUDIO_LANGUAGE_CODE_ENGLISH,
                android_report_info={},
                web_report_info=None))
        model_entity = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                entity_id))
        self.expected_output.append(
            (
                u'[u\'failed validation check for submitted_on datetime check '
                'of AppFeedbackReportModel\', [u\'Entity id %s: The '
                'submitted_on field has a value %s which is less than the '
                'earliest possible submission date\']]') % (
                    model_entity.id, model_entity.submitted_on))

        self.run_job_and_check_output(
            self.expected_output, sort=True, literal_eval=False)

    def test_model_with_scrubbed_by_field_failure(self):
        model_entity = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.report_id))
        model_entity.created_on = (
            datetime.datetime.utcnow() - datetime.timedelta(days=100))
        model_entity.update_timestamps()
        model_entity.put()
        output = [
            (
                u'[u\'failed validation check for scrubbed_by field check of '
                'AppFeedbackReportModel\', '
                '[u"Entity id %s: based on entity created_on date %s, expected'
                ' model AppFeedbackReportModel to have field scrubbed_by but it'
                ' doesn\'t exist"]]') % (
                    model_entity.id, model_entity.created_on.isoformat())]

        self.run_job_and_check_output(
            output, sort=False, literal_eval=False)


class AppFeedbackReportTicketModelValidatorTests(test_utils.AuditJobsTestBase):
    USER_1_EMAIL = 'some@email.com'
    USER_1_USERNAME = 'username1'
    PLATFORM_ANDROID = 'android'
    # The timestamp in sec since epoch for Mar 7 2021 21:17:16 UTC.
    REPORT_SUBMITTED_TIMESTAMP = datetime.datetime.fromtimestamp(1615151836)
    REPORT_IDS_LIST = ['%s.%s.%s' % (
        PLATFORM_ANDROID, REPORT_SUBMITTED_TIMESTAMP.second,
        'randomInteger123')]
    TICKET_NAME = 'example ticket name'
    REPORT_TYPE_SUGGESTION = 'suggestion'
    CATEGORY_OTHER = 'other'
    PLATFORM_VERSION = '0.1-alpha-abcdef1234'
    COUNTRY_LOCALE_CODE_INDIA = 'in'
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
    ANDROID_REPORT_INFO_SCHEMA_VERSION = 1

    def setUp(self):
        super(AppFeedbackReportTicketModelValidatorTests, self).setUp()

        self.signup(self.USER_1_EMAIL, self.USER_1_USERNAME)
        self.user_1_id = self.get_user_id_from_email(self.USER_1_EMAIL)

        self.ticket_id = (
            app_feedback_report_models.AppFeedbackReportTicketModel.create(
                ticket_name=self.TICKET_NAME,
                github_issue_number=None,
                newest_report_timestamp=self.REPORT_SUBMITTED_TIMESTAMP,
                report_ids=self.REPORT_IDS_LIST))
        app_feedback_report_models.AppFeedbackReportModel(
            id='%s.%s.%s' % (
                self.PLATFORM_ANDROID, self.REPORT_SUBMITTED_TIMESTAMP.second,
                'randomInteger123'),
            platform=self.PLATFORM_ANDROID,
            ticket_id=self.ticket_id,
            submitted_on=self.REPORT_SUBMITTED_TIMESTAMP,
            report_type=self.REPORT_TYPE_SUGGESTION,
            category=self.CATEGORY_OTHER,
            platform_version=self.PLATFORM_VERSION,
            device_country_locale_code=self.COUNTRY_LOCALE_CODE_INDIA,
            android_device_model=self.ANDROID_DEVICE_MODEL,
            android_sdk_version=self.ANDROID_SDK_VERSION,
            entry_point=self.ENTRY_POINT_NAVIGATION_DRAWER,
            text_language_code=self.TEXT_LANGUAGE_CODE_ENGLISH,
            audio_language_code=self.AUDIO_LANGUAGE_CODE_ENGLISH,
            android_report_info=self.ANDROID_REPORT_INFO,
            android_report_info_schema_version=(
                self.ANDROID_REPORT_INFO_SCHEMA_VERSION)
        ).put()

        self.expected_output = [
            u'[u\'fully-validated AppFeedbackReportTicketModel\', 1]']
        self.job_class = (
            prod_validation_jobs.AppFeedbackReportTicketModelAuditOneOffJob)

    def test_standard_model(self):
        self.run_job_and_check_output(
            self.expected_output, sort=False, literal_eval=False)

    def test_model_validation_fails_with_invalid_id(self):
        app_feedback_report_models.AppFeedbackReportTicketModel(
            id='invalid_entity_id', ticket_name=self.TICKET_NAME,
            github_issue_number=None, archived=False,
            newest_report_timestamp=self.REPORT_SUBMITTED_TIMESTAMP,
            report_ids=self.REPORT_IDS_LIST
        ).put()
        self.expected_output.append(
            u'[u\'failed validation check for model id check of '
            'AppFeedbackReportTicketModel\', '
            '[u\'Entity id invalid_entity_id: Entity id does not match regex '
            'pattern\']]')

        self.run_job_and_check_output(
            self.expected_output, sort=True, literal_eval=False)

    def test_model_with_newest_report_timestamp_greater_than_current_datetime(
            self):
        model_entity = (
            app_feedback_report_models.AppFeedbackReportTicketModel.get_by_id(
                self.ticket_id))
        model_entity.newest_report_timestamp = (
            datetime.datetime.utcnow() + datetime.timedelta(days=2))
        model_entity.update_timestamps()
        model_entity.put()
        output = [
            (
                u'[u\'failed validation check for newest_report_timestamp '
                'datetime check of AppFeedbackReportTicketModel\', '
                '[u\'Entity id %s: The newest_report_timestamp field has a '
                'value %s which is greater than the time when the job was '
                'run\']]') % (
                    model_entity.id, model_entity.newest_report_timestamp)]

        self.run_job_and_check_output(
            output, sort=False, literal_eval=False)

    def test_model_with_newest_report_timestamp_less_than_earliest_datetime(
            self):
        model_entity = (
            app_feedback_report_models.AppFeedbackReportTicketModel.get_by_id(
                self.ticket_id))
        model_entity.newest_report_timestamp = (
            EARLIEST_VALID_DATETIME - datetime.timedelta(days=2))
        model_entity.update_timestamps()
        model_entity.put()
        output = [
            (
                u'[u\'failed validation check for newest_report_timestamp '
                'datetime check of AppFeedbackReportTicketModel\', [u\'Entity '
                'id %s: The newest_report_timestamp field has a value %s which '
                'is less than the earliest possible submission date\']]') % (
                    model_entity.id, model_entity.newest_report_timestamp)]

        self.run_job_and_check_output(
            output, sort=False, literal_eval=False)

    def test_model_validation_with_invalid_external_references(self):
        model_entity = (
            app_feedback_report_models.AppFeedbackReportTicketModel.get_by_id(
                self.ticket_id))
        model_entity.report_ids = ['invalid_report_id']
        model_entity.update_timestamps()
        model_entity.put()
        output = [
            (
                u'[u\'failed validation check for report_ids field check of '
                'AppFeedbackReportTicketModel\', '
                '[u"Entity id %s: based on field report_ids having value '
                'invalid_report_id, expected model AppFeedbackReportModel'
                ' with id invalid_report_id but it doesn\'t exist"]]') % (
                    model_entity.id)]

        self.run_job_and_check_output(
            output, sort=False, literal_eval=False)


class AppFeedbackReportStatsModelValidatorTests(test_utils.AuditJobsTestBase):
    USER_1_EMAIL = 'some@email.com'
    USER_1_USERNAME = 'username1'
    PLATFORM_ANDROID = 'android'
    # Timestamp in sec since epoch for Mar 19 2021 17:10:36 UTC.
    TICKET_CREATION_TIMESTAMP = datetime.datetime.fromtimestamp(1616173836)
    TICKET_ID = '%s.%s.%s' % (
        'random_hash', TICKET_CREATION_TIMESTAMP.second, '16CharString1234')
    # Timestamp date in sec since epoch for Mar 19 2021 UTC.
    STATS_DATE_TIMESTAMP = datetime.date.fromtimestamp(1616173836)
    DAILY_STATS = {
        'daily_param_stats': {
            'report_type': {
                'suggestion': 1, 'issue': 1, 'crash': 1}},
        'daily_total_report_submitted': 3}
    STATS_ID = '%s:%s:%s' % (
        PLATFORM_ANDROID, TICKET_ID, STATS_DATE_TIMESTAMP.isoformat())

    # The timestamp in sec since epoch for Mar 7 2021 21:17:16 UTC.
    REPORT_SUBMITTED_TIMESTAMP = datetime.datetime.fromtimestamp(1615151836)
    REPORT_ID = '%s.%s.%s' % (
        PLATFORM_ANDROID, REPORT_SUBMITTED_TIMESTAMP.second, 'randomInteger123')

    def setUp(self):
        super(AppFeedbackReportStatsModelValidatorTests, self).setUp()

        self.signup(self.USER_1_EMAIL, self.USER_1_USERNAME)
        self.user_1_id = self.get_user_id_from_email(self.USER_1_EMAIL)

        self.entity_id = (
            app_feedback_report_models.AppFeedbackReportStatsModel.create(
                platform=self.PLATFORM_ANDROID,
                ticket_id=self.TICKET_ID,
                stats_tracking_date=self.STATS_DATE_TIMESTAMP,
                daily_ticket_stats=self.DAILY_STATS
            ))
        app_feedback_report_models.AppFeedbackReportTicketModel(
            id=self.TICKET_ID, ticket_name='example ticket',
            github_issue_number=None, archived=False,
            newest_report_timestamp=self.REPORT_SUBMITTED_TIMESTAMP,
            report_ids=[self.REPORT_ID]).put()

        self.expected_output = [
            u'[u\'fully-validated AppFeedbackReportStatsModel\', 1]']
        self.job_class = (
            prod_validation_jobs.AppFeedbackReportStatsModelAuditOneOffJob)

    def test_standard_model(self):
        self.run_job_and_check_output(
            self.expected_output, sort=False, literal_eval=False)

    def test_model_validation_fails_with_invalid_id(self):
        app_feedback_report_models.AppFeedbackReportStatsModel(
            id='invalid_entity_id',
            ticket_id=self.TICKET_ID,
            platform=self.PLATFORM_ANDROID,
            stats_tracking_date=self.STATS_DATE_TIMESTAMP,
            daily_ticket_stats=self.DAILY_STATS,
            daily_ticket_stats_schema_version=(
                feconf.CURRENT_REPORT_STATS_SCHEMA_VERSION)
        ).put()
        self.expected_output.append(
            (
                u'[u\'failed validation check for model id check of '
                'AppFeedbackReportStatsModel\', '
                '[u\'Entity id invalid_entity_id: Entity id does not match '
                'regex pattern\']]'))

        self.run_job_and_check_output(
            self.expected_output, sort=True, literal_eval=False)

    def test_model_fails_with_stats_schema_version_greater_than_current_schema(
            self):
        model_entity = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_by_id(
                self.entity_id))
        model_entity.daily_ticket_stats_schema_version = 2
        model_entity.update_timestamps()
        model_entity.put()
        output = [
            (
                u'[u\'failed validation check for report stats schema version '
                'check of AppFeedbackReportStatsModel\', '
                '[u\'Entity id %s: daily stats schema version %s is greater '
                'than current version %s\']]') % (
                    model_entity.id,
                    model_entity.daily_ticket_stats_schema_version,
                    feconf.CURRENT_ANDROID_REPORT_SCHEMA_VERSION)]

        self.run_job_and_check_output(
            output, sort=False, literal_eval=False)

    def test_model_validation_with_invalid_external_references(self):
        entity_id = (
            app_feedback_report_models.AppFeedbackReportStatsModel.create(
                platform=self.PLATFORM_ANDROID,
                ticket_id='invalid_ticket_id',
                stats_tracking_date=self.STATS_DATE_TIMESTAMP,
                daily_ticket_stats=self.DAILY_STATS))
        model_entity = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_by_id(
                entity_id))
        self.expected_output.append(
            (
                u'[u\'failed validation check for ticket_id field check of '
                'AppFeedbackReportStatsModel\', '
                '[u"Entity id %s: based on field ticket_id having value '
                'invalid_ticket_id, expected model AppFeedbackReportTicketModel'
                ' with id invalid_ticket_id but it doesn\'t exist"]]') % (
                    model_entity.id))

        self.run_job_and_check_output(
            self.expected_output, sort=True, literal_eval=False)
