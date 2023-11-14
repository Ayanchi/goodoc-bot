from datetime import date, timedelta, datetime

import telebot
import sqlite3

from openai import OpenAI
from telebot import types
from telebot.types import Message, CallbackQuery

from utilities import add_user_to_table, add_pill_to_table


client = OpenAI(
    api_key="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",
)

bot_client = telebot.TeleBot(token='6895428130:AAG4i9ZgakJzn048GOYFKNjwVUYjg9f2n_c')

pillName = ''
duration = 0
interval = 0
countOfDay = []
user_id = 0


@bot_client.message_handler(func=lambda message: message.text == "Создать цикл таблеток 🔗💊")
def goToPills(message: Message):
    bot_client.reply_to(message, 'Введите название таблетки или таблеток ниже 👇'
                                 '(если у них один цикл, время приема)')
    bot_client.register_next_step_handler(message, duration_pills)


def duration_pills(message: Message):
    global pillName
    pillName = message.text
    markup = types.InlineKeyboardMarkup()

    btnWeek = types.InlineKeyboardButton('1 Неделю', callback_data='1week')
    btnDay = types.InlineKeyboardButton('1 День', callback_data='1day')
    btn1Month = types.InlineKeyboardButton('1 Месяц', callback_data='1month')
    btn2Month = types.InlineKeyboardButton('2 Месяца', callback_data='2month')
    btnYear = types.InlineKeyboardButton('1 Год', callback_data='1year')

    markup.add(btnWeek, btn1Month, btn2Month, btnYear, btnDay)

    bot_client.send_message(message.chat.id, "На какой срок вы будете принимать таблетки", reply_markup=markup)


@bot_client.callback_query_handler(func=lambda call: call.data in ['1week', '1month', '2month', '1year', '1day'])
def handle_callback_query(call: CallbackQuery):
    global duration
    if call.data == '1week':
        duration = 7
    elif call.data == '1month':
        duration = 30
    elif call.data == '2month':
        duration = 60
    elif call.data == '1year':
        duration = 365

    else:
        duration = 0

    countPillOfDay(call.message)


def countPillOfDay(message: Message):
    chat_id = message.chat.id
    bot_client.send_message(chat_id, 'Введите количество приёма таблеток в день ('
                                     'Наример если принимаете два раза в день: 11:22, 21:00;'
                                     'если принимаете три раза в день: 13:00, 17:30, 18:45)')

    bot_client.register_next_step_handler(message, interval_pills)


def interval_pills(message: Message):
    global countOfDay
    countOfDay = message.text
    markup = types.InlineKeyboardMarkup()

    btnWeek = types.InlineKeyboardButton('Каждый день', callback_data='everyday')
    btnDay = types.InlineKeyboardButton('Через день', callback_data='dayahead')
    btn1Month = types.InlineKeyboardButton('Каждые 2 дня', callback_data='every2day')
    btn2Month = types.InlineKeyboardButton('Каждые 3 дня', callback_data='every3day')
    btnYear = types.InlineKeyboardButton('Раз в неделю', callback_data='everyweek')

    markup.add(btnWeek, btn1Month, btn2Month, btnYear, btnDay)

    bot_client.send_message(message.chat.id, "С каким интервалом вы будете принимать таблетки", reply_markup=markup)


@bot_client.callback_query_handler(
    func=lambda call: call.data in ['everyday', 'dayahead', 'every2day', 'every3day', 'everyweek'])
def handle_callback_query(call: CallbackQuery):
    global interval
    if call.data == 'dayahead':
        interval = 1
    elif call.data == 'every2day':
        interval = 2
    elif call.data == 'every3day':
        interval = 3
    elif call.data == 'everyweek':
        interval = 7
    else:
        interval = 0

    final(call.message.chat.id)


def final(user_id_id):
    current_date = date.today()
    new_date_interval = current_date + timedelta(days=interval)
    new_date_duration = current_date + timedelta(days=duration)
    print("Текущая дата:", new_date_interval)
    print(pillName, duration, countOfDay, interval, new_date_interval)
    add_pill_to_table(pillName, countOfDay, new_date_duration, user_id, interval, new_date_interval)

    bot_client.send_message(user_id_id, "Цикл добавлен 💖😘")


@bot_client.message_handler(commands=['get_data'])
def get_data_section(message: Message):
    user_id_pills = message.from_user.id

    conn = sqlite3.connect('goodoc.db')
    cursor = conn.cursor()

    # Получение данных из таблицы для данного пользователя
    cursor.execute('SELECT * FROM pill WHERE userId = ?', (user_id_pills,))
    result = cursor.fetchall()
    print(result)

    if result:
        user_name = message.from_user.username if message.from_user.username else "Нет имени пользователя"
        response = f"Данные пользователя {user_name}:\n"

        for row in result:
            response += f"ID: {row[0]}\n" \
                        f"Медикамент: {row[1]}\n" \
                        f"Время выпивания: {row[2]}\n" \
                        f"Конечный период: {row[3]}\n" \
                        f"ID: {row[4]}\n" \
                        f"Интервал: {row[5]}\n" \
                        f"Дата следующего приёма: {row[6]}\n" \
                        f"{'-' * 20}\n"

        bot_client.send_message(message.chat.id, response)
    else:
        bot_client.send_message(message.chat.id, f"Данные для пользователя {user_id} не найдены.")


@bot_client.message_handler(commands=['check_data'])
def renewal(message: Message):
    current_date = date.today()
    current_time = datetime.now().strftime('%H:%M')

    user_id_pills = message.from_user.id

    conn = sqlite3.connect('goodoc.db')
    cursor = conn.cursor()

    # Получение данных из таблицы для данного пользователя
    cursor.execute('SELECT * FROM pill WHERE userId = ?', (user_id_pills,))
    result = cursor.fetchall()
    print(result)

    if result:
        user_name = message.from_user.username if message.from_user.username else "Нет имени пользователя"
        response = f"Данные пользователя {user_name}:\n"

        for row in result:
            time_obj = datetime.strptime(row[2], '%H:%M').time()
            formatted_time = time_obj.strftime('%H:%M')

            interval_date_str = row[6]
            interval_date = datetime.strptime(interval_date_str, '%Y-%m-%d').date()

            duration_date_str = row[3]
            duration_date = datetime.strptime(duration_date_str, '%Y-%m-%d').date()

            if formatted_time == current_time and interval_date == current_date:
                print('true')
            if duration_date == current_date:
                cursor.execute('DELETE FROM pill WHERE userId = ?', (user_id_pills,))
                bot_client.send_message(message.chat.id, f"Данная таблетка удалена {row[1]}")
                print('true')

            if formatted_time == current_time and interval_date == current_date:
                interval_num_str = row[5]
                interval_num = int(interval_num_str)

                new_date_interval = interval_date + timedelta(days=interval_num)

                cursor.execute('''
                     UPDATE pill
                     SET intervalExDay=?
                     WHERE id=?
                 ''', (new_date_interval, row[0]))

                bot_client.send_message(chat_id=message.chat.id,
                                        text=f'Уже {current_time} время принять {row[1]} 😊💊,\n'
                                             f'Cледующий день принятия 🤩 {new_date_interval}')


@bot_client.message_handler(commands=['start'])
def start(message: Message):
    global user_id
    conn = sqlite3.connect('goodoc.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    first_name TEXT
                )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS pill (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pill TEXT,
                    timeDate TEXT,
                    duration DATA,
                    userId INTEGER PRIMARY KEY,
                    intervalEx INTEGER,
                    intervalExDay DATA,
                    FOREIGN KEY (userId) REFERENCES users(id)
                )''')

    conn.commit()

    cursor.close()
    conn.close()

    # send user data into users Table
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    add_user_to_table(user_id, username, first_name)

    # create burger menu
    markup = types.ReplyKeyboardMarkup()
    item2 = types.KeyboardButton('Создать цикл таблеток 🔗💊')

    markup.add(item2)

    bot_client.send_message(chat_id=message.chat.id,
                            text='Добро 😘 пожаловать этот чат бот служит помощником по приему лекарств 💖🤠')
    bot_client.send_message(chat_id=message.chat.id,
                            text='Ну давайте начнем сначало заполните свой календарь приёмов. Он находится ниже 👇',
                            reply_markup=markup)
    print(user_id)


@bot_client.message_handler(commands=['gpt'])
def handle_start(message: Message):
    print('Запущен бот')
    bot_client.send_message(message.chat.id, "Привет! Я бот. Отправь мне текст, и я передам его ChatGPT.")
    bot_client.register_next_step_handler(message, get_gpt_response)


def get_gpt_response(message: Message):
    bot_client.send_message(message.chat.id, 'Ответ в обработке, пожайлуста подождите 🙏☺️')
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{message.text}. Составь текст не больше 10 предложений",
            }
        ],
        model="gpt-3.5-turbo",
    )

    bot_client.reply_to(message, f'Спасибо за вопрос вот ваш ответ 🤝\n' + response.choices[0].message.content)


bot_client.polling(none_stop=True)
