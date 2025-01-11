from aiogram import Router, html, F
import asyncio, os
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove, ContentType
from aiogram.filters import CommandStart, Command, StateFilter
from python_db import user_dict, users_db, coloda, index_list, bot_command_list
from filters import PRE_START, IS_DIGIT, IS_ADMIN
from lexikon import *
from external_functions import scheduler_job
from copy import deepcopy
from aiogram.fsm.context import FSMContext
from keyboards import pre_start_clava
from bot_instance import FSM_ST, bot_storage_key, dp, user_recording_status
from random import randint, choice
from contextlib import suppress
from inlinekeyboards import *
from postgress_function import *
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from sprech_carten import sprech_dict
from process_audio import process_audio_file, notify_user_20_seconds


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
        await state.set_data({'card_list':[], 'cart_pos':0, 'timer':0, 'leader':0,'erc':''})
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
        await message.answer('Der Bot wurde auf dem Server neu gestartet')



@ch_router.message(PRE_START())
async def before_start(message: Message):
    prestart_ant = await message.answer(text='Klicken <b>start</b> !',
                                        reply_markup=pre_start_clava)
    await message.delete()
    await asyncio.sleep(8)
    await prestart_ant.delete()


@ch_router.message(Command('help'))
async def help_command(message: Message):
    att = await message.answer(help)
    await asyncio.sleep(2)
    await message.delete()
    await asyncio.sleep(12)
    await att.delete()


@ch_router.message(Command('get_card'), ~StateFilter(FSM_ST.zusamm))
async def get_card_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.set_state(FSM_ST.alone)
    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['bot_answer'] = ''
    key = choice(index_list)
    att = await message.answer_photo(photo=coloda[key][0],
                         reply_markup=cart_kb)
    users_db[user_id]['bot_answer']=att

    users_db[user_id]['explaining_card']=key
    await kard_inkrement(user_id)
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(Command('zusammen_spielen'), ~StateFilter(FSM_ST.zusamm))
async def leader_zusammen_spielen_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['bot_answer'] = ''

    await state.set_state(FSM_ST.zusamm)
    spiel_kit = index_list.copy()
    uniq = randint(1, 101)  #  Это ключ в словаре для командной колоды и код для вступления в групповую игру
    users_db[user_id]['uniq_spiel_kode'] = str(uniq)
    sc = users_db[user_id]['secret_code']
    if sc:
        with suppress(TelegramBadRequest):
            await sc.delete()
            users_db[user_id]['secret_code'] = ''

    secret_code = await message.answer(f'Отправьте уникальный идентификатор <b>{uniq}</b>  игры другим игрокам\n\n'
                         f'Senden Sie die eindeutige ID <b>{uniq}</b> des Spiels an andere Spieler')
    users_db[user_id]['secret_code'] = secret_code
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    start_kart = choice(index_list)   # Получаю случайную карту от 1 до 507
    await asyncio.sleep(0.8)
    att = await message.answer_photo(photo=coloda[start_kart][0], reply_markup=cart_kb)
    users_db[user_id]['bot_answer'] = att
    spiel_kit.remove(start_kart)  # Удаляю стартовую карту из колоды
    # print('spiel_kit = ', spiel_kit)  # Переписываю список по уникальному номеру
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
    user_id = message.from_user.id
    att = await message.answer('Отправьте уникальный идентификатор игры\n\n'
                         'Senden Sie die eindeutige ID des Spiels')
    sc = users_db[user_id]['secret_code']
    if sc:
        with suppress(TelegramBadRequest):
            await sc.delete()
    users_db[user_id]['secret_code'] = att
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(F.text, StateFilter(FSM_ST.zusamm), IS_DIGIT())
async def join_to_team(message: Message):
    user_id = message.from_user.id
    join_team_key = message.text
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    if join_team_key in bot_dict:
        users_db[user_id]['uniq_spiel_kode'] = join_team_key
        first_kard_inline_button = await message.answer(text='Чтобы получить карточку нажмите Получить карту\n\n'
                                  'Um eine Karte zu erhalten, klicken Sie auf die Schaltfläche',
                             reply_markup=get_kard_kb)
        temp_data = users_db[user_id]['zusamm_inline_button']
        if temp_data:
            with suppress(TelegramBadRequest):
                await temp_data.delete()
        users_db[user_id]['zusamm_inline_button'] = first_kard_inline_button

        temp_data = users_db[user_id]['bot_answer']
        if temp_data:
            with suppress(TelegramBadRequest):
                await temp_data.delete()
                users_db[user_id]['bot_answer'] = ''

    else:
        att = await message.answer('Ungültiger Code   🤷🏿‍♀️')
        await asyncio.sleep(3)
        await att.delete()
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(Command('exit'), StateFilter(FSM_ST.zusamm, FSM_ST.erclar))
async def exit_zusammen_spiel(message: Message, state:FSMContext):
    user_id = message.from_user.id
    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['bot_answer']
            await temp_message.delete()
            users_db[user_id]['bot_answer'] = ''
    us_redis_dict = await state.get_data()

    await state.set_state(FSM_ST.alone)  # Вывожу из состояния объяснения с ботом
    await state.update_data(erc='') #  Обнуляю карточку

    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            await temp_data.delete()
            users_db[user_id]['bot_answer'] = ''

    if not us_redis_dict['leader']:
        users_db[user_id]['uniq_spiel_kode'] = 0  # reset Spiel code

    else:
        sc = users_db[user_id]['secret_code']
        if sc:
            with suppress(TelegramBadRequest):
                await sc.delete()
                users_db[user_id]['secret_code'] = ''
        zusammen_spiel_key = users_db[user_id]['uniq_spiel_kode']
        print('zusammen_spiel_key = ', zusammen_spiel_key)
        new_bot_dict = await dp.storage.get_data(key=bot_storage_key)
        new_bot_dict.pop(zusammen_spiel_key)  #  Удаляю уникальный код игры из соловаря бота
        await dp.storage.set_data(key=bot_storage_key, data=new_bot_dict)  #  Удалить ключ нельзя, можно только перезаписать словарь
        users_db[user_id]['uniq_spiel_kode']=0  # Ресет ключа
    att = await message.answer('Du bist aus dem Spiel')
    users_db[user_id]['bot_answer'] = att
    await asyncio.sleep(3)
    await message.delete()


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
        att = await message.answer('Stoppuhr ist zeitgesteuert')
        await asyncio.sleep(3)
        await message.delete()
        await asyncio.sleep(120)
        await att.delete()
        await asyncio.sleep(10)
        deleted_msg = users_db[user_id]['bot_answer']
        if deleted_msg:
            with suppress(TelegramBadRequest):
                await deleted_msg.delete()
                users_db[user_id]['bot_answer'] = ''
    else:
        att = await message.answer('<b>2</b> Minuten gehen')
        await asyncio.sleep(5)
        await att.delete()

@ch_router.message(Command('erklaeren'), StateFilter(FSM_ST.after_start, FSM_ST.alone))
async def process_erklaeren_command(message: Message, state:FSMContext):
    user_id = message.from_user.id
    user_recording_status[user_id] = True
    await state.set_state(FSM_ST.erclar)
    await message.answer(f"Halten Sie das Mikrofon gedrückt und beginnen Sie zu sprechen. Sie haben maximal 45 Sekunden Zeit.")
    # Запускаем задачу с уведомлением
    asyncio.create_task(notify_user_20_seconds(user_id))
    definitiv = choice(sorted(sprech_dict))  # blume
    erste_card = sprech_dict[definitiv]
    await state.update_data(erc=definitiv) # Передаю название объясняемого слова
    att = await message.answer_photo(photo=erste_card[0],
                               reply_markup=sprech_kb)
    users_db[user_id]['zusamm_inline_button'] = att


@ch_router.message(F.content_type == ContentType.VOICE, StateFilter(FSM_ST.erclar))
async def handle_voice_message(message: Message, state:FSMContext):
    """Принимает голосовое сообщение и обрабатывает его."""
    user_id = message.from_user.id
    file_id = message.voice.file_id
    words = wav_path = ''
    try:
        words, wav_path = await process_audio_file(file_id, user_id)
        if words:
            print(f"Распознанные слова: {words}")
        else:
            print("Не удалось распознать текст.")
    finally:
        # Удаляем временные файлы
        if os.path.exists(wav_path):
            try:
                os.remove(wav_path)
                print(f"Файл {wav_path} успешно удалён.")
            except Exception as e:
                print(f"Ошибка при удалении файла {wav_path}: {e}")
                pass
        else:
            print(f"Файл {wav_path} не существует.")
            pass
    user_dict = await state.get_data()
    erc = user_dict['erc']
    control_set = sprech_dict[erc][1]
    if isinstance(words, set):
        if len(words.intersection(control_set)) > 1:
            att = await message.answer(f'Das ist <b>{erc}</b> !',
                                 reply_markup=sprech_kb)
        else:
            att = await message.answer('Ich weiß nicht, was das ist! Aber Sie können es mit'
                                 ' einem anderen Wort versuchen!',
                                 reply_markup=sprech_kb)
        users_db[user_id]['bot_answer'] = att
    else:
        await message.answer('Sprache nicht erkannt 🤷', reply_markup=sprech_kb)




#############################################################################################

@ch_router.message(Command('admin'), IS_ADMIN())
async def admin_enter(message: Message):
    print('admin_enter works')
    await message.answer(admin_eintritt)


@ch_router.message(Command('skolko'), IS_ADMIN())
async def get_quantyty_users(message: Message):
    print('\n\nSkolko works\n\n')
    qu = await return_quantity_users()
    await message.answer(f'Бота запустили {len(qu)} юзеров')

@ch_router.message(Command('send_msg'), IS_ADMIN())
async def send_message(message: Message, state: FSMContext ):
    await state.set_state(FSM_ST.admin)
    await message.answer('Schreib ihre Nachrichten')

@ch_router.message(StateFilter(FSM_ST.admin))
async def send_message(message: Message, state: FSMContext):
    us_list = await return_quantity_users()
    # await message.send_copy(chat_id=6831521683) # Второй акаунт
    for chat_id in us_list:
        try:
            await message.send_copy(chat_id=chat_id)
            await asyncio.sleep(0.2)
        except Exception:
            pass
        # await message.send_copy(chat_id=chat_id)

    await state.set_state(FSM_ST.alone)
    await message.answer('Mailing abgeschlossen')


@ch_router.message()
async def trasher(message: Message, state: FSMContext):
    print('TRASHER')
    current_state = await state.get_state()
    if current_state == 'FSM_ST:zusamm' and message.text in bot_command_list:
        att = await message.answer(exit_from_zusamm)
        await asyncio.sleep(5)
        await att.delete()
    await asyncio.sleep(1)
    await message.delete()












