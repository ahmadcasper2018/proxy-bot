import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

bot_token = os.getenv("BOT_TOKEN")
# Initialize bot and dispatcher
bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Define states for the conversation
class ButtonState(StatesGroup):
    MAIN_MENU = State()
    PAYMENT = State()
    ACCOUNT = State()
    SUPPORT = State()
    CHARGE = State()


# Button texts
BUTTON_TEXTS = {
    "main_menu": ["شراء بروكسي", "حسابي", "التواصل مع الدعم", "إضافة رصيد", "حول البوت"],
    "payment_options": ["شراء بروكسي يومي SOCKS 5", "شراء بروكسي مؤقت SOCKS 5", "شراء مودم روتيت", "شراء روتيت يومي"],
    "back_button": "رجوع ↪️"
}


# Handler for the /start command or when the bot is started
@dp.message_handler(CommandStart())
async def start_command(message: types.Message):
    await show_main_menu(message)


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


# Handlers for button selections
@dp.message_handler(text=BUTTON_TEXTS["main_menu"], state="*")
async def main_menu_selected(message: types.Message, state: FSMContext):
    await ButtonState.MAIN_MENU.set()
    if message.text == "شراء بروكسي":
        await ButtonState.PAYMENT.set()
        await show_payment_options(message)
    elif message.text == "حسابي":
        await ButtonState.ACCOUNT.set()
        await message.reply("You selected Button حسابي. Write your reply message:")
    elif message.text == "التواصل مع الدعم":
        await ButtonState.SUPPORT.set()
        await bot.send_message(message.chat.id, "التواصل مع الدعم:\nيمكنك التواصل مع الدعم على الرابط التالي: https://t.me/Proxies_bot_support")
    elif message.text == "إضافة رصيد":
        await ButtonState.CHARGE.set()
        await message.reply("You selected Button إضافة رصيد. Write your reply message:")
    elif message.text == "حول البوت":
        await ButtonState.MAIN_MENU.set()
        channel_link = "رابط القناة:\nhttps://t.me/Proxies1Channel"
        group_link = "رابط المجموعة:\nhttp://t.me/Proxies_Group_Chat"
        support_link = "رابط مراسلة الدعم للاستفسار:\nhttp://t.me/Proxies_bot_support"
        reply_message = f"{channel_link}\n\n{group_link}\n\n{support_link}"
        await bot.send_message(message.chat.id, reply_message)


@dp.message_handler(text=[BUTTON_TEXTS["back_button"]], state="*")
async def cancel_selected(message: types.Message, state: FSMContext):
    await state.finish()  # Clear the current state
    await show_main_menu(message)


# Handler for reply messages
@dp.message_handler(state=ButtonState.ACCOUNT)
async def handle_button_account_reply(message: types.Message, state: FSMContext):
    reply_message = message.text
    await state.finish()
    await message.reply(f"You replied to Button حسابي: {reply_message}")


@dp.message_handler(state=ButtonState.SUPPORT)
async def handle_button_support_reply(message: types.Message, state: FSMContext):
    reply_message = message.text
    await state.finish()
    await message.reply(f"You replied to Button الدعم: {reply_message}")


@dp.message_handler(state=ButtonState.CHARGE)
async def handle_button_charge_reply(message: types.Message, state: FSMContext):
    reply_message = message.text
    await state.finish()
    await message.reply(f"You replied to Button إضافة رصيد: {reply_message}")


if __name__ == "__main__":
    # Start the bot
    executor.start_polling(dp)
