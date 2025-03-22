import sqlite3


def save_filter(user_id, city, meters):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO filters (user_id, city, meters)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            city = excluded.city,

            meters = excluded.meters
    ''', (user_id, city, meters))

    conn.commit()
    conn.close()


def get_user_filters(user_id):
    """Получаем фильтры пользователя из таблицы filters"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT city, meters FROM filters WHERE user_id = ?''', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {"city": result[0], "meters": result[1]}
    else:
        return None