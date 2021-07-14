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

"""Tests for services that operate on app feedback reports."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

import datetime

from core.domain import app_feedback_report_constants as constants
from core.domain import app_feedback_report_domain
from core.domain import app_feedback_report_services
from core.platform import models
from core.tests import test_utils

import feconf
import python_utils
import utils

(app_feedback_report_models,) = models.Registry.import_models(
    [models.NAMES.app_feedback_report]) # type: ignore[no-untyped-call]


class AppFeedbackReportServicesUnitTests(test_utils.GenericTestBase):
    """Tests for functions in app_feedback_report_services."""

    USER_EMAIL = 'user@example.com'
    USER_USERNAME = 'user'
    EXP_1_ID = 'exp_1_id'

    PLATFORM_ANDROID = 'android'
    PLATFORM_WEB = 'web'
    # Timestamp in sec since epoch for Mar 12 2021 3:22:17 UTC.
    REPORT_SUBMITTED_TIMESTAMP = datetime.datetime.fromtimestamp(1615519337)
    # Timestamp in sec since epoch for Mar 19 2021 17:10:36 UTC.
    TIMESTAMP_AT_MAX_DAYS = datetime.datetime.utcnow() - (
        feconf.APP_FEEDBACK_REPORT_MAXIMUM_NUMBER_OF_DAYS)
    TIMESTAMP_OVER_MAX_DAYS = datetime.datetime.utcnow() - (
        feconf.APP_FEEDBACK_REPORT_MAXIMUM_NUMBER_OF_DAYS +
        datetime.timedelta(days=2))
    TICKET_CREATION_TIMESTAMP = datetime.datetime.fromtimestamp(1616173836)
    TICKET_CREATION_TIMESTAMP_MSEC = utils.get_time_in_millisecs(
        TICKET_CREATION_TIMESTAMP)
    TICKET_NAME = 'a ticket name'
    TICKET_ID = '%s.%s.%s' % (
        'random_hash', int(TICKET_CREATION_TIMESTAMP_MSEC), '16CharString1234')
    USER_ID = 'user_1'
    REPORT_TYPE_SUGGESTION = constants.REPORT_TYPE.suggestion
    CATEGORY_OTHER = constants.CATEGORY.other_suggestion
    ANDROID_PLATFORM_VERSION = '0.1-alpha-abcdef1234'
    COUNTRY_LOCALE_CODE_INDIA = 'in'
    ANDROID_DEVICE_MODEL = 'Pixel 4a'
    ANDROID_SDK_VERSION = 23
    ENTRY_POINT_NAVIGATION_DRAWER = constants.ENTRY_POINT.navigation_drawer
    TEXT_LANGUAGE_CODE_ENGLISH = 'en'
    AUDIO_LANGUAGE_CODE_ENGLISH = 'en'
    ANDROID_REPORT_INFO = {
        'user_feedback_selected_items': None,
        'user_feedback_other_text_input': 'add an admin',
        'event_logs': ['event1', 'event2'],
        'logcat_logs': ['logcat1', 'logcat2'],
        'package_version_code': 1,
        'build_fingerprint': 'example_fingerprint_id',
        'network_type': 'wifi',
        'android_device_language_locale_code': 'en',
        'entry_point_info': {
            'entry_point_name': 'crash',
        },
        'text_size': 'medium_text_size',
        'only_allows_wifi_download_and_update': True,
        'automatically_update_topics': False,
        'account_is_profile_admin': False
    }
    WEB_PLATFORM_VERSION = '3.0.8'
    WEB_REPORT_INFO = {
        'user_feedback_other_text_input': 'add an admin'
    }
    ANDROID_REPORT_INFO_SCHEMA_VERSION = 1
    WEB_REPORT_INFO_SCHEMA_VERSION = 1

    REPORT_JSON = {
        'android_report_info_schema_version': 1,
        'app_context': {
            'entry_point': {
                'entry_point_name': 'navigation_drawer',
                'entry_point_exploration_id': None,
                'entry_point_story_id': None,
                'entry_point_topic_id': None,
                'entry_point_subtopic_id': None,
            },
            'text_size': 'large_text_size',
            'text_language_code': 'en',
            'audio_language_code': 'en',
            'only_allows_wifi_download_and_update': True,
            'automatically_update_topics': False,
            'account_is_profile_admin': False,
            'event_logs': ['example', 'event'],
            'logcat_logs': ['example', 'log']
        },
        'device_context': {
            'android_device_model': 'example_model',
            'android_sdk_version': 23,
            'build_fingerprint': 'example_fingerprint_id',
            'network_type': 'wifi'
        },
        'report_submission_timestamp_sec': 1615519337,
        'report_submission_utc_offset_hrs': 0,
        'system_context': {
            'platform_version': '0.1-alpha-abcdef1234',
            'package_version_code': 1,
            'android_device_country_locale_code': 'in',
            'android_device_language_locale_code': 'en'
        },
        'user_supplied_feedback': {
            'report_type': 'suggestion',
            'category': 'language_suggestion',
            'user_feedback_selected_items': None,
            'user_feedback_other_text_input': 'french'
        }
    }

    REPORT_STATS = {
        'platform': {PLATFORM_ANDROID: 1},
        'report_type': {REPORT_TYPE_SUGGESTION.name: 1},
        'country_locale_code': {COUNTRY_LOCALE_CODE_INDIA: 1},
        'entry_point_name': {ENTRY_POINT_NAVIGATION_DRAWER.name: 1},
        'text_language_code': {TEXT_LANGUAGE_CODE_ENGLISH: 1},
        'audio_language_code': {AUDIO_LANGUAGE_CODE_ENGLISH: 1},
        'android_sdk_version': {python_utils.UNICODE(ANDROID_SDK_VERSION): 1},
        'version_name': {ANDROID_PLATFORM_VERSION: 1}
    }

    def setUp(self):
        # type: () -> None
        super(AppFeedbackReportServicesUnitTests, self).setUp()
        self.signup(self.USER_EMAIL, self.USER_USERNAME)
        self.user_id = self.get_user_id_from_email(self.USER_EMAIL)

        self.android_report_id = (
            app_feedback_report_models.AppFeedbackReportModel.generate_id(
                self.PLATFORM_ANDROID, self.REPORT_SUBMITTED_TIMESTAMP))
        app_feedback_report_models.AppFeedbackReportModel.create(
            self.android_report_id, self.PLATFORM_ANDROID,
            self.REPORT_SUBMITTED_TIMESTAMP, 0,
            self.REPORT_TYPE_SUGGESTION.name, self.CATEGORY_OTHER.name,
            self.ANDROID_PLATFORM_VERSION,
            self.COUNTRY_LOCALE_CODE_INDIA,
            self.ANDROID_SDK_VERSION, self.ANDROID_DEVICE_MODEL,
            self.ENTRY_POINT_NAVIGATION_DRAWER.name, None, None, None, None,
            self.TEXT_LANGUAGE_CODE_ENGLISH, self.AUDIO_LANGUAGE_CODE_ENGLISH,
            self.ANDROID_REPORT_INFO, None)
        self.android_report_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.android_report_id))
        self.android_report_obj = (
            app_feedback_report_services.get_report_from_model(
                self.android_report_model))

        self.android_ticket_id = (
            app_feedback_report_models.AppFeedbackReportTicketModel.generate_id(
                self.TICKET_NAME))
        app_feedback_report_models.AppFeedbackReportTicketModel.create(
            self.android_ticket_id, self.TICKET_NAME, self.PLATFORM_ANDROID,
            None, None, self.REPORT_SUBMITTED_TIMESTAMP,
            [self.android_report_id])
        self.android_ticket_model = (
            app_feedback_report_models.AppFeedbackReportTicketModel.get_by_id(
                self.android_ticket_id))
        self.android_ticket_obj = (
            app_feedback_report_services.get_ticket_from_model(
                self.android_ticket_model))

    def test_get_reports_returns_same_report(self):
        # type: () -> None
        report_models = app_feedback_report_services.get_report_models(
            [self.android_report_id])
        self.assertEqual(report_models[0].id, self.android_report_id)

    def test_get_multiple_reports_returns_all_reports(self):
        # type: () -> None
        new_report_id_1 = (
            app_feedback_report_models.AppFeedbackReportModel.generate_id(
                self.PLATFORM_ANDROID, self.REPORT_SUBMITTED_TIMESTAMP))
        app_feedback_report_models.AppFeedbackReportModel.create(
            new_report_id_1, self.PLATFORM_ANDROID,
            self.REPORT_SUBMITTED_TIMESTAMP, 0,
            self.REPORT_TYPE_SUGGESTION.name, self.CATEGORY_OTHER.name,
            self.ANDROID_PLATFORM_VERSION,
            self.COUNTRY_LOCALE_CODE_INDIA,
            self.ANDROID_SDK_VERSION, self.ANDROID_DEVICE_MODEL,
            self.ENTRY_POINT_NAVIGATION_DRAWER.name, None, None, None, None,
            self.TEXT_LANGUAGE_CODE_ENGLISH, self.AUDIO_LANGUAGE_CODE_ENGLISH,
            self.ANDROID_REPORT_INFO, None)
        new_report_id_2 = (
            app_feedback_report_models.AppFeedbackReportModel.generate_id(
                self.PLATFORM_ANDROID, self.REPORT_SUBMITTED_TIMESTAMP))
        app_feedback_report_models.AppFeedbackReportModel.create(
            new_report_id_2, self.PLATFORM_ANDROID,
            self.REPORT_SUBMITTED_TIMESTAMP, 0,
            self.REPORT_TYPE_SUGGESTION.name, self.CATEGORY_OTHER.name,
            self.ANDROID_PLATFORM_VERSION,
            self.COUNTRY_LOCALE_CODE_INDIA,
            self.ANDROID_SDK_VERSION, self.ANDROID_DEVICE_MODEL,
            self.ENTRY_POINT_NAVIGATION_DRAWER.name, None, None, None, None,
            self.TEXT_LANGUAGE_CODE_ENGLISH, self.AUDIO_LANGUAGE_CODE_ENGLISH,
            self.ANDROID_REPORT_INFO, None)

        report_models = app_feedback_report_services.get_report_models(
            [self.android_report_id, new_report_id_1, new_report_id_2])
        report_ids = [report_model.id for report_model in report_models]
        self.assertEqual(len(report_models), 3)
        self.assertTrue(self.android_report_id in report_ids)
        self.assertTrue(new_report_id_1 in report_ids)
        self.assertTrue(new_report_id_2 in report_ids)

    def test_get_nonexistent_report_returns_no_report(self):
        # type: () -> None
        report_models = app_feedback_report_services.get_report_models(
            ['bad_id'])
        self.assertIsNone(report_models[0])

    def test_get_report_from_model_has_same_report_info(self):
        # type: () -> None
        self.assertEqual(
            self.android_report_model.id, self.android_report_obj.report_id)
        self.assertEqual(
            self.android_report_model.platform,
            self.android_report_obj.platform)
        self.assertEqual(self.android_report_model.ticket_id, None)
        self.assertEqual(self.android_report_model.scrubbed_by, None)

    def test_get_web_report_raises_error(self):
        # type: () -> None
        mock_web_report_model = self.android_report_obj
        mock_web_report_model.platform = self.PLATFORM_WEB

        with self.assertRaisesRegexp(
            NotImplementedError,
            'Web app feedback report domain objects must be defined.'):
            app_feedback_report_services.get_report_from_model(
                mock_web_report_model)

    def test_get_report_from_model_has_same_user_supplied_feedback_info(self):
        # type: () -> None
        user_supplied_feedback = self.android_report_obj.user_supplied_feedback

        self.assertEqual(
            user_supplied_feedback.report_type.name,
            self.android_report_model.report_type)
        self.assertEqual(
            user_supplied_feedback.category.name,
            self.android_report_model.category)
        self.assertEqual(
            user_supplied_feedback.user_feedback_selected_items, None)
        self.assertEqual(
            user_supplied_feedback.user_feedback_other_text_input,
            self.android_report_model.android_report_info[
                'user_feedback_other_text_input'])

    def test_get_report_from_model_has_same_device_system_info(self):
        # type: () -> None
        device_system_context = self.android_report_obj.device_system_context

        self.assertTrue(isinstance(
            device_system_context,
            app_feedback_report_domain.AndroidDeviceSystemContext))
        self.assertEqual(
            device_system_context.version_name,
            self.android_report_model.platform_version)
        self.assertEqual(
            device_system_context.package_version_code,
            self.android_report_model.android_report_info[
                'package_version_code'])
        self.assertEqual(
            device_system_context.device_country_locale_code,
            self.android_report_model.android_device_country_locale_code)
        self.assertEqual(
            device_system_context.device_model,
            self.android_report_model.android_device_model)
        self.assertEqual(
            device_system_context.sdk_version,
            self.android_report_model.android_sdk_version)
        self.assertEqual(
            device_system_context.build_fingerprint,
            self.android_report_model.android_report_info[
                'build_fingerprint'])
        self.assertEqual(
            device_system_context.network_type.name,
            self.android_report_model.android_report_info[
                'network_type'])

    def test_get_report_from_model_has_same_app_info(self):
        # type: () -> None
        app_context = self.android_report_obj.app_context

        self.assertTrue(isinstance(
            app_context, app_feedback_report_domain.AndroidAppContext))
        self.assertEqual(
            app_context.entry_point.entry_point_name,
            self.android_report_model.entry_point)
        self.assertEqual(
            app_context.text_language_code,
            self.android_report_model.text_language_code)
        self.assertEqual(
            app_context.audio_language_code,
            self.android_report_model.audio_language_code)
        self.assertEqual(
            app_context.text_size.name,
            self.android_report_model.android_report_info['text_size'])
        self.assertEqual(
            app_context.only_allows_wifi_download_and_update,
            self.android_report_model.android_report_info[
                'only_allows_wifi_download_and_update'])
        self.assertEqual(
            app_context.automatically_update_topics,
            self.android_report_model.android_report_info[
                'automatically_update_topics'])
        self.assertEqual(
            app_context.account_is_profile_admin,
            self.android_report_model.android_report_info[
                'account_is_profile_admin'])
        self.assertEqual(
            app_context.event_logs,
            self.android_report_model.android_report_info['event_logs'])
        self.assertEqual(
            app_context.logcat_logs,
            self.android_report_model.android_report_info['logcat_logs'])

    def test_save_android_report_and_get_from_model_has_new_info(self):
        # type: () -> None
        self.assertIsNone(self.android_report_obj.scrubbed_by)

        # Add a user in the scrubbed_by field and verify that the updated model
        # is saved to storage.
        self.android_report_obj.scrubbed_by = self.user_id
        app_feedback_report_services.save_feedback_report_to_storage(
            self.android_report_obj)
        scrubbed_report_models = app_feedback_report_services.get_report_models(
            [self.android_report_id])
        scrubbed_report_obj = (
            app_feedback_report_services.get_report_from_model(
                scrubbed_report_models[0]))

        self.assertEqual(scrubbed_report_obj.scrubbed_by, self.user_id)

    def test_save_web_report_raises_exception(self):
        # type: () -> None
        mock_web_report_obj = self.android_report_obj
        mock_web_report_obj.platform = self.PLATFORM_WEB

        with self.assertRaisesRegexp(
            utils.InvalidInputException,
            'Web report domain objects have not been defined.'):
            app_feedback_report_services.save_feedback_report_to_storage(
                mock_web_report_obj)

    def test_get_ticket_from_model_has_same_ticket_info(self):
        # type: () -> None
        self.assertEqual(
            self.android_ticket_obj.ticket_id, self.android_ticket_model.id)
        self.assertEqual(
            self.android_ticket_obj.ticket_name,
            self.android_ticket_model.ticket_name)
        self.assertEqual(
            self.android_ticket_obj.platform,
            self.android_ticket_model.platform)
        self.assertEqual(self.android_ticket_obj.github_issue_repo_name, None)
        self.assertEqual(
            self.android_ticket_obj.github_issue_number, None)
        self.assertEqual(self.android_ticket_obj.archived, False)
        self.assertEqual(
            self.android_ticket_obj.newest_report_creation_timestamp,
            self.android_ticket_model.newest_report_timestamp)
        self.assertEqual(
            self.android_ticket_obj.reports,
            self.android_ticket_model.report_ids)

    def test_get_ticket_from_model_with_github_info_has_same_ticket_info(self):
        # type: () -> None
        report_id = (
            app_feedback_report_models.AppFeedbackReportModel.generate_id(
                self.PLATFORM_ANDROID, self.REPORT_SUBMITTED_TIMESTAMP))
        ticket_id = (
            app_feedback_report_models.AppFeedbackReportTicketModel.generate_id(
                self.TICKET_NAME))
        ticket_model = (
            app_feedback_report_models.AppFeedbackReportTicketModel(
                id=ticket_id, ticket_name=self.TICKET_NAME,
                platform=self.PLATFORM_ANDROID,
                github_issue_repo_name=self.PLATFORM_ANDROID,
                github_issue_number=12, archived=False,
                newest_report_timestamp=self.REPORT_SUBMITTED_TIMESTAMP,
                report_ids=[report_id]))
        ticket_obj = app_feedback_report_services.get_ticket_from_model(
            ticket_model)

        self.assertEqual(ticket_obj.ticket_id, ticket_id)
        self.assertEqual(ticket_obj.platform, ticket_model.platform)
        self.assertEqual(
            ticket_obj.github_issue_repo_name,
            ticket_model.github_issue_repo_name)
        self.assertEqual(
            ticket_obj.github_issue_number, ticket_model.github_issue_number)
        self.assertEqual(ticket_obj.archived, ticket_model.archived)
        self.assertEqual(
            ticket_obj.newest_report_creation_timestamp,
            ticket_model.newest_report_timestamp)
        self.assertEqual(ticket_obj.reports, ticket_model.report_ids)

    def test_get_ticket_from_model_is_archived_has_same_ticket_info(self):
        # type: () -> None
        self.android_ticket_model.archived = True
        self.android_ticket_model.update_timestamps()
        self.android_ticket_model.put()
        ticket_obj = app_feedback_report_services.get_ticket_from_model(
            self.android_ticket_model)

        self.assertEqual(ticket_obj.ticket_id, self.android_ticket_model.id)
        self.assertEqual(
            ticket_obj.platform, self.android_ticket_model.platform)
        self.assertEqual(
            ticket_obj.github_issue_repo_name,
            self.android_ticket_model.github_issue_repo_name)
        self.assertEqual(
            ticket_obj.github_issue_number,
            self.android_ticket_model.github_issue_number)
        self.assertEqual(ticket_obj.ticket_id, self.android_ticket_model.id)
        self.assertEqual(ticket_obj.archived, True)
        self.assertEqual(
            ticket_obj.newest_report_creation_timestamp,
            self.android_ticket_model.newest_report_timestamp)
        self.assertEqual(
            ticket_obj.reports, self.android_ticket_model.report_ids)

    def test_create_android_report_from_json_is_correct_object(self):
        # type: () -> None
        report_obj = (
            app_feedback_report_services.create_android_report_from_json(
                self.REPORT_JSON))

        self.assertTrue(isinstance(
            report_obj, app_feedback_report_domain.AppFeedbackReport))
        self.assertTrue(isinstance(
            report_obj.device_system_context,
            app_feedback_report_domain.AndroidDeviceSystemContext))
        self.assertTrue(isinstance(
            report_obj.app_context,
            app_feedback_report_domain.AndroidAppContext))
        self.assertEqual(report_obj.platform, self.PLATFORM_ANDROID)
        self.assertEqual(
            report_obj.submitted_on_timestamp, self.REPORT_SUBMITTED_TIMESTAMP)

    def test_save_new_android_report_from_json_saves_model_to_storage(self):
        # type: () -> None
        report_obj = (
            app_feedback_report_services.create_android_report_from_json(
                self.REPORT_JSON))
        app_feedback_report_services.save_feedback_report_to_storage(
            report_obj, new_incoming_report=True)
        report_id = report_obj.report_id
        report_models = app_feedback_report_services.get_report_models(
            [report_id])
        actual_model = report_models[0]

        self.assertEqual(actual_model.id, report_id)
        # Verify some of the model's fields based on input JSON.
        self.assertEqual(actual_model.platform, self.PLATFORM_ANDROID)
        self.assertEqual(
            actual_model.submitted_on, self.REPORT_SUBMITTED_TIMESTAMP)
        self.assertEqual(
            actual_model.report_type, self.REPORT_TYPE_SUGGESTION.name)
        self.assertEqual(
            actual_model.entry_point, self.ENTRY_POINT_NAVIGATION_DRAWER.name)

    def test_new_reports_added_updates_unticketed_stats_model_correctly(self):
        # type: () -> None
        report_obj_1 = (
            app_feedback_report_services.create_android_report_from_json(
                self.REPORT_JSON))
        report_obj_2 = (
            app_feedback_report_services.create_android_report_from_json(
                self.REPORT_JSON))
        app_feedback_report_services.store_incoming_report_stats(report_obj_1)
        app_feedback_report_services.store_incoming_report_stats(report_obj_2)

        # Both reports should be added to the unticketed stat model.
        unticketed_stats_id = (
            app_feedback_report_models.AppFeedbackReportStatsModel.calculate_id(
                self.PLATFORM_ANDROID,
                constants.UNTICKETED_ANDROID_REPORTS_STATS_TICKET_ID,
                self.REPORT_SUBMITTED_TIMESTAMP.date()))
        unticketed_stats_model = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_by_id(
                unticketed_stats_id))

        expected_json = {
            constants.STATS_PARAMETER_NAMES.report_type.name: {
                self.REPORT_TYPE_SUGGESTION.name: 2
            },
            constants.STATS_PARAMETER_NAMES.country_locale_code.name: {
                self.COUNTRY_LOCALE_CODE_INDIA: 2
            },
            constants.STATS_PARAMETER_NAMES.entry_point_name.name: {
                self.ENTRY_POINT_NAVIGATION_DRAWER.name: 2
            },
            constants.STATS_PARAMETER_NAMES.text_language_code.name: {
                self.TEXT_LANGUAGE_CODE_ENGLISH: 2
            },
            constants.STATS_PARAMETER_NAMES.audio_language_code.name: {
                self.AUDIO_LANGUAGE_CODE_ENGLISH: 2
            },
            constants.STATS_PARAMETER_NAMES.android_sdk_version.name: {
                python_utils.UNICODE(self.ANDROID_SDK_VERSION): 2
            },
            constants.STATS_PARAMETER_NAMES.version_name.name: {
                self.ANDROID_PLATFORM_VERSION: 2
            }
        }

        self.assertEqual(unticketed_stats_model.platform, self.PLATFORM_ANDROID)
        self.assertEqual(unticketed_stats_model.total_reports_submitted, 2)
        self._verify_stats_model(
            unticketed_stats_model.daily_param_stats, expected_json)

    def test_new_report_added_updates_all_reports_stats_model_correctly(self):
        # type: () -> None
        report_obj_1 = (
            app_feedback_report_services.create_android_report_from_json(
                self.REPORT_JSON))
        report_obj_2 = (
            app_feedback_report_services.create_android_report_from_json(
                self.REPORT_JSON))
        app_feedback_report_services.store_incoming_report_stats(report_obj_1)
        app_feedback_report_services.store_incoming_report_stats(report_obj_2)

        # Both reports should be added to the all reports stats model.
        all_report_stats_id = (
            app_feedback_report_models.AppFeedbackReportStatsModel.calculate_id(
                self.PLATFORM_ANDROID,
                constants.ALL_ANDROID_REPORTS_STATS_TICKET_ID,
                self.REPORT_SUBMITTED_TIMESTAMP.date()))
        all_reports_stats_model = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_by_id(
                all_report_stats_id))

        expected_json = {
            constants.STATS_PARAMETER_NAMES.report_type.name: {
                self.REPORT_TYPE_SUGGESTION.name: 2
            },
            constants.STATS_PARAMETER_NAMES.country_locale_code.name: {
                self.COUNTRY_LOCALE_CODE_INDIA: 2
            },
            constants.STATS_PARAMETER_NAMES.entry_point_name.name: {
                self.ENTRY_POINT_NAVIGATION_DRAWER.name: 2
            },
            constants.STATS_PARAMETER_NAMES.text_language_code.name: {
                self.TEXT_LANGUAGE_CODE_ENGLISH: 2
            },
            constants.STATS_PARAMETER_NAMES.audio_language_code.name: {
                self.AUDIO_LANGUAGE_CODE_ENGLISH: 2
            },
            constants.STATS_PARAMETER_NAMES.android_sdk_version.name: {
                python_utils.UNICODE(self.ANDROID_SDK_VERSION): 2
            },
            constants.STATS_PARAMETER_NAMES.version_name.name: {
                self.ANDROID_PLATFORM_VERSION: 2
            }
        }

        self.assertEqual(
            all_reports_stats_model.platform, self.PLATFORM_ANDROID)
        self.assertEqual(all_reports_stats_model.total_reports_submitted, 2)
        self._verify_stats_model(
            all_reports_stats_model.daily_param_stats, expected_json)

    def test_get_all_expiring_reports(self):
        # type: () -> None
        expiring_report_id_1 = (
            self._add_expiring_android_report_with_no_scrubber())
        expiring_report_id_2 = (
            self._add_expiring_android_report_with_no_scrubber())

        expiring_reports = (
            app_feedback_report_services.get_all_expiring_reports_to_scrub())
        expiring_report_ids = [report.report_id for report in expiring_reports]

        self.assertEqual(len(expiring_reports), 2)
        self.assertTrue(expiring_report_id_1 in expiring_report_ids)
        self.assertTrue(expiring_report_id_2 in expiring_report_ids)

    def test_get_all_filter_options(self):
        # type: () -> None
        filter_options = app_feedback_report_services.get_all_filter_options()
        filter_fields = [
            filter_obj.filter_field for filter_obj in filter_options]

        for filter_obj in filter_options:
            self.assertTrue(filter_obj.filter_field in filter_fields)
            if filter_obj.filter_field == (
                    constants.FILTER_FIELD_NAMES.report_type):
                self.assertEqual(
                    filter_obj.filter_options[0],
                    self.REPORT_TYPE_SUGGESTION.name)
            elif filter_obj.filter_field == (
                    constants.FILTER_FIELD_NAMES.platform):
                self.assertEqual(
                    filter_obj.filter_options[0], self.PLATFORM_ANDROID)
            elif filter_obj.filter_field == (
                    constants.FILTER_FIELD_NAMES.entry_point):
                self.assertEqual(
                    filter_obj.filter_options[0],
                    self.ENTRY_POINT_NAVIGATION_DRAWER.name)
            elif filter_obj.filter_field == (
                    constants.FILTER_FIELD_NAMES.submitted_on):
                self.assertEqual(
                    filter_obj.filter_options[0],
                    self.REPORT_SUBMITTED_TIMESTAMP.date())
            elif filter_obj.filter_field == (
                    constants.FILTER_FIELD_NAMES.android_device_model):
                self.assertEqual(
                    filter_obj.filter_options[0], self.ANDROID_DEVICE_MODEL)
            elif filter_obj.filter_field == (
                    constants.FILTER_FIELD_NAMES.android_sdk_version):
                self.assertEqual(
                    filter_obj.filter_options[0], self.ANDROID_SDK_VERSION)
            elif filter_obj.filter_field == (
                    constants.FILTER_FIELD_NAMES.text_language_code):
                self.assertEqual(
                    filter_obj.filter_options[0],
                    self.TEXT_LANGUAGE_CODE_ENGLISH)
            elif filter_obj.filter_field == (
                    constants.FILTER_FIELD_NAMES.audio_language_code):
                self.assertEqual(
                    filter_obj.filter_options[0],
                    self.AUDIO_LANGUAGE_CODE_ENGLISH)
            elif filter_obj.filter_field == (
                    constants.FILTER_FIELD_NAMES.platform_version):
                self.assertEqual(
                    filter_obj.filter_options[0], self.ANDROID_PLATFORM_VERSION)
            elif filter_obj.filter_field == (
                    constants.FILTER_FIELD_NAMES.android_device_country_locale_code):  # pylint: disable=line-too-long
                self.assertEqual(
                    filter_obj.filter_options[0],
                    self.COUNTRY_LOCALE_CODE_INDIA)

    def test_edit_ticket_name_updates_ticket_model(self):
        # type: () -> None
        self.android_report_obj.ticket_id = self.android_ticket_id
        new_ticket_name = 'a ticket name'
        app_feedback_report_services.edit_ticket_name(
            self.android_ticket_obj, new_ticket_name)

        new_ticket_model = (
            app_feedback_report_models.AppFeedbackReportTicketModel.get_by_id(
                self.android_ticket_id))

        self.assertEqual(self.android_ticket_obj.ticket_id, new_ticket_model.id)
        self.assertEqual(new_ticket_model.ticket_name, new_ticket_name)
        self.assertEqual(self.android_report_obj.ticket_id, new_ticket_model.id)

    def test_edit_ticket_name_does_not_change_ticket_id(self):
        # type: () -> None
        new_ticket_name = 'a new ticket name'
        app_feedback_report_services.edit_ticket_name(
            self.android_ticket_obj, new_ticket_name)

        new_ticket_model = (
            app_feedback_report_models.AppFeedbackReportTicketModel.get_by_id(
                self.android_ticket_id))

        self.assertEqual(new_ticket_model.ticket_name, new_ticket_name)
        self.assertEqual(self.android_ticket_obj.ticket_id, new_ticket_model.id)
        self.assertEqual(
            self.android_report_obj.platform, new_ticket_model.platform)

    def test_edit_ticket_name_does_not_change_stats_model(self):
        # type: () -> None
        self.android_ticket_obj.reports = []
        old_ticket_name = 'old ticket name'
        old_ticket_id = (
            app_feedback_report_models.AppFeedbackReportTicketModel.generate_id(
                old_ticket_name))
        app_feedback_report_models.AppFeedbackReportTicketModel.create(
            old_ticket_id, old_ticket_name, self.PLATFORM_ANDROID,
            None, None, self.REPORT_SUBMITTED_TIMESTAMP,
            [self.android_report_id])
        self.android_report_model.ticket_id = old_ticket_id
        self.android_report_model.update_timestamps()
        self.android_report_model.put()
        self.android_report_obj = (
            app_feedback_report_services.get_report_from_model(
                self.android_report_model))

        old_stats_id = (
            app_feedback_report_models.AppFeedbackReportStatsModel.calculate_id(
                self.android_report_obj.platform,
                self.android_report_obj.ticket_id,
                self.android_report_obj.submitted_on_timestamp.date()))
        app_feedback_report_models.AppFeedbackReportStatsModel.create(
            old_stats_id, self.android_report_obj.platform, old_ticket_id,
            self.android_report_obj.submitted_on_timestamp.date(), 1,
            self.REPORT_STATS)
        old_stats_model = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_by_id(
                old_stats_id))

        new_ticket_name = 'a new ticket name'
        app_feedback_report_services.edit_ticket_name(
            self.android_ticket_obj, new_ticket_name)

        new_report_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.android_report_id))
        new_report_obj = (
            app_feedback_report_services.get_report_from_model(
                new_report_model))
        new_stats_id = (
            app_feedback_report_models.AppFeedbackReportStatsModel.calculate_id(
                new_report_obj.platform,
                new_report_obj.ticket_id,
                new_report_obj.submitted_on_timestamp.date()))
        new_stats_model = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_by_id(
                new_stats_id))

        self.assertEqual(old_stats_id, new_stats_id)
        self.assertEqual(old_stats_model.ticket_id, new_stats_model.ticket_id)
        self.assertEqual(
            old_stats_model.total_reports_submitted,
            new_stats_model.total_reports_submitted)
        self.assertEqual(
            old_stats_model.platform, new_stats_model.platform)
        self.assertEqual(
            old_stats_model.stats_tracking_date,
            new_stats_model.stats_tracking_date)
        self._verify_stats_model(
            new_stats_model.daily_param_stats,
            old_stats_model.daily_param_stats)

    def test_reassign_report_to_ticket_updates_increasing_stats_model(self):
        # type: () -> None
        new_ticket_id = self._add_new_android_ticket(
            'ticket_name', ['report_id'])
        new_ticket_model = (
            app_feedback_report_models.AppFeedbackReportTicketModel.get_by_id(
                new_ticket_id))
        new_ticket_obj = app_feedback_report_services.get_ticket_from_model(
            new_ticket_model)

        app_feedback_report_services.store_incoming_report_stats(
            self.android_report_obj)
        old_stats_id = (
            app_feedback_report_models.AppFeedbackReportStatsModel.calculate_id(
                self.android_report_obj.platform,
                self.android_report_obj.ticket_id,
                self.android_report_obj.submitted_on_timestamp.date()))

        app_feedback_report_services.reassign_ticket(
            self.android_report_obj, new_ticket_obj)
        new_stats_id = (
            app_feedback_report_models.AppFeedbackReportStatsModel.calculate_id(
                new_ticket_obj.platform,
                new_ticket_obj.ticket_id,
                self.android_report_obj.submitted_on_timestamp.date()))
        new_stats_model = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_by_id(
                new_stats_id))

        expected_json = {
            constants.STATS_PARAMETER_NAMES.report_type.name: {
                self.REPORT_TYPE_SUGGESTION.name: 1
            },
            constants.STATS_PARAMETER_NAMES.country_locale_code.name: {
                self.COUNTRY_LOCALE_CODE_INDIA: 1
            },
            constants.STATS_PARAMETER_NAMES.entry_point_name.name: {
                self.ENTRY_POINT_NAVIGATION_DRAWER.name: 1
            },
            constants.STATS_PARAMETER_NAMES.text_language_code.name: {
                self.TEXT_LANGUAGE_CODE_ENGLISH: 1
            },
            constants.STATS_PARAMETER_NAMES.audio_language_code.name: {
                self.AUDIO_LANGUAGE_CODE_ENGLISH: 1
            },
            constants.STATS_PARAMETER_NAMES.android_sdk_version.name: {
                python_utils.UNICODE(self.ANDROID_SDK_VERSION): 1
            },
            constants.STATS_PARAMETER_NAMES.version_name.name: {
                self.ANDROID_PLATFORM_VERSION: 1
            }
        }
        self.assertNotEqual(old_stats_id, new_stats_id)
        self.assertEqual(new_stats_model.total_reports_submitted, 1)
        self._verify_stats_model(
            new_stats_model.daily_param_stats,
            expected_json)

    def test_reassign_ticket_updates_decreasing_stats_model(self):
        # type: () -> None
        new_ticket_id = self._add_new_android_ticket(
            'ticket_name', ['report_id'])
        new_ticket_model = (
            app_feedback_report_models.AppFeedbackReportTicketModel.get_by_id(
                new_ticket_id))
        new_ticket_obj = app_feedback_report_services.get_ticket_from_model(
            new_ticket_model)

        app_feedback_report_services.store_incoming_report_stats(
            self.android_report_obj)
        old_stats_id = (
            app_feedback_report_models.AppFeedbackReportStatsModel.calculate_id(
                self.android_report_obj.platform,
                self.android_report_obj.ticket_id,
                self.android_report_obj.submitted_on_timestamp.date()))

        app_feedback_report_services.reassign_ticket(
            self.android_report_obj, new_ticket_obj)
        # Get the updated stats from the old model.
        decremented_stats_model = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_by_id(
                old_stats_id))

        expected_json = {
            constants.STATS_PARAMETER_NAMES.report_type.name: {
                self.REPORT_TYPE_SUGGESTION.name: 0
            },
            constants.STATS_PARAMETER_NAMES.country_locale_code.name: {
                self.COUNTRY_LOCALE_CODE_INDIA: 0
            },
            constants.STATS_PARAMETER_NAMES.entry_point_name.name: {
                self.ENTRY_POINT_NAVIGATION_DRAWER.name: 0
            },
            constants.STATS_PARAMETER_NAMES.text_language_code.name: {
                self.TEXT_LANGUAGE_CODE_ENGLISH: 0
            },
            constants.STATS_PARAMETER_NAMES.audio_language_code.name: {
                self.AUDIO_LANGUAGE_CODE_ENGLISH: 0
            },
            constants.STATS_PARAMETER_NAMES.android_sdk_version.name: {
                python_utils.UNICODE(self.ANDROID_SDK_VERSION): 0
            },
            constants.STATS_PARAMETER_NAMES.version_name.name: {
                self.ANDROID_PLATFORM_VERSION: 0
            }
        }
        self.assertEqual(decremented_stats_model.total_reports_submitted, 0)
        self._verify_stats_model(
            decremented_stats_model.daily_param_stats,
            expected_json)

    def test_reassign_ticket_does_not_change_all_report_stats_model(self):
        # type: () -> None
        new_ticket_id = self._add_new_android_ticket(
            'ticket_name', ['report_id'])
        new_ticket_model = (
            app_feedback_report_models.AppFeedbackReportTicketModel.get_by_id(
                new_ticket_id))
        new_ticket_obj = app_feedback_report_services.get_ticket_from_model(
            new_ticket_model)

        app_feedback_report_services.store_incoming_report_stats(
            self.android_report_obj)
        old_all_report_stats_id = (
            app_feedback_report_models.AppFeedbackReportStatsModel.calculate_id(
                self.android_report_obj.platform,
                constants.ALL_ANDROID_REPORTS_STATS_TICKET_ID,
                self.android_report_obj.submitted_on_timestamp.date()))
        old_all_reports_stats_model = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_by_id(
                old_all_report_stats_id))

        app_feedback_report_services.reassign_ticket(
            self.android_report_obj, new_ticket_obj)
        new_all_reports_stats_model = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_by_id(
                old_all_report_stats_id))

        self.assertEqual(
            new_all_reports_stats_model.total_reports_submitted,
            old_all_reports_stats_model.total_reports_submitted)
        self._verify_stats_model(
            new_all_reports_stats_model.daily_param_stats,
            old_all_reports_stats_model.daily_param_stats)

    def test_reassign_web_ticket_raises_error(self):
        # type: () -> None
        mock_web_report_obj = self.android_report_obj
        mock_web_report_obj.platform = self.PLATFORM_WEB

        with self.assertRaisesRegexp(
            NotImplementedError,
            'Assigning web reports to tickets has not been implemented yet.'):
            app_feedback_report_services.reassign_ticket(
                mock_web_report_obj, None)

    def test_reassign_ticket_with_invalid_stats_model_raises_error(self):
        # type: () -> None
        # Set an invalid ticket_id so that the stats model calculates an invalid
        # id for this ticket's stats model.
        self.android_report_obj.ticket_id = 'invalid_id'
        with self.assertRaisesRegexp(
            utils.InvalidInputException,
            'The report is being removed from an invalid ticket id'):
            app_feedback_report_services.reassign_ticket(
                self.android_report_obj, None)

    def test_scrub_android_report_removes_info(self):
        # type: () -> None
        app_feedback_report_services.scrub_single_app_feedback_report(
            self.android_report_obj, self.user_id)
        scrubbed_report_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                self.android_report_obj.report_id))

        expected_report_dict = {
            'user_feedback_selected_items': None,
            'user_feedback_other_text_input': None,
            'event_logs': None,
            'logcat_logs': None,
            'package_version_code': 1,
            'android_device_language_locale_code': 'en',
            'build_fingerprint': 'example_fingerprint_id',
            'network_type': 'wifi',
            'text_size': 'medium_text_size',
            'only_allows_wifi_download_and_update': True,
            'automatically_update_topics': False,
            'account_is_profile_admin': False
        }

        self.assertEqual(scrubbed_report_model.scrubbed_by, self.user_id)
        self.assertEqual(
            scrubbed_report_model.android_report_info, expected_report_dict)

    def test_scrubbing_on_current_and_expired_reports_only_scrubs_expired(self):
        # type: () -> None
        current_report_id = self._add_current_report()
        expired_report_id = self._add_expiring_android_report_with_no_scrubber()
        app_feedback_report_services.scrub_all_unscrubbed_expiring_reports(
            self.user_id)

        scrubbed_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                expired_report_id))
        current_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                current_report_id))

        self._verify_report_is_scrubbed(scrubbed_model, self.user_id)
        self._verify_report_is_not_scrubbed(current_model)

    def test_scrubbing_with_no_reports_in_storage_does_not_scrub_storage(self):
        # type: () -> None
        current_models_query = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_all())
        current_models = current_models_query.fetch()
        self.assertEqual(len(current_models), 0)
        app_feedback_report_services.scrub_all_unscrubbed_expiring_reports(
            'scrubber_user')

        stored_models_query = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_all())
        stored_models = stored_models_query.fetch()
        self.assertEqual(len(stored_models), 0)

    def test_scrubbing_on_only_current_reports_does_not_scrub_models(self):
        # type: () -> None
        current_report_id = self._add_current_report()
        app_feedback_report_services.scrub_all_unscrubbed_expiring_reports(
            self.user_id)

        current_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                current_report_id))
        self._verify_report_is_not_scrubbed(current_model)

    def test_scrubbing_on_all_expired_models_updates_all_models(self):
        # type: () -> None
        android_report_id_1 = (
            self._add_expiring_android_report_with_no_scrubber())
        android_report_id_2 = (
            self._add_expiring_android_report_with_no_scrubber())
        app_feedback_report_services.scrub_all_unscrubbed_expiring_reports(
            self.user_id)

        android_model_1 = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                android_report_id_1))
        android_model_2 = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                android_report_id_2))

        self._verify_report_is_scrubbed(android_model_1, self.user_id)
        self._verify_report_is_scrubbed(android_model_2, self.user_id)

    def test_scrubbing_on_already_scrubbed_models_does_not_change_models(self):
        # type: () -> None
        report_id = self._add_scrubbed_report('scrubber_user')
        app_feedback_report_services.scrub_all_unscrubbed_expiring_reports(
            self.user_id)

        scrubbed_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                report_id))

        self._verify_report_is_scrubbed(scrubbed_model, 'scrubber_user')

    def test_scrubbing_on_newly_added_expired_models_scrubs_new_models(self):
        # type: () -> None
        expired_report_id = (
            self._add_expiring_android_report_with_no_scrubber())
        app_feedback_report_services.scrub_all_unscrubbed_expiring_reports(
            self.user_id)
        scrubbed_android_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                expired_report_id))
        self._verify_report_is_scrubbed(
            scrubbed_android_model, self.user_id)

        to_scrub_report_id = (
            self._add_expiring_android_report_with_no_scrubber())
        app_feedback_report_services.scrub_all_unscrubbed_expiring_reports(
            'different_user')

        newly_scrubbed_model = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                to_scrub_report_id))
        self._verify_report_is_scrubbed(
            newly_scrubbed_model, 'different_user')
        # Check that the originally-scrubbed model is still valid.
        self._verify_report_is_scrubbed(
            scrubbed_android_model, self.user_id)

    def test_get_report_type_from_string_returns_expected_report_type(self):
        # type: () -> None
        for report_type in constants.REPORT_TYPE:
            self.assertEqual(
                app_feedback_report_services.get_report_type_from_string(
                    report_type.name), report_type)

    def test_get_report_type_from_string_with_invalid_string_raises_error(self):
        # type: () -> None
        invalid_report_type = 'invalid_report_type'
        with self.assertRaisesRegexp(
            utils.InvalidInputException,
            'The given report type %s is invalid.' % invalid_report_type):
            app_feedback_report_services.get_report_type_from_string(
                invalid_report_type)

    def test_get_category_from_string_returns_expected_category(self):
        # type: () -> None
        for category in constants.ALLOWED_CATEGORIES:
            self.assertEqual(
                app_feedback_report_services.get_category_from_string(
                    category.name), category)

    def test_get_category_from_string_with_invalid_string_raises_error(self):
        # type: () -> None
        invalid_category = 'invalid_category'
        with self.assertRaisesRegexp(
            utils.InvalidInputException,
            'The given category %s is invalid.' % invalid_category):
            app_feedback_report_services.get_category_from_string(
                invalid_category)

    def test_get_android_text_size_from_string_returns_expected_text_size(self):
        # type: () -> None
        for text_size in constants.ALLOWED_ANDROID_TEXT_SIZES:
            self.assertEqual(
                app_feedback_report_services.get_android_text_size_from_string(
                    text_size.name), text_size)

    def test_get_android_text_size_from_string_with_invalid_string_raises_error(
            self):
        # type: () -> None
        invalid_text_size = 'invalid_text_size'
        with self.assertRaisesRegexp(
            utils.InvalidInputException,
            'The given Android app text size %s is invalid.' % (
                invalid_text_size)):
            app_feedback_report_services.get_android_text_size_from_string(
                invalid_text_size)

    def test_get_entry_point_from_json_returns_expected_entry_point_obj(self):
        # type: () -> None
        entry_point_json = {
            'entry_point_name': '',
            'entry_point_topic_id': 'topic_id',
            'entry_point_story_id': 'story_id',
            'entry_point_exploration_id': 'exploration_id',
            'entry_point_subtopic_id': 'subtopic_id'
        }

        entry_point_json['entry_point_name'] = (
            constants.ENTRY_POINT.navigation_drawer.name)
        navigation_drawer_obj = (
            app_feedback_report_services.get_entry_point_from_json(
                entry_point_json))
        self.assertTrue(
            isinstance(
                navigation_drawer_obj,
                app_feedback_report_domain.NavigationDrawerEntryPoint))

        entry_point_json['entry_point_name'] = (
            constants.ENTRY_POINT.lesson_player.name)
        lesson_player_obj = (
            app_feedback_report_services.get_entry_point_from_json(
                entry_point_json))
        self.assertTrue(
            isinstance(
                lesson_player_obj,
                app_feedback_report_domain.LessonPlayerEntryPoint))

        entry_point_json['entry_point_name'] = (
            constants.ENTRY_POINT.revision_card.name)
        revision_card_obj = (
            app_feedback_report_services.get_entry_point_from_json(
                entry_point_json))
        self.assertTrue(
            isinstance(
                revision_card_obj,
                app_feedback_report_domain.RevisionCardEntryPoint))

        entry_point_json['entry_point_name'] = (
            constants.ENTRY_POINT.crash.name)
        crash_obj = (
            app_feedback_report_services.get_entry_point_from_json(
                entry_point_json))
        self.assertTrue(
            isinstance(
                crash_obj, app_feedback_report_domain.CrashEntryPoint))

    def test_get_entry_point_from_json_with_invalid_json_raises_error(self):
        # type: () -> None
        invalid_json = {
            'entry_point_name': 'invalid_entry_point_name'
        }
        with self.assertRaisesRegexp(
            utils.InvalidInputException,
            'The given entry point %s is invalid.' % (
                'invalid_entry_point_name')):
            app_feedback_report_services.get_entry_point_from_json(
                invalid_json)

    def test_get_android_network_type_from_string_returns_expected_network_type(
            self):
        # type: () -> None
        for network_type in constants.ANDROID_NETWORK_TYPES:
            self.assertEqual(
                app_feedback_report_services.get_android_network_type_from_string( # pylint: disable=line-too-long
                    network_type.name), network_type)

    def test_get_android_network_type_from_string_invalid_string_raises_error(
            self):
        # type: () -> None
        invalid_network_type = 'invalid_text_size'
        with self.assertRaisesRegexp(
            utils.InvalidInputException,
            'The given Android network type %s is invalid.' % (
                invalid_network_type)):
            app_feedback_report_services.get_android_network_type_from_string(
                invalid_network_type)

    def test_store_incoming_report_stats_with_web_platform_raises_error(self):
        # type: () -> None
        mock_web_report_obj = self.android_report_obj
        mock_web_report_obj.platform = constants.PLATFORM_CHOICE_WEB

        with self.assertRaisesRegexp(
            NotImplementedError,
            'Stats aggregation for incoming web reports have not been '
            'implemented yet.'):
            app_feedback_report_services.store_incoming_report_stats(
                mock_web_report_obj)

    def test_calculate_new_stats_count_for_parameter_adds_new_stats_val_to_dict(
            self):
        # type: () -> None
        stats_map = {
            'parameter_name': {
                'value_1': 1
            }
        }
        delta = 1

        new_stats_map = (
            app_feedback_report_services.calculate_new_stats_count_for_parameter( # pylint: disable=line-too-long
                stats_map, 'value_2', delta))

        self.assertEqual(new_stats_map['value_2'], delta)

    def test_calculate_new_stats_count_with_invalid_delta_raises_error(self):
        # type: () -> None
        stats_map = {
            'parameter_name': {
                'current_value': 1
            }
        }
        delta = -1

        with self.assertRaisesRegexp(
            utils.InvalidInputException,
            'Cannot decrement a count for a parameter value that does '
            'not exist'):
            app_feedback_report_services.calculate_new_stats_count_for_parameter( # pylint: disable=line-too-long
                stats_map, 'value_2', delta)

    def _verify_report_is_scrubbed(self, model_entity, scrubber):
        # type: (app_feedback_report_models.AppFeedbackReportModel, str) -> None
        """Verifies the report model is scrubbed."""
        self.assertIsNotNone(model_entity)
        self.assertEqual(
            model_entity.scrubbed_by, scrubber)

    def _verify_report_is_not_scrubbed(self, model_entity):
        # type: (app_feedback_report_models.AppFeedbackReportModel) -> None
        """Verifies the report model is not scrubbed."""
        self.assertIsNotNone(model_entity)
        self.assertIsNone(model_entity.scrubbed_by)

    def _add_current_report(self):
        # type: () -> None
        """Adds reports to the model that should not be scrubbed."""
        report_id = (
            app_feedback_report_models.AppFeedbackReportModel.generate_id(
                self.PLATFORM_ANDROID, self.TIMESTAMP_AT_MAX_DAYS))
        ticket_id = self._add_new_android_ticket(
            'current report ticket name', [report_id])
        current_feedback_report_model = (
            app_feedback_report_models.AppFeedbackReportModel(
                id=report_id,
                platform=self.PLATFORM_ANDROID,
                ticket_id=ticket_id,
                submitted_on=self.REPORT_SUBMITTED_TIMESTAMP,
                local_timezone_offset_hrs=0,
                report_type=self.REPORT_TYPE_SUGGESTION.name,
                category=self.CATEGORY_OTHER.name,
                platform_version=self.ANDROID_PLATFORM_VERSION,
                android_device_country_locale_code=(
                    self.COUNTRY_LOCALE_CODE_INDIA),
                android_device_model=self.ANDROID_DEVICE_MODEL,
                android_sdk_version=self.ANDROID_SDK_VERSION,
                entry_point=self.ENTRY_POINT_NAVIGATION_DRAWER.name,
                text_language_code=self.TEXT_LANGUAGE_CODE_ENGLISH,
                audio_language_code=self.AUDIO_LANGUAGE_CODE_ENGLISH,
                android_report_info=self.ANDROID_REPORT_INFO,
                android_report_info_schema_version=(
                    self.ANDROID_REPORT_INFO_SCHEMA_VERSION)))
        current_feedback_report_model.created_on = self.TIMESTAMP_AT_MAX_DAYS
        current_feedback_report_model.put()
        return report_id

    def _add_expiring_android_report_with_no_scrubber(self):
        # type: () -> None
        """Adds reports to the model that should be scrubbed."""
        report_id = (
            app_feedback_report_models.AppFeedbackReportModel.generate_id(
                self.PLATFORM_ANDROID, self.TIMESTAMP_OVER_MAX_DAYS))
        ticket_id = self._add_new_android_ticket(
            'expiring report ticket name', [report_id])
        expiring_android_report_model = (
            app_feedback_report_models.AppFeedbackReportModel(
                id=report_id,
                platform=self.PLATFORM_ANDROID,
                ticket_id=ticket_id,
                submitted_on=self.REPORT_SUBMITTED_TIMESTAMP,
                local_timezone_offset_hrs=0,
                report_type=self.REPORT_TYPE_SUGGESTION.name,
                category=self.CATEGORY_OTHER.name,
                platform_version=self.ANDROID_PLATFORM_VERSION,
                android_device_country_locale_code=(
                    self.COUNTRY_LOCALE_CODE_INDIA),
                android_device_model=self.ANDROID_DEVICE_MODEL,
                android_sdk_version=self.ANDROID_SDK_VERSION,
                entry_point=self.ENTRY_POINT_NAVIGATION_DRAWER.name,
                text_language_code=self.TEXT_LANGUAGE_CODE_ENGLISH,
                audio_language_code=self.AUDIO_LANGUAGE_CODE_ENGLISH,
                android_report_info=self.ANDROID_REPORT_INFO,
                android_report_info_schema_version=(
                    self.ANDROID_REPORT_INFO_SCHEMA_VERSION)))
        expiring_android_report_model.created_on = self.TIMESTAMP_OVER_MAX_DAYS
        expiring_android_report_model.put()
        return report_id

    def _add_scrubbed_report(self, scrubber_user):
        # type: (str) -> None
        """Add an already-scrubbed report to the model."""
        report_id = (
            app_feedback_report_models.AppFeedbackReportModel.generate_id(
                self.PLATFORM_ANDROID, self.REPORT_SUBMITTED_TIMESTAMP))
        ticket_id = self._add_new_android_ticket(
            'scrubbed report ticket name', [report_id])
        expiring_android_report_model = (
            app_feedback_report_models.AppFeedbackReportModel(
                id=report_id,
                platform=self.PLATFORM_ANDROID,
                scrubbed_by=scrubber_user,
                ticket_id=ticket_id,
                submitted_on=self.REPORT_SUBMITTED_TIMESTAMP,
                local_timezone_offset_hrs=0,
                report_type=self.REPORT_TYPE_SUGGESTION.name,
                category=self.CATEGORY_OTHER.name,
                platform_version=self.ANDROID_PLATFORM_VERSION,
                android_device_country_locale_code=(
                    self.COUNTRY_LOCALE_CODE_INDIA),
                android_device_model=self.ANDROID_DEVICE_MODEL,
                android_sdk_version=self.ANDROID_SDK_VERSION,
                entry_point=self.ENTRY_POINT_NAVIGATION_DRAWER.name,
                text_language_code=self.TEXT_LANGUAGE_CODE_ENGLISH,
                audio_language_code=self.AUDIO_LANGUAGE_CODE_ENGLISH,
                android_report_info=self.ANDROID_REPORT_INFO,
                android_report_info_schema_version=(
                    self.ANDROID_REPORT_INFO_SCHEMA_VERSION)))
        expiring_android_report_model.created_on = self.TIMESTAMP_OVER_MAX_DAYS
        expiring_android_report_model.put()
        return report_id

    def _add_new_android_ticket(self, ticket_name, report_ids):
        # type: (str, List[str]) -> None
        """Create an Android report ticket."""
        android_ticket_id = (
            app_feedback_report_models.AppFeedbackReportTicketModel.generate_id(
                ticket_name))
        app_feedback_report_models.AppFeedbackReportTicketModel.create(
            android_ticket_id, ticket_name, self.PLATFORM_ANDROID,
            None, None, self.REPORT_SUBMITTED_TIMESTAMP, report_ids)
        return android_ticket_id

    def _verify_stats_model(self, stats_json, expected_json):
        # type: (Dict[str, Dict[str, int]) -> None
        """Verify the fields of the feedback report stats model."""
        self.assertEqual(
            stats_json['report_type'],
            expected_json['report_type'])
        self.assertEqual(
            stats_json['country_locale_code'],
            expected_json['country_locale_code'])
        self.assertEqual(
            stats_json['entry_point_name'],
            expected_json['entry_point_name'])
        self.assertEqual(
            stats_json['text_language_code'],
            expected_json['text_language_code'])
        self.assertEqual(
            stats_json['audio_language_code'],
            expected_json['audio_language_code'])
        self.assertEqual(
            stats_json['android_sdk_version'],
            expected_json['android_sdk_version'])
        self.assertEqual(
            stats_json['version_name'],
            expected_json['version_name'])
