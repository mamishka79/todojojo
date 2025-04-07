import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
from config import TOKEN
from handlers import solo, group, points, reports, shop, language, admin, reminders

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(solo.router)
dp.include_router(group.router)
dp.include_router(points.router)
dp.include_router(reports.router)
dp.include_router(shop.router)
dp.include_router(language.router)
dp.include_router(admin.router)
dp.include_router(reminders.router)  # новый router для напоминаний / реактивации

async def main():
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="help", description="Инструкции для личного режима"),
            BotCommand(command="report", description="Пожаловаться")
        ],
        scope=BotCommandScopeAllPrivateChats()
    )

    await bot.set_my_commands(
        [
            BotCommand(command="help_group", description="Инструкции для группового режима"),
            BotCommand(command="start_group", description="Активировать групповой режим"),
            BotCommand(command="join_group", description="Присоединиться к группе"),
            BotCommand(command="add_task", description="Добавить групповую задачу"),
            BotCommand(command="group_tasks", description="Список групповых задач"),
            BotCommand(command="done", description="Завершить групповую задачу"),
            BotCommand(command="edit_task", description="Редактировать групповую задачу"),
            BotCommand(command="delete_task", description="Удалить групповую задачу"),
            BotCommand(command="group_members", description="Список участников группы"),
            BotCommand(command="group_members_by", description="Список участников группы"),
            BotCommand(command="leave_group", description="Выйти из группы")
        ],
        scope=BotCommandScopeAllGroupChats()
    )

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
