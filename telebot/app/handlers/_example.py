from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message

router = Router()


async def catch_photo(message: Message, bot: Bot):
    await message.answer(text="Поймал!")


# register all handlers ========================================
router.message.register(catch_photo, F.photo)
