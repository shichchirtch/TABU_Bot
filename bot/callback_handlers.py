from aiogram import Router
from filters import *
from python_db import coloda, index_list
from aiogram.filters import StateFilter
import asyncio
from aiogram.types import CallbackQuery, InputMediaPhoto
from python_db import users_db
from aiogram.exceptions import TelegramBadRequest
from lexikon import *
from aiogram.fsm.context import FSMContext
from bot_instance import FSM_ST, dp, bot_storage_key
from inlinekeyboards import *
from random import choice
from postgress_function import kard_inkrement



cb_router = Router()

@cb_router.callback_query(IN_OUT_FILTER())
async def in_out_process(callback: CallbackQuery, state: FSMContext):
    print('in_out_process works')
    user_id = callback.from_user.id
    us_data = await state.get_data()
    if us_data['cart_pos']:
        await state.update_data(cart_pos=0)
    else:
        await state.update_data(cart_pos=1)

    us_data = await state.get_data()
    position_key = us_data['cart_pos']
    cart_index = users_db[user_id]['explaining_card']
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=coloda[cart_index][position_key]),
            reply_markup=cart_kb
        )
    except TelegramBadRequest:
        print('////Into Exeption in_out_process')
    await callback.answer()



@cb_router.callback_query(StateFilter(FSM_ST.alone, FSM_ST.after_start), SKIP_FILTER())
async def skip_process(callback: CallbackQuery, state: FSMContext):
    print('skip_process works')
    user_id = callback.from_user.id
    await state.update_data(cart_pos=0)
    key = choice(index_list)
    users_db[user_id]['explaining_card'] = key
    await kard_inkrement(user_id)
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=coloda[key][0]),
            reply_markup=cart_kb)
    except TelegramBadRequest:
        print('////Into Exeption skip_process')
    await callback.answer()


@cb_router.callback_query(StateFilter(FSM_ST.zusamm), SKIP_FILTER())
async def skip_zusamm_process(callback: CallbackQuery, state: FSMContext):
    print('skip_zusamm_process works')
    user_id = callback.from_user.id
    await state.update_data(cart_pos=0)
    spiel_index = users_db[user_id]['uniq_spiel_kode']
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    if spiel_index not in bot_dict.keys():
        await callback.message.answer(spiel_beschlisst)
    else:
        zusamm_list = bot_dict[spiel_index]
        key = choice(zusamm_list)
        bot_dict[spiel_index].remove(key)
        # print('bot_dict[spiel_index] = ', bot_dict[spiel_index])
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)
        users_db[user_id]['explaining_card'] = key
        await kard_inkrement(user_id)
        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=coloda[key][0]),
                reply_markup=cart_kb)
        except TelegramBadRequest:  # Срабатывает, когда выдаёт первую карточку
            print('////Into Exeption skip_zusamm_process 86 line')
            await callback.message.answer_photo(photo=coloda[key][0],  reply_markup=cart_kb)
        await callback.answer()










