import csv
import re
import sqlite3



def add_apartment(title, price, city, meters, description):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO apartments (title, price, city, meters, description) VALUES (?, ?, ?,?, ?)",
                   (title, price, city, meters, description))

    conn.commit()
    conn.close()


def get_apartment(apartment_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM apartments WHERE id = ?", (apartment_id,))
    apartment = cursor.fetchone()

    conn.close()

    return apartment



def load_apartments_from_csv():
    with open('database/apartments.csv', newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            add_apartment(row["title"], int(row["price"]), row["city"], int(row["meters"]), row["description"])


# Функция для запроса квартир из базы
def get_apartments_by_filter(city, meters_range):
    # Регулярное выражение для извлечения чисел из диапазона
    meters_pattern = r"(\d+)\s*(?:-\s*(\d+))?"  # (Первое число) - (второе число, если есть)

    # Проверка диапазона метража
    match = re.match(meters_pattern, meters_range)
    if match:
        min_meters = int(match.group(1))  # Минимальное значение
        max_meters = match.group(2)  # Максимальное значение (если есть)

        # Если максимальное значение отсутствует, то ищем только от min_meters и далее
        if max_meters is None:
            query = "SELECT id, title, price, meters, description FROM apartments WHERE city = ? AND meters >= ?"
            params = (city, min_meters)
        else:
            max_meters = int(max_meters)  # Преобразуем в int, если есть максимальное значение
            query = "SELECT id, title, price, meters, description FROM apartments WHERE city = ? AND meters BETWEEN ? AND ?"
            params = (city, min_meters, max_meters)

        # Подключение к базе данных
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(query, params)

        results = cursor.fetchall()
        conn.close()

        return results
    else:
        return None