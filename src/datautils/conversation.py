import sqlite3

import aiosqlite

sqlite_db_path = 'data/bodymass.sqlite'
sqlite_db_users_conversation = 'users_conversation'
sqlite_db_users_language = 'users_language'


def _assert_enum_consistency(cls: type):
    for k, v in vars(cls).items():
        if not k.startswith('_'):
            assert k == v


class ConversationState:
    init = 'init'
    awaiting_body_weight = 'awaiting_body_weight'
    awaiting_erase_confirmation = 'awaiting_erase_confirmation'
    awaiting_csv_table = 'awaiting_csv_table'
    awaiting_language = 'awaiting_language'
    existing_challenge = 'existing_challenge'
    start_challenge_confirm = 'start_challenge_confirm'
    disable_challenge_confirm = 'disable_challenge_confirm'

    awaiting_starting_weight = 'awaiting_starting_weight'
    awaiting_starting_date = 'awaiting_starting_date'
    awaiting_target_weight = 'awaiting_target_weight'
    awaiting_target_date = 'awaiting_target_date'

    awaiting_challenge_finalize_confirmation = 'awaiting_challenge_finalize_confirmation'


_assert_enum_consistency(ConversationState)
conversation_states = [k for k in vars(ConversationState).keys() if not k.startswith('_')]


class Language:
    english = 'english'
    russian = 'russian'


DEFAULT_LANGUAGE = Language.english

_assert_enum_consistency(Language)
languages = [k for k in vars(Language).keys() if not k.startswith('_')]


async def get_conversation_data(user_id: int) -> dict:
    async with aiosqlite.connect(sqlite_db_path) as db:
        result = dict()
        result['conversation_state'] = await get_conversation_state(db, user_id)
        result['language'] = await get_language(db, user_id) or DEFAULT_LANGUAGE

        return result


async def get_conversation_state(db: aiosqlite.Connection, user_id: int) -> str:
    async with db.cursor() as cursor:
        query = f"SELECT conversation_state FROM {sqlite_db_users_conversation} " \
                f"WHERE user_id = '{user_id}';"
        await cursor.execute(query)
        conversation_state = await cursor.fetchone()
        conversation_state = conversation_state[0] if conversation_state is not None else 'init'
        assert conversation_state in conversation_states

        return conversation_state


async def get_language(db: aiosqlite.Connection, user_id: int) -> str | None:
    try:
        async with db.cursor() as cursor:
            query = f"SELECT language FROM {sqlite_db_users_language} " \
                    f"WHERE user_id = '{user_id}';"
            await cursor.execute(query)
            language = await cursor.fetchone()
            if language is not None:
                language = language[0]
                assert language in languages

            return language
    except sqlite3.OperationalError as exc:
        if str(exc) == f'no such table: {sqlite_db_users_language}':
            return
        raise exc


async def write_conversation_data(user_id: int, user_data: dict) -> None:
    async with aiosqlite.connect(sqlite_db_path) as db:
        await write_conversation_state(db, user_data['conversation_state'], user_id)
        if 'language' in user_data:
            await write_language(db, user_data['language'], user_id)


async def write_conversation_state(db: aiosqlite.Connection, conversation_state: str, user_id: int):
    query = f"INSERT INTO {sqlite_db_users_conversation} (user_id, conversation_state) " \
            f"VALUES ('{user_id}', '{conversation_state}'); "
    await db.execute(query)
    await db.commit()


async def write_language(db: aiosqlite.Connection, language: str, user_id: int):
    try:
        query = f"INSERT INTO {sqlite_db_users_language} (user_id, language) " \
                f"VALUES ('{user_id}', '{language}'); "
        await db.execute(query)
        await db.commit()
    except sqlite3.OperationalError as exc:
        if str(exc) == f'no such table: {sqlite_db_users_language}':
            return
        raise exc
