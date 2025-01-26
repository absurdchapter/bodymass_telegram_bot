import asyncio
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional

from telebot.async_telebot import AsyncTeleBot
from telebot import types
from telebot import logger

from src.glossaries import Glossary
from src.conversationdata import get_conversation_data, write_conversation_data, ConversationState
from src.datautils import (plot_user_data, add_record_now, date_format, user_data_to_csv, user_data_from_csv_url,
                           delete_user_data)
from src.datautils import CSVParsingError
import src.config


bot = AsyncTeleBot(src.config.TELEGRAM_TOKEN)

logger.setLevel(logging.DEBUG)
os.makedirs('logs', exist_ok=True)
fh = logging.handlers.TimedRotatingFileHandler('logs/log', when='midnight', encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'))
logger.addHandler(fh)


def glossary(user_dict: dict) -> Glossary:
    return Glossary(user_dict.get('language'))


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
    logger.debug("User data:"+str(user_data))

    conversation_state = user_data['conversation_state']

    message_text = message.text.strip() if message.text is not None else ''

    if message_text:
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
        else:
            assert False, "Conversation state assertion"
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


async def reply_start(message: types.Message, user_data: dict):
    text = glossary(user_data).hello()
    text += glossary(user_data).command_list()

    await bot.send_message(message.chat.id, text, reply_markup=default_markup(user_data), parse_mode="HTML")
    user_data['conversation_state'] = ConversationState.init


async def reply_enter_weight(message: types.Message, user_data: dict):
    text = glossary(user_data).how_much_do_you_weight()
    await bot.send_message(message.chat.id, text, parse_mode="HTML")
    user_data['conversation_state'] = ConversationState.awaiting_body_weight


def text_deficit_maintenance_surplus(speed_week_kg: Optional[float], mean_mass: float, user_data: dict) -> str:
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
        body_weight = float(message.text.strip())
        if not (0 < body_weight < src.config.MAX_BODY_WEIGHT):
            raise ValueError
    except ValueError:
        await bot.reply_to(message, glossary(user_data).please_enter_valid_positive_number())
        return

    await add_record_now(message.chat.id, body_weight)
    img_path, speed_week_kg, mean_mass = await plot_user_data(message.chat.id,
                                                              only_two_weeks=True,
                                                              plot_label=glossary(user_data).bodyweight_plot_label())
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


async def reply_plot(message: types.Message, user_data: dict):
    img_path, speed_week_kg, mean_mass = await plot_user_data(message.chat.id,
                                                              only_two_weeks=True,
                                                              plot_label=glossary(user_data).bodyweight_plot_label())
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
    img_path, speed_week_kg, mean_mass = await plot_user_data(message.chat.id,
                                                              only_two_weeks=False,
                                                              plot_label=glossary(user_data).bodyweight_plot_label())
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
    csv_file_path = await user_data_to_csv(message.chat.id)
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
        await user_data_from_csv_url(message.chat.id, file_url, src.config.MAX_BODY_WEIGHT)
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

    img_path, speed_week_kg, mean_mass = await plot_user_data(message.chat.id,
                                                              only_two_weeks=False,
                                                              plot_label=glossary(user_data).bodyweight_plot_label())
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

    csv_file_path = await user_data_to_csv(message.chat.id)
    await delete_user_data(message.chat.id)

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

asyncio.run(bot.polling(non_stop=True))
