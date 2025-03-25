import sqlite3

def save_user(user_id, username):
    # Подключение к базе данных
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Добавляем пользователя или обновляем его
    cursor.execute('''
        INSERT INTO users (user_id, username) 
        VALUES (?, ?) 
        ON CONFLICT(user_id, username) DO NOTHING
    ''', (user_id, username))

    # Сохраняем изменения в базе данных
    conn.commit()
    conn.close()


def get_username(user_id):
    """Получает username пользователя по user_id из базы данных."""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Выполняем запрос для получения username по user_id
    cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0]