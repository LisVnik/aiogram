import asyncio
import logging
import random
import urllib

import aiogram.utils.markdown as fmt
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

from confg import API_TOKEN

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer("/test1\n/test2\n/test4\n/dice\n/random\n/numbers\n/inline_url\n/start1\n/special_buttons\n/help\n/да_иди_ты\n/show\n/who_am_i")
    await asyncio.sleep(0)
    await types.ChatActions.upload_photo()
    media = types.MediaGroup()
    media.attach_photo(types.InputFile('documents/file_3.jpg'), 'Photo')
    media.attach_photo(types.InputFile('documents/file_4.jpg'), 'And another photo')
    media.attach_photo('https://disk.yandex.ru/i/3CWxYN2PQGXFGg', 'Sunset')
    await message.answer_media_group(media=media)

@dp.message_handler(Text(equals="Матан_УМ"), content_types=['document'])
#@dp.message_handler(content_types=['document'])
async def scan_message_matan(msg: types.Message):
    document_id = msg.document.file_id
    file_info = await bot.get_file(document_id)
    fi = file_info.file_path
    name = msg.document.file_name
    urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{API_TOKEN}/{fi}',f'./documents/Матан/{name}')
    await bot.send_message(msg.from_user.id, 'Файл успешно сохранён в папку Матан')

@dp.message_handler(Text(contains="Очевидна", ignore_case=True))
@dp.message_handler(Text(contains="Очев", ignore_case=True))
@dp.message_handler(Text(contains="04евидн0", ignore_case=True))
@dp.message_handler(Text(contains="О4евидно", ignore_case=True))
@dp.message_handler(Text(contains="Очевидно", ignore_case=True))   #ochevidno=["Очевидно", "Очевидна", "Очев", "04евидн0", "О4евидно"]
async def delete_message(message: types.Message):
    await message.delete()      #await message.answer("Ты нехороший человек!")

@dp.message_handler(commands="show")
async def cmd_test1(message: types.Message):
    await message.answer("Подожди 0 секунд")
    await asyncio.sleep(0)
    await types.ChatActions.upload_document()
    media = types.MediaGroup()
    media.attach_document(types.InputFile('article/10.1016@j.ces.2020.116015.pdf'))
    media.attach_document(types.InputFile('article/10.1016@j.jcat.2019.09.029.pdf'))
    media.attach_document(types.InputFile('article/cosseron2013.pdf'))
    media.attach_document(types.InputFile('article/dutta1991.pdf'))
    media.attach_document(types.InputFile('article/fyfe1988.pdf'))
    media.attach_document(types.InputFile('article/jakob2008.pdf'))
    media.attach_document(types.InputFile('article/kalvachev2013.pdf'))
    media.attach_document(types.InputFile('article/lebedev2016.pdf'))
    media.attach_document(types.InputFile('article/schmidt2016.pdf'))
    media.attach_document(types.InputFile('article/toktarev2010.pdf'))
    await message.answer_media_group(media=media)

# States
class Form(StatesGroup):
    name = State()  # Will be represented in storage as 'Form:name'
    age = State()  # Will be represented in storage as 'Form:age'
    group = State()  # Will be represented in storage as 'Form:group'

@dp.message_handler(commands='who_am_i')
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    # Set state
    await Form.name.set()
    await message.reply("Привет! Как тебя зовут?")



# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['name'] = message.text
        f = open('data.txt', 'a')
        f.write('chat_id'+','+'')
        f.write(data['name']+','+'')
        f.close()
    await Form.next()
    await message.reply("Сколько тебе лет?")


# Check age. Age gotta be digit
@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.age)
async def process_age_invalid(message: types.Message):
    """
    If age is invalid
    """
    return await message.reply("Age gotta be a number.\nHow old are you? (digits only)")


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    # Update state and data
    await Form.next()
    await state.update_data(age=int(message.text))
    # Configure ReplyKeyboardMarkup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("111", "113")
    markup.add("Другая")

    await message.reply("В какой ты группе?", reply_markup=markup)


@dp.message_handler(lambda message: message.text not in ["111", "113", "Другая"], state=Form.group)
async def process_gender_invalid(message: types.Message):
    """
    In this example gender has to be one of: Male, Female, Other.
    """
    return await message.reply("Неправильный номер группы. Выберите группу из предложенных на клавиатуре")


@dp.message_handler(state=Form.group)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['group'] = message.text
        f = open('data.txt', 'a')
        f.write(data['group']+'\n')
        f.close()
        # Remove keyboard
        markup = types.ReplyKeyboardRemove()

        # And send message
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Привет! Приятно познакомиться,', md.bold(data['name'])),
                md.text('Возраст:', md.code(data['age'])),
                md.text('Группа:', data['group']),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )
    # Finish conversation
    await state.finish()


@dp.message_handler(commands="да_иди_ты")
async def cmd_start1(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["В баню", "На матан"]
    keyboard.add(*buttons)
    await message.answer("Сам иди. У меня для тебя даже есть варианты:", reply_markup=keyboard)

@dp.message_handler(Text(equals="В баню"))
async def with_puree(message: types.Message):
    await message.reply("Отличный выбор!", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(Text(equals="На матан"))
async def with_puree(message: types.Message):
    await message.reply("Про якобиан не забудь!", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(commands="random")
async def cmd_random(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Нажми меня", callback_data="random_value"))
    await message.answer("Нажмите на кнопку, чтобы бот отправил число от 1 до 10", reply_markup=keyboard)

# Здесь хранятся пользовательские данные.
# Т.к. это словарь в памяти, то при перезапуске он очистится
user_data = {}

def get_keyboard():
    # Генерация клавиатуры.
    buttons = [
        types.InlineKeyboardButton(text="-1", callback_data="num_decr"),
        types.InlineKeyboardButton(text="+1", callback_data="num_incr"),
        types.InlineKeyboardButton(text="Подтвердить", callback_data="num_finish")
    ]
    # Благодаря row_width=2, в первом ряду будет две кнопки, а оставшаяся одна
    # уйдёт на следующую строку
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard

async def update_num_text(message: types.Message, new_value: int):
    # Общая функция для обновления текста с отправкой той же клавиатуры
    await message.edit_text(f"Укажите число: {new_value}", reply_markup=get_keyboard())

@dp.message_handler(commands="numbers")
async def cmd_numbers(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("Укажите число: 0", reply_markup=get_keyboard())

@dp.callback_query_handler(Text(startswith="num_"))
async def callbacks_num(call: types.CallbackQuery):
    # Получаем текущее значение для пользователя, либо считаем его равным 0
    user_value = user_data.get(call.from_user.id, 0)
    # Парсим строку и извлекаем действие, например `num_incr` -> `incr`
    action = call.data.split("_")[1]
    if action == "incr":
        user_data[call.from_user.id] = user_value+1
        await update_num_text(call.message, user_value+1)
    elif action == "decr":
        user_data[call.from_user.id] = user_value-1
        await update_num_text(call.message, user_value-1)
    elif action == "finish":
        # Если бы мы не меняли сообщение, то можно было бы просто удалить клавиатуру
        # вызовом await call.message.delete_reply_markup().
        # Но т.к. мы редактируем сообщение и не отправляем новую клавиатуру,
        # то она будет удалена и так.
        await call.message.edit_text(f"Итого: {user_value}")
    # Не забываем отчитаться о получении колбэка
    await call.answer()




@dp.callback_query_handler(text="random_value")
async def send_random_value(call: types.CallbackQuery):
    await call.message.answer(str(random.randint(1, 10)))

@dp.message_handler(commands="inline_url")
async def cmd_inline_url(message: types.Message):
    buttons = [
        types.InlineKeyboardButton(text="GitHub", url="https://github.com"),
        types.InlineKeyboardButton(text="Оф. канал Telegram", url="tg://resolve?domain=telegram")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await message.answer("Кнопки-ссылки", reply_markup=keyboard)

@dp.message_handler(commands="special_buttons")
async def cmd_special_buttons(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Запросить геолокацию", request_location=True))
    keyboard.add(types.KeyboardButton(text="Запросить контакт", request_contact=True))
    keyboard.add(types.KeyboardButton(text="Создать викторину",
                                      request_poll=types.KeyboardButtonPollType(type=types.PollType.QUIZ)))
    await message.answer("Выберите действие:", reply_markup=keyboard)

@dp.message_handler(commands="start1")
async def cmd_start1(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["С пюрешкой", "Без пюрешки"]
    keyboard.add(*buttons)
    await message.answer("Как подавать котлеты?", reply_markup=keyboard)

@dp.message_handler(Text(equals="С пюрешкой"))
async def with_puree(message: types.Message):
    await message.reply("Отличный выбор!", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text == "Без пюрешки")
async def without_puree(message: types.Message):
    await message.reply("Так невкусно!")

# Хэндлер на команду /test1
@dp.message_handler(commands="test1")
async def cmd_test1(message: types.Message):
    await message.reply("Test 1")

@dp.message_handler(content_types=['document'])
async def scan_message(msg: types.Message):
    document_id = msg.document.file_id
    file_info = await bot.get_file(document_id)
    fi = file_info.file_path
    name = msg.document.file_name
    urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{API_TOKEN}/{fi}',f'./documents/{name}')
    await bot.send_message(msg.from_user.id, 'Файл успешно сохранён в папку documents')

#@dp.message_handler(content_types=[types.ContentType.DOCUMENT])
#async def download_doc(message: types.Message):
#    # Скачивание в каталог с ботом с созданием подкаталогов по типу файла
#    await message.document.download()

@dp.message_handler(commands="dice")
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")

# Хэндлер на команду /test2
@dp.message_handler(commands="test2")
async def cmd_test1(message: types.Message):
    await message.answer("Test 2")

@dp.message_handler(commands="test4")
async def with_hidden_link(message: types.Message):
    await message.answer(
        f"{fmt.hide_link('https://telegram.org/blog/video-calls/ru')}Кто бы мог подумать, что "
        f"в 2020 году в Telegram появятся видеозвонки!\n\nОбычные голосовые вызовы "
        f"возникли в Telegram лишь в 2017, заметно позже своих конкурентов. А спустя три года, "
        f"когда огромное количество людей на планете приучились работать из дома из-за эпидемии "
        f"коронавируса, команда Павла Дурова не растерялась и сделала качественные "
        f"видеозвонки на WebRTC!\n\nP.S. а ещё ходят слухи про демонстрацию своего экрана :)",
        parse_mode=types.ParseMode.HTML)

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)