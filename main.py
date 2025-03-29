import asyncio
import logging.handlers
import os
import sys
import typing as t
from datetime import datetime

from telebot import logger
from telebot import types
from telebot.async_telebot import AsyncTeleBot

import src.config
from src.datautils import date_format, update_database_schema
from src.datautils.bodymass import add_bodymass_record_now, delete_user_bodymass_data, \
    plot_user_bodymass_data, user_bodymass_data_to_csv, \
    CSVParsingError, user_bodymass_data_from_csv_url, add_bodymass_record
from src.datautils.challenge import get_challenge, insert_challenge, get_challenge_not_none, Challenge, \
    delete_challenges, get_active_challenge, get_desired_speed_per_week
from src.datautils.conversation import get_conversation_data, write_conversation_data, ConversationState, Language
from src.glossaries import Glossary

bot = AsyncTeleBot(src.config.TELEGRAM_TOKEN)

debug_mode = False
if os.environ.get("DEBUG"):
    debug_mode = True

if debug_mode:
    logger.setLevel(logging.DEBUG)
    logger.info("Enabling debug logging")
else:
    logger.setLevel(logging.INFO)

if os.environ.get("UPDATE_DATABASE"):
    logger.info("UPDATE_DATABASE is defined. Updating database schema.")
    update_database_schema()

os.makedirs('logs', exist_ok=True)
fh = logging.handlers.TimedRotatingFileHandler('logs/log', when='midnight', encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'))
logger.addHandler(fh)


def glossary(user_data: dict) -> Glossary:
    return Glossary(user_data.get('language'))


@bot.message_handler(content_types=['document'])
@bot.message_handler(func=lambda _: True)
async def handler(message):
    logger.info("Message from %s: %s", message.chat.id, message.text)
    try:
        user_data = await get_conversation_data(message.chat.id)
        await reply(message, user_data)
    except Exception as exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.critical("Unexpected error [%s:%d]: %s: %s" % (fname, exc_tb.tb_lineno, type(exception).__name__,
                                                              exception))


def reply_markup(buttons):
    markup = types.ReplyKeyboardMarkup()
    markup.row(*buttons)
    markup.one_time_keyboard = True
    return markup


def default_markup(user_data: dict):
    return reply_markup([glossary(user_data).enter_weight_button(), glossary(user_data).show_menu_button()])


async def reply(message: types.Message, user_data: dict):
    logger.debug("User data:" + str(user_data))

    conversation_state = user_data['conversation_state']

    message_text = message.text.strip() if message.text is not None else ''

    if message_text:
        # ======================
        #    SPECIAL COMMANDS
        # ======================
        if message_text == '/info':
            await reply_info(message, user_data)
        elif message_text in glossary(user_data).enter_weight_commands():
            await reply_enter_weight(message, user_data)
        elif message_text in glossary(user_data).show_menu_commands():
            await reply_start(message, user_data)
        elif message_text == '/plot':
            await reply_plot(message, user_data)
        elif message_text == '/plot_all':
            await reply_plot_all(message, user_data)
        elif message_text == '/download':
            await reply_download(message, user_data)
        elif message_text == '/upload':
            await reply_upload(message, user_data)
        elif message_text == '/erase':
            await reply_erase(message, user_data)
        elif message_text == '/language':
            await reply_language(message, user_data)
        elif message_text == '/notfat':
            await reply_notfat(message, user_data)
        elif message_text == '/challenge':
            await reply_challenge(message, user_data)
        elif message_text == '/clear_challenge':
            await reply_clear_challenge(message, user_data)
        # ======================
        #  END SPECIAL COMMANDS
        # ======================

        # Special commands prioritized, then everything else
        elif conversation_state == ConversationState.awaiting_body_weight:
            await reply_body_weight(message, user_data)
        elif conversation_state == ConversationState.awaiting_erase_confirmation:
            await reply_erase_confirmation(message, user_data)
        elif conversation_state == ConversationState.awaiting_csv_table:
            await reply_csv_table(message, user_data)
        elif message.document is not None:
            await reply_unexpected_document(message, user_data)
        elif conversation_state == ConversationState.init:
            await reply_start(message, user_data)
        elif conversation_state == ConversationState.awaiting_language:
            await reply_language_selected(message, user_data)
        elif conversation_state == ConversationState.start_challenge_confirm:
            await reply_start_challenge_confirm(message, user_data)
        elif conversation_state == ConversationState.awaiting_starting_weight:
            await reply_starting_weight(message, user_data)
        elif conversation_state == ConversationState.awaiting_starting_date:
            await reply_starting_date(message, user_data)
        elif conversation_state == ConversationState.awaiting_target_weight:
            await reply_target_weight(message, user_data)
        elif conversation_state == ConversationState.awaiting_target_date:
            await reply_target_date(message, user_data)
        elif conversation_state == ConversationState.awaiting_challenge_finalize_confirmation:
            await reply_challenge_finalize_confirmation(message, user_data)
        elif conversation_state == ConversationState.clear_challenge_confirm:
            await reply_clear_challenge_confirm(message, user_data)
        else:
            logger.critical(f"Invalid conversation state: {conversation_state}. Forcing init state.")
            user_data['conversation_state'] = ConversationState.init
    else:
        if conversation_state == ConversationState.awaiting_csv_table:
            await reply_csv_table(message, user_data)
        elif message.document is not None:
            await reply_unexpected_document(message, user_data)

    await write_conversation_data(message.chat.id, user_data)


async def reply_info(message: types.Message, user_data: dict):
    text = glossary(user_data).info()

    await bot.send_message(message.chat.id, text,
                           reply_markup=default_markup(user_data),
                           parse_mode="HTML",
                           disable_web_page_preview=True)
    user_data['conversation_state'] = ConversationState.init


async def reply_notfat(message: types.Message, user_data: dict):
    text = glossary(user_data).notfat(message.id)
    try:
        text = text.replace("%USERNAME%", message.chat.first_name or f'@{message.chat.username}' or "%USERNAME%")
    except:
        pass

    await bot.send_message(message.chat.id, text,
                           reply_markup=default_markup(user_data),
                           parse_mode="HTML",
                           disable_web_page_preview=True)
    user_data['conversation_state'] = ConversationState.init


async def reply_challenge(message: types.Message, user_data: dict):
    challenge = await get_challenge(message.chat.id)

    if (not challenge) or (not challenge.is_active):
        return await _reply_ask_new_challenge(message, user_data)

    try:
        desired_speed = get_desired_speed_per_week(challenge)
    except (ValueError, ZeroDivisionError):
        logger.error(f"Unexpected existing challenge info: {challenge}. Asking user to create a new one.")
        return await _reply_ask_new_challenge(message, user_data)

    img_path, speed_week_kg, mean_mass = await plot_user_bodymass_data(message.chat.id,
                                                                       only_two_weeks=False,
                                                                       only_challenge_range=True,
                                                                       plot_label=glossary(
                                                                        user_data).bodyweight_plot_label())

    text = glossary(user_data).challenge_reply_template().format(
        target_weight=challenge.target_weight,
        target_date=challenge.end_date,
        start_weight=challenge.start_weight,
        start_date=challenge.start_date,
        desired_speed=desired_speed,
        current_speed=speed_week_kg
    )

    with open(img_path, 'rb') as img_file_object:
        await bot.send_photo(message.chat.id, caption=text,
                             photo=img_file_object,
                             reply_markup=default_markup(user_data),
                             reply_to_message_id=message.id,
                             parse_mode='HTML')

    try:
        os.remove(img_path)
    except OSError:
        pass

    user_data['conversation_state'] = ConversationState.init


async def _reply_ask_new_challenge(message: types.Message, user_data: dict):
    text = glossary(user_data).start_challenge_question()
    markup = glossary(user_data).confirmation_markup()
    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=reply_markup(markup),
                           parse_mode="HTML")
    user_data['conversation_state'] = ConversationState.start_challenge_confirm


async def reply_start(message: types.Message, user_data: dict):
    text = glossary(user_data).hello()
    text += glossary(user_data).command_list()

    await bot.send_message(message.chat.id, text, reply_markup=default_markup(user_data), parse_mode="HTML")
    user_data['conversation_state'] = ConversationState.init


async def reply_enter_weight(message: types.Message, user_data: dict):
    text = glossary(user_data).how_much_do_you_weigh()
    await bot.send_message(message.chat.id, text, parse_mode="HTML")
    user_data['conversation_state'] = ConversationState.awaiting_body_weight


def text_deficit_maintenance_surplus(speed_week_kg: t.Optional[float], mean_mass: float, user_data: dict) -> str:
    text = ""
    if speed_week_kg is not None:
        maintenance_threshold = mean_mass * src.config.MAINTENANCE_THRESHOLD
        if abs(speed_week_kg) < maintenance_threshold:
            text += glossary(user_data).you_are_maintaining()
        else:
            if speed_week_kg > 0:
                text += glossary(user_data).you_are_surplus()
            else:
                text += glossary(user_data).you_are_deficit()

        if speed_week_kg > 0:
            text += glossary(user_data).you_are_gaining_template() % speed_week_kg
        elif speed_week_kg <= 0:
            text += glossary(user_data).you_are_losing_template() % abs(speed_week_kg)

        if abs(speed_week_kg) < maintenance_threshold:
            text += glossary(user_data).which_is_too_slow()

    return text


async def reply_body_weight(message: types.Message, user_data: dict):
    try:
        body_weight = validate_body_weight(message)
    except ValueError:
        await bot.reply_to(message, glossary(user_data).please_enter_valid_positive_number())
        return

    await add_bodymass_record_now(message.chat.id, body_weight)
    img_path, speed_week_kg, mean_mass = await plot_user_bodymass_data(message.chat.id,
                                                                       only_two_weeks=True,
                                                                       plot_label=glossary(
                                                                           user_data).bodyweight_plot_label())
    with open(img_path, 'rb') as img_file_object:
        text = f"{glossary(user_data).successfully_added_new_entry()}\n" \
               f"<b>{datetime.now().strftime(date_format)} - {body_weight} kg</b>\n"
        text += text_deficit_maintenance_surplus(speed_week_kg, mean_mass, user_data)

        await bot.send_photo(message.chat.id, caption=text,
                             photo=img_file_object,
                             reply_markup=default_markup(user_data),
                             reply_to_message_id=message.id,
                             parse_mode='HTML')

    try:
        os.remove(img_path)
    except OSError:
        pass
    user_data['conversation_state'] = ConversationState.init


def validate_body_weight(message: types.Message):
    """
    :raises: ValueError if weight is not a float number, 0 < x < src.config.BO
    """
    body_weight = float(message.text.strip())
    if not (0 < body_weight < src.config.MAX_BODY_WEIGHT):
        raise ValueError
    return body_weight


def validate_date(message: types.Message) -> str:
    text = message.text.strip()
    if text.lower() in Glossary.todays_lowercase():
        return datetime.now().strftime(date_format)
    try:
        text = text.replace('\\', '/')  # replace backslash with slash for user-friendliness
        datetime.strptime(text, date_format)
    except (ValueError, TypeError):
        raise ValueError

    return text


async def reply_plot(message: types.Message, user_data: dict):
    img_path, speed_week_kg, mean_mass = await plot_user_bodymass_data(message.chat.id,
                                                                       only_two_weeks=True,
                                                                       plot_label=glossary(
                                                                           user_data).bodyweight_plot_label())
    with open(img_path, 'rb') as img_file_object:
        text = glossary(user_data).here_plot_last_two_weeks()
        text += text_deficit_maintenance_surplus(speed_week_kg, mean_mass, user_data)

        await bot.send_photo(message.chat.id, caption=text,
                             photo=img_file_object,
                             reply_markup=default_markup(user_data),
                             reply_to_message_id=message.id,
                             parse_mode='HTML')
    try:
        os.remove(img_path)
    except OSError:
        pass
    user_data['conversation_state'] = ConversationState.init


async def reply_plot_all(message: types.Message, user_data: dict):
    img_path, speed_week_kg, mean_mass = await plot_user_bodymass_data(message.chat.id,
                                                                       only_two_weeks=False,
                                                                       only_challenge_range=True,
                                                                       plot_label=glossary(
                                                                           user_data).bodyweight_plot_label())
    with open(img_path, 'rb') as img_file_object:
        text = glossary(user_data).here_plot_overall_progress()
        text += text_deficit_maintenance_surplus(speed_week_kg, mean_mass, user_data)

        await bot.send_photo(message.chat.id, caption=text,
                             photo=img_file_object,
                             reply_markup=default_markup(user_data),
                             reply_to_message_id=message.id,
                             parse_mode='HTML')
    try:
        os.remove(img_path)
    except OSError:
        pass

    user_data['conversation_state'] = ConversationState.init


async def reply_download(message: types.Message, user_data: dict):
    csv_file_path = await user_bodymass_data_to_csv(message.chat.id)
    file_size = os.path.getsize(csv_file_path)
    if file_size == 0:
        text = glossary(user_data).no_data_to_download_yet()
        await bot.reply_to(message, text, reply_markup=default_markup(user_data))
    else:
        text = glossary(user_data).here_all_your_data()
        text += glossary(user_data).you_can_analyze_or_backup()
        with open(csv_file_path, 'rb') as csv_file_object:
            await bot.send_document(chat_id=message.chat.id,
                                    reply_to_message_id=message.id,
                                    reply_markup=default_markup(user_data),
                                    document=csv_file_object,
                                    parse_mode='HTML',
                                    caption=text)
    try:
        os.remove(csv_file_path)
    except OSError:
        pass

    user_data['conversation_state'] = ConversationState.init


async def reply_upload(message: types.Message, user_data: dict):
    text = glossary(user_data).reply_upload()
    await bot.reply_to(message, text)
    user_data['conversation_state'] = ConversationState.awaiting_csv_table


async def reply_csv_table(message: types.Message, user_data: dict):
    document = message.document
    if document is None:
        await bot.reply_to(message, glossary(user_data).no_valid_document())
        return

    file_id = document.file_id
    file_size = document.file_size
    if file_size > src.config.MAX_FILE_SIZE:
        await bot.reply_to(message, glossary(user_data).file_too_big())
        return

    file_info = await bot.get_file(file_id)
    file_url = 'https://api.telegram.org/file/bot{0}/{1}'.format(src.config.TELEGRAM_TOKEN, file_info.file_path)

    try:
        await user_bodymass_data_from_csv_url(message.chat.id, file_url, src.config.MAX_BODY_WEIGHT)
    except CSVParsingError:
        await bot.reply_to(message, glossary(user_data).file_invalid())
        return
    except Exception as exception:
        await bot.reply_to(message, glossary(user_data).file_unexpected_error())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.critical("Unexpected error while processing CSV file [%s:%d]: %s: %s" % (fname, exc_tb.tb_lineno,
                                                                                        type(exception).__name__,
                                                                                        exception))

        return

    img_path, speed_week_kg, mean_mass = await plot_user_bodymass_data(message.chat.id,
                                                                       only_two_weeks=False,
                                                                       plot_label=glossary(
                                                                           user_data).bodyweight_plot_label())
    with open(img_path, 'rb') as img_file_object:
        text = glossary(user_data).data_uploaded_successfully()
        await bot.send_photo(message.chat.id, caption=text,
                             photo=img_file_object,
                             reply_markup=default_markup(user_data),
                             reply_to_message_id=message.id,
                             parse_mode='HTML')

    user_data['conversation_state'] = ConversationState.init
    try:
        os.remove(img_path)
    except OSError:
        pass


async def reply_erase(message: types.Message, user_data: dict):
    text = glossary(user_data).reply_erase()
    await bot.reply_to(message, text, parse_mode='HTML')
    user_data['conversation_state'] = ConversationState.awaiting_erase_confirmation


async def reply_erase_confirmation(message, user_data: dict):
    if message.text.strip().lower() != glossary(user_data).confirmation_word():
        text = glossary(user_data).cancel_delete()
        await bot.reply_to(message, text, reply_markup=default_markup(user_data))
        user_data['conversation_state'] = ConversationState.init
        return

    csv_file_path = await user_bodymass_data_to_csv(message.chat.id)
    await delete_user_bodymass_data(message.chat.id)
    await delete_challenges(message.chat.it)

    file_size = os.path.getsize(csv_file_path)
    if file_size == 0:
        text = glossary(user_data).no_data_yet()
        await bot.reply_to(message, text, reply_markup=default_markup(user_data))
        user_data['conversation_state'] = ConversationState.init
        return

    text = glossary(user_data).erase_complete()

    with open(csv_file_path, 'rb') as csv_file_object:
        await bot.send_document(chat_id=message.chat.id,
                                reply_to_message_id=message.id,
                                reply_markup=default_markup(user_data),
                                document=csv_file_object,
                                caption=text)
    try:
        os.remove(csv_file_path)
    except OSError:
        pass
    user_data['conversation_state'] = ConversationState.init


async def reply_unexpected_document(message: types.Message, user_data: dict):
    text = glossary(user_data).unexpected_document()
    await bot.reply_to(message, text, reply_markup=default_markup(user_data))
    user_data['conversation_state'] = ConversationState.init


async def reply_language(message: types.Message, user_data: dict):
    text = Glossary.select_language()
    await bot.reply_to(message, text, reply_markup=reply_markup(["English", "Русский"]))
    user_data['conversation_state'] = ConversationState.awaiting_language


async def reply_language_selected(message: types.Message, user_data: dict):
    language = message.text.strip().lower()
    language_map = {
        'english': Language.english,
        'русский': Language.russian
    }
    if language not in language_map:
        await bot.reply_to(message, Glossary.unknown_language(), reply_markup=reply_markup(["English", "Русский"]))
        return

    user_data['language'] = language_map[language]

    text = glossary(user_data).language_selected()
    await bot.reply_to(message, text, reply_markup=default_markup(user_data))
    user_data['conversation_state'] = ConversationState.init


async def reply_clear_challenge(message: types.Message, user_data: dict):
    text = glossary(user_data).disable_challenge_question()
    await bot.reply_to(message, text, reply_markup=reply_markup(glossary(user_data).confirmation_markup()))
    user_data['conversation_state'] = ConversationState.clear_challenge_confirm


async def reply_clear_challenge_confirm(message: types.Message, user_data: dict):
    try:
        result = message.text.strip().lower()
    except (AttributeError, TypeError):
        result = ''

    if result in Glossary.confirmation_words():
        await insert_challenge(Challenge(user_id=str(message.chat.id), is_active=0))
        text = glossary(user_data).challenge_disabled()
    else:
        text = glossary(user_data).action_cancelled()

    await bot.reply_to(message, text)

    user_data['conversation_state'] = ConversationState.init


async def reply_start_challenge_confirm(message: types.Message, user_data: dict):
    text = message.text.strip()
    if text.lower() not in Glossary.confirmation_words():
        await reply_start(message, user_data)
        user_data['conversation_state'] = ConversationState.init
        return

    challenge = Challenge(user_id=str(message.chat.id))
    challenge.is_active = 0
    await insert_challenge(challenge)

    answer = glossary(user_data).enter_starting_weight()
    await bot.reply_to(message, answer)
    user_data['conversation_state'] = ConversationState.awaiting_starting_weight


async def reply_starting_weight(message: types.Message, user_data: dict):
    try:
        body_weight = validate_body_weight(message)
    except ValueError:
        await bot.reply_to(message, glossary(user_data).please_enter_valid_positive_number())
        return

    challenge = await get_challenge_not_none(message.chat.id)
    challenge.start_weight = body_weight
    challenge.is_active = 0

    await insert_challenge(challenge)

    answer = glossary(user_data).enter_starting_date()
    today = glossary(user_data).today_lowercase().capitalize()
    await bot.reply_to(message, answer, parse_mode="HTML", reply_markup=reply_markup([today]))
    user_data['conversation_state'] = ConversationState.awaiting_starting_date


async def reply_starting_date(message: types.Message, user_data: dict):
    try:
        start_date = validate_date(message)
    except ValueError:
        await bot.reply_to(message, glossary(user_data).please_enter_valid_date())
        return

    challenge = await get_challenge_not_none(message.chat.id)
    assert challenge.start_weight, "start_weight expected to be specified at this point of interaction with user"
    challenge.start_date = start_date
    challenge.is_active = 0

    await insert_challenge(challenge)

    answer = glossary(user_data).enter_target_weight()
    await bot.reply_to(message, answer)
    user_data['conversation_state'] = ConversationState.awaiting_target_weight


async def reply_target_weight(message: types.Message, user_data: dict):
    try:
        target_weight = validate_body_weight(message)
    except ValueError:
        await bot.reply_to(message, glossary(user_data).please_enter_valid_positive_number())
        return

    challenge = await get_challenge_not_none(message.chat.id)
    assert challenge.start_weight, "start_weight expected to be specified at this point of interaction with user"
    assert challenge.start_date, "start_date expected to be specified at this point of interaction with user"

    # if target_weight == challenge.start_weight:
    #     await bot.reply_to(message, "Target weight cannot be the same as the starting weight.\nTry again")
    #     return

    challenge.target_weight = target_weight
    challenge.is_active = 0

    await insert_challenge(challenge)
    answer = glossary(user_data).when_do_you_want_to_reach_template().format(target_weight=challenge.target_weight)
    await bot.reply_to(message, answer, parse_mode="HTML")
    user_data['conversation_state'] = ConversationState.awaiting_target_date


async def reply_target_date(message: types.Message, user_data: dict):
    try:
        target_date = validate_date(message)
    except ValueError:
        await bot.reply_to(message, glossary(user_data).please_enter_valid_date())
        return

    challenge = await get_challenge_not_none(message.chat.id)
    assert challenge.start_weight, "start_weight expected to be specified at this point of interaction with user"
    assert challenge.start_date, "start_date expected to be specified at this point of interaction with user"
    assert challenge.target_weight, "target_weight expected to be specified at this point of interaction with user"

    if datetime.strptime(challenge.start_date, date_format) > datetime.strptime(target_date, date_format):
        text = glossary(user_data).target_date_cannot_be_earlier_template().format(start_date=challenge.start_date)
        await bot.reply_to(message, text)
        return

    challenge.end_date = target_date
    challenge.is_active = 0

    await insert_challenge(challenge)

    answer = glossary(user_data).please_confirm() + '\n\n'
    if challenge.start_weight < challenge.target_weight:
        answer += glossary(user_data).you_want_to_gain_weight_template().format(start_weight=challenge.start_weight,
                                                                                target_weight=challenge.target_weight)
    elif challenge.start_weight > challenge.target_weight:
        answer += glossary(user_data).you_want_to_lose_weight_template().format(start_weight=challenge.start_weight,
                                                                                target_weight=challenge.target_weight)
    else:
        answer += glossary(user_data).you_want_to_maintain_weight()

    answer += '\n'
    answer += glossary(user_data).you_start_and_finish_template().format(start_date=challenge.start_date,
                                                                         target_date=challenge.end_date) + '\n'

    start_datetime = datetime.strptime(challenge.start_date, date_format)
    end_datetime = datetime.strptime(challenge.end_date, date_format)
    delta = end_datetime - start_datetime
    answer += glossary(user_data).your_challenge_will_last_template().format(days=delta.days) + '\n'
    answer += glossary(user_data).your_desired_speed_is_template().format(speed=get_desired_speed_per_week(challenge))

    await bot.reply_to(message, answer, parse_mode="HTML", reply_markup=reply_markup(glossary(user_data).yes_cancel_markup()))
    user_data['conversation_state'] = ConversationState.awaiting_challenge_finalize_confirmation


async def reply_challenge_finalize_confirmation(message: types.Message, user_data: dict):
    text = message.text.strip()
    if text.lower() not in  Glossary.confirmation_words():
        await bot.reply_to(message, glossary(user_data).action_cancelled())
        user_data['conversation_state'] = ConversationState.init
        return

    challenge = await get_challenge_not_none(message.chat.id)
    assert challenge.start_weight, 'all challenge fields expected to be specified'
    assert challenge.start_date, 'all challenge fields expected to be specified'
    assert challenge.target_weight, 'all challenge fields expected to be specified'
    assert challenge.end_date, 'all challenge fields expected to be specified'
    challenge.is_active = 1

    await insert_challenge(challenge)
    await add_bodymass_record(challenge.user_id,
                              datetime.strptime(challenge.start_date, date_format),
                              challenge.start_weight)
    answer = glossary(user_data).challenge_successfully_created()
    await bot.reply_to(message, answer)
    user_data['conversation_state'] = ConversationState.init


asyncio.run(bot.polling(non_stop=True))
