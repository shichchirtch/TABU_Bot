import re, os, asyncio
from bot_instance import bot, AZURE_API_KEY, AZURE_REGION, user_recording_status
from azure.cognitiveservices.speech import SpeechConfig, SpeechRecognizer, AudioConfig
import azure.cognitiveservices.speech as speechsdk

async def notify_user_20_seconds(user_id: int):
    """Отправляет уведомление через 20 секунд, если запись всё ещё продолжается."""
    await asyncio.sleep(35)
    # Проверяем, не завершил ли пользователь запись
    if user_recording_status.get(user_id, False):
        await bot.send_message(chat_id=user_id, text="Zum Schließen verbleiben Ihnen noch 10 Sekunden.")


async def process_audio_file(file_id: str, user_id):
    """Скачивает и обрабатывает аудиофайл из Telegram, возвращая множество слов и путь к WAV-файлу."""
    user_recording_status[user_id] = False #  Если  юзер закончил запись раньше - то напрминалка не придёт
    os.makedirs("downloads", exist_ok=True)

    recognition_done = asyncio.Event()

    # Обработчик завершения сессии
    def handle_session_stopped(evt):
        print("Сеанс распознавания завершён.")
        recognition_done.set()  # Устанавливаем событие завершения

    # Скачиваем файл
    file_info = await bot.get_file(file_id)
    local_path = f"downloads/{file_id}.ogg"
    await bot.download_file(file_info.file_path, destination=local_path)

    # Конвертируем в WAV
    wav_path = f"downloads/{file_id}.wav"
    os.system(f"ffmpeg -i {local_path} -ar 16000 -ac 1 {wav_path}")
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"Файл {wav_path} не найден.")

    # Используем Azure для распознавания речи
    speech_config = SpeechConfig(subscription=AZURE_API_KEY, region=AZURE_REGION)
    speech_config.speech_recognition_language = "de-DE"
    audio_config = AudioConfig(filename=wav_path)

    recognizer = SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    recognized_text = []

    # Обработчик для распознанного текста
    def handle_recognized(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Распознанный текст: {evt.result.text}")
            recognized_text.append(evt.result.text)  # Добавляем текст в список
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print("Не удалось распознать текст.")

    recognizer.session_stopped.connect(handle_session_stopped)
    recognizer.recognized.connect(handle_recognized)

    # Запуск непрерывного распознавания
    recognizer.start_continuous_recognition()
    print("Распознавание началось...")

    # Ожидание завершения
    await recognition_done.wait()

    # Остановка распознавания
    recognizer.stop_continuous_recognition_async().get()
    print("Распознавание завершено.")

    print('recognized_text = ', recognized_text)
    full_text = " ".join(recognized_text).lower()
    clean_text = re.sub(r"[^a-zA-Zа-яА-ЯёЁäüößÄÜÖ\s]", "", full_text)
    words_set = set(clean_text.split())

    return words_set, wav_path

