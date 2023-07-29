import json
import logging
import os
import threading

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import requests
import aiomysql
import asyncio
from api import TrueSocksClient
from extra import *
from utils import *
from messages import *
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle


"""
================================================================
Global configuration 
================================================================
"""
socks_response = {}
response_lock = threading.Lock()

"""
================================================================
GET socks 5 data 
================================================================
"""


def execute_code():
    global socks_response
    client = TrueSocksClient(api_key="b03a14b7128ec274b4abb70e164399b3")
    response_dict = client.get_response_dict()
    # Process the response data as needed
    # Store the result in the shared variable
    with response_lock:
        socks_response = response_dict


thread = threading.Thread(target=execute_code)
thread.start()
thread.join()

"""
================================================================
ٍSettings 
================================================================
"""
load_dotenv()
second = False
email = ""

second_gift = False
gift_id = ""
admin_user_id = "892998733"

# Set up logging
logging.basicConfig(level=logging.INFO)

bot_token = os.getenv("BOT_TOKEN")
# Initialize bot and dispatcher
bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_database = os.getenv("DB_DATABASE")


async def create_pool():
    return await aiomysql.create_pool(
        host=db_host, user=db_user, password=db_password, db=db_database
    )


loop = asyncio.get_event_loop()
pool = loop.run_until_complete(create_pool())

"""
================================================================
Socks client
================================================================
"""

"""
================================================================
Define states for the conversation 
================================================================
"""


class ButtonState(StatesGroup):
    MAIN_MENU = State()
    PAYMENT = State()
    ACCOUNT = State()
    CHARGE = State()
    GIFT = State()
    SOCKS9800 = State()
    STATE9800 = State()
    TEST = State()
    ISP09800 = State()
    SOCKSFILTERSELECTED = State()
    SPEED9800 = State()
    TRANS = State()
    SEX = State()
    UPLOAD = State()
    CODE = State()


# Button texts
BUTTON_TEXTS = {
    "main_menu": [
        "شراء بروكسي",
        "حسابي",
        "إضافة رصيد",
        "التواصل مع الدعم",
        "حول البوت",
    ],
    "payment_options": [
        "شراء بروكسي يومي SOCKS 5",
        "شراء بروكسي مؤقت SOCKS 5",
        "شراء مودم روتيت",
        "شراء روتيت يومي",
    ],
    "back_button": "رجوع ↪️",
    "account_options": [
        "شحن حساب non-voip",
        "إهداء رصيد",
    ],
}

"""
================================================================
DB operations
================================================================
"""


async def get_user_wallet(user_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT balance FROM wallets WHERE user_id = %s", (user_id,)
            )
            result = await cur.fetchone()
            if result:
                return result[0]
            else:
                return None


async def charge_user_balance(user_id, amount):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Retrieve the current balance of the user
            await cur.execute(
                "SELECT balance FROM wallets WHERE user_id = %s", (user_id,)
            )
            result = await cur.fetchone()

            if result:
                current_balance = result[0]
                new_balance = current_balance + amount

                # Update the user's balance
                await cur.execute(
                    "UPDATE wallets SET balance = %s WHERE user_id = %s",
                    (new_balance, user_id),
                )
                await conn.commit()

                return new_balance
            else:
                # User doesn't have a wallet
                return None


async def withdraw_user_balance(user_id, amount):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Retrieve the current balance of the user
            await cur.execute(
                "SELECT balance FROM wallets WHERE user_id = %s", (user_id,)
            )
            result = await cur.fetchone()

            if result:
                current_balance = result[0]

                if current_balance >= amount:
                    new_balance = current_balance - amount

                    # Update the user's balance
                    await cur.execute(
                        "UPDATE wallets SET balance = %s WHERE user_id = %s",
                        (new_balance, user_id),
                    )
                    await conn.commit()

                    return new_balance
                else:
                    # Insufficient balance
                    return None
            else:
                # User doesn't have a wallet
                return None


async def create_user_wallet(user_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Check if the user already has a wallet
            await cur.execute(
                "SELECT balance FROM wallets WHERE user_id = %s", (user_id,)
            )
            result = await cur.fetchone()
            if result:
                # User already has a wallet, update the balance
                return
            else:
                # User doesn't have a wallet, insert a new row
                await cur.execute(
                    "INSERT INTO wallets (user_id, balance) VALUES (%s, 0)", (user_id,)
                )
            await conn.commit()


"""
================================================================
Bot API
================================================================
"""


# Show the main menu
async def show_main_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = BUTTON_TEXTS["main_menu"]
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.row(buttons[i], buttons[i + 1])  # Add buttons in pairs
        else:
            keyboard.add(
                buttons[i]
            )  # Add the last button alone if there's only one left
    await bot.send_message(message.chat.id, "اختر طلبك 👇🏻 :", reply_markup=keyboard)


@dp.message_handler(content_types=types.ContentType.PHOTO, state=ButtonState.UPLOAD)
async def handle_image(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await bot.send_photo(chat_id=admin_user_id, photo=photo_id)
    await state.finish()  # Clear the current state
    await show_main_menu(message)  # Show the main menu with the appropriate keyboard


@dp.message_handler(content_types=types.ContentType.TEXT, state=ButtonState.CODE)
async def handle_code(message: types.Message, state: FSMContext):
    text = message.text
    await bot.send_message(message.chat.id, text)
    await state.finish()  # Clear the current state
    await show_main_menu(message)  # Show the main menu with the appropriate keyboard


# Show the payment options menu
async def show_payment_options(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = BUTTON_TEXTS["payment_options"]
    for button_text in buttons:
        keyboard.add(button_text)
    keyboard.add(BUTTON_TEXTS["back_button"])
    await bot.send_message(message.chat.id, "اختر طلبك 👇🏻 :", reply_markup=keyboard)


# Handlers for button selections
@dp.message_handler(text=BUTTON_TEXTS["main_menu"], state=ButtonState.MAIN_MENU)
async def main_menu_selected(message: types.Message, state: FSMContext):
    await ButtonState.MAIN_MENU.set()
    if message.text == "شراء بروكسي":
        await ButtonState.PAYMENT.set()
        await show_payment_options(message)
    elif message.text == "حسابي":
        await ButtonState.ACCOUNT.set()
        user_id = message.from_user.id
        wallet_balance = await get_user_wallet(user_id)
        await bot.send_message(
            message.chat.id,
            f"رصيدي ل.س: {wallet_balance}\nرصيدي بروكسيات يومية: 0\nالايدي الخاص بي: {user_id}",
        )
        await show_account_menu(message)
    elif message.text == "التواصل مع الدعم":
        await bot.send_message(
            message.chat.id,
            "التواصل مع الدعم:\nيمكنك التواصل مع الدعم على الرابط التالي: https://t.me/Proxies_bot_support",
        )

    elif message.text == "إضافة رصيد":
        await ButtonState.CHARGE.set()
        callback_options = [
            types.InlineKeyboardButton(text="تحويل الهرم 🏧", callback_data="haram"),
            types.InlineKeyboardButton(text="تحويل بنك بيمو 🏦", callback_data="bemo"),
            types.InlineKeyboardButton(text="📶 MTN cash", callback_data="mtn"),
            types.InlineKeyboardButton(
                text="📶 Syriatel cash", callback_data="syriatel"
            ),
            types.InlineKeyboardButton(text="روابط بايبال 🌐", callback_data="paypal"),
            types.InlineKeyboardButton(text="آيتونز 🎵", callback_data="tunes"),
            types.InlineKeyboardButton(text="💶 Payeer", callback_data="payeer"),
            types.InlineKeyboardButton(text="💶 USDT", callback_data="usd"),
            types.InlineKeyboardButton(text="💳 Master Card", callback_data="master"),
            types.InlineKeyboardButton(text="فيزا (لاتدمج)💳", callback_data="visa"),
            types.InlineKeyboardButton(text="Razer gold", callback_data="razer"),
            types.InlineKeyboardButton(text="Amazon", callback_data="amazon"),
        ]

        callback_markup = types.InlineKeyboardMarkup(row_width=2)
        for i in range(0, len(callback_options), 2):
            if i + 1 < len(callback_options):
                callback_markup.row(callback_options[i], callback_options[i + 1])
            else:
                callback_markup.add(callback_options[i])

        await bot.send_message(
            message.chat.id, "اختر خيار إضافة الرصيد:", reply_markup=callback_markup
        )

    elif message.text == "حول البوت":
        await bot.send_message(
            message.chat.id, f"{channel_link}\n\n{group_link}\n\n{support_link}"
        )


@dp.message_handler(text="رجوع ↪️", state=ButtonState.UPLOAD)
async def upload_done(message: types.Message, state: FSMContext):
    await ButtonState.MAIN_MENU.set()  # Clear the current state
    await show_main_menu(message)


async def show_account_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = BUTTON_TEXTS["account_options"]
    for button_text in buttons:
        keyboard.add(button_text)
    keyboard.add(BUTTON_TEXTS["back_button"])

    await bot.send_message(message.chat.id, "اختر طلبك 👇🏻 :", reply_markup=keyboard)


@dp.message_handler(state=ButtonState.PAYMENT)
async def payment_option_selected(message: types.Message, state: FSMContext):
    await ButtonState.SOCKS9800.set()
    fixed_countries = [
        "UNITED STATES",
        "CANADA",
        "SPAIN",
        "GERMANY",
        "UNITED KINGDOM",
    ]
    callback_options = [
        types.InlineKeyboardButton(
            text=country.capitalize(), callback_data=country.capitalize()
        )
        for country in fixed_countries
    ]

    callback_markup = types.InlineKeyboardMarkup(row_width=1)
    for option in callback_options:
        callback_markup.add(option)

    await bot.send_message(message.chat.id, socks9message, reply_markup=callback_markup)


@dp.callback_query_handler(state=ButtonState.SOCKS9800)
async def handle_socks9800_countries_callback(
    query: types.CallbackQuery, state: FSMContext
):
    if not query.data == "back":
        country_query = query.data.upper()

        fixed_filters = [
            "By state",
            "BY ISP",
            "BY Speed",
        ]
        callback_options = [
            types.InlineKeyboardButton(text=element, callback_data=element)
            for element in fixed_filters
        ]
        callback_options.append(
            types.InlineKeyboardButton(text="back", callback_data="back")
        )

        callback_markup = types.InlineKeyboardMarkup(row_width=1)
        for option in callback_options:
            callback_markup.add(option)

        await ButtonState.SOCKSFILTERSELECTED.set()
        # Store the selected country in session
        await state.update_data(selected_country=country_query)

        await query.message.edit_reply_markup(reply_markup=callback_markup)
    else:
        await ButtonState.SOCKS9800.set()
        fixed_countries = [
            "UNITED STATES",
            "CANADA",
            "SPAIN",
            "GERMANY",
            "UNITED KINGDOM",
        ]
        callback_options = [
            types.InlineKeyboardButton(
                text=country.capitalize(), callback_data=country.capitalize()
            )
            for country in fixed_countries
        ]

        callback_markup = types.InlineKeyboardMarkup(row_width=1)
        for option in callback_options:
            callback_markup.add(option)
        await query.message.edit_reply_markup(reply_markup=callback_markup)


@dp.callback_query_handler(state=ButtonState.SOCKSFILTERSELECTED)
async def handle_socks9800_filters_callback(
    query: types.CallbackQuery, state: FSMContext
):
    query_data = query.data
    # Store the selected filter in session
    await state.update_data(selected_filter=query_data)
    data = await state.get_data()
    proxies_list = socks_response["result"]["ProxyList"]
    country_query = data["selected_country"]
    if query_data == "By state":
        await ButtonState.STATE9800.set()

        # Replace 'data["country_query"]' with the actual country you want to filter

        states = [state for state in get_states(proxies_list, country_query)]

        # Split the states list into groups of 4
        states_groups = [states[i : i + 4] for i in range(0, len(states), 4)]

        callback_markup = types.InlineKeyboardMarkup(row_width=2)
        for group in states_groups:
            callback_options = [
                types.InlineKeyboardButton(
                    text=element.capitalize(),
                    switch_inline_query_current_chat=f"SOCKS5 |{country_query} |{element}",
                )
                for element in group
            ]
            callback_markup.row(*callback_options)
        callback_markup.row(
            types.InlineKeyboardButton(text="back", callback_data="back")
        )

        await bot.send_message(
            query.from_user.id,
            "اختر الولاية المرادة:",
            reply_markup=callback_markup,
        )

    elif query_data == "BY Speed":
        pass

    elif query_data == "BY ISP":
        await ButtonState.ISP09800.set()
        if country_query == "UNITED STATES":
            await choose_country_isp(bot, query, usa)
        elif country_query == "UNITED KINGDOM":
            await choose_country_isp(bot, query, uk)

        elif country_query == "GERMANY":
            await choose_country_isp(bot, query, germany)

        elif country_query == "SPAIN":
            await choose_country_isp(bot, query, spain)

        elif country_query == "CANADA":
            await choose_country_isp(bot, query, canada)
    else:
        await ButtonState.SOCKS9800.set()
        await handle_socks9800_countries_callback(query, state)



@dp.callback_query_handler(state=ButtonState.STATE9800)
async def handle_socks9800_state_filter_callback(
        query: types.CallbackQuery, state: FSMContext
):
    query_data = query.data
    if query_data == 'back':
        data = await state.get_data()
        country_query = data["selected_country"]
        fixed_filters = [
            "By state",
            "BY ISP",
            "BY Speed",
        ]
        callback_options = [
            types.InlineKeyboardButton(text=element, callback_data=element)
            for element in fixed_filters
        ]
        callback_options.append(
            types.InlineKeyboardButton(text="back", callback_data="back")
        )

        callback_markup = types.InlineKeyboardMarkup(row_width=1)
        for option in callback_options:
            callback_markup.add(option)

        await ButtonState.SOCKSFILTERSELECTED.set()
        # Store the selected country in session
        await state.update_data(selected_country=country_query)

        await query.message.edit_reply_markup(reply_markup=callback_markup)


    # selected_state = query_data
    # selected_country = await state.get_data('selected_country') # Replace this with the actual country name
    #
    # formatted_message = f"@amjad_ahmad_bot p:SOCKS5 | c: {selected_country} | s:{selected_state}"
    #
    # # Edit the user's input message to the formatted message
    # await bot.send_message(
    #     query.from_user.id,
    #     formatted_message,
    #     reply_to_message_id=query.message.message_id,
    #     reply_markup=types.InlineKeyboardMarkup().add(
    #         types.InlineKeyboardButton(
    #             text="Select State", switch_inline_query_current_chat=f"SOCKS5 | c: {selected_country} | s:{selected_state}"
    #         )
    #     ),
    # )


@dp.message_handler(state=ButtonState.ACCOUNT)
async def non_voip_selected(message: types.Message, state: FSMContext):
    if message.text == "شحن حساب non-voip":
        await ButtonState.TRANS.set()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(BUTTON_TEXTS["back_button"])
        await bot.send_message(message.chat.id, voip_message)
        await bot.send_message(
            message.chat.id,
            "🔻 قم بارسل الايميل خاص ب حسابك على الموقع",
            reply_markup=keyboard,
        )

    elif message.text == BUTTON_TEXTS["back_button"]:
        await ButtonState.MAIN_MENU.set()
        await show_main_menu(message)

    elif message.text == "إهداء رصيد":
        await ButtonState.GIFT.set()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(BUTTON_TEXTS["back_button"])
        await bot.send_message(
            message.chat.id,
            gift_message,
            reply_markup=keyboard,
        )


# todo fix it with states
@dp.message_handler(state=ButtonState.GIFT)
async def gift_handler(message: types.Message, state: FSMContext):
    global second_gift, gift_id

    if message.text == BUTTON_TEXTS["back_button"]:
        await ButtonState.ACCOUNT.set()
        second_gift = False
        await show_account_menu(message)

    elif second_gift:
        print(gift_id)
        print(second_gift)

    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(BUTTON_TEXTS["back_button"])
        await bot.send_message(
            message.chat.id,
            "🔻 أرسل قيمة الرصيد المراد اهداؤها",
            reply_markup=keyboard,
        )
        second_gift = True


@dp.message_handler(state=ButtonState.TRANS)
async def non_voip_handler(message: types.Message, state: FSMContext):
    global second, email

    if message.text == BUTTON_TEXTS["back_button"]:
        await ButtonState.ACCOUNT.set()
        second = False
        await show_account_menu(message)

    elif second:
        creds = int(message.text)
        discounted = creds * voip_credit
        currnet_wallet = await get_user_wallet(message.from_user.id)
        if discounted > currnet_wallet:
            await bot.send_message(
                message.chat.id,
                f"ليس لديك رصيد كافي لاجراء عملية التحويل المطلوبة",
            )
            await bot.send_message(
                message.chat.id,
                f"العودة الى القائمة الرئيسية ...",
            )
            await ButtonState.MAIN_MENU.set()
            await show_main_menu(message)

        else:
            url = "https://non-voip.com/api/reseller/transfer_credit/"
            headers = {"api_key": "vHAn43BNXCKqSd", "email": "stievelame@gmail.com"}
            data = {"email_to": email, "amount": str(creds)}
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                response_json = response.json()
                if response_json.get("code") == 200:
                    await bot.send_message(
                        message.chat.id,
                        f"تم شحن حسابك ب {creds} credits",
                    )
                    discounted = creds * voip_credit
                    await withdraw_user_balance(message.from_user.id, discounted)
                    await bot.send_message(
                        message.chat.id,
                        f"تم اقتطاع {discounted} من رصيد حسابك على البوت",
                    )
                    await ButtonState.ACCOUNT.set()
                    await show_account_menu(message)
                else:
                    await bot.send_message(
                        message.chat.id,
                        "خطأ في القيم المدخلة",
                    )
                    await ButtonState.ACCOUNT.set()
                    await show_account_menu(message)
            else:
                print(f"POST request failed with status code: {response.status_code}")

    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(BUTTON_TEXTS["back_button"])
        email = message.text
        await bot.send_message(
            message.chat.id,
            "🔻 قم بإدخال عدد الكريدت المراد شحن حسابك به على الموقع",
            reply_markup=keyboard,
        )
        second = True


@dp.message_handler(state=ButtonState.CHARGE)
async def charge_balance(message: types.Message, state: FSMContext):
    # Process the user's reply message here
    await state.finish()  # Clear the current state
    await show_main_menu(message)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await ButtonState.MAIN_MENU.set()
    await create_user_wallet(message.from_user.id)
    await show_main_menu(message)


async def send_transfer_image(query, message):
    await ButtonState.UPLOAD.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(BUTTON_TEXTS["back_button"])
    await bot.send_message(
        query.from_user.id,
        message,
        reply_markup=keyboard,
    )


async def send_transfer_code(query, message):
    await ButtonState.CODE.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(BUTTON_TEXTS["back_button"])
    await bot.send_message(
        query.from_user.id,
        message,
        reply_markup=keyboard,
    )


@dp.callback_query_handler(state=ButtonState.CHARGE)
async def process_callback_option(query: types.CallbackQuery):
    callback_data = query.data
    if callback_data == "haram":
        await bot.send_message(query.from_user.id, haram_message)
        await send_transfer_image(query, image_message)

    elif callback_data == "bemo":
        await bot.send_message(query.from_user.id, bemo_message)
        await send_transfer_image(query, image_message)

    elif callback_data == "mtn":
        await bot.send_message(query.from_user.id, mtn_message)
        await send_transfer_code(query, transfer_message)

    elif callback_data == "syriatel":
        await bot.send_message(query.from_user.id, syriatel_message)
        await send_transfer_code(query, transfer_message)

    elif callback_data == "paypal":
        await bot.send_message(query.from_user.id, paypal_message)
        await send_transfer_code(query, paypal_link)

    elif callback_data == "tunes":
        await bot.send_message(query.from_user.id, itunes_message)
        await send_transfer_code(query, itunes_link)

    elif callback_data == "usd":
        await bot.send_message(query.from_user.id, usd_message)
        await send_transfer_image(query, image_message)

    elif callback_data == "payeer":
        await bot.send_message(query.from_user.id, payeer_message)
        await send_transfer_code(query, transfer_message)

    elif callback_data == "master":
        await bot.send_message(query.from_user.id, master_message)
        await send_transfer_code(query, master_code)

    elif callback_data == "visa":
        await bot.send_message(query.from_user.id, visa_message)
        await send_transfer_code(query, visa_code)

    elif callback_data == "razer":
        await bot.send_message(query.from_user.id, razer_message)
        await send_transfer_code(query, razer_code)

    elif callback_data == "amazon":
        await bot.send_message(query.from_user.id, amazon_message)
        await send_transfer_code(query, amazon_code)


"""
================================================================
INLINE QUERIES HANDLERS
================================================================
"""


@dp.inline_handler(state=ButtonState.STATE9800)
async def handle_inline_query(query: InlineQuery):
    query_text = query.query  # Convert query to lowercase
    query_parts = query_text.split("|")  # Split the query by the pipe symbol "|"

    if len(query_parts) == 3:
        proxy_type = query_parts[0].strip()  # Extract proxy type
        country = query_parts[1].strip()  # Extract country
        state = query_parts[2].strip()  # Extract state
        state_proxies = filter_by_state(socks_response["result"]["ProxyList"], state)
        state_proxies = state_proxies[:40]
        results = []
        for proxy in state_proxies:
            id = proxy["ProxyID"]
            city = proxy["City"]
            code = proxy["CountryCode"]
            zip = proxy["ZipCode"]
            isp = proxy["ISP"]
            title = f"{code}-{state}-{city}-{zip}"
            content = f"Proxy id {id} - p:{proxy_type} | c:{country} | s:{state}"
            result = InlineQueryResultArticle(
                id=str(id),
                title=title,
                input_message_content=InputTextMessageContent(content),
                thumb_url="https://static.vecteezy.com/system/resources/previews/008/174/237/non_2x/internet-icon-click-to-go-online-icon-connect-to-internet-icon-web-surfing-and-internet-symbol-free-vector.jpg",
                description=isp,
            )
            results.append(result)

        await bot.answer_inline_query(query.id, results)
    else:
        # Invalid format, provide an error message
        error_result = InlineQueryResultArticle(
            id="error",
            title="Invalid Format",
            input_message_content=InputTextMessageContent(
                "Please use the following format: p:ProxyType | c:Country | s:State"
            ),
        )
        await bot.answer_inline_query(query.id, [error_result])


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
