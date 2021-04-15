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

"""Constants used for app feedback reporting."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

import utils


PLATFORM_CHOICE_ANDROID = 'android'
PLATFORM_CHOICE_WEB = 'web'
PLATFORM_CHOICES = [PLATFORM_CHOICE_ANDROID, PLATFORM_CHOICE_WEB]
GITHUB_REPO_CHOICES = PLATFORM_CHOICES


# IDs to use for stats model entities tracking all reports and all unticketed
# reports.
ALL_ANDROID_REPORTS_STATS_TICKET_ID = 'all_android_reports_stats_ticket_id'
UNTICKETED_ANDROID_REPORTS_STATS_TICKET_ID = (
    'unticketed_android_reports_stats_ticket_id')

MAXIMUM_TICKET_NAME_LENGTH = 100
MINIMUM_ANDROID_SDK_VERSION = 2
TIMEZONE_MINIMUM_OFFSET = -12
TIMEZONE_MAXIMUM_OFFSET = 14
REPORT_ID_DELIMITER = '.'
TICKET_ID_DELIMITER = '.'
STATS_ID_DELIMITER = ':'

ReportType = utils.create_enum('suggestion', 'issue', 'crash')
Category = utils.create_enum(
    'suggestion_new_feature', 'suggestion_new_language', 'suggestion_other',
    'issue_lesson_question', 'issue_language_general', 'issue_language_audio',
    'issue_language_text', 'issue_topics', 'issue_profile', 'issue_other',
    'crash_lesson_player', 'crash_practice_questions', 'crash_options_page',
    'crash_profile_page', 'crash_other')
EntryPoint = utils.create_enum(
    'navigation_drawer', 'lesson_player', 'revision_card', 'crash')
StatsParameterNames = utils.create_enum(
    'platform', 'report_type', 'country_locale_code',
    'entry_point_name', 'text_language_code', 'audio_language_code',
    'android_sdk_version', 'version_name')
FilterFieldNames = utils.create_enum(
    'platform', 'report_type', 'entry_point', 'submitted_on',
    'android_device_model', 'android_sdk_version', 'text_language_code',
    'audio_language_code', 'platform_version',
    'android_device_country_locale_code')

AndroidTextSize = utils.create_enum(
    'text_size_unspecified', 'small_text_size', 'medium_text_size',
    'large_text_size', 'extra_large_text_size')
ANDROID_ENTRY_POINT = [
    EntryPoint.navigation_drawer, EntryPoint.lesson_player,
    EntryPoint.revision_card, EntryPoint.crash]
ANDROID_VERSION_NAME_DELIMITER = '-'
AndroidNetworkTypes = utils.create_enum('wifi', 'cellular', 'none')

ALLOWED_REPORT_TYPES = [
    ReportType.suggestion, ReportType.issue, ReportType.crash]
ALLOWED_CATEGORIES = [
    Category.suggestion_new_feature, Category.suggestion_new_language,
    Category.suggestion_other, Category.issue_language_general,
    Category.issue_language_audio, Category.issue_language_text,
    Category.issue_topics, Category.issue_profile, Category.issue_other,
    Category.crash_lesson_player, Category.crash_practice_questions,
    Category.crash_options_page, Category.crash_profile_page,
    Category.crash_other]
ALLOWED_ONLY_INPUT_TEXT_CATEGORIES = [
    Category.suggestion_other, Category.issue_other,
    Category.crash_lesson_player, Category.crash_practice_questions,
    Category.crash_options_page, Category.crash_profile_page,
    Category.crash_other]
ALLOWED_SELECTION_ITEMS_CATEGORIES = [
    Category.issue_language_audio, Category.issue_language_text,
    Category.issue_topics, Category.issue_profile, Category.issue_other]
ALLOWED_STATS_PARAMETERS = [
    StatsParameterNames.report_type,
    StatsParameterNames.country_locale_code,
    StatsParameterNames.entry_point_name,
    StatsParameterNames.text_language_code,
    StatsParameterNames.audio_language_code,
    StatsParameterNames.android_sdk_version,
    StatsParameterNames.version_name]
ALLOWED_FILTERS = [
    FilterFieldNames.report_type, FilterFieldNames.platform,
    FilterFieldNames.entry_point, FilterFieldNames.submitted_on,
    FilterFieldNames.android_device_model,
    FilterFieldNames.android_sdk_version,
    FilterFieldNames.text_language_code,
    FilterFieldNames.audio_language_code, FilterFieldNames.platform_version,
    FilterFieldNames.android_device_country_locale_code]
ALLOWED_ANDROID_NETWORK_TYPES = [
    AndroidNetworkTypes.wifi, AndroidNetworkTypes.cellular,
    AndroidNetworkTypes.none]
ALLOWED_ANDROID_TEXT_SIZES = [
    AndroidTextSize.text_size_unspecified, AndroidTextSize.small_text_size,
    AndroidTextSize.medium_text_size, AndroidTextSize.large_text_size,
    AndroidTextSize.extra_large_text_size]
