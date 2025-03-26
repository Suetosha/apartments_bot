import sqlite3


# Сохранение фильтра арендатора
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

# Получение фильтра арендатора
def get_user_filters(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT city, meters FROM filters WHERE user_id = ?''', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {"city": result[0], "meters": result[1]}
    else:
        return None