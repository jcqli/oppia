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

"""Services to operate on app feedback report app_feedback_report_models."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

import datetime

from core.domain import app_feedback_report_constants as constants
from core.domain import app_feedback_report_domain
from core.platform import models

import feconf
import python_utils
import utils

(app_feedback_report_models,) = models.Registry.import_models(
    [models.NAMES.app_feedback_report])
transaction_services = models.Registry.import_transaction_services()

PLATFORM_ANDROID = constants.PLATFORM_CHOICE_ANDROID
PLATFORM_WEB = constants.PLATFORM_CHOICE_WEB


def get_report_models(report_ids):
    """Fetches and returns the AppFeedbackReportModels with the given ids.

    Args:
        report_ids: list(str). The ids for the models to fetch.

    Returns:
        list(AppFeedbackReportModel). A list of models that correspond to the
        requested reports.
    """
    return (
        app_feedback_report_models.AppFeedbackReportModel.get_multi(report_ids))


def create_android_report_from_json(report_json):
    """Creates an AppFeedbackReport domain object instance from the incoming
    JSON request.

    Args:
        report_json: dict. The JSON for the app feedback report.

    Returns:
        AppFeedbackReport. The domain object for an Android feedback report.
    """
    user_supplied_feedback_json = report_json['user_supplied_feedback']
    user_supplied_feedback_obj = (
        app_feedback_report_domain.UserSuppliedFeedback(
            get_report_type_from_string(
                user_supplied_feedback_json['report_type']),
            get_category_from_string(user_supplied_feedback_json['category']),
            user_supplied_feedback_json['user_feedback_selected_items'],
            user_supplied_feedback_json['user_feedback_other_text_input']))

    system_context_json = report_json['system_context']
    device_context_json = report_json['device_context']
    device_system_context_obj = (
        app_feedback_report_domain.AndroidDeviceSystemContext(
            system_context_json['platform_version'],
            system_context_json['package_version_code'],
            system_context_json['android_device_country_locale_code'],
            system_context_json['android_device_language_locale_code'],
            device_context_json['android_device_model'],
            device_context_json['android_sdk_version'],
            device_context_json['build_fingerprint'],
            get_android_network_type_from_string(
                device_context_json['network_type'])))

    app_context_json = report_json['app_context']
    entry_point_obj = get_entry_point_from_json(
        app_context_json['entry_point'])
    app_context_obj = app_feedback_report_domain.AndroidAppContext(
        entry_point_obj, app_context_json['text_language_code'],
        app_context_json['audio_language_code'],
        get_android_text_size_from_string(app_context_json['text_size']),
        app_context_json['only_allows_wifi_download_and_update'],
        app_context_json['automatically_update_topics'],
        app_context_json['account_is_profile_admin'],
        app_context_json['event_logs'], app_context_json['logcat_logs'])

    report_datetime = datetime.datetime.fromtimestamp(
        report_json['report_submission_timestamp_sec'])
    report_id = app_feedback_report_models.AppFeedbackReportModel.generate_id(
        PLATFORM_ANDROID, report_datetime)
    report_obj = app_feedback_report_domain.AppFeedbackReport(
        report_id, report_json['android_report_info_schema_version'],
        PLATFORM_ANDROID, report_datetime,
        report_json['report_submission_utc_offset_hrs'], None, None,
        user_supplied_feedback_obj, device_system_context_obj, app_context_obj)

    return report_obj


def get_report_type_from_string(report_type_name):
    """Determines the report type based on the JSON value.

    Args:
        report_type_name: str. The name of the report type.

    Returns:
        REPORT_TYPE. The enum representing this report type.
    """
    for report_type in constants.ALLOWED_REPORT_TYPES:
        if report_type_name == report_type.name:
            return report_type
    raise utils.InvalidInputException(
        'The given report type %s is invalid.' % report_type_name)


def get_category_from_string(category_name):
    """Determines the category based on the JSON value.

    Args:
        category_name: str. The name of the report type.

    Returns:
        CATEGORY. The enum representing this category.
    """
    for category_type in constants.ALLOWED_CATEGORIES:
        if category_name == category_type.name:
            return category_type
    raise utils.InvalidInputException(
        'The given category %s is invalid.' % category_name)


def get_android_text_size_from_string(text_size_name):
    """Determines the app text size based on the JSON value.

    Args:
        text_size_name: str. The name of the app's text size set.

    Returns:
        ANDROID_TEXT_SIZE. The enum representing the text size.
    """
    for text_size_type in constants.ALLOWED_ANDROID_TEXT_SIZES:
        if text_size_name == text_size_type.name:
            return text_size_type
    raise utils.InvalidInputException(
        'The given Android app text size %s is invalid.' % text_size_name)


def get_entry_point_from_json(entry_point_json):
    """Determines the entry point type based on the rececived JSON.

    Args:
        entry_point_json: dict. The JSON data of the entry point.

    Returns:
        EntryPoint. The EntryPoint domain object representing the entry point.

    Raises:
        InvalidInputException. The given entry point is invalid.
    """
    entry_point_name = entry_point_json['entry_point_name']
    if entry_point_name == constants.ENTRY_POINT.navigation_drawer.name:
        return app_feedback_report_domain.NavigationDrawerEntryPoint()
    elif entry_point_name == constants.ENTRY_POINT.lesson_player.name:
        return app_feedback_report_domain.LessonPlayerEntryPoint(
            entry_point_json['entry_point_topic_id'],
            entry_point_json['entry_point_story_id'],
            entry_point_json['entry_point_exploration_id'])
    elif entry_point_name == constants.ENTRY_POINT.revision_card.name:
        return app_feedback_report_domain.RevisionCardEntryPoint(
            entry_point_json['entry_point_topic_id'],
            entry_point_json['entry_point_subtopic_id'])
    elif entry_point_name == constants.ENTRY_POINT.crash.name:
        return app_feedback_report_domain.CrashEntryPoint()
    else:
        raise utils.InvalidInputException(
            'The given entry point %s is invalid.' % entry_point_name)


def get_android_network_type_from_string(network_type_name):
    """Determines the network type based on the JSON value.

    Args:
        network_type_name: str. The name of the network type.

    Returns:
        ANDROID_NETWORK_TYPE. The enum representing the network type.
    """
    for network_type in constants.ALLOWED_ANDROID_NETWORK_TYPES:
        if network_type_name == network_type.name:
            return network_type
    raise utils.InvalidInputException(
        'The given Android network type %s is invalid.' % network_type_name)


def store_incoming_report_stats(report_obj):
    """Adds a new report's stats to the aggregate stats model.

    Args:
        report_obj: AppFeedbackReport. AppFeedbackReport domain object.
    """
    if report_obj.platform == PLATFORM_WEB:
        raise NotImplementedError(
            'Stats aggregation for incoming web reports have not been '
            'implemented yet.')

    platform = PLATFORM_ANDROID
    unticketed_id = constants.UNTICKETED_ANDROID_REPORTS_STATS_TICKET_ID
    all_reports_id = constants.ALL_ANDROID_REPORTS_STATS_TICKET_ID

    stats_date = report_obj.submitted_on_timestamp.date()
    _update_report_stats_model_in_transaction(
        unticketed_id, platform, stats_date, report_obj, 1)
    _update_report_stats_model_in_transaction(
        all_reports_id, platform, stats_date, report_obj, 1)


@transaction_services.run_in_transaction_wrapper
def _update_report_stats_model_in_transaction(
        ticket_id, platform, date, report_obj, delta):
    """Adds a new report's stats to the stats model for a specific ticket's
    stats.

    Args:
        ticket_id: str. The id of the ticket that we want to update stats for.
        platform: str. The platform of the report being aggregated.
        date: datetime.date. The date of the stats.
        report_obj: AppFeedbackReport. AppFeedbackReport domain object.
        delta: int. The amount to increment the stats by, depending on if the
            report is added or removed from the model.
    """
    # The stats we want to aggregate on.
    report_type = report_obj.user_supplied_feedback.report_type.name
    country_locale_code = (
        report_obj.device_system_context.device_country_locale_code)
    entry_point_name = report_obj.app_context.entry_point.entry_point_name
    text_language_code = report_obj.app_context.text_language_code
    audio_language_code = report_obj.app_context.audio_language_code
    # All the keys in the stats dict must be a string.
    sdk_version = python_utils.UNICODE(
        report_obj.device_system_context.sdk_version)
    version_name = report_obj.device_system_context.version_name

    stats_id = (
        app_feedback_report_models.AppFeedbackReportStatsModel.calculate_id(
            platform, ticket_id, date))
    stats_model = (
        app_feedback_report_models.AppFeedbackReportStatsModel.get_by_id(
            stats_id))
    if stats_model is None:
        assert(delta > 0)
        # Create new stats model entity. These are the individual report fields
        # that we will want to splice aggregate stats by and they will each have
        # a count of 1 since this is the first report added for this entity.
        stats_dict = {
            constants.STATS_PARAMETER_NAMES.report_type.name: {
                report_type: 1
            },
            constants.STATS_PARAMETER_NAMES.country_locale_code.name: {
                country_locale_code: 1
            },
            constants.STATS_PARAMETER_NAMES.entry_point_name.name: {
                entry_point_name: 1
            },
            constants.STATS_PARAMETER_NAMES.text_language_code.name: {
                text_language_code: 1
            },
            constants.STATS_PARAMETER_NAMES.audio_language_code.name: {
                audio_language_code: 1
            },
            constants.STATS_PARAMETER_NAMES.android_sdk_version.name: {
                sdk_version: 1
            },
            constants.STATS_PARAMETER_NAMES.version_name.name: {
                version_name: 1
            }
        }
        app_feedback_report_models.AppFeedbackReportStatsModel.create(
            stats_id, platform, ticket_id, date, 0, stats_dict)
        stats_model = (
            app_feedback_report_models.AppFeedbackReportStatsModel.get_by_id(
                stats_id))
    else:
        # Update existing stats model.
        stats_dict = stats_model.daily_param_stats

        stats_dict[constants.STATS_PARAMETER_NAMES.report_type.name] = (
            calculate_new_stats_count_for_parameter(
                stats_dict[constants.STATS_PARAMETER_NAMES.report_type.name],
                report_type, delta))
        stats_dict[constants.STATS_PARAMETER_NAMES.country_locale_code.name] = (
            calculate_new_stats_count_for_parameter(
                stats_dict[
                    constants.STATS_PARAMETER_NAMES.country_locale_code.name],
                country_locale_code, delta))
        stats_dict[constants.STATS_PARAMETER_NAMES.entry_point_name.name] = (
            calculate_new_stats_count_for_parameter(
                stats_dict[
                    constants.STATS_PARAMETER_NAMES.entry_point_name.name],
                entry_point_name, delta))
        stats_dict[constants.STATS_PARAMETER_NAMES.audio_language_code.name] = (
            calculate_new_stats_count_for_parameter(
                stats_dict[
                    constants.STATS_PARAMETER_NAMES.audio_language_code.name],
                audio_language_code, delta))
        stats_dict[constants.STATS_PARAMETER_NAMES.text_language_code.name] = (
            calculate_new_stats_count_for_parameter(
                stats_dict[
                    constants.STATS_PARAMETER_NAMES.text_language_code.name],
                text_language_code, delta))
        stats_dict[constants.STATS_PARAMETER_NAMES.android_sdk_version.name] = (
            calculate_new_stats_count_for_parameter(
                stats_dict[
                    constants.STATS_PARAMETER_NAMES.android_sdk_version.name],
                sdk_version, delta))
        stats_dict[constants.STATS_PARAMETER_NAMES.version_name.name] = (
            calculate_new_stats_count_for_parameter(
                stats_dict[constants.STATS_PARAMETER_NAMES.version_name.name],
                version_name, delta))

    stats_model.daily_param_stats = stats_dict
    stats_model.total_reports_submitted += delta

    stats_model.update_timestamps()
    stats_model.put()


def calculate_new_stats_count_for_parameter(
        current_stats_map, current_value, delta):
    """Helper to increment or initialize the stats count for a parameter.

    Args:
        current_stats_map: dict. The current stats map for the parameter we are
            updating.
        current_value: str. The value for the parameter that we are updating
            the stats of.
        delta: int. The amount to increment the current count by, either -1 or
            +1.

    Returns:
        int. The new report count to put into the stats dict for a single
        parameter value.
    """
    if current_stats_map.has_key(current_value):
        current_stats_map[current_value] += delta
    else:
        # The stats did not previously have this parameter value.
        if delta < 0:
            raise utils.InvalidInputException(
                'Cannot decrement a count for a parameter value that does not '
                'exist for this stats model.')
        # Update the stats so that it now contains this new value.
        current_stats_map[current_value] = 1
    return current_stats_map


def get_report_from_model(report_model):
    """Create and return a domain object AppFeedbackReport given a model loaded
    from the the data.

    Args:
        report_model: AppFeedbackReportModel. The model loaded from the
            datastore.

    Returns:
        AppFeedbackReport. An AppFeedbackReport domain object corresponding to
        the given model.

    Raises:
        NotImplementedError. The web report domain object needs to be
            implemented.
    """
    if report_model.platform == PLATFORM_ANDROID:
        return get_android_report_from_model(report_model)
    else:
        raise NotImplementedError(
            'Web app feedback report domain objects must be defined.')


def get_ticket_from_model(ticket_model):
    """Create and return a domain object AppFeedbackReportTicket given a model
    loaded from the the data.

    Args:
        ticket_model: AppFeedbackReportTicketModel. The model loaded from the
            datastore.

    Returns:
        AppFeedbackReportTicket. An AppFeedbackReportTicket domain object
        corresponding to the given model.
    """
    return app_feedback_report_domain.AppFeedbackReportTicket(
        ticket_model.id, ticket_model.ticket_name, ticket_model.platform,
        ticket_model.github_issue_repo_name, ticket_model.github_issue_number,
        ticket_model.archived, ticket_model.newest_report_timestamp,
        ticket_model.report_ids)


def get_stats_from_model(stats_model):
    """Create and return a domain object AppFeedbackReportDailyStats given a
    model loaded from the the data.

    Args:
        stats_model: AppFeedbackReportStatsModel. The model loaded from the
            datastore.

    Returns:
        AppFeedbackReportDailyStats. An AppFeedbackReportDailyStats domain
        object corresponding tothe given model.
    """
    ticket = app_feedback_report_models.AppFeedbackReportTicketModel.get_by_id(
        stats_model.ticket_id)
    param_stats = create_app_daily_stats_from_model_json(
        stats_model.daily_param_stats)
    app_feedback_report_domain.AppFeedbackReportDailyStats(
        stats_model.id, ticket, stats_model.platform,
        stats_model.stats_tracking_date, stats_model.total_reports_submitted,
        param_stats)


def create_app_daily_stats_from_model_json(daily_param_stats):
    """Create and return a dict representing the AppFeedbackReportDailyStats
    domain object's daily_param_stats.

    Args:
        daily_param_stats: dict. The stats data from the model.

    Returns:
        dict. A dict mapping param names to ReportStatsParameterValueCounts
        domain objects.
    """
    stats_dict = {}
    for (stats_name, stats_values_dict) in daily_param_stats.items():
        # For each parameter possible, create a
        # ReportStatsParameterValueCounts domain object of possible parameter
        # values and number of reports with that value.
        parameter_counts = {
            value_name: value_count
            for (value_name, value_count) in stats_values_dict.items()
        }
        counts_obj = (
            app_feedback_report_domain.ReportStatsParameterValueCounts(
                parameter_counts))
        stats_dict[stats_name] = counts_obj
    return stats_dict


def get_android_report_from_model(android_report_model):
    """Creates a domain object that represents an android feedback report from
    the given model.

    Args:
        android_report_model: AppFeedbackReportModel. The model to convert to a
            domain object.

    Returns:
        AppFeedbackReport. The corresponding AppFeedbackReport domain object.
    """
    if android_report_model.android_report_info_schema_version < (
            feconf.CURRENT_ANDROID_REPORT_SCHEMA_VERSION):
        raise NotImplementedError(
            'Android app feedback report migrations must be added for new '
            'report schemas implemented.')
    report_info_dict = android_report_model.android_report_info
    user_supplied_feedback = app_feedback_report_domain.UserSuppliedFeedback(
        get_report_type_from_string(android_report_model.report_type),
        get_category_from_string(android_report_model.category),
        report_info_dict['user_feedback_selected_items'],
        report_info_dict['user_feedback_other_text_input'])
    device_system_context = (
        app_feedback_report_domain.AndroidDeviceSystemContext(
            android_report_model.platform_version,
            report_info_dict['package_version_code'],
            android_report_model.android_device_country_locale_code,
            report_info_dict['android_device_language_locale_code'],
            android_report_model.android_device_model,
            android_report_model.android_sdk_version,
            report_info_dict['build_fingerprint'],
            get_android_network_type_from_string(
                report_info_dict['network_type'])))
    entry_point = get_entry_point_from_json(
        {
            'entry_point_name': android_report_model.entry_point,
            'entry_point_topic_id': android_report_model.entry_point_topic_id,
            'entry_point_story_id': android_report_model.entry_point_story_id,
            'entry_point_exploration_id': (
                android_report_model.entry_point_exploration_id),
            'entry_point_subtopic_id': (
                android_report_model.entry_point_subtopic_id)
        })
    app_context = app_feedback_report_domain.AndroidAppContext(
        entry_point, android_report_model.text_language_code,
        android_report_model.audio_language_code,
        get_android_text_size_from_string(report_info_dict['text_size']),
        report_info_dict['only_allows_wifi_download_and_update'],
        report_info_dict['automatically_update_topics'],
        report_info_dict['account_is_profile_admin'],
        report_info_dict['event_logs'], report_info_dict['logcat_logs'])
    return app_feedback_report_domain.AppFeedbackReport(
        android_report_model.id,
        android_report_model.android_report_info_schema_version,
        android_report_model.platform, android_report_model.submitted_on,
        android_report_model.local_timezone_offset_hrs,
        android_report_model.ticket_id, android_report_model.scrubbed_by,
        user_supplied_feedback, device_system_context, app_context)


def scrub_all_unscrubbed_expiring_reports(scrubbed_by):
    """Fetches the reports that are expiring and must be scrubbed.

    Args:
        scrubbed_by: str. The ID of the user initiating scrubbing or
            feconf.APP_FEEDBACK_REPORT_SCRUBBER_BOT_ID if scrubbed by the cron
            job.
    """
    reports_to_scrub = get_all_expiring_reports_to_scrub()
    for report in reports_to_scrub:
        scrub_single_app_feedback_report(report, scrubbed_by)


def get_all_expiring_reports_to_scrub():
    """Fetches the reports that are expiring and must be scrubbed.

    Returns:
        list(AppFeedbackReport). The list of AppFeedbackReportModel domain
        objects that need to be scrubbed.
    """
    model_class = app_feedback_report_models.AppFeedbackReportModel
    model_entities = model_class.get_all_unscrubbed_expiring_report_models()
    return [
        get_report_from_model(model_entity) for model_entity in model_entities]


def scrub_single_app_feedback_report(report, scrubbed_by):
    """Scrubs the instance of AppFeedbackReportModel with given ID, removing
    any user-entered input in the entity.

    Args:
        report: AppFeedbackReport. The domain object of the report to scrub.
        scrubbed_by: str. The id of the user that is initiating scrubbing of
            this report, or a constant
            feconf.APP_FEEDBACK_REPORT_SCRUBBER_BOT_ID if scrubbed by the cron
            job.
    """
    report.scrubbed_by = scrubbed_by
    report.user_supplied_feedback.user_feedback_other_text_input = None
    if report.platform == PLATFORM_ANDROID:
        report.app_context.event_logs = None
        report.app_context.logcat_logs = None
    save_feedback_report_to_storage(report)


def save_feedback_report_to_storage(report, new_incoming_report=False):
    """Saves the AppFeedbackReport domain object to persistent storage.

    Args:
        report: AppFeedbackReport. The domain object of the report to save.
        new_incoming_report: bool. Whether the report is a new incoming report
            that does not have a corresponding model entity.
    """
    user_supplied_feedback = report.user_supplied_feedback
    device_system_context = report.device_system_context
    app_context = report.app_context
    entry_point = app_context.entry_point

    report_info_json = {
        'user_feedback_selected_items': (
            user_supplied_feedback.user_feedback_selected_items),
        'user_feedback_other_text_input': (
            user_supplied_feedback.user_feedback_other_text_input)
    }
    if report.platform == PLATFORM_ANDROID:
        report_info_json = {
            'user_feedback_selected_items': (
                user_supplied_feedback.user_feedback_selected_items),
            'user_feedback_other_text_input': (
                user_supplied_feedback.user_feedback_other_text_input),
            'event_logs': app_context.event_logs,
            'logcat_logs': app_context.logcat_logs,
            'package_version_code': device_system_context.package_version_code,
            'android_device_language_locale_code': (
                device_system_context.device_language_locale_code),
            'build_fingerprint': device_system_context.build_fingerprint,
            'network_type': device_system_context.network_type.name,
            'text_size': app_context.text_size.name,
            'only_allows_wifi_download_and_update': (
                app_context.only_allows_wifi_download_and_update),
            'automatically_update_topics': (
                app_context.automatically_update_topics),
            'account_is_profile_admin': app_context.account_is_profile_admin
        }

    if new_incoming_report:
        app_feedback_report_models.AppFeedbackReportModel.create(
            report.report_id, report.platform,
            report.submitted_on_timestamp,
            report.local_timezone_offset_hrs,
            user_supplied_feedback.report_type.name,
            user_supplied_feedback.category.name,
            device_system_context.version_name,
            device_system_context.device_country_locale_code,
            device_system_context.sdk_version,
            device_system_context.device_model,
            entry_point.entry_point_name, entry_point.topic_id,
            entry_point.story_id, entry_point.exploration_id,
            entry_point.subtopic_id, app_context.text_language_code,
            app_context.audio_language_code, None, None)
    model_entity = app_feedback_report_models.AppFeedbackReportModel.get_by_id(
        report.report_id)
    if report.platform == PLATFORM_ANDROID:
        model_entity.android_report_info = report_info_json
    else:
        raise utils.InvalidInputException(
            'Web report domain objects have not been defined.')

    model_entity.scrubbed_by = report.scrubbed_by
    model_entity.update_timestamps()
    model_entity.put()


def get_all_filter_options():
    """Fetches all the possible values that moderators can filter reports or
    tickets by.

    Returns:
        list(AppFeedbackReportFilter). A list of filters and the possible values
        they can have.
    """
    filter_list = list()
    model_class = app_feedback_report_models.AppFeedbackReportModel
    for filter_field in constants.ALLOWED_FILTERS:
        filter_values = model_class.get_filter_options_for_field(filter_field)
        filter_list.append(app_feedback_report_domain.AppFeedbackReportFilter(
            filter_field.name, filter_values))
    return filter_list


def reassign_ticket(report, new_ticket):
    """Reassign the ticket the report is associated with.

    Args:
        report: AppFeedbackReport. The report being assigned to a new ticket.
        new_ticket: AppFeedbackReportTicket|None. The ticket domain object to
            reassign the report to or None if removing the report form a ticket
            wihtout reassigning.
    """
    if report.platform == PLATFORM_WEB:
        raise NotImplementedError(
            'Assigning web reports to tickets has not been implemented yet.')

    # Update the old ticket model to remove the report from the old ticket's
    # list of reports.
    old_ticket_id = report.ticket_id
    if old_ticket_id is None:
        # If the report was unticketed, remove the it from unticketed reports.
        old_ticket_id = constants.UNTICKETED_ANDROID_REPORTS_STATS_TICKET_ID
    old_ticket_model = (
        app_feedback_report_models.AppFeedbackReportTicketModel.get_by_id(
            old_ticket_id))
    if old_ticket_model is None:
        raise utils.InvalidInputException(
            'The report is being removed from an invalid ticket id: %s.'
            % old_ticket_id)
    old_ticket_obj = get_ticket_from_model(old_ticket_model)
    old_ticket_obj.reports.remove(report)
    if old_ticket_obj.newest_report_creation_timestamp == (
            report.submitted_on_timestamp):
        report_models = get_report_models(old_ticket_obj.reports)
        latest_timestamp = report_models[0].submitted_on_datetime
        for index in python_utils.RANGE(1, len(report_models)):
            if report_models[index].submitted_on_datetime > (
                    latest_timestamp):
                latest_timestamp = (
                    report_models[index].submitted_on_datetime)
        old_ticket_obj.newest_report_creation_timestamp = latest_timestamp
    _save_ticket(old_ticket_obj)
    _update_report_stats_model_in_transaction(
        old_ticket_id, platform, stats_date, report, -1)

    # Get the info of the new ticket to add the report to.
    new_ticket_id = constants.UNTICKETED_ANDROID_REPORTS_STATS_TICKET_ID
    if new_ticket is not None:
        new_ticket_id = new_ticket.ticket_id
    new_ticket_model = (
        app_feedback_report_models.AppFeedbackReportTicketModel.get_by_id(
            new_ticket_id))
    new_ticket_obj = get_ticket_from_model(new_ticket_model)
    new_ticket_obj.reports.add(report)
    if report.submitted_on_timestamp > (
            new_ticket_obj.newest_report_creation_timestamp):
        new_ticket_obj.newest_report_creation_timestamp = (
            report.submitted_on_timestamp)
    _save_ticket(new_ticket_obj)

    platform = report.platform
    stats_date = report.submitted_on_timestamp.date()
    _update_report_stats_model_in_transaction(
        new_ticket_id, platform, stats_date, report, 1)

    # Update the report model to the new ticket id.
    report.ticket_id = new_ticket.ticket_id
    save_feedback_report_to_storage(report)

def edit_ticket_name(ticket, new_name):
    """Updates the ticket name.

    Returns:
        ticket: AppFeedbackReportTicket. The domain object for a ticket.
        new_name: str. The new name to assign the ticket.
    """
    ticket.ticket_name = new_name
    _save_ticket(ticket)


def _save_ticket(ticket):
    """Saves the ticket to persistent storage.

    Returns:
        ticket: AppFeedbackReportTicket. The domain object to save to storage.
    """
    model_class = app_feedback_report_models.AppFeedbackReportTicketModel
    ticket_model = model_class.get_by_id(ticket.ticket_id)
    ticket_model.ticket_name = ticket.ticket_name
    ticket_model.platform = ticket.platform
    ticket_model.github_issue_repo_name = ticket.github_issue_repo_name
    ticket_model.github_issue_number = ticket.github_issue_number
    ticket_model.archived = ticket.archived
    ticket_model.newest_report_timestamp = (
        ticket.newest_report_creation_timestamp)
    ticket_model.report_ids = [report_id for report_id in ticket.reports]
    ticket_model.update_timestamps()
    ticket_model.put()