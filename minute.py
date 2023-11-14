#!/usr/bin/env python3

from datetime import date, timedelta, datetime
import sqlite3
import telebot
from telebot import types
from telebot.types import Message, CallbackQuery

# Путь к файлу логов
log_file_path = '/var/www/telegrambot/sendMessage.log'

def log_message(message):
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")

def sendMessage():
    try:
        global bot_client  # Делаем bot_client глобальным
        current_date = date.today()
        current_time = (datetime.now() + timedelta(hours=3)).strftime('%H:%M')

        conn = sqlite3.connect('/var/www/telegrambot/goodoc.db')
        cursor = conn.cursor()

        # Получение данных из таблицы для данного пользователя
        cursor.execute('SELECT * FROM pill')
        results = cursor.fetchall()

        # Фильтрация записей по текущему дню и времени
        filtered_results = []
        for result in results:
            times = result[2].split(', ')  # Разделение строки времени на список
            pill_date = datetime.strptime(result[6], '%Y-%m-%d').date()

            if current_date == pill_date and current_time in times:
                filtered_results.append(result)

        for result in filtered_results:
            try:
                user_id = result[4]
                new_date = datetime.strptime(result[6], '%Y-%m-%d').date() + timedelta(days=result[5])
                message_text = f'Уже {current_time} время принять {result[1]} 😊💊,\nCледующий день принятия 🤩 {new_date.strftime("%Y-%m-%d")}'
                log_message(f"Message sent to user {user_id}: {message_text}")
                bot_client.send_message(chat_id=user_id, text=message_text)

            except Exception as e:
                error_message = f"Failed to send message to user {user_id}. Exception: {e}"
                log_message(error_message)
                print(error_message)

    except Exception as e:
        error_message = f"An error occurred: {e}"
        print(error_message)
        log_message(error_message)

# Создаем экземпляр бота
bot_client = telebot.TeleBot(token='6895428130:AAG4i9ZgakJzn048GOYFKNjwVUYjg9f2n_c')

# Вызываем функцию
sendMessage()