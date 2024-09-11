from aiogram import Router, html, F
import asyncio
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command, StateFilter
from python_db import user_dict, users_db, coloda, index_list
from filters import PRE_START, IS_DIGIT, IS_ADMIN
from lexikon import *
from external_functions import scheduler_job
from copy import deepcopy
from aiogram.fsm.context import FSMContext
from keyboards import pre_start_clava
from bot_instance import FSM_ST, bot, bot_storage_key, dp
from random import randint, choice
from contextlib import suppress
from inlinekeyboards import *
from postgress_function import *


ch_router = Router()

@ch_router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    if not await check_user_in_table(user_id):
        await insert_new_user_in_table(user_id, user_name)
        users_db[message.from_user.id] = deepcopy(user_dict)
        await insert_new_user_in_admin_table(user_id)
        await state.set_state(FSM_ST.after_start)
        await state.set_data({'card_list':[], 'cart_pos':0, 'timer':0, 'leader':0})
        await message.answer(text=f'{html.bold(html.quote(user_name))}, '
                                  f'Hallo !\n'
                                  f'Ich bin Bot für Spiele TABU spielen\n\n'
                                  f'Um mit mir zusammenzuarbeiten, klicken Sie auf die Schaltfläche '
                                  f'<b>menu</b> oder\n\n 🔹                   /help\n\n'
                                  f'🎲',
                             parse_mode=ParseMode.HTML,
                             reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(1)
        await add_in_list(user_id)  # Кто стартанул бота - добавляю в список админа
    else:
        users_db[message.from_user.id] = deepcopy(user_dict) # Просто создаю юзеру БД для сообщений
        await message.answer('Бот перезапущен на сервере')



@ch_router.message(PRE_START())
async def before_start(message: Message):
    prestart_ant = await message.answer(text='Klicken <b>start</b> !',
                                        reply_markup=pre_start_clava)
    await message.delete()
    await asyncio.sleep(8)
    await prestart_ant.delete()



@ch_router.message(Command('help'))
async def help_command(message: Message):
    user_id = message.from_user.id
    att = await message.answer(help)
    users_db[user_id]['bot_answer'] = att
    await asyncio.sleep(2)
    await message.delete()
    await asyncio.sleep(20)
    await att.delete()


@ch_router.message(Command('get_card'), ~StateFilter(FSM_ST.zusamm))
async def get_card_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.set_state(FSM_ST.alone)
    key = choice(index_list)
    await message.answer_photo(photo=coloda[key][0],
                         reply_markup=cart_kb)
    users_db[user_id]['explaining_card']=key
    await kard_inkrement(user_id)
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(Command('zusammen_spielen'))
async def leader_zusammen_spielen_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.set_state(FSM_ST.zusamm)
    spiel_kit = index_list.copy()
    uniq = randint(1, 101)  #  Это ключ в словаре для командной колоды и код для вступления в групповую игру
    users_db[user_id]['uniq_spiel_kode'] = str(uniq)
    await message.answer(f'Отправьте уникальный идентификатор <b>{uniq}</b>  игры другим игрокам\n\n'
                         f'Senden Sie die eindeutige ID <b>{uniq}</b> des Spiels an andere Spieler')
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    start_kart = choice(index_list)   # Получаю случайную карту от 1 до 507
    await asyncio.sleep(0.8)
    await message.answer_photo(photo=coloda[start_kart][0], reply_markup=cart_kb)
    spiel_kit.remove(start_kart)  # Удаляю стартовую карту из колоды
    print('spiel_kit = ', spiel_kit)  # Переписываю список по уникальному номеру
    await state.update_data(leader=1)  #Устанавливаю состояние в лидера
    bot_dict[str(uniq)] = spiel_kit
    users_db[user_id]['explaining_card'] = start_kart
    await kard_inkrement(user_id)
    await dp.storage.set_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
    # bot_dict = await dp.storage.get_data(key=bot_storage_key)
    # print('\n\n\n\n104 bot_dict = ', bot_dict)
    await message.delete()


@ch_router.message(Command('mitmachen'), ~StateFilter(FSM_ST.zusamm))
async def mitmachen_command(message: Message, state: FSMContext):
    await state.set_state(FSM_ST.zusamm)
    await message.answer('Отправьте уникальный идентификатор игры\n\n'
                         'Senden Sie die eindeutige ID des Spiels')
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(F.text, StateFilter(FSM_ST.zusamm), IS_DIGIT())
async def join_to_team(message: Message):
    user_id = message.from_user.id
    join_team_key = message.text
    users_db[user_id]['uniq_spiel_kode'] = join_team_key
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    if join_team_key in bot_dict:
        await message.answer(text='Чтобы получить карточку нажмите Получить карту\n\n'
                                  'Um eine Karte zu erhalten, klicken Sie auf die Schaltfläche',
                             reply_markup=get_kard_kb)
    else:
        await message.answer('Ungültiger Code   🤷🏿‍♀️')
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(Command('exit'),StateFilter(FSM_ST.zusamm))
async def exit_zusammen_spiel(message: Message, state:FSMContext):
    user_id = message.from_user.id
    us_redis_dict = await state.get_data()
    await state.set_state(FSM_ST.alone)
    if not us_redis_dict['leader']:
        users_db[user_id]['uniq_spiel_kode'] = 0  # reset Spiel code

    else:
        zusammen_spiel_key = users_db[user_id]['uniq_spiel_kode']
        print('zusammen_spiel_key = ', zusammen_spiel_key)
        new_bot_dict = await dp.storage.get_data(key=bot_storage_key)
        new_bot_dict.pop(zusammen_spiel_key)  #  Удаляю уникальный код игры из соловаря бота
        await dp.storage.set_data(key=bot_storage_key, data=new_bot_dict) #  Удалить ключ нельзя, можно только перезаписать словарь
        users_db[user_id]['uniq_spiel_kode']=0
    await message.answer('Du bist aus dem Spiel')


@ch_router.message(Command('karten_menge'))
async def get_skipping_karts_number(message: Message):
    user_id = message.from_user.id
    katrten_taily = await return_kart_menge(user_id)
    await message.answer(f'Sie haben schon <b>{katrten_taily}</b> Karten gespielt 🥳')


@ch_router.message(Command('start_timer'))
async def timer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    us_dict = await state.get_data()
    if not us_dict['timer']:
        await state.update_data(timer=1)
        scheduler_job(user_id, state) # Запускаю секундомер на 2 минуты
        await message.answer('Stoppuhr ist zeitgesteuert')
    else:
        await message.answer('<b>2</b> Minuten gehen')


@ch_router.message(Command('admin'), IS_ADMIN())
async def admin_enter(message: Message):
    print('admin_enter works')
    await message.answer(admin_eintritt)


@ch_router.message(Command('skolko'), IS_ADMIN())
async def get_quantyty_users(message: Message):
    qu = await return_quantity_users()
    await message.answer(f'Бота запустили {len(qu)} юзеров')

@ch_router.message(Command('send_msg'), IS_ADMIN())
async def send_message(message: Message, state: FSMContext ):
    await state.set_state(FSM_ST.admin)
    await message.answer('Schreib ihre Nachrichten')

@ch_router.message(StateFilter(FSM_ST.admin))
async def send_message(message: Message, state: FSMContext):
    us_list = await return_quantity_users()
    us_list.remove(6685637602)
    for chat_id in us_list:
        await message.send_copy(chat_id=chat_id)
        await asyncio.sleep(0.2)

    await state.set_state(FSM_ST.alone)
    await message.answer('Mailing abgeschlossen')


@ch_router.message()
async def trasher(message: Message):
    print('TRASHER')
    await asyncio.sleep(1)
    await message.delete()











