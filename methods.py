from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import globals


def send_main_menu(context, chat_id, lang_id, message_id=None):
    buttons = [
        [KeyboardButton(text=globals.BTN_ORDER[lang_id])],
        [KeyboardButton(text=globals.BTN_MY_ORDERS[lang_id]), KeyboardButton(text=globals.BTN_ABOUT_US[lang_id])],
        [KeyboardButton(text=globals.BTN_COMMENTS[lang_id]), KeyboardButton(text=globals.BTN_SETTINGS[lang_id])]
    ]
    if message_id:
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=globals.TEXT_MAIN_MENU[lang_id],
            reply_markup=ReplyKeyboardMarkup(
                keyboard=buttons,
                resize_keyboard=True
            )
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=globals.TEXT_MAIN_MENU[lang_id],
            reply_markup=ReplyKeyboardMarkup(
                keyboard=buttons,
                resize_keyboard=True
            )
        )


def send_category_buttons(categories, lang_id):
    buttons = []
    row = []
    for i in range(len(categories)):
        row.append(
            InlineKeyboardButton(
                text=categories[i][f'name_{globals.LANGUAGE_CODE[lang_id]}'],
                callback_data=f"category_{categories[i]['id']}"
            )
        )

        if len(row) == 2 or (len(categories) % 2 == 1 and i == len(categories) - 1):
            buttons.append(row)
            row = []
    return buttons


def send_product_buttons(products, lang_id):
    buttons = []
    row = []
    for i in range(len(products)):
        row.append(
            InlineKeyboardButton(
                text=products[i][f'name_{globals.LANGUAGE_CODE[lang_id]}'],
                callback_data=f"category_product_{products[i]['id']}"
            )
        )

        if len(row) == 2 or (len(products) % 2 == 1 and i == len(products) - 1):
            buttons.append(row)
            row = []

    return buttons
