import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
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
    BUTTON1 = State()
    BUTTON2 = State()
    BUTTON3 = State()
    BUTTON4 = State()
    BUTTON5 = State()


# Handler for the /start command
@dp.message_handler(Command("start"))
async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("شراء بروكسي", "حسابي")
    keyboard.row("التواصل مع الدعم", "إضافة رصيد")
    keyboard.add("حول البوت")
    await bot.send_message(message.chat.id, "اختر طلبك 👇🏻 :", reply_markup=keyboard)


# Handlers for button selections
@dp.message_handler(text=["شراء بروكسي"], state="*")
async def button1_selected(message: types.Message, state: FSMContext):
    await ButtonState.BUTTON1.set()
    await message.reply("You selected Button 1. Write your reply message:")


@dp.message_handler(text=["حسابي"], state="*")
async def button2_selected(message: types.Message, state: FSMContext):
    await ButtonState.BUTTON2.set()
    await message.reply("You selected Button 2. Write your reply message:")


@dp.message_handler(text=["التواصل مع الدعم"], state="*")
async def button3_selected(message: types.Message, state: FSMContext):
    await ButtonState.BUTTON3.set()
    await bot.send_message(message.chat.id,
                           "التواصل مع الدعم:\nيمكنك التواصل مع الدعم على الرابط التالي: https://t.me/Proxies_bot_support")


@dp.message_handler(text=["إضافة رصيد"], state="*")
async def button4_selected(message: types.Message, state: FSMContext):
    await ButtonState.BUTTON4.set()
    await message.reply("You selected Button 4. Write your reply message:")


@dp.message_handler(text=["حول البوت"], state="*")
async def button5_selected(message: types.Message, state: FSMContext):
    await ButtonState.BUTTON5.set()
    channel_link = "رابط القناة:\nhttps://t.me/Proxies1Channel"
    group_link = "رابط المجموعة:\nhttp://t.me/Proxies_Group_Chat"
    support_link = "رابط مراسلة الدعم للاستفسار:\nhttp://t.me/Proxies_bot_support"
    reply_message = f"{channel_link}\n\n{group_link}\n\n{support_link}"
    await bot.send_message(message.chat.id, reply_message)


# Handler for reply messages
@dp.message_handler(state=ButtonState.BUTTON1)
async def handle_button1_reply(message: types.Message, state: FSMContext):
    reply_message = message.text
    await state.finish()
    await message.reply(f"You replied to Button 1: {reply_message}")


@dp.message_handler(state=ButtonState.BUTTON2)
async def handle_button2_reply(message: types.Message, state: FSMContext):
    reply_message = message.text
    await state.finish()
    await message.reply(f"You replied to Button 2: {reply_message}")


@dp.message_handler(state=ButtonState.BUTTON3)
async def handle_button3_reply(message: types.Message, state: FSMContext):
    reply_message = message.text
    await state.finish()
    await message.reply(f"You replied to Button 3: {reply_message}")


@dp.message_handler(state=ButtonState.BUTTON4)
async def handle_button4_reply(message: types.Message, state: FSMContext):
    reply_message = message.text
    await state.finish()
    await message.reply(f"You replied to Button 4: {reply_message}")


@dp.message_handler(state=ButtonState.BUTTON5)
async def handle_button5_reply(message: types.Message, state: FSMContext):
    await state.finish()
    channel_link = "رابط القناة:\nhttps://t.me/Proxies1Channel"
    group_link = "رابط المجموعة:\nhttp://t.me/Proxies_Group_Chat"
    support_link = "رابط مراسلة الدعم للاستفسار:\nhttp://t.me/Proxies_bot_support"
    reply_message = f"{channel_link}\n\n{group_link}\n\n{support_link}"
    await bot.send_message(message.chat.id, reply_message)


if __name__ == "__main__":
    # Start the bot
    executor.start_polling(dp)
