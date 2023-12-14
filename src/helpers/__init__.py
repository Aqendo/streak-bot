from aiogram.types import Message
from aiogram import Bot
# Is delete_chat is really a `function` type? IDK.
async def check_admins(message: Message, bot: Bot, delete_if_chat):
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