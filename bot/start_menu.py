from aiogram.types import BotCommand
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Функция для настройки кнопки Menu бота
async def set_main_menu(bot):
    # Создаем список с командами и их описанием для кнопки menu
    # bot
    main_menu_commands = [
        BotCommand(command='/get_card',
                   description='Bekommen die Karte'),

        BotCommand(command='/help',
                   description='meine Faehigkeiten'),

        BotCommand(command='/erklaeren',
                   description='Erklären Definiven für Bot'),

        BotCommand(command='/zusammen_spielen',
                   description='Spielen mit Freunde'),

        BotCommand(command='/mitmachen',
                   description='Mitmachen zusammen Spile'),

        BotCommand(command='/start_timer',
                   description='Zeit 2 Minuten')
    ]

    await bot.set_my_commands(main_menu_commands)

pre_start_button = KeyboardButton(text='/start')

pre_start_clava = ReplyKeyboardMarkup(
    keyboard=[[pre_start_button]],
    resize_keyboard=True,
    input_field_placeholder='Beginn spielen !'
)