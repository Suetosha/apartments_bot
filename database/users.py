import sqlite3


# Сохранение пользователя
def save_user(user_id, username):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO users (user_id, username) 
        VALUES (?, ?) 
        ON CONFLICT(user_id, username) DO NOTHING
    ''',(user_id, username))

    conn.commit()
    conn.close()


# Получение имени пользователя в тг
def get_username(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0]
