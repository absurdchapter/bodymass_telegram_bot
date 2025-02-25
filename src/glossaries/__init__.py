import random

import src.glossaries._english as _english
import src.glossaries._russian as _russian
from src.datautils.conversation import Language, DEFAULT_LANGUAGE


def _modules():
    return _english, _russian


class Glossary:
    def __init__(self, language: str = None):
        self.language = language or DEFAULT_LANGUAGE

    def _module(self):
        if self.language == Language.russian:
            return _russian
        else:
            return _english

    def command_list(self) -> str:
        return self._module().COMMAND_LIST

    def enter_weight_button(self) -> str:
        return self._module().ENTER_WEIGHT_BUTTON

    @classmethod
    def enter_weight_commands(cls) -> list[str]:
        # Merge all languages (for edge cases, e.g. user has just changed language)
        return sum((module.ENTER_WEIGHT_COMMANDS for module in _modules()), [])

    def show_menu_button(self) -> str:
        return self._module().SHOW_MENU_BUTTON

    @classmethod
    def show_menu_commands(cls) -> list[str]:
        # Merge all languages (for edge cases, e.g. user has just changed language)
        return sum((module.SHOW_MENU_COMMANDS for module in _modules()), [])

    def info(self) -> str:
        return self._module().INFO

    def hello(self) -> str:
        return self._module().HELLO

    def how_much_do_you_weigh(self) -> str:
        return self._module().HOW_MUCH_DO_YOU_WEIGH

    def you_are_maintaining(self) -> str:
        return self._module().YOU_ARE_MAINTAINING

    def you_are_surplus(self) -> str:
        return self._module().YOU_ARE_SURPLUS

    def you_are_deficit(self) -> str:
        return self._module().YOU_ARE_DEFICIT

    def you_are_gaining_template(self) -> str:
        return self._module().YOU_ARE_GAINING_TEMPLATE

    def you_are_losing_template(self) -> str:
        return self._module().YOU_ARE_LOSING_TEMPLATE

    def which_is_too_slow(self) -> str:
        return self._module().WHICH_IS_TOO_SLOW

    def please_enter_valid_positive_number(self) -> str:
        return self._module().PLEASE_ENTER_VALID_POSITIVE_NUMBER

    def successfully_added_new_entry(self) -> str:
        return self._module().SUCCESSFULLY_ADDED_NEW_ENTRY

    def here_plot_last_two_weeks(self) -> str:
        return self._module().HERE_PLOT_LAST_TWO_WEEKS

    def here_plot_overall_progress(self) -> str:
        return self._module().HERE_PLOT_OVERALL_PROGRESS

    def no_data_to_download_yet(self) -> str:
        return self._module().NO_DATA_TO_DOWNLOAD_YET

    def here_all_your_data(self) -> str:
        return self._module().HERE_ALL_YOUR_DATA

    def you_can_analyze_or_backup(self) -> str:
        return self._module().YOU_CAN_ANALYZE_OR_BACKUP

    def reply_upload(self) -> str:
        return self._module().REPLY_UPLOAD

    def no_valid_document(self) -> str:
        return self._module().NO_VALID_DOCUMENT

    def file_too_big(self) -> str:
        return self._module().FILE_TOO_BIG

    def file_invalid(self) -> str:
        return self._module().FILE_INVALID

    def file_unexpected_error(self) -> str:
        return self._module().FILE_UNEXPECTED_ERROR

    def data_uploaded_successfully(self) -> str:
        return self._module().DATA_UPLOADED_SUCCESSFULLY

    def confirmation_word(self) -> str:
        return self._module().CONFIRMATION_WORD

    @classmethod
    def confirmation_words(cls) -> list[str]:
        return [module.CONFIRMATION_WORD for module in _modules()]

    def reply_erase(self) -> str:
        return self._module().REPLY_ERASE

    def cancel_delete(self) -> str:
        return self._module().CANCEL_DELETE

    def no_data_yet(self) -> str:
        return self._module().NO_DATA_YET

    def erase_complete(self) -> str:
        return self._module().ERASE_COMPLETE

    def unexpected_document(self) -> str:
        return self._module().UNEXPECTED_DOCUMENT

    def bodyweight_plot_label(self) -> str:
        return self._module().BODYWEIGHT_PLOT_LABEL

    def language_selected(self) -> str:
        return self._module().LANGUAGE_SELECTED

    @classmethod
    def select_language(cls) -> str:
        return "Select language / Выберите язык"

    @classmethod
    def unknown_language(cls) -> str:
        return "Unknown language / Неизвестный язык"

    def notfat(self, message_id: int = None):
        if not isinstance(message_id, int):
            return random.choice(self._module().NOTFAT_OPTIONS)

        # Rolling logic so that user does not get same answers.
        # The division by two is required because this is how message ids are numbered:
        # +1 for the user response, +1 for the bot response.

        message_id //= 2
        n = len(self._module().NOTFAT_OPTIONS)
        return self._module().NOTFAT_OPTIONS[message_id % n]

    def challenge_reply_template(self) -> str:
        return self._module().CHALLENGE_REPLY_TEMPLATE

    def start_challenge_question(self) -> str:
        return self._module().START_CHALLENGE_QUESTION

    def disable_challenge_question(self) -> str:
        return self._module().DISABLE_CHALLENGE_QUESTION

    def confirmation_markup(self) -> list[str]:
        return self._module().CONFIRMATION_MARKUP

    def today_lowercase(self) -> str:
        return self._module().TODAY_LOWERCASE

    @classmethod
    def todays_lowercase(cls) -> list[str]:
        return [module.TODAY_LOWERCASE for module in _modules()]

    def enter_starting_weight(self) -> str:
        return self._module().ENTER_STARTING_WEIGHT

    def enter_starting_date(self) -> str:
        return self._module().ENTER_STARTING_DATE

    def please_enter_valid_date(self) -> str:
        return self._module().PLEASE_ENTER_VALID_DATE

    def enter_target_weight(self) -> str:
        return self._module().ENTER_TARGET_WEIGHT

    def when_do_you_want_to_reach_template(self) -> str:
        return self._module().WHEN_DO_YOU_WANT_TO_REACH_TEMPLATE

    def target_date_cannot_be_earlier_template(self) -> str:
        return self._module().TARGET_DATE_CANNOT_BE_EARLIER_TEMPLATE

    def please_confirm(self) -> str:
        return self._module().PLEASE_CONFIRM

    def you_want_to_lose_weight_template(self) -> str:
        return self._module().YOU_WANT_TO_LOSE_WEIGHT_TEMPLATE

    def you_want_to_gain_weight_template(self) -> str:
        return self._module().YOU_WANT_TO_GAIN_WEIGHT_TEMPLATE

    def you_want_to_maintain_weight(self) -> str:
        return self._module().YOU_WANT_TO_MAINTAIN_WEIGHT

    def you_start_and_finish_template(self) -> str:
        return self._module().YOU_START_AND_FINISH_TEMPLATE

    def your_challenge_will_last_template(self) -> str:
        return self._module().YOUR_CHALLENGE_WILL_LAST_TEMPLATE

    def your_desired_speed_is_template(self) -> str:
        return self._module().YOUR_DESIRED_SPEED_IS_TEMPLATE

    def challenge_disabled(self) -> str:
        return self._module().CHALLENGE_DISABLED

    def action_cancelled(self) -> str:
        return self._module().ACTION_CANCELLED

    def challenge_successfully_created(self) -> str:
        return self._module().CHALLENGE_SUCCESSFULLY_CREATED

    def yes_cancel_markup(self) -> list[str]:
        return self._module().YES_CANCLEL_MARKUP