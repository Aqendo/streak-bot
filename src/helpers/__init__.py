from aiogram.types import Message
from aiogram import Bot
# Is delete_chat is really a `function` type? IDK.
async def check_admins(message: Message, bot: Bot, delete_if_chat, matter_if_admin_can_delete_user = True) -> bool:
    try:
        user_who_deletes = await bot.get_chat_member(
            message.chat.id, message.from_user.id
        )
    except:
        msg = await message.reply(
            "I can't get chat admins! Please report this error to the support group."
        )
        await delete_if_chat(message, msg)
        return False
    if (
        (matter_if_admin_can_delete_user and not user_who_deletes.can_restrict_members)
        and not (user_who_deletes.status != "administrator" or user_who_deletes.status != "creator")
    ):
        msg = await message.reply(
            "This command is admin-only (with ability to restrict members)!"
        )
        await delete_if_chat(message, msg)
        return False
    return True