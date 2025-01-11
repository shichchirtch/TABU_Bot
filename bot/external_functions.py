from datetime import datetime, timedelta
from bot_instance import bot, scheduler
from aiogram.fsm.context import FSMContext
from python_db import users_db
# import speech_recognition as sr
# import time
# import re
# Инициализация распознавателя
# recognizer = sr.Recognizer()

# Настройка времени паузы
# recognizer.pause_threshold = 3.0  # Пауза до 3 секунд

# Ключевая фраза для завершения
# END_PHRASE = "ich bin fertig"

# Максимальная длительность объяснения (в секундах)
# MAX_DURATION = 60



#
# def listen_and_recognize():
#     start_time = time.time()  # Засекаем начало записи
#     full_text = []  # Хранилище для всех распознанных частей
#     try:
#         with sr.Microphone() as mic:
#             print(f"Начинайте говорить. Вы можете делать паузы до 3 секунд.")
#             print(f"У вас есть максимум {MAX_DURATION} секунд. Завершите словами: 'ich bin fertig'.")
#
#             recognizer.adjust_for_ambient_noise(mic, duration=1)  # Подстройка под шум
#
#             while True:
#                 # Проверяем, не истекло ли время
#                 elapsed_time = time.time() - start_time
#                 if elapsed_time > MAX_DURATION:
#                     print("Время объяснения истекло!")
#                     break
#
#                 try:
#                     # Запись и распознавание очередного фрагмента
#                     audio = recognizer.listen(mic, timeout=MAX_DURATION - elapsed_time, phrase_time_limit=10)
#                     recognized_text = recognizer.recognize_azure(
#                         audio_data=audio,
#                         key=AZURE_API_KEY,  # Укажите ваш API-ключ
#                         location=AZURE_REGION,  # Укажите ваш регион (например, "westeurope")
#                         language="de-DE"  # Немецкий язык
#                     )
#
#                     print(f"Распознанный текст ex funk: {recognized_text}")
#                     full_text.append(recognized_text)
#
#                     # Проверяем ключевую фразу
#                     if END_PHRASE in recognized_text[0]:
#                         print("Вы произнесли ключевую фразу! Запись завершена.")
#                         break
#
#                 except sr.UnknownValueError:
#                     print("Речь не распознана. Попробуйте продолжать говорить.")
#                 except sr.RequestError as e:
#                     print(f"Произошла ошибка при обращении к Azure: {e}")
#                     break
#                 except sr.WaitTimeoutError:
#                     print("Вы молчали слишком долго. Запись завершена.")
#                     break
#
#         # Объединяем все части и убираем ключевую фразу, если она была
#         print('67 full text = ', full_text)
#         s = ''
#         for chunck in full_text:
#             s+=chunck[0]
#             print('s = ', s)
#
#         final_text = s.replace(END_PHRASE, "").strip()
#         f_text = re.sub(r"[^a-zA-Zа-яА-ЯёЁäüößÄÜÖ\s]", "", final_text)
#         print('final_text = ', f_text, type(f_text))
#         res_arr = f_text.split()
#         print(res_arr)
#         return set(res_arr)
#     except OSError as e:
#         print("Ошибка: устройство ввода недоступно:", e)
#         return "Микрофон не найден"





async  def zwei_minuten(bot, user_id, state:FSMContext):
    att = await bot.send_message(chat_id=user_id, text="2 Minuten sind vergangen")
    await state.update_data(timer=0)
    users_db[user_id]['bot_answer'] = att




def scheduler_job(user_id, state):
    print('scheduler_job works')
    time_now = datetime.now()  # Время сейчас
    delta = timedelta(seconds=120)  # Время, которое отводится на ответ
    future = time_now+delta  # Время когда действие должно быть закончено
    stop_2_min_time = str(user_id)
    scheduler.add_job(zwei_minuten, "date", run_date=future, args=(bot, user_id, state), id=stop_2_min_time)





