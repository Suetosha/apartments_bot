import csv
import re
import sqlite3



def add_apartment(user_id, title, price, city, meters, description, photo):
    try:
        """Добавляет новую квартиру в базу данных, включая фото"""
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO apartments (user_id, title, price, city, meters, description, photo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, title, price, city, meters, description, photo))

        conn.commit()
        conn.close()
    except Exception as error:
        print('error', error)


def get_apartment(apartment_id):
    """Получает данные об одной квартире по ID"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM apartments WHERE id = ?", (apartment_id,))
    apartment = cursor.fetchone()

    conn.close()

    return apartment


def load_apartments_from_csv():
    """Загружает данные из CSV-файла и добавляет квартиры в базу"""
    with open('database/apartments.csv', newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            add_apartment(int(row["user_id"]), row["title"], row["price"], row["city"], int(row["meters"]), row["description"], row["photo"])


def get_apartments_by_filter(city, meters_range):
    """Возвращает список квартир по фильтру (по городу и диапазону метража)"""
    meters_pattern = r"(\d+)\s*(?:-\s*(\d+))?"  # Регулярное выражение для диапазона

    match = re.match(meters_pattern, meters_range)
    if match:
        min_meters = int(match.group(1))
        max_meters = match.group(2)

        if max_meters is None:
            query = "SELECT * FROM apartments WHERE city = ? AND meters >= ?"
            params = (city, min_meters)


        else:
            max_meters = int(max_meters)
            query = "SELECT * FROM apartments WHERE city = ? AND meters BETWEEN ? AND ?"
            params = (city, min_meters, max_meters)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(query, params)

        results = cursor.fetchall()
        conn.close()

        return results
    else:
        return None


def get_apartments_by_landlord(user_id):
    """Возвращает список квартир, добавленных конкретным арендодателем (user_id)"""
    query = "SELECT * FROM apartments WHERE user_id = ?"
    params = (user_id,)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(query, params)

    results = cursor.fetchall()
    conn.close()

    return results


def delete_apartment(apartment_id):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Удаление квартиры из таблицы apartments по ID
        cursor.execute("DELETE FROM apartments WHERE id = ?", (apartment_id,))
        conn.commit()

        conn.close()
    except sqlite3.Error as e:
        print(f"Ошибка при удалении квартиры: {e}")


def get_unique_cities():
    """Возвращает уникальные города из базы данных."""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # SQL запрос для получения уникальных городов
    query = "SELECT DISTINCT city FROM apartments"
    cursor.execute(query)

    # Получаем результаты
    cities = cursor.fetchall()
    conn.close()

    # Преобразуем результат в список городов
    unique_cities = [city[0] for city in cities]

    return unique_cities


