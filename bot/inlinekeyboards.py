from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

trans_button = InlineKeyboardButton(text='Umdrehen', callback_data='1')
skip_button = InlineKeyboardButton(text='Wirf die Karte ab', callback_data='Новая карта' )
new_card_button = InlineKeyboardButton(text='Bekommen die Karte', callback_data='Новая карта' )


cart_kb = InlineKeyboardMarkup(
            inline_keyboard=[[trans_button, skip_button]])

get_kard_kb = InlineKeyboardMarkup(
            inline_keyboard=[[new_card_button]])

sprech_button = InlineKeyboardButton(text='Wirf die Karte ab', callback_data='neu_sprechkarte' )
exit_button = InlineKeyboardButton(text='◀️', callback_data='exit_command')
sprech_kb = InlineKeyboardMarkup(
            inline_keyboard=[[exit_button, sprech_button]])



