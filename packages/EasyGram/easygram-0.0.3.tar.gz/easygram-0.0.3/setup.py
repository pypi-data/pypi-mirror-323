from setuptools import setup, find_packages

setup(
    name='EasyGram',
    version='0.0.3',
    description='Библиотека для удобного и многофункционального(в будущем) использования.',
    long_description="""
Установить:
```bash
pip install EasyGram
```

## Быстрый старт

#### Эхо бот(синхронный)
```python
from EasyGram import SyncBot, types

bot = SyncBot('Token here')

@bot.message(content_types='text')
def echo_bot(message: types.Message):
	message.answer(message.text)

bot.polling()
```

#### Эхо бот(асинхронный)
```python
from EasyGram.Async import AsyncBot, types

bot = AsyncBot('Token here')

@bot.message(content_types='text')
async def echo_bot(message: types.Message):
	await message.answer(message.text)

bot.executor()
```

---

#### Бот рандомайзер(синхронный):
```python
from EasyGram import SyncBot, types
from random import randint

bot = SyncBot('Token here')

@bot.message(commands='start')
def start(message: types.Message):
	#Делаем маленькую кнопку
	button = types.ReplyKeyboardMarkup(resize_keyboard=True)
	button.add('От 1 до 10')
	
	message.answer('Привет!', reply_markup=button)

@bot.message(lambda message: message.text == 'От 1 до 10')
def random_number(message: types.Message):
	message.answer(f'Тебе выпало: {randint(1, 10)}!')

bot.polling()
```


#### Бот рандомайзер(асинхронный)
```python
from EasyGram.Async import AsyncBot, types
from random import randint

bot = AsyncBot('Token here')

@bot.message(commands='start')
async def start(message: types.Message):
	#Делаем маленькую кнопку
	button = types.ReplyKeyboardMarkup(resize_keyboard=True)
	button.add('От 1 до 10')
	
	await message.answer('Привет!', reply_markup=button)

@bot.message(lambda message: message.text == 'От 1 до 10')
async def random_number(message: types.Message):
	await message.answer(f'Тебе выпало: {randint(1, 10)}!')

bot.executor()
```

## Что нового?

С новой версии `0.0.3` добавилось:

- Добавился метод в классе `SyncBot`: `start_polling()`
- Добавлен класс `Poll` в types `ах
- Переименован класс `InputPollOption` на `PollOption` для удобства и схожести с именами как в Telegram API
- Добавлен обработчик `poll`:

### Пример:

```python
from EasyGram import SyncBot, types

bot = ...

# Все опросы
@bot.poll()
def all_polls(poll: types.Poll):
    print(poll) # Вывод словаря в строки

bot.start_polling()
```

- Исправлены ошибки в `EasyGram.Async`
- Добавлены методы edit в объектах `Message`
- Добавлен класс `StateRegExp` в `EasyGram.state`:

### Пример:

```python
from EasyGram import SyncBot, types
from EasyGram.state import State, StatesGroup, StateRegExp

bot = ...

class States(StatesGroup):
    room = State()

@bot.message(commands='start')
def start(message: types.Message):
    message.answer('Привет, введи своё имя.')
    States.room.set_state(message.chat.id, message.from_user.id, 'Enter name')

@bot.message(state=StateRegExp(States.room, 'Enter name'))
def entered_name(message: types.Message, data: str):
    message.reply(f'Твоё имя: {message.text}')
    States.room.remove_state(message.chat.id, message.from_user.id)

bot.polling()
```

- Добавлен метод `query_next_step_handler`, схож с `next_step_handler`

## Что добавить ещё?

Связаться:

- 📞💌Telegram channel: [Channel](https://t.me/oprosmenya)
    """,
    long_description_content_type='text/markdown',
    author='flexyyy',
    packages=find_packages(),
    package_data={
        "": ['readme.md']
    },
    install_requires=[
        'aiohttp'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    url='https://github.com/flexyyyapk/EasyGram/'
)