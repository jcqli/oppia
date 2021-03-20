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

"""Models for Oppia feedback reports from both Android and web."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

from core.platform import models
import feconf
import python_utils
import utils

(base_models,) = models.Registry.import_models([models.NAMES.base_model])

datastore_services = models.Registry.import_datastore_services()

PLATFORM_CHOICE_ANDROID = 'android'
PLATFORM_CHOICE_WEB = 'web'
PLATFORM_CHOICES = [PLATFORM_CHOICE_ANDROID, PLATFORM_CHOICE_WEB]


class AppFeedbackReportModel(base_models.BaseModel):
    """Model for storing feedback reports sent from learners.

    Instances of this model contain information about learner's device and Oppia
    app settings, as well as information provided by the user in the feedback
    report.

    The id of each model instance is determined by concatenating the platform,
    the timestamp of the reports (in ms since epoch, in UTC), and a hash of a
    string representation of a random int.
    """

    # The platform (web or Android) that the report is sent from and that the 
    # feedback corresponds to
    platform = datastore_services.StringProperty(
        required=True, indexed=True, choices=PLATFORM_CHOICES)
    # The ID of the user that scrubbed this report, if it has been scrubbed
    scrubbed_by = datastore_services.StringProperty(
        required=False, indexed=True)
    # Unique ID for the ticket this report is assigned to (see 
    # AppFeedbackReportTicketModel for how this is constructed)
    ticket_id = datastore_services.TextProperty(required=True, indexed=False)
    # Datetime in UTC of when the report was submitted by the user on their
    # device. This may be much earlier than the model entity's creation date if
    # the report was locally cached for a long time on an Android device.
    submitted_on = datastore_services.DateTimeProperty(
        required=True, indexed=True)
    # The type of feedback for this report; choices are not specified as
    # iterations of the report structure may introduce new types and we cannot
    # rely on the backend updates to fully sync with the frontend report
    # updates.
    report_type = datastore_services.StringProperty(required=True, indexed=True)
    # The category that this feedback is for
    category = datastore_services.TextProperty(required=True, indexed=False)
    # The version of the app; on Android this is the package version name (e.g.
    # 1.0-release-arm...) and on web this is the release version (e.g. 3.0.8)
    platform_version = datastore_services.StringProperty(
        required=True, indexed=True)
    # The user's country locale represented as a ISO-3166 code; the locale is
    # determined by the user's Android device settings.
    device_country_locale_code = datastore_services.StringProperty(
        required=True, indexed=True)
    # The entry point location that the user is accessing the feedback report 
    # from on both web & Android devices. On Android, this could be
    # navigation_drawer, lesson_player, revision_card, or crash.
    entry_point = datastore_services.StringProperty(required=True, indexed=True)
    # Additional topic / story / exploration IDs that may be collected depending on
    # the entry_point used to send the report; lesson player will have topic_id,
    # story_id, and exploration_id, while revision card while have topic_id and
    # subtopic_id
    entry_point_topic_id = datastore_services.StringProperty(
        required=False, indexed=False)
    entry_point_story_id = datastore_services.StringProperty(
        required=False, indexed=False)
    entry_point_exploration_id = datastore_services.StringProperty(
        required=False, indexed=False)
    entry_point_subtopic_id = datastore_services.StringProperty(
        required=False, indexed=False)

    # The text language on Oppia set by the user in its ISO-639 language code;
    # this is set by the user in Oppia's app preferences. Current languages on
    # Android can be: EN, FR, HI, or ZH
    text_language_code = datastore_services.StringProperty(
        required=True, indexed=True)
    # The audio language ISO-639 code on Oppia set by the user as declared in
    # the app. Current supported languages: English, Hindi, and Hinglish
    audio_language_code = datastore_services.StringProperty(
        required=True, indexed=True)

    # The Android device model used to submit the report
    android_device_model = datastore_services.StringProperty(
        required=False, indexed=True)
    # The Android SDK version on the user's device
    android_sdk_version = datastore_services.IntegerProperty(
        required=False, indexed=True)
    # The rest of the report info collected on Android. Using the JSON here
    # allows us to iterate on the report structure without requiring backend
    # updates each time the frontend structure is changed, allowing for better
    # backwards compatibility with Android report structures, as well as
    # greater specificity between web and Android feedback.
    android_report_info = datastore_services.JsonProperty(
        required=False, indexed=False)
    # The schema version for the feedback report info
    android_report_info_schema_version = datastore_services.IntegerProperty(
        required=False, indexed=False)

    # The rest of the web report info collected. Using a JSON here allows us to
    # iterate on the report structure allows for better backwards
    # compatibility and specificity between web and Android feedback.
    web_report_info = datastore_services.JsonProperty(
        required=False, indexed=False)
    # The schema version for the feedback report info
    web_report_info_schema_version = datastore_services.IntegerProperty(
        required=False, indexed=False)


    @classmethod
    def create(cls, platform):
        """Creates a new AppFeedbackReportModel instance and returns it.

        Args:
            user_id: str. The id of the user.
            exploration_id: str. The id of the exploration.

        Returns:
            AppFeedbackReportModel. The newly created AppFeedbackReportModel
            instance.
        """
        entity_id = cls._generate_id(user_id, exploration_id)
        return cls(
            id=entity_id, user_id=user_id, exploration_id=exploration_id)

    @classmethod
    def _generate_id(cls, platform, submitted_on_sec):
        """Generates key for the instance of AppFeedbackReportModel
        class in the required format with the arguments provided.

        Args:
            platform: str. The platform the user is the report from.
            submitted_on_sec: float. The timestamp that the report was submitted
                on, in seconds since epoch (in UTC).

        Returns:
            str. The generated ID for this entity using platform,
                submitted_on_sec, and a random string, of the form
                '[user_id].[exploration_id].[random hash]'.
        """
        for _ in python_utils.RANGE(base_models.MAX_RETRIES):
            random_hash = utils.convert_to_hash(
                python_utils.UNICODE(utils.get_random_int(base_models.RAND_RANGE)),
                base_models.ID_LENGTH))
            new_id = '%s.%s.%s' % (platform, exploration_id, random_hash)
            if not cls.get_by_id(new_id):
                return new_id
        raise Exception(
            'The id generator for AppFeedbackReportModel is producing too'
            'many collisions.')

    @staticmethod
    def get_deletion_policy():
        """Model stores the user ID of who has scrubbed this report for auditing
        purposes but otherwise does not contain data directly corresponding to
        the user themselves.
        """
        return base_models.DELETION_POLICY.LOCALLY_PSEUDONYMIZE

    @classmethod
    def get_export_policy(cls):
        """Model contains data referencing user and will be exported."""
        return dict(super(cls, cls).get_export_policy(), **{
            'id':base_models.EXPORT_POLICY.EXPORTED_AS_KEY_FOR_TAKEOUT_DICT,
            'platform': base_models.EXPORT_POLICY.EXPORTED,
            'scrubbed_by': base_models.EXPORT_POLICY.EXPORTED,
            'ticket_id': base_models.EXPORT_POLICY.EXPORTED,
            'submitted_on': base_models.EXPORT_POLICY.EXPORTED,
            'report_type': base_models.EXPORT_POLICY.EXPORTED,
            'category': base_models.EXPORT_POLICY.EXPORTED,
            'platform_version': base_models.EXPORT_POLICY.EXPORTED,
            'country_locale_code': base_models.EXPORT_POLICY.EXPORTED,
            'android_device_model': base_models.EXPORT_POLICY.EXPORTED,
            'android_sdk_version': base_models.EXPORT_POLICY.EXPORTED,
            'entry_point': base_models.EXPORT_POLICY.EXPORTED,
            'text_language_code': base_models.EXPORT_POLICY.EXPORTED,
            'audio_language': base_models.EXPORT_POLICY.EXPORTED,
            'android_report_info': base_models.EXPORT_POLICY.EXPORTED,
            'android_report_info_schema_version': 
                base_models.EXPORT_POLICY.EXPORTED,
            'web_report_info': base_models.EXPORT_POLICY.EXPORTED,
            'web_report_info_schema_version': 
                base_models.EXPORT_POLICY.EXPORTED
        })

    @classmethod
    def export_data(cls, user_id):
        """Exports the data from AppFeedbackReportModel
        into dict format for Takeout.

        Args:
            user_id: str. The ID of the user whose data should be exported;
            this would be the ID of the user who has scrubbed the report.

        Returns:
            dict. Dictionary of the data from AppFeedbackReportModel.
        """

        user_data = dict()
        report_models = cls.get_all().filter(
            cls.scrubbed_by == user_id).fetch()

        for report_model in report_models:
            user_data[report_model.id] = {
                'platform': report_model.platform,
                'ticket_id': report_model.ticket_id,
                'submitted_on': report_model.submitted_on,
                'report_type': report_model.report_type,
                'category': report_model.category,
                'platform_version': report_model.platform_version,
                'device_country_locale_code': (
                    report_model.device_country_locale_code),
                'android_device_model': report_model.android_device_model,
                'android_sdk_version': report_model.android_sdk_version,
                'entry_point': report_model.entry_point,
                'entry_point_topic_id': report_model.entry_point_story_id,
                'entry_point_story_id': report_model.entry_point_story_id,
                'entry_point_exploration_id': (
                    report_model.entry_point_exploration_id),
                'entry_point_subtopic_id': entry_point_subtopic_id,
                'text_language_code': report_model.text_language_code,
                'audio_language_code': report_model.audio_language_code,
                'android_report_info': report_model.android_report_info,
                'android_report_info_schema_version': (
                    report_model.android_report_info_schema_version),
                'web_report_info':report_model.web_report_info,
                'web_report_info_schema_version': (
                    report_model.web_report_info_schema_version)
            }
        return user_data

    @staticmethod
    def get_model_association_to_user():
        """Model is exported as multiple instances per user since there
        are multiple reports relevant to a user.
        """
        return base_models.MODEL_ASSOCIATION_TO_USER.MULTIPLE_INSTANCES_PER_USER

    @staticmethod
    def get_lowest_supported_role():
        """The lowest supported role for feedback reports will be moderator"""
        return feconf.ROLE_ID_MODERATOR


class AppFeedbackReportTicketModel(base_models.BaseModel):
    """Model for storing tickets created to triage feedback reports.

    Instances of this model contain information about ticket and associated
    reports.

    The id of each model instance is created by combining the entity's
    ticket_name hash, creation timestamp, and a random 16-character string
    """

    # A name for the ticket given by the maintainer, limited to 100 characters.
    # Tickets with the same ID must have the same name.
    ticket_name = datastore_services.StringProperty(required=True, indexed=True)
    # Github issue number that applies to this ticket
    github_issue_number = datastore_services.IntegerProperty(
        required=True, indexed=True)
    # Whether this ticket has been archived
    is_archived = datastore_services.BooleanProperty(
        required=True, indexed=False)
    # The datetime in UTC that the newest report in this ticket was created on,
    # to help with sorting tickets.
    newest_report_timestamp = datastore_services.DateTimeProperty(
        required=True, indexed=True)
    # A list of report IDs associated with this ticket
    report_ids = datastore_services.StringProperty(indexed=True, repeated=True)

    @staticmethod
    def get_deletion_policy():
        """Model doesn't contain any information directly corresponding to a
        user.
        """
        return base_models.DELETION_POLICY.NOT_APPLICABLE

    @classmethod
    def get_export_policy(cls):
        """Model doesn't contain any data directly corresponding to a user."""
        return dict(super(cls, cls).get_export_policy(), **{
            'ticket_name': base_models.EXPORT_POLICY.NOT_APPLICABLE,
            'github_issue_number': base_models.EXPORT_POLICY.NOT_APPLICABLE,
            'is_archived': base_models.EXPORT_POLICY.NOT_APPLICABLE,
            'newest_report_timestamp': base_models.EXPORT_POLICY.NOT_APPLICABLE,
            'report_ids': base_models.EXPORT_POLICY.NOT_APPLICABLE
        })

    @staticmethod
    def get_model_association_to_user():
        """Model doesn't contain any user data."""
        return base_models.MODEL_ASSOCIATION_TO_USER.NOT_CORRESPONDING_TO_USER

    @staticmethod
    def get_lowest_supported_role():
        """The lowest supported role for feedback report tickets will be
        moderator
        """
        return feconf.ROLE_ID_MODERATOR


class AppFeedbackReportStatsModel(base_models.VersionedModel):
    """Model for storing aggregate report stats on the tickets created.

    Instances of this model contain statistics for different report types based
    on the ticket they are assigned to and the date of the aggregation is on.

    The id of each model instance is calculated by concatenating the platform,
    ticket ID, and the date (in isoformat) this entity is tracking stats for.
    """
    
    # The unique ticket ID that this entity is aggregating for
    ticket_id = datastore_services.StringProperty(required=True, indexed=True)
    # The platform that these statistics are for
    platform = datastore_services.TextProperty(
        required=True, indexed=False, choices=PLATFORM_CHOICES)
    # The date in UTC that this entity is tracking on -- this should correspond
    # to the creation date of the reports aggregated in this model
    stats_tracking_date = datastore_services.DateProperty(
        required=True, indexed=False)
    # JSON struct that maps the daily statistics for this ticket on the date
    # specified in stats_tracking_date. The JSON will look contain two keys:
    # daily_param_stats and daily_total_reports_submitted.
    # The daily_param_stats will map each param_name (defined below
    # by the const ALLOWED_STATS_PARAM_NAMES) to a dictionary of all the
    # possible param_values for that parameter and the number of reports
    # submitted on that day that satisfy that param value"
    #
    #   daily_param_stats : { param_name1 : { param_value1 : report_count1,
    #                                         param_value2 : report_count2,
    #                                         param_value3 : report_count3 } ,
    #                         param_name2 : { param_value1 : report_count1,
    #                                         param_value2 : report_count2,
    #                                         param_value3 : report_count3 } }
    #
    # The second key in the JSON -- daily_total_reports_submitted -- simply has
    # the total number of reports submitted on this date.
    #
    #   daily_total_reports_submitted : total_reports_count
    #
    daily_ticket_stats = datastore_services.JsonProperty(
        required=True, indexed=False)
    # The schema version for parameter statistics in this entity
    daily_ticket_stats_schema_version = datastore_services.IntegerProperty(
        required=True, indexed=False)

    @staticmethod
    def get_deletion_policy():
        """Model doesn't contain any information directly corresponding to a
        user.
        """
        return base_models.DELETION_POLICY.NOT_APPLICABLE

    @classmethod
    def get_export_policy(cls):
        """Model doesn't contain any data directly corresponding to a user."""
        return dict(super(cls, cls).get_export_policy(), **{
            'ticket_id': base_models.EXPORT_POLICY.NOT_APPLICABLE,
            'platform': base_models.EXPORT_POLICY.NOT_APPLICABLE,
            'stats_tracking_date': base_models.EXPORT_POLICY.NOT_APPLICABLE,
            'daily_ticket_stats_schema_version':
                base_models.EXPORT_POLICY.NOT_APPLICABLE,
            'daily_tickets_stats': base_models.EXPORT_POLICY.NOT_APPLICABLE
        })

    @staticmethod
    def get_model_association_to_user():
        """Model doesn't contain any user data."""
        return base_models.MODEL_ASSOCIATION_TO_USER.NOT_CORRESPONDING_TO_USER

    @staticmethod
    def get_lowest_supported_role():
        """The lowest supported role for feedback reports stats will be
        moderator
        """
        return feconf.ROLE_ID_MODERATOR
