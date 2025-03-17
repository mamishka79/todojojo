from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils import update_user, get_user

router = Router()

def language_inline_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Русский", callback_data="set_lang_ru"),
            InlineKeyboardButton(text="English", callback_data="set_lang_en")
        ]
    ])

@router.message(F.text.in_(["🌐 Language", "🌐 Язык"]))
async def language_menu(message: Message):
    await message.answer("Выберите язык / Choose language:", reply_markup=language_inline_keyboard())

@router.callback_query(F.data.in_(["set_lang_ru", "set_lang_en"]))
async def language_callback(callback: CallbackQuery):
    lang_code = "ru" if callback.data == "set_lang_ru" else "en"
    update_user(callback.from_user.id, "language", lang_code)
    # Импортируем локально функцию для генерации клавиатуры из solo.py, чтобы избежать циклического импорта
    from handlers.solo import get_solo_keyboard
    new_keyboard = get_solo_keyboard(lang_code)
    # Отправляем сообщение с обновлённой клавиатурой
    await callback.message.answer(
        f"Язык изменён на {'Русский' if lang_code == 'ru' else 'English'}. Интерфейс обновлён.",
        reply_markup=new_keyboard
    )
    await callback.answer(text=f"Язык изменён на {'Русский' if lang_code == 'ru' else 'English'}", show_alert=True)
