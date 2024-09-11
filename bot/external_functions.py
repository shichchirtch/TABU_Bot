from datetime import datetime, timedelta
from bot_instance import bot, scheduler
from aiogram.fsm.context import FSMContext

async  def zwei_minuten(bot, user_id, state:FSMContext):
    await bot.send_message(chat_id=user_id, text="2 Minuten sind vergangen")
    await state.update_data(timer=0)


def scheduler_job(user_id, state):
    print('scheduler_job works')
    time_now = datetime.now()  # Время сейчас
    delta = timedelta(seconds=120)  # Время, которое отводится на ответ
    future = time_now+delta  # Время когда действие должно быть закончено
    stop_2_min_time = str(user_id)
    scheduler.add_job(zwei_minuten, "date", run_date=future, args=(bot, user_id, state), id=stop_2_min_time)











