import sqlite3

def save_user(user_id):
    # Подключение к базе данных
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Добавляем пользователя или обновляем его
    cursor.execute('''
        INSERT INTO users (user_id) 
        VALUES (?) 
        ON CONFLICT(user_id) DO NOTHING
    ''', (user_id,))

    # Сохраняем изменения в базе данных
    conn.commit()
    conn.close()