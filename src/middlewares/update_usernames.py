from typing import Any, Awaitable, Callable, Dict

from aiogram.types import Update
from kink import di
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Users, Groups


async def update_users_info(
    handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: Dict[str, Any],
) -> Any:
    event_old = event
    if not event.callback_query and not event.message: return await handler(event_old, data)
    event = event.callback_query.message or event.message
    if event is None:
        return
    session: AsyncSession
    async with di["async_session"]() as session:
        user = await session.scalar(
            select(Users).where(Users.user_id == event.from_user.id)
        )
        if user is not None and (
            user.name != event.from_user.full_name
            or user.username != event.from_user.username
        ):
            user.name = event.from_user.full_name
            user.username = event.from_user.username
            session.add(user)
            await session.commit()
        if event.chat.id != event.from_user.id:
            group = await session.scalar(select(Groups).where(Groups.group_id == event.chat.id))
            if group:
                data["autodelete"] = group.autodelete
        else:
            data["autodelete"] = False
    return await handler(event_old, data)
