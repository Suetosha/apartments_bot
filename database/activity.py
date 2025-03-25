import sqlite3

DB_NAME = "database.db"


def mark_as_viewed(user_id, apartment_id):
    """ Отмечает квартиру как просмотренную пользователем """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_activity (user_id, apartment_id, viewed, liked) 
            VALUES (?, ?, 1, 0) 
            ON CONFLICT(user_id, apartment_id) DO UPDATE SET viewed = 1
        ''', (user_id, apartment_id))
        conn.commit()

def is_apartment_viewed(user_id, apartment_id):
    """Проверяет, была ли квартира уже просмотрена пользователем"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT viewed FROM user_activity WHERE user_id = ? AND apartment_id = ?
    ''', (user_id, apartment_id))
    result = cursor.fetchone()

    # Закрытие соединения
    conn.close()

    # Если результат есть, возвращаем состояние поля 'viewed' (1 - просмотрена, 0 - не просмотрена)
    if result:
        return result[0] == 1  # True, если квартира была просмотрена
    else:
        return False  # Если нет записи, то квартира не была просмотрена




def mark_as_liked(user_id, apartment_id):
    """ Отмечает квартиру как лайкнутую пользователем """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_activity (user_id, apartment_id, viewed, liked) 
        VALUES (?, ?, 1, 1) 
        ON CONFLICT(user_id, apartment_id) DO UPDATE SET liked = 1
    ''', (user_id, apartment_id))
    conn.commit()
    conn.close()


def mark_as_unliked(user_id, apartment_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO user_activity (user_id, apartment_id, viewed, liked) 
    VALUES (?, ?, 1, 0) 
    ON CONFLICT(user_id, apartment_id) DO UPDATE 
    SET viewed = 1, liked = 0
    ''', (user_id, apartment_id))

    conn.commit()
    cursor.close()
    conn.close()



def get_liked_apartments(user_id):
    """ Получает список лайкнутых квартир пользователя """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.id, a.title, a.price, a.city FROM apartments a
        JOIN user_activity ua ON a.id = ua.apartment_id
        WHERE ua.user_id = ? AND ua.liked = 1
    ''', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results



def get_viewed_apartments(user_id):
    """ Получает список просмотренных квартир пользователя """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT a.id, a.title, a.price, a.city FROM apartments a
        JOIN user_activity ua ON a.id = ua.apartment_id
        WHERE ua.user_id = ? AND ua.viewed = 1
    ''', (user_id,))

    results = cursor.fetchall()
    conn.close()
    return results
