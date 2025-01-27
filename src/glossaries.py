import random

import src.glossary_english
import src.glossary_russian

from src.conversationdata import Language, DEFAULT_LANGUAGE


def _modules():
    return src.glossary_english, src.glossary_russian


class Glossary:
    def __init__(self, language: str = None):
        self.language = language or DEFAULT_LANGUAGE

    def _module(self):
        if self.language == Language.russian:
            return src.glossary_russian
        else:
            return src.glossary_english

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

