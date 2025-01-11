from aiogram.types import CallbackQuery, Message
from aiogram.filters import BaseFilter
from python_db import users_db
from aiogram.fsm.context import FSMContext


class PRE_START(BaseFilter):
    async def __call__(self, message: Message):
        if message.from_user.id not in users_db:
            return True
        return False


class IN_OUT_FILTER(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data  == '1':
            return True
        return False

class SKIP_FILTER(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data  == 'Новая карта':
            return True
        return False

class IS_DIGIT(BaseFilter):
    async def __call__(self, message: Message):
        if message.text.isdigit() and int(message.text) < 100:
            return True
        return False

class IS_ADMIN(BaseFilter):
    async def __call__(self, message: Message):
        if message.from_user.id == 6685637602:
            return True
        return False


class NEW_ERC_KARD_FILTER(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data  == 'neu_sprechkarte':
            return True
        return False

class CB_EXIT_FILTER(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data  == 'exit_command':
            return True
        return False



