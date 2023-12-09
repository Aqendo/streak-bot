from typing import Any, Awaitable, Callable, Dict

from aiogram.types import Update
from kink import di
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Users


async def update_users_info(
    handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: Dict[str, Any],
) -> Any:
    event_old = event
    event = event.callback_query or event.message
    if event is None:
        return
    session: AsyncSession
    async with di["async_session"]() as session:
        session_result = await session.execute(
            select(Users).where(Users.user_id == event.from_user.id)
        )
        session_result = session_result.scalar()
        if session_result is not None and (
            session_result.name != event.from_user.full_name
            or session_result.username != event.from_user.username
        ):
            session_result.name = event.from_user.full_name
            session_result.username = event.from_user.username
            session.add(session_result)
            await session.commit()
    return await handler(event_old, data)
