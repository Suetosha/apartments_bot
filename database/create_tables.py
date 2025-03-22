import sqlite3


def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Создание таблицы пользователей
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE)''')


    # Создание таблицы квартир
    cursor.execute('''CREATE TABLE IF NOT EXISTS apartments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        price INTEGER,
                        city TEXT,
                        meters INTEGER,
                        description TEXT)''')


    # Создание таблицы активности пользователей
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_activity (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        apartment_id INTEGER,
                        viewed INTEGER DEFAULT 0,
                        liked INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (user_id),
                        FOREIGN KEY (apartment_id) REFERENCES apartments (id))''')

    # Создание уникального индекса на сочетание user_id и apartment_id для предотвращения дублирования записей
    cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS user_activity_unique_idx ON user_activity (user_id, apartment_id)
    ''')


    # Создание таблицы с фильтрами
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS filters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            city TEXT,
            meters TEXT
        )
    ''')


    conn.commit()
    conn.close()