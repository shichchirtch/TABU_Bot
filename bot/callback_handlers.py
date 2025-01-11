from aiogram import Router
from filters import *
from python_db import coloda, index_list
from aiogram.filters import StateFilter
from contextlib import suppress
from aiogram.types import CallbackQuery, InputMediaPhoto
from python_db import users_db
from aiogram.exceptions import TelegramBadRequest
from lexikon import *
from aiogram.fsm.context import FSMContext
from bot_instance import FSM_ST, dp, bot_storage_key
from inlinekeyboards import *
from random import choice
from postgress_function import kard_inkrement
import asyncio
from sprech_carten import sprech_dict
from process_audio import notify_user_20_seconds



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
    temp_data = users_db[user_id]['zusamm_inline_button']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['zusamm_inline_button'] = ''
    temp_data = users_db[user_id]['secret_code']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['secret_code'] = ''
    await state.update_data(cart_pos=0)
    spiel_index = users_db[user_id]['uniq_spiel_kode']
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    if spiel_index not in bot_dict.keys():
        await callback.message.answer(spiel_beschlisst)
    else:
        zusamm_list = bot_dict[spiel_index]
        key = choice(zusamm_list)
        bot_dict[spiel_index].remove(key)  # Удаляю карту из колоды
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
            att = await callback.message.answer_photo(photo=coloda[key][0],  reply_markup=cart_kb)
            users_db[user_id]['bot_answer'] = att
        await callback.answer()


##############################################################################################################

@cb_router.callback_query(StateFilter(FSM_ST.erclar), NEW_ERC_KARD_FILTER())
async def new_card_erklaren(callback: CallbackQuery, state: FSMContext):
    print('new_card_erklaren works\n\n')
    user_id = callback.from_user.id
    temp_data = users_db[user_id]['zusamm_inline_button']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['zusamm_inline_button']
            await temp_message.delete()
            users_db[user_id]['zusamm_inline_button'] = ''

    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['bot_answer']
            await temp_message.delete()
            users_db[user_id]['bot_answer'] = ''

    asyncio.create_task(notify_user_20_seconds(user_id))
    definitiv = choice(sorted(sprech_dict))  # blume
    neue_card = sprech_dict[definitiv]
    await state.update_data(erc=definitiv)  # Передаю название объясняемого слова
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=neue_card[0]),
            reply_markup=sprech_kb)
    except TelegramBadRequest:
        print('////Into Exeption 122 line')
        att = await callback.message.answer_photo(photo=neue_card[0], reply_markup=sprech_kb)
        users_db[user_id]['zusamm_inline_button'] = att



@cb_router.callback_query(StateFilter(FSM_ST.erclar), CB_EXIT_FILTER())
async def exit_aus_erclaren(callback: CallbackQuery, state: FSMContext):
    print('exit_aus_erclaren')
    user_id = callback.from_user.id
    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['bot_answer']
            await temp_message.delete()
            users_db[user_id]['bot_answer'] = ''

    temp_data = users_db[user_id]['zusamm_inline_button']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['zusamm_inline_button']
            await temp_message.delete()
            users_db[user_id]['zusamm_inline_button'] = ''

    await state.set_state(FSM_ST.alone)  # Вывожу из состояния объяснения с ботом
    await state.update_data(erc='')  # Обнуляю карточку

    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['bot_answer'] = ''
    att = await callback.message.answer('Sie haben den Kartenerklärungsmodus verlassen')
    users_db[user_id]['bot_answer'] = att
    await asyncio.sleep(3)




