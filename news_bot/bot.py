import json
from config import BOT_TOKEN
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from asyncio import sleep

# Импортируем парсеры новостей
from pars import parse_kommersant, parse_ria, parse_rbc, parse_cnn

# Глобальные переменные
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)
all_news = {}

# Файл для хранения настроек пользователей
SETTINGS_FILE = "user_settings.json"

# Загрузка настроек из файла
def load_user_settings():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Сохранение настроек в файл
def save_user_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False, indent=4)

# Загрузка новостей
async def load_news():
    global all_news
    all_news = {
        "Коммерсант": parse_kommersant(),
        "РИА Новости": parse_ria(),
        "РБК": parse_rbc(),
        "CNN": parse_cnn(),
    }
    print("Новости загружены!")

# Создание главного меню
def get_main_menu():
    buttons = ["НОВОСТИ", "НАСТРОЙКИ"]
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)

# Создание подменю новостей
def get_news_submenu():
    buttons = ["Все новости", "Последние новости", "Выбрать источник", "НАЗАД"]
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)

# Создание меню настроек
def get_settings_menu():
    buttons = ["Источник по умолчанию", "Количество новостей", "НАЗАД"]
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)

# Команда /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Здравствуйте, пока я получаю новости...Представляю вашему вниманию бота, "
                         "который парсит информацию с новостных сайтов!Дождитесь пока новости будут загружены."
                         "Желаю хорошо провести время!")
    await load_news()
    await sleep(3)
    await message.answer("Новости загружены!", reply_markup=get_main_menu())

# Обработчик кнопки "НОВОСТИ"
@dp.message_handler(Text(equals="НОВОСТИ"))
async def news_menu(message: types.Message):
    await message.answer("Выберите раздел новостей:", reply_markup=get_news_submenu())

# Обработчик кнопки "НАЗАД"
@dp.message_handler(Text(equals="НАЗАД"))
async def back_to_main(message: types.Message):
    await message.answer("Главное меню:", reply_markup=get_main_menu())

# Обработчик кнопки "Все новости"
@dp.message_handler(Text(equals="Все новости"))
async def send_all_news(message: types.Message):
    user_id = str(message.from_user.id)
    settings = load_user_settings()

    # Получаем количество новостей из настроек (по умолчанию 5)
    limit = settings.get(user_id, {}).get("news_limit", 5)

    if not all_news:
        await message.answer("Не удалось получить новости.")
        return

    for source, news_list in all_news.items():
        for news_item in news_list[:limit]:
            await message.answer(f"{news_item['title']}\n{news_item['link']}")
    await message.answer("Выберите действие:", reply_markup=get_news_submenu())

# Обработчик кнопки "Последние новости"
@dp.message_handler(Text(equals="Последние новости"))
async def send_latest_news(message: types.Message):
    if not all_news:
        await message.answer("Не удалось получить новости.")
        return

    latest_news = []
    for source, news_list in all_news.items():
        if news_list:
            latest_news.append(news_list[0])

    for news_item in latest_news:
        await message.answer(f"{news_item['title']}\n{news_item['link']}")
    await message.answer("Выберите действие:", reply_markup=get_news_submenu())

# Обработчик кнопки "Выбрать источник"
@dp.message_handler(Text(equals="Выбрать источник"))
async def choose_source(message: types.Message):
    sources = list(all_news.keys())
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*sources).add("НАЗАД")  # Добавляем кнопку назад
    await message.answer("Выберите источник новостей:", reply_markup=markup)

# Обработчик выбора конкретного источника
@dp.message_handler(lambda message: message.text in all_news.keys())
async def send_news_by_source(message: types.Message):
    source = message.text
    news_list = all_news.get(source, [])
    markup = get_news_submenu()  # Возвращаемся к подменю новостей

    if not news_list:
        await message.answer(f"Новости из '{source}' не найдены.", reply_markup=markup)
        return

    for news_item in news_list:
        await message.answer(f"{news_item['title']}\n{news_item['link']}")
    await message.answer("Выберите действие:", reply_markup=markup)

# Обработчик кнопки "НАСТРОЙКИ"
@dp.message_handler(Text(equals="НАСТРОЙКИ"))
async def settings_menu(message: types.Message):
    await message.answer("Настройки:", reply_markup=get_settings_menu())

# Обработчик кнопки "Источник по умолчанию"
@dp.message_handler(Text(equals="Источник по умолчанию"))
async def set_default_source(message: types.Message):
    sources = list(all_news.keys())
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*sources).add("НАЗАД")
    await message.answer("Выберите источник по умолчанию:", reply_markup=markup)

# Обработчик выбора источника по умолчанию
@dp.message_handler(lambda message: message.text in all_news.keys())
async def save_default_source(message: types.Message):
    user_id = str(message.from_user.id)
    source = message.text
    settings = load_user_settings()
    if user_id not in settings:
        settings[user_id] = {}
    settings[user_id]["default_source"] = source
    save_user_settings(settings)
    await message.answer(f"Источник по умолчанию установлен: {source}", reply_markup=get_main_menu())  # Переход в главное меню

# Обработчик кнопки "Количество новостей"
@dp.message_handler(Text(equals="Количество новостей"))
async def set_news_limit(message: types.Message):
    await message.answer("Введите количество новостей (число от 1 до 20):")

# Обработчик ввода числа для количества новостей
@dp.message_handler(lambda message: message.text.isdigit())
async def save_news_limit(message: types.Message):
    user_id = str(message.from_user.id)
    limit = int(message.text)
    if 1 <= limit <= 20:
        settings = load_user_settings()
        if user_id not in settings:
            settings[user_id] = {}
        settings[user_id]["news_limit"] = limit
        save_user_settings(settings)
        await message.answer(f"Количество новостей установлено: {limit}", reply_markup=get_main_menu())  # Переход в главное меню
    else:
        await message.answer("Неверное значение. Введите число от 1 до 20.")

# Обработчик для всех остальных сообщений
@dp.message_handler()
async def handle_unknown_message(message: types.Message):
    await message.answer("Привет! Чтобы начать работу с ботом, используйте команду /start.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)