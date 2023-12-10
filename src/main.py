import asyncio
import datetime
import logging

import aiogram
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from dotenv import find_dotenv, load_dotenv
from kink import di
from sqlalchemy import asc, delete, select
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from consts import (
    BASE_REPO,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_LOGIN,
    POSTGRES_PASSWORD,
    SHOW_BASE_REPO_IN_HELP,
    SQLALCHEMY_ECHO,
    TIMEOUT_SCOREBOARD_IN_SECONDS,
    TOKEN,
)
from messages import get_help_message, get_relapse_message, get_stats_text
from middlewares.update_usernames import update_users_info
from models.database import Groups, Users

load_dotenv(find_dotenv())


di["engine"] = create_async_engine(
    f"postgresql+asyncpg://{POSTGRES_LOGIN}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}",
    echo=SQLALCHEMY_ECHO,
)

di["async_session"] = async_sessionmaker(di["engine"], expire_on_commit=False)

router = Router()
pool = None
scoreboards = {}
dp = Dispatcher()
dp.include_router(router)


async def create_all() -> None:
    conn: AsyncConnection
    async with di["engine"].begin() as conn:
        await conn.run_sync(Users.metadata.create_all)
        await conn.run_sync(Groups.metadata.create_all)


dp.update.outer_middleware.register(update_users_info)

async def delete_if_chat(message, msg_sent):
    if message.chat.id != message.from_user.id:
        await asyncio.sleep(20)
        try:
            await msg_sent.delete()
        except:
            pass


@router.message(Command(commands=["start"]))
async def command_start_handler(message: Message) -> None:
    msg = await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>. To start a streak, write /streak")
    await delete_if_chat(message, msg)

@router.message(Command(commands=["enablescoreboard", "enableScoreboard"]))
async def enablescoreboard_handler(message: Message) -> None:
    if message.chat.id == message.from_user.id:
        msg = await message.reply("🚫 You can't enable scoreboards in private chat.")
        await delete_if_chat(message, msg)
        return
    session: AsyncSession
    async with di["async_session"]() as session:
        session_result = await session.execute(
            select(Users).where(Users.user_id == message.from_user.id)
        )
        session_result = session_result.scalar()
        if session_result is None:
            msg = await message.reply("↪️ Use /streak to start a new streak.")
            await delete_if_chat(message, msg)
            return
        session_result = await session.execute(
            select(Groups).where(
                Groups.user_id == message.from_user.id,
                Groups.group_id == message.chat.id,
            )
        )
        session_result = session_result.scalar()
        if session_result is None:
            session.add(Groups(user_id=message.from_user.id, group_id=message.chat.id))
            await session.commit()
            msg = await message.reply(
                "✅ You are now appearing on the scoreboard.",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Turn this message into a scoreboard",
                                callback_data=f"turn_{message.from_user.id}",
                            )
                        ]
                    ]
                ),
            )
        else:
           msg = await message.reply(
                "🚫 You already enabled scoreboards.",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Turn this message into a scoreboard",
                                callback_data=f"turn_{message.from_user.id}",
                            )
                        ]
                    ]
                ),
            )
    await delete_if_chat(message, msg)


@router.message(Command(commands=["streak"]))
async def register_handler(message: Message) -> None:
    session: AsyncSession
    async with di["async_session"]() as session:
        session_result = await session.execute(
            select(Users).where(Users.user_id == message.from_user.id)
        )
        session_result = session_result.scalar()
        if session_result is None:
            session.add(
                Users(
                    user_id=message.from_user.id,
                    name=message.from_user.full_name,
                    username=message.from_user.username,
                    streak=datetime.datetime.now(),
                    attempts=1,
                    maximum_days=0,
                    all_days=0,
                )
            )
            await session.commit()
            msg = await message.reply("Streak has been started! You have 0 days!")
        else:
            days = (datetime.datetime.now() - session_result.streak).days
            days_str = "days" if days != 1 else "day"
            msg = await message.answer(
                f"Hey {message.from_user.full_name}.\n🔥 Your streak is {days} {days_str} long.\n\n❌ Use /relapse if you have relapsed.",
                parse_mode=None,
            )
    await delete_if_chat(message, msg)


@router.message(Command(commands=["stats"]))
async def stats_handler(message: Message) -> None:
    session: AsyncSession
    async with di["async_session"]() as session:
        session_result = await session.execute(
            select(Users).where(Users.user_id == message.from_user.id)
        )
        session_result = session_result.scalar()
        if session_result is None:
            msg = await message.reply("↪️ Use /streak to start a new streak.")
            await delete_if_chat(message, msg)
            return
        attempts = session_result.attempts
        days = (datetime.datetime.now() - session_result.streak).days

        # I believe this was taken from here: https://stackoverflow.com/questions/3644417/python-format-datetime-with-st-nd-rd-th-english-ordinal-suffix-likes
        days_text = str(attempts) + (
            "th"
            if 4 <= attempts % 100 <= 20
            else {1: "st", 2: "nd", 3: "rd"}.get(attempts % 10, "th")
        )
        msg = await message.reply(
            get_stats_text(
                name=message.from_user.full_name,
                all_days=session_result.all_days + days,
                highest=session_result.maximum_days,
                attempt=days_text,
                current=days,
            )
        )
        await delete_if_chat(message, msg)


@router.message(Command(commands=["deleteAllDataAboutMe", "deletealldataaboutme"]))
async def deleteAllDataAboutMe_handler(message: Message) -> None:
    session: AsyncSession
    async with di["async_session"]() as session:
        session_result = await session.execute(
            select(Users).where(Users.user_id == message.from_user.id)
        )
        session_result = session_result.scalar()
        if session_result is None:
            msg = await message.reply(
                "I don't have any info about you at the moment. You can register a streak with /streak command."
            )
            await delete_if_chat(message, msg)
            return
        msg = await message.reply(
            "Are you sure you want to delete <b>ALL</b> data about yourself? This is <b>IRREVERSIBLE</b> and no one on the entire planet Earth will be able to restore your streaks!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Yes",
                            callback_data=f"remove_{message.from_user.id}",
                        ),
                        InlineKeyboardButton(
                            text="No",
                            callback_data=f"cancel_{message.from_user.id}",
                        ),
                    ]
                ]
            ),
        )
        await delete_if_chat(message, msg)


@router.message(Command(commands=["relapse"]))
async def relapse_handler(message: Message) -> None:
    session: AsyncSession
    async with di["async_session"]() as session:
        session_result = await session.execute(
            select(Users).where(Users.user_id == message.from_user.id)
        )
        session_result = session_result.scalar()
        if session_result is None:
            msg = await message.reply("To start a streak, write /streak")
            await delete_if_chat(message, msg)
            return
        msg = await message.reply(
            "Are you sure you want to register a <b>relapse</b>?",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Yes",
                            callback_data=f"relapse_{message.from_user.id}",
                        ),
                        InlineKeyboardButton(
                            text="No",
                            callback_data=f"cancel_{message.from_user.id}",
                        ),
                    ]
                ]
            ),
        )
        await delete_if_chat(message, msg)


@router.callback_query(F.data.startswith("cancel_"))
async def cancel_relapse(callback_query: CallbackQuery) -> None:
    if callback_query.from_user.id != int(callback_query.data.split("_", 1)[1]):
        await callback_query.answer("🚫 This button was not meant for you")
        return
    msg = await callback_query.message.edit_text("🆗 Cancelled.")
    await delete_if_chat(callback_query, msg)


@router.message(Command(commands=["help"]))
async def help(message: Message) -> None:
    message_to_reply = get_help_message()
    if SHOW_BASE_REPO_IN_HELP:
        message_to_reply += (
            "\nIf you like this bot and want to support development, consider giving this project a star on GitHub:\n"
            + BASE_REPO
        )
    msg = await message.reply(
        message_to_reply, disable_web_page_preview=True, parse_mode=None
    )
    await delete_if_chat(message, msg)


@router.message(Command(commands=["removeFromLeaderboard", "removefromleaderboard"]))
async def check(message: Message, bot: Bot, command: CommandObject) -> None:
    if message.chat.id == message.from_user.id:
        msg = await message.reply("❌ This command works only in groups.")
        await delete_if_chat(message, msg)
        return
    if not command.args:
        msg = await message.reply(
            "❌ Not enough arguments\.\n**USAGE**:\n`/removeFromLeaderboard \<\+id/\+username\>`\n\n_Deletes an account from scoreboard \(admins only\)_",
            parse_mode="MarkdownV2",
        )
        await delete_if_chat(message, msg)
        return
    user_to_delete = command.args
    session: AsyncSession
    async with di["async_session"]() as session:
        if not user_to_delete.isnumeric():
            user_result = await session.scalar(
                select(Users).where(Users.username == user_to_delete.strip("@"))
            )
            if not user_result:
                msg = await message.reply("This user never used me")
                await delete_if_chat(message, msg)
                return
            user_to_delete = user_result.user_id
        user_to_delete = int(user_to_delete)
        user = await session.scalar(
            select(Groups).where(
                Groups.group_id == message.chat.id, Groups.user_id == user_to_delete
            )
        )
        user.is_banned = True
        try:
            user_who_deletes = await bot.get_chat_member(
                message.chat.id, message.from_user.id
            )
        except:
            msg = await message.reply(
                "I can't get chat admins! Please report this error to the support group."
            )
            await delete_if_chat(message, msg)
            return
        if (
            not user_who_deletes.can_restrict_members
            and user_who_deletes.status != "creator"
        ):
            msg = await message.reply(
                "This command is admin-only (with ability to restrict members)!"
            )
            await delete_if_chat(message, msg)
            return
        session.add(user)
        await session.commit()
        msg = await message.answer(
            f"Succesfully removed account with id {user_to_delete} from scoreboard of this group."
        )
        await delete_if_chat(message, msg)


@router.message(Command(commands=["returnToLeaderboard", "returntoleaderboard"]))
async def check(message: Message, bot: Bot, command: CommandObject) -> None:
    if message.chat.id == message.from_user.id:
        await message.reply("❌ This command works only in groups.")
        return
    if not command.args:
        msg = await message.reply(
            "❌ Not enough arguments\.\n**USAGE**:\n`/returnToLeaderboard \<\+id/\+username\>`\n\Returns an account to scoreboard if it's banned \(admins only\)_",
            parse_mode="MarkdownV2",
        )
        await delete_if_chat(message, msg)
        return
    user_to_delete = command.args
    session: AsyncSession
    async with di["async_session"]() as session:
        if not user_to_delete.isnumeric():
            user_result = await session.scalar(
                select(Users).where(Users.username == user_to_delete.strip("@"))
            )
            if not user_result:
                msg = await message.reply("This user never used me")
                await delete_if_chat(message, msg)
                return
            user_to_delete = user_result.user_id
        user_to_delete = int(user_to_delete)
        user = await session.scalar(
            select(Groups).where(
                Groups.group_id == message.chat.id, Groups.user_id == user_to_delete
            )
        )
        user.is_banned = False
        try:
            user_who_deletes = await bot.get_chat_member(
                message.chat.id, message.from_user.id
            )
        except:
            msg = await message.reply(
                "I can't get chat admins! Please report this error to the support group."
            )
            await delete_if_chat(message, msg)
            return
        if (
            not user_who_deletes.can_restrict_members
            and user_who_deletes.status != "creator"
        ):
            msg = await message.reply(
                "This command is admin-only (with ability to restrict members)!"
            )
            await delete_if_chat(message, msg)
            return
        session.add(user)
        await session.commit()
        msg = await message.answer(
            f"Succesfully returned an account with id {user_to_delete} to scoreboard of this group."
        )
        await delete_if_chat(message, msg)


@router.message(Command(commands=["check"]))
async def check(message: Message, bot: Bot, command: CommandObject) -> None:
    if not command.args:
        msg = await message.reply(
            "❌ Not enough arguments\.\n**USAGE**:\n`/check \<\+id/\+username\>`\n\n_Deletes an account from scoreboard if it's been deleted_",
            parse_mode="MarkdownV2",
        )
        await delete_if_chat(message, msg)
        return
    user_to_delete = command.args
    session: AsyncSession
    async with di["async_session"]() as session:
        if not user_to_delete.isnumeric():
            user_result = await session.scalar(
                select(Users).where(Users.username == user_to_delete.strip("@"))
            )
            if not user_result:
                msg = await message.reply("This user never used me")
                await delete_if_chat(message, msg)
                return
            user_to_delete = user_result.user_id
        else:
            user_result = await session.scalar(
                select(Users).where(Users.user_id == int(user_to_delete))
            )
            if not user_result:
                msg =await message.reply("This user never used me")
                await delete_if_chat(message, msg)
                return
            user_to_delete = int(user_to_delete)
        member = None
        try:
            member = await bot.get_chat_member(message.chat.id, user_to_delete)
        except:
            msg = await message.reply(
                "Query failed. If you sure you entered right ID, then wait some time to Telegram to wake up from maintenance or something."
            )
            await delete_if_chat(message, msg)
            return
        if not member:
            return
        if member.user.first_name != "" and member.user.first_name != "Deleted Account":
            msg = await message.reply(
                "This user is alive and hasn't deleted his account yet."
            )
            await delete_if_chat(message, msg)
            return
        await session.delete(user_result)
        await session.execute(delete(Groups).where(Groups.user_id == user_to_delete))
        await session.commit()
        msg = await message.answer(
            f"Succesfully removed account with id {user_to_delete} from my database."
        )
        await delete_if_chat(message, msg)


@router.callback_query(F.data.startswith("relapse_"))
async def register_a_relapse(callback_query: CallbackQuery) -> None:
    if callback_query.from_user.id != int(callback_query.data.split("_", 1)[1]):
        await callback_query.answer("🚫 This button was not meant for you")
        return
    session: AsyncSession
    async with di["async_session"]() as session:
        session_result = await session.execute(
            select(Users).where(Users.user_id == callback_query.from_user.id)
        )
        session_result = session_result.scalar()
        days = (datetime.datetime.now() - session_result.streak).days
        if days > session_result.maximum_days:
            session_result.maximum_days = days
        session_result.all_days += days
        session_result.streak = datetime.datetime.now()
        session_result.attempts += 1
        session.add(session_result)
        await session.commit()
        msg = await callback_query.message.edit_text(
            get_relapse_message(days=days, name=callback_query.from_user.full_name),
            disable_web_page_preview=True,
        )
        await delete_if_chat(callback_query, msg)


@router.callback_query(F.data.startswith("remove_"))
async def remove_all_data_logic(callback_query: CallbackQuery) -> None:
    if callback_query.from_user.id != int(callback_query.data.split("_", 1)[1]):
        await callback_query.answer("🚫 This button was not meant for you")
        return
    session: AsyncSession
    async with di["async_session"]() as session:
        await session.execute(
            delete(Users).where(Users.user_id == callback_query.from_user.id)
        )
        await session.execute(
            delete(Groups).where(Groups.user_id == callback_query.from_user.id)
        )
        await session.commit()
        msg = await callback_query.message.edit_text(
            f"""🗑 From now I know nothing about you! All your data was erased forever. If you want to start again, just use /streak command.""",
        )
        await delete_if_chat(callback_query, msg)


async def scoreboard(callback_query: CallbackQuery) -> None:
    session: AsyncSession
    async with di["async_session"]() as session:
        session_result = await session.execute(
            select(Users)
            .join(Groups, Users.user_id == Groups.user_id)
            .filter(
                Groups.group_id == callback_query.message.chat.id,
                Groups.is_banned == False,
            )
            .order_by(asc(Users.streak))
            .limit(50)
        )
        message_result = "🏆 Scoreboard\n\n"
        for id, users_tuple in enumerate(session_result.all()):
            username = users_tuple[0].username
            name_text = users_tuple[0].name
            username_text = ""
            days = (datetime.datetime.now() - users_tuple[0].streak).days
            if username is not None:
                username_text = " (@" + username + ")"
            else:
                name_text = (
                    f"<a href='tg://user?id={users_tuple[0].user_id}'>{name_text}</a>"
                )

            message_result += "%d. %s %s — <b>%d %s</b>\n" % (
                id + 1,
                name_text,
                username_text,
                days,
                "days" if days != 1 else "day",
            )
        try:
            await callback_query.message.edit_text(message_result)            
        except aiogram.exceptions.TelegramBadRequest:
            return


@router.callback_query(F.data.startswith("turn_"))
async def turn_scoreboard(callback_query: CallbackQuery) -> None:
    if callback_query.from_user.id != int(callback_query.data.split("_", 1)[1]):
        await callback_query.answer("🚫 This button was not meant for you")
        return
    scoreboards[callback_query.chat_instance] = callback_query.message
    while scoreboards[callback_query.chat_instance] == callback_query.message:
        await scoreboard(callback_query)
        await asyncio.sleep(TIMEOUT_SCOREBOARD_IN_SECONDS)


@router.message(Command(commands=["setstreak", "setStreak"]))
async def set_streak(message: Message) -> None:
    days = message.text.split(" ", 1)[-1]
    if not days.isnumeric() or int(days) > 100000:
        return
    days = int(days)
    session: AsyncSession
    async with di["async_session"]() as session:
        session_result = await session.execute(
            select(Users).where(Users.user_id == message.from_user.id)
        )
        session_result = session_result.scalar()
    if session_result is None:
        msg = await message.answer("↪️ Use /streak to start a new streak.")
        await delete_if_chat(message, msg)
        return
    session_result.streak = datetime.datetime.now() - datetime.timedelta(days=days)
    session.add(session_result)
    await session.commit()
    msg = await message.answer("Done")
    await delete_if_chat(message, msg)


async def main() -> None:
    await create_all()
    logging.info("created")
    bot = Bot(TOKEN, parse_mode="HTML")
    await dp.start_polling(bot)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    logging.basicConfig(level=logging.INFO)
    loop.run_until_complete(main())
