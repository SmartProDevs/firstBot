from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from telegram import (
    InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, ChatAction
)

from database import Database
import globals
import methods

db = Database("food-db.db")

ADMIN_ID = 697775505

def check(update, context):
    user = update.message.from_user
    db_user = db.get_user_by_chat_id(user.id)

    if not db_user:
        db.create_user(user.id)
        buttons = [
            [KeyboardButton(text=globals.BTN_LANG_UZ), KeyboardButton(text=globals.BTN_LANG_RU)]
        ]
        update.message.reply_text(text=globals.WELCOME_TEXT)
        update.message.reply_text(
            text=globals.CHOOSE_LANG,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=buttons,
                resize_keyboard=True
            )
        )
        context.user_data["state"] = globals.STATES["reg"]

    elif not db_user["lang_id"]:
        buttons = [
            [KeyboardButton(text=globals.BTN_LANG_UZ), KeyboardButton(text=globals.BTN_LANG_RU)]
        ]
        update.message.reply_text(
            text=globals.CHOOSE_LANG,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=buttons,
                resize_keyboard=True
            )
        )
        context.user_data["state"] = globals.STATES["reg"]

    elif not db_user["first_name"]:
        update.message.reply_text(
            text=globals.TEXT_ENTER_FIRST_NAME[db_user['lang_id']],
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["state"] = globals.STATES["reg"]

    elif not db_user["last_name"]:
        update.message.reply_text(
            text=globals.TEXT_ENTER_LAST_NAME[db_user['lang_id']],
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["state"] = globals.STATES["reg"]

    elif not db_user["phone_number"]:
        buttons = [
            [KeyboardButton(text=globals.BTN_SEND_CONTACT[db_user['lang_id']], request_contact=True)]
        ]
        update.message.reply_text(
            text=globals.TEXT_ENTER_CONTACT[db_user['lang_id']],
            parse_mode='HTML',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=buttons,
                resize_keyboard=True
            )
        )
        context.user_data["state"] = globals.STATES["reg"]

    else:
        methods.send_main_menu(context, user.id, db_user['lang_id'])
        context.user_data["state"] = globals.STATES["menu"]


def check_data_decorator(func):
    def inner(update, context):
        user = update.message.from_user
        db_user = db.get_user_by_chat_id(user.id)
        state = context.user_data.get("state", 0)

        if state != globals.STATES['reg']:

            if not db_user:
                db.create_user(user.id)
                buttons = [
                    [KeyboardButton(text=globals.BTN_LANG_UZ), KeyboardButton(text=globals.BTN_LANG_RU)]
                ]
                update.message.reply_text(text=globals.WELCOME_TEXT)
                update.message.reply_text(
                    text=globals.CHOOSE_LANG,
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=buttons,
                        resize_keyboard=True
                    )
                )
                context.user_data["state"] = globals.STATES["reg"]

            elif not db_user["lang_id"]:
                buttons = [
                    [KeyboardButton(text=globals.BTN_LANG_UZ), KeyboardButton(text=globals.BTN_LANG_RU)]
                ]
                update.message.reply_text(
                    text=globals.CHOOSE_LANG,
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=buttons,
                        resize_keyboard=True
                    )
                )
                context.user_data["state"] = globals.STATES["reg"]

            elif not db_user["first_name"]:
                update.message.reply_text(
                    text=globals.TEXT_ENTER_FIRST_NAME[db_user['lang_id']],
                    reply_markup=ReplyKeyboardRemove()
                )
                context.user_data["state"] = globals.STATES["reg"]

            elif not db_user["last_name"]:
                update.message.reply_text(
                    text=globals.TEXT_ENTER_LAST_NAME[db_user['lang_id']],
                    reply_markup=ReplyKeyboardRemove()
                )
                context.user_data["state"] = globals.STATES["reg"]

            elif not db_user["phone_number"]:
                buttons = [
                    [KeyboardButton(text=globals.BTN_SEND_CONTACT[db_user['lang_id']], request_contact=True)]
                ]
                update.message.reply_text(
                    text=globals.TEXT_ENTER_CONTACT[db_user['lang_id']],
                    parse_mode='HTML',
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=buttons,
                        resize_keyboard=True
                    )
                )
                context.user_data["state"] = globals.STATES["reg"]

            else:
                return func(update, context)

            return False

        else:
            return func(update, context)

    return inner


def start_handler(update, context):
    check(update, context)


@check_data_decorator
def message_handler(update, context):
    global text
    message = update.message.text
    user = update.message.from_user
    state = context.user_data.get("state", 0)
    db_user = db.get_user_by_chat_id(user.id)

    if state == 0:
        check(update, context)

    elif state == 1:

        if not db_user["lang_id"]:

            if message == globals.BTN_LANG_UZ:
                db.update_user_data(user.id, "lang_id", 1)
                check(update, context)

            elif message == globals.BTN_LANG_RU:
                db.update_user_data(user.id, "lang_id", 2)
                check(update, context)

            else:
                update.message.reply_text(
                    text=globals.TEXT_LANG_WARNING
                )

        elif not db_user["first_name"]:
            db.update_user_data(user.id, "first_name", message)
            check(update, context)

        elif not db_user["last_name"]:
            db.update_user_data(user.id, "last_name", message)
            buttons = [
                [KeyboardButton(text=globals.BTN_SEND_CONTACT[db_user['lang_id']], request_contact=True)]
            ]
            check(update, context)

        elif not db_user["phone_number"]:
            db.update_user_data(user.id, "phone_number", message)
            check(update, context)

        else:
            check(update, context)

    elif state == 2:
        if message == globals.BTN_ORDER[db_user['lang_id']]:
            categories = db.get_categories_by_parent()
            buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])

            if context.user_data.get("carts", {}):
                carts = context.user_data.get("carts")
                text = f"{globals.AT_KORZINKA[db_user['lang_id']]}:\n\n"
                lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]
                total_price = 0
                for cart, val in carts.items():
                    product = db.get_product_for_cart(int(cart))
                    text += f"{val} x {product[f'cat_name_{lang_code}']} {product[f'name_{lang_code}']}\n"
                    total_price += product['price'] * val

                text += f"\n{globals.ALL[db_user['lang_id']]}: {total_price}"
                buttons.append([InlineKeyboardButton(text=globals.BTN_KORZINKA[db_user['lang_id']], callback_data="cart")])

            else:
                text = globals.TEXT_ORDER[db_user['lang_id']]
            update.message.reply_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons,
                )
            )

        elif message == globals.BTN_MY_ORDERS[db_user['lang_id']]:
            if context.user_data.get("carts", {}):
                carts = context.user_data.get("carts")
                text = "\n"
                lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]
                total_price = 0
                for cart, val in carts.items():
                    product = db.get_product_for_cart(int(cart))
                    text += f"{val} x {product[f'cat_name_{lang_code}']} {product[f'name_{lang_code}']}\n"
                    total_price += product['price'] * val
                text += f"\n{globals.ALL[db_user['lang_id']]}: {total_price} {globals.SUM[db_user['lang_id']]}"

                update.message.reply_text(
                    text=f"<b>Ma'lumotlarim:</b>\n\n"
                         f"👤 <b>Ism-familiya:</b> {db_user['first_name']} {db_user['last_name']}\n"
                         f"📞 <b>Telefon raqam:</b> {db_user['phone_number']} \n\n"
                         f"📥 <b>Buyurtmalarim:</b> \n"
                         f"{text}",
                    parse_mode='HTML'
                )

            else:
                update.message.reply_text(
                    text=globals.NO_ZAKAZ[db_user['lang_id']])

        elif message == globals.BTN_ABOUT_US[db_user['lang_id']]:
            update.message.reply_text(
                text=globals.ABOUT_COMPANY[db_user['lang_id']],
                parse_mode="HTML"
            )

        elif message == globals.BTN_SETTINGS[db_user['lang_id']]:
            user = update.message.from_user
            db_user = db.get_user_by_chat_id(user.id)
            buttons = [
                [KeyboardButton(text=globals.BTN_LANG_UZ), KeyboardButton(text=globals.BTN_LANG_RU)]
            ]
            update.message.reply_text(
                text=globals.CHOOSE_LANG,
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=buttons,
                    resize_keyboard=True
                )
            )
            context.user_data["state"] = globals.STATES["settings"]
    
    elif state ==3:
        if message == globals.BTN_LANG_UZ:
            db.update_user_data(db_user['chat_id'], "lang_id", 1)
            context.user_data["state"] = globals.STATES["reg"]
            check(update, context)

        elif message == globals.BTN_LANG_RU:
            db.update_user_data(db_user['chat_id'], "lang_id", 2)
            context.user_data["state"] = globals.STATES["reg"]
            check(update, context)


        else:
            update.message.reply_text(
                text=globals.TEXT_LANG_WARNING
            )
            
    else:
        update.message.reply_text("Salom")


def inline_handler(update, context):

    query = update.callback_query
    data_sp = str(query.data).split("_")
    db_user = db.get_user_by_chat_id(query.message.chat_id)

    if data_sp[0] == "category":
        if data_sp[1] == "product":
            if data_sp[2] == "back":
                query.message.delete()
                products = db.get_products_by_category(category_id=int(data_sp[3]))
                buttons = methods.send_product_buttons(products=products, lang_id=db_user["lang_id"])

                clicked_btn = db.get_category_parent(int(data_sp[3]))

                if clicked_btn and clicked_btn['parent_id']:
                    buttons.append([InlineKeyboardButton(
                        text="Back", callback_data=f"category_back_{clicked_btn['parent_id']}"
                    )])
                else:
                    buttons.append([InlineKeyboardButton(
                        text="Back", callback_data=f"category_back"
                    )])

                query.message.reply_text(
                    text=globals.TEXT_ORDER[db_user['lang_id']],
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=buttons,
                    )
                )

            else:
                if len(data_sp) == 4:
                    query.message.delete()
                    carts = context.user_data.get("carts", {})
                    carts[f"{data_sp[2]}"] = carts.get(f"{data_sp[2]}", 0) + int(data_sp[3])
                    context.user_data["carts"] = carts

                    categories = db.get_categories_by_parent()
                    buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])

                    text = f"{globals.AT_KORZINKA[db_user['lang_id']]}:\n\n"
                    lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]
                    total_price = 0
                    for cart, val in carts.items():
                        product = db.get_product_for_cart(int(cart))
                        text += f"{val} x {product[f'cat_name_{lang_code}']} {product[f'name_{lang_code}']}\n"
                        total_price += product['price'] * val

                    text += f"\n{globals.ALL[db_user['lang_id']]}: {total_price}"
                    buttons.append([InlineKeyboardButton(text=f"{globals.BTN_KORZINKA[db_user['lang_id']]}", callback_data="cart")])

                    query.message.reply_text(
                        text=text,
                        reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=buttons,
                        )
                    )

                else:
                    product = db.get_product_by_id(int(data_sp[2]))
                    query.message.delete()

                    caption = f"{globals.TEXT_PRODUCT_PRICE[db_user['lang_id']]} " + str(product["price"]) + \
                              f"\n{globals.TEXT_PRODUCT_DESC[db_user['lang_id']]}" + \
                              product[f"description_{globals.LANGUAGE_CODE[db_user['lang_id']]}"]

                    buttons = [
                        [
                            InlineKeyboardButton(
                                text="1️⃣",
                                callback_data=f"category_product_{data_sp[2]}_{1}"
                            ),
                            InlineKeyboardButton(
                                text="2️⃣",
                                callback_data=f"category_product_{data_sp[2]}_{2}"
                            ),
                            InlineKeyboardButton(
                                text="3️⃣",
                                callback_data=f"category_product_{data_sp[2]}_{3}"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="4️⃣",
                                callback_data=f"category_product_{data_sp[2]}_{4}"
                            ),
                            InlineKeyboardButton(
                                text="5️⃣",
                                callback_data=f"category_product_{data_sp[2]}_{5}"
                            ),
                            InlineKeyboardButton(
                                text="6️⃣",
                                callback_data=f"category_product_{data_sp[2]}_{6}"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="7️⃣",
                                callback_data=f"category_product_{data_sp[2]}_{7}"
                            ),
                            InlineKeyboardButton(
                                text="8️⃣",
                                callback_data=f"category_product_{data_sp[2]}_{8}"
                            ),
                            InlineKeyboardButton(
                                text="9️⃣",
                                callback_data=f"category_product_{data_sp[2]}_{9}"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="Back",
                                callback_data=f"category_product_back_{product['category_id']}"
                            )
                        ]
                    ]

                    query.message.reply_photo(
                        photo=open(product['image'], "rb"),
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
                    )
        elif data_sp[1] == "back":
            if len(data_sp) == 3:
                parent_id = int(data_sp[2])
            else:
                parent_id = None

            categories = db.get_categories_by_parent(parent_id=parent_id)
            buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])

            if parent_id:
                clicked_btn = db.get_category_parent(parent_id)

                if clicked_btn and clicked_btn['parent_id']:
                    buttons.append([InlineKeyboardButton(
                        text="Back", callback_data=f"category_back_{clicked_btn['parent_id']}"
                    )])
                else:
                    buttons.append([InlineKeyboardButton(
                        text="Back", callback_data=f"category_back"
                    )])

            query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons
                )
            )
        else:
            categories = db.get_categories_by_parent(parent_id=int(data_sp[1]))
            if categories:
                buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])
            else:
                products = db.get_products_by_category(category_id=int(data_sp[1]))
                buttons = methods.send_product_buttons(products=products, lang_id=db_user["lang_id"])

            clicked_btn = db.get_category_parent(int(data_sp[1]))

            if clicked_btn and clicked_btn['parent_id']:
                buttons.append([InlineKeyboardButton(
                    text="Back", callback_data=f"category_back_{clicked_btn['parent_id']}"
                )])
            else:
                buttons.append([InlineKeyboardButton(
                    text="Back", callback_data=f"category_back"
                )])

            query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons
                )
            )
    elif data_sp[0] == "cart":
        if len(data_sp) == 2 and data_sp[1] == "clear":
            context.user_data.pop("carts")
            categories = db.get_categories_by_parent()
            buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])
            text = globals.TEXT_ORDER[db_user['lang_id']]

            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons,
                )
            )

        elif len(data_sp) == 2 and data_sp[1] == "back":
            categories = db.get_categories_by_parent()
            buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])

            if context.user_data.get("carts", {}):
                carts = context.user_data.get("carts")
                text = f"{globals.AT_KORZINKA[db_user['lang_id']]}:\n\n"
                lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]
                total_price = 0
                for cart, val in carts.items():
                    product = db.get_product_for_cart(int(cart))
                    text += f"{val} x {product[f'cat_name_{lang_code}']} {product[f'name_{lang_code}']}\n"
                    total_price += product['price'] * val

                text += f"\n{globals.ALL[db_user['lang_id']]}: {total_price}"

                context.user_data.get('cart_text',text)

                buttons.append([InlineKeyboardButton(text=f"{globals.BTN_KORZINKA}", callback_data="cart")])

            else:
                text = globals.TEXT_ORDER[db_user['lang_id']]
            query.message.edit_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons,
                )
            )

        else:
            buttons = [
                [
                    InlineKeyboardButton(text="Buyurtma berish",  callback_data="order"),
                    InlineKeyboardButton(text="Savatchani bo'shatish",  callback_data="cart_clear")
                ],
                [InlineKeyboardButton(text="Orqaga",  callback_data="cart_back")],
            ]
            query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons
                )
            )

    elif data_sp[0] == "order":
        if len(data_sp) > 1 and data_sp[1] == "payment":
            context.user_data['payment_type'] = int(data_sp[2])
            query.message.delete()
            query.message.reply_text(
                text=globals.SEND_LOCATION[db_user["lang_id"]],
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text=globals.SEND_LOCATION[db_user["lang_id"]], request_location=True)]],
                                                 resize_keyboard=True)
            )
        else:
            query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(text="Naqd pul", callback_data="order_payment_1"),
                        InlineKeyboardButton(text="Karta", callback_data="order_payment_2"),
                    ]]
                )
            )

        # db.create_order(db_user['id'], context.user_data.get("carts", {}))
def contact_handler(update, context):
    db_user = db.get_user_by_chat_id(update.message.from_user.id)
    contact = update.message.contact.phone_number
    db.update_user_data(update.message.from_user.id, "phone_number", contact)
    check(update, context)

def location_handler(update, context):
    db_user = db.get_user_by_chat_id(update.message.from_user.id)
    location = update.message.location
    payment_type = context.user_data.get("payment_type", None)
    db.create_order(db_user['id'], context.user_data.get("carts", {}), payment_type, location)
    categories = db.get_categories_by_parent()
    buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])

    if context.user_data.get("carts", {}):
        carts = context.user_data.get("carts")
        text = "\n"
        lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]
        total_price = 0
        for cart, val in carts.items():
            product = db.get_product_for_cart(int(cart))
            text += f"{val} x {product[f'cat_name_{lang_code}']} {product[f'name_{lang_code}']}\n"
            total_price += product['price'] * val

        text += f"\n{globals.ALL[db_user['lang_id']]}: {total_price} {globals.SUM[db_user['lang_id']]}"

    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"<b>Yangi buyurtma:</b>\n\n"
             f"👤 <b>Ism-familiya:</b> {db_user['first_name']} {db_user['last_name']}\n"
             f"📞 <b>Telefon raqam:</b> {db_user['phone_number']} \n\n"
             f"📥 <b>Buyurtma:</b> \n"
             f"{text}",
        parse_mode='HTML'
    )


    context.bot.send_location(
        chat_id=ADMIN_ID,
        latitude=float(location.latitude),
        longitude=float(location.longitude)
    )
    methods.send_main_menu(context, update.message.from_user.id, db_user['lang_id'])


def main():
    updater = Updater("1699599225:AAGJ-jxsE9kC2f_uJOnJpyXBPxMRv_FgW1w")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(MessageHandler(Filters.contact, contact_handler))
    dispatcher.add_handler(MessageHandler(Filters.location, location_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    dispatcher.add_handler(CallbackQueryHandler(inline_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
