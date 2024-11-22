import logging
from functools import partial

from environs import Env
import redis
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
      CallbackContext, CallbackQueryHandler

from strapi import get_products, get_product, get_or_create_cart, \
    create_cart_product, add_cart_product_to_cart, get_cart_by_id, \
    get_cart_product, delete_cart_product, get_or_create_client


logger = logging.getLogger(__name__)

_database = None


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def start(update: Updater, context: CallbackContext, strapi_api_token):
    products = get_products(strapi_api_token)
    keyboard = [[InlineKeyboardButton(
        product['title'],
        callback_data=product['documentId']
    )] for product in products]

    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text(
            'Добрый день!\nЭто рыбный магазин.\nВыберите продукт:',
            reply_markup=reply_markup,
        )
    else:
        query = update.callback_query
        query.message.reply_text(
            'Выберите продукт:',
            reply_markup=reply_markup,
        )
    return 'HANDLE_MENU'


def handle_menu(update: Updater, context: CallbackContext, strapi_api_token, db):
    query = update.callback_query
    query.answer()

    product_id = query.data
    product, image_data = get_product(strapi_api_token, product_id)
    text = f'''{product['title']} ({product['price']} руб. за кг)\n
    {product['description']}'''

    db.set('product_id', query.data)

    keyboard = [
        [InlineKeyboardButton('В меню', callback_data='menu')],
        [InlineKeyboardButton('Добавить в корзину', callback_data='add_to_cart')],
        [InlineKeyboardButton('Моя корзина', callback_data='show_cart')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=image_data,
        caption=text,
        reply_markup=reply_markup,
    )

    context.bot.delete_message(chat_id=query.message.chat.id,
                               message_id=query.message.message_id)

    return 'HANDLE_DESCRIPTION'


def handle_description(update: Updater,
                       context: CallbackContext,
                       strapi_api_token,
                       db):
    query = update.callback_query
    query.answer()
    if query.data == 'add_to_cart':
        user_id = query.from_user.id
        product_id = db.get('product_id').decode('utf-8')
        db.set('product_id', '')
        cart_id = get_or_create_cart(strapi_api_token, str(user_id))
        cart_product_id = create_cart_product(strapi_api_token, product_id)['data']['documentId']
        add_cart_product_to_cart(strapi_api_token, cart_id, cart_product_id)
        query.message.reply_text(
            'Добавлено в корзину'
        )
        return 'HANDLE_DESCRIPTION'

    if query.data == 'menu':
        start(update, context, strapi_api_token)
        return 'HANDLE_MENU'

    if query.data == 'show_cart':
        user_id = query.from_user.id
        cart_products = get_cart_by_id(strapi_api_token, user_id)
        reply_text = 'Ваши товары: \n'
        total_sum = 0
        keyboard = []
        for cart_product in cart_products:
            cart_product_id = cart_product['documentId']
            cart_product = get_cart_product(strapi_api_token, cart_product_id)
            title = cart_product['data']['product']['title']
            quantity = cart_product['data']['quantity']
            price = cart_product['data']['product']['price']
            reply_text += f'{title} - {quantity} кг по цене {price} руб. за кг \n'
            total_sum += quantity * price
            keyboard.append(
                [InlineKeyboardButton(f'Убрать {title}',
                                      callback_data=cart_product_id)]
            )
        reply_text += f'Ваш заказ на сумму {total_sum} руб.'
        keyboard.append([InlineKeyboardButton('В меню', callback_data='menu')])
        keyboard.append([InlineKeyboardButton('Оплатить', callback_data='payment')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(
            chat_id=query.from_user.id,
            text=reply_text,
            reply_markup=reply_markup
        )
        return 'HANDLE_CART'


def handle_cart(update: Updater,
                context: CallbackContext,
                strapi_api_token):
    query = update.callback_query
    query.answer()
    if query.data == 'menu':
        start(update, context, strapi_api_token)
        return 'HANDLE_MENU'
    if query.data == 'payment':
        context.bot.send_message(
            chat_id=query.from_user.id,
            text='Для согласования оплаты укажите Ваш email'
        )
        return 'WAITING_EMAIL'
    else:
        cart_product_id = query.data
        delete_cart_product(strapi_api_token, cart_product_id)
        query.message.reply_text(
            'Товар удален'
        )
        return 'HANDLE_CART'


def handle_email(update: Updater,
                 context: CallbackContext,
                 strapi_api_token):

    user_id = update.effective_chat.id
    cart_id = get_or_create_cart(strapi_api_token, str(user_id))
    if update.message:
        email = update.message.text
        update.message.reply_text(
            text=f'Вы прислали мне эту почту {email}'
        )
        get_or_create_client(
            strapi_api_token,
            str(user_id),
            email,
            cart_id
        )
        update.message.reply_text(
            'Заказ оформлен'
        )
    return 'HANDLE_MENU'


def get_database_connection(redis_db_host, redis_db_port):
    global _database
    if _database is None:
        _database = redis.Redis(host=redis_db_host, port=redis_db_port)
    return _database


def handle_users_reply(update,
                       context,
                       db,
                       strapi_api_token):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': partial(start,
                         strapi_api_token=strapi_api_token),
        'HANDLE_MENU': partial(handle_menu,
                               strapi_api_token=strapi_api_token,
                               db=db),
        'HANDLE_DESCRIPTION': partial(handle_description,
                                      strapi_api_token=strapi_api_token,
                                      db=db),
        'HANDLE_CART': partial(handle_cart,
                               strapi_api_token=strapi_api_token),
        'WAITING_EMAIL': partial(handle_email,
                                 strapi_api_token=strapi_api_token),
    }
    state_handler = states_functions[user_state]

    try:
        next_state = state_handler(update, context)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def main() -> None:
    env = Env()
    env.read_env()
    tg_bot_token = env.str('TG_BOT_TOKEN')
    tg_chat_id = env.str('TG_CHAT_ID')
    redis_db_host = env.str('REDIS_DB_HOST')
    redis_db_port = env.str('REDIS_DB_PORT')
    strapi_api_token = env.str('STRAPI_API_TOKEN')
    bot = Bot(tg_bot_token)
    db = get_database_connection(redis_db_host, redis_db_port)

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger.addHandler(TelegramLogsHandler(bot, tg_chat_id))
    logger.info('Бот запущен')

    updater = Updater(tg_bot_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        CallbackQueryHandler(partial(handle_users_reply,
                                     db=db,
                                     strapi_api_token=strapi_api_token)))
    dispatcher.add_handler(
        MessageHandler(Filters.text, partial(handle_users_reply,
                                             db=db,
                                             strapi_api_token=strapi_api_token)))
    dispatcher.add_handler(
        CommandHandler('start', partial(handle_users_reply,
                                        db=db,
                                        strapi_api_token=strapi_api_token)))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
