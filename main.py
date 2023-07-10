import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import aiomysql
import asyncio
from messages import *

load_dotenv()

admin_user_id = "822439274"

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


# Define states for the conversation
class ButtonState(StatesGroup):
    MAIN_MENU = State()
    PAYMENT = State()
    ACCOUNT = State()
    SUPPORT = State()
    CHARGE = State()
    UPLOAD = State()
    CODE = State()
    TEMP_SOCKS_MENU = State()


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
    "temp_socks_menu": [
        "شراء بروكسي بورت (9800)",
        "شراء باقة بروكسيات يومية",
        "اإمكانية إعادة حساب",
        "Button 4",
        "Button 5",
    ],
}


@dp.message_handler(content_types=types.ContentType.PHOTO, state=ButtonState.UPLOAD)
async def handle_image(message: types.Message, state: FSMContext):
    # Get the photo file ID
    photo_id = message.photo[-1].file_id

    # Download the photo file
    await bot.send_photo(chat_id=admin_user_id, photo=photo_id)

    # Delete the downloaded photo file

    await state.finish()  # Clear the current state
    await show_main_menu(message)  # Show the main menu with the appropriate keyboard


@dp.message_handler(content_types=types.ContentType.TEXT, state=ButtonState.CODE)
async def handle_code(message: types.Message, state: FSMContext):
    # Get the photo file ID
    text = message.text

    # Download the photo file
    await bot.send_photo(chat_id=admin_user_id, photo=text)

    # Delete the downloaded photo file

    await state.finish()  # Clear the current state
    await show_main_menu(message)  # Show the main menu with the appropriate keyboard


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


# Show the main menu
async def show_main_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = BUTTON_TEXTS["main_menu"]
    keyboard.add(*buttons)
    await bot.send_message(message.chat.id, "اختر طلبك 👇🏻 :", reply_markup=keyboard)


# Show the payment options menu
async def show_payment_options(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = BUTTON_TEXTS["payment_options"]
    for button_text in buttons:
        keyboard.add(button_text)
    keyboard.add(BUTTON_TEXTS["back_button"])
    await bot.send_message(message.chat.id, "اختر طلبك 👇🏻 :", reply_markup=keyboard)


# Show the temporary SOCKS menu


# Handlers for button selections
@dp.message_handler(text=BUTTON_TEXTS["main_menu"], state="*")
async def main_menu_selected(message: types.Message, state: FSMContext):
    await ButtonState.MAIN_MENU.set()
    if message.text == "شراء بروكسي":
        await ButtonState.PAYMENT.set()
        await show_payment_options(message)
    elif message.text == "حسابي":
        await ButtonState.ACCOUNT.set()
        user_id = message.from_user.id
        wallet_balance = await get_user_wallet(user_id)
        await state.finish()
        await bot.send_message(
            message.chat.id,
            f"رصيدي ل.س: {wallet_balance}\nرصيدي بروكسيات يومية: 0\nالايدي الخاص بي: {user_id}",
        )
    elif message.text == "التواصل مع الدعم":
        await ButtonState.SUPPORT.set()
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
        await ButtonState.MAIN_MENU.set()
        await bot.send_message(
            message.chat.id, f"{channel_link}\n\n{group_link}\n\n{support_link}"
        )


@dp.message_handler(
    text=[BUTTON_TEXTS["back_button"]], state=ButtonState.TEMP_SOCKS_MENU
)
async def temp_socks_menu_back_selected(message: types.Message, state: FSMContext):
    await state.finish()  # Clear the current state
    await show_payment_options(message)


@dp.message_handler(text="رجوع ↪️", state=ButtonState.PAYMENT)
async def payment_options_back_selected(message: types.Message, state: FSMContext):
    await state.finish()  # Clear the current state
    await show_main_menu(message)


@dp.message_handler(text="رجوع ↪️", state=ButtonState.UPLOAD)
async def upload_done(message: types.Message, state: FSMContext):
    await state.finish()  # Clear the current state
    await show_main_menu(message)


# Show the temporary SOCKS menu
async def show_temp_socks_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = BUTTON_TEXTS["temp_socks_menu"]
    for button_text in buttons:
        keyboard.add(button_text)
    keyboard.add(BUTTON_TEXTS["back_button"])
    await bot.send_message(message.chat.id, "اختر طلبك 👇🏻 :", reply_markup=keyboard)


@dp.message_handler(text=BUTTON_TEXTS["payment_options"], state=ButtonState.PAYMENT)
async def payment_option_selected(message: types.Message, state: FSMContext):
    if message.text == "شراء بروكسي يومي SOCKS 5":
        await ButtonState.TEMP_SOCKS_MENU.set()
        await show_temp_socks_menu(message)


@dp.message_handler(
    text=[BUTTON_TEXTS["back_button"]], state=ButtonState.TEMP_SOCKS_MENU
)
async def temp_socks_menu_back_selected(message: types.Message, state: FSMContext):
    await state.finish()  # Clear the current state
    await show_payment_options(message)


@dp.message_handler(text=[BUTTON_TEXTS["back_button"]], state=ButtonState.PAYMENT)
async def payment_options_back_selected(message: types.Message, state: FSMContext):
    await state.finish()  # Clear the current state
    await show_main_menu(message)


@dp.message_handler(state=ButtonState.CHARGE)
async def charge_balance(message: types.Message, state: FSMContext):
    # Process the user's reply message here
    await state.finish()  # Clear the current state
    await show_main_menu(message)


# Start command handler
@dp.message_handler(CommandStart())
async def start(message: types.Message):
    await create_user_wallet(message.from_user.id)
    await show_main_menu(message)


@dp.callback_query_handler(state=ButtonState.CHARGE)
async def process_callback_option(query: types.CallbackQuery):
    print(query.data)
    callback_data = query.data
    if callback_data == "haram":
        await bot.send_message(query.from_user.id, haram_message)
        await bot.send_message(query.from_user.id, image_message)

    elif callback_data == "bemo":
        await bot.send_message(query.from_user.id, bemo_message)
        await bot.send_message(query.from_user.id, image_message)
        await ButtonState.UPLOAD.set()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(BUTTON_TEXTS["back_button"])
        await bot.send_message(
            query.from_user.id,
            "You can send an image or press the back button:",
            reply_markup=keyboard,
        )

    elif callback_data == "mtn":
        await bot.send_message(query.from_user.id, mtn_message)
        await bot.send_message(query.from_user.id, transfer_message)

    elif callback_data == "syriatel":
        await bot.send_message(query.from_user.id, syriatel_message)
        await bot.send_message(query.from_user.id, transfer_message)

    elif callback_data == "paypal":
        await bot.send_message(query.from_user.id, paypal_message)
        await bot.send_message(query.from_user.id, paypal_link)

    elif callback_data == "tunes":
        await bot.send_message(query.from_user.id, itunes_message)
        await bot.send_message(query.from_user.id, itunes_link)

    elif callback_data == "usd":
        await bot.send_message(query.from_user.id, usd_message)
        await bot.send_message(query.from_user.id, image_message)

    elif callback_data == "payeer":
        await bot.send_message(query.from_user.id, payeer_message)

        await bot.send_message(query.from_user.id, transfer_message)

    elif callback_data == "master":
        await bot.send_message(query.from_user.id, master_message)

        await bot.send_message(query.from_user.id, master_code)

    elif callback_data == "visa":
        await bot.send_message(query.from_user.id, visa_message)

        await bot.send_message(query.from_user.id, visa_code)

    elif callback_data == "razer":
        await bot.send_message(query.from_user.id, razer_message)

        await bot.send_message(query.from_user.id, razer_code)

    elif callback_data == "amazon":
        await bot.send_message(query.from_user.id, amazon_message)

        await bot.send_message(query.from_user.id, amazon_code)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
