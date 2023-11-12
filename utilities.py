import sqlite3


def add_user_to_table(user_id, username, first_name):
    conn = sqlite3.connect('goodoc.db')
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO users (id, username, first_name) VALUES (?, ?, ?)",
                   (user_id, username, first_name))
    conn.commit()

    cursor.close()
    conn.close()


def add_pill_to_table(pill, timeDate, duration, user_id, intervalEx, intervalExDay):
    conn = sqlite3.connect('goodoc.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO pill (pill, timeDate, duration, userId, intervalEx, intervalExDay) VALUES (?, ?, ?, ?, ?, ?)",
                   (pill, timeDate, duration, user_id, intervalEx, intervalExDay))
    conn.commit()

    cursor.close()
    conn.close()



