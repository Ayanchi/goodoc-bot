#!/usr/bin/env python3

from datetime import date, timedelta, datetime
import sqlite3

# Путь к файлу логов
log_file_path = '/var/www/telegrambot/sendMessage.log'

def log_message(message):
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")

def checkDay():
    current_date = date.today()
    current_time = (datetime.now() + timedelta(hours=3)).strftime('%H:%M')

    conn = sqlite3.connect('/var/www/telegrambot/goodoc.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM pill')
    results = cursor.fetchall()

    for result in results:
        try:
            pill_date = datetime.strptime(result[6], '%Y-%m-%d').date()

            if isinstance(result[3], str):
                end_date = datetime.strptime(result[3], '%Y-%m-%d').date()
            else:
                cursor.execute('DELETE FROM pill WHERE id=?', (result[0],))

            if pill_date < current_date:
                new_date = pill_date + timedelta(days=result[5])
                cursor.execute('UPDATE pill SET intervalExDay=? WHERE id=?', (new_date.strftime('%Y-%m-%d'), result[0]))
            elif (pill_date > end_date) or (current_date > end_date):
                cursor.execute('DELETE FROM pill WHERE id=?', (result[0],))


        except Exception as e:
            error_message = f"An error occurred: {e}"
            log_message(error_message)

    conn.commit()
    conn.close()

checkDay()