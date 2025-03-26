import re

from aiogram.types import PhotoSize
from geopy import Nominatim


# Проверяет, существует ли такой город с помощью Nominatim API + Проверка на длину города
def validate_city_name(city):
    geolocator = Nominatim(user_agent="apartments_tg_bot")
    try:
        location = geolocator.geocode(city, exactly_one=True)
        if location and len(city) > 1:
            return location.raw.get("display_name").split(",")[0]
    except Exception as e:
        print(f"Ошибка при запросе к Nominatim API: {e}")


# Функция для проверки правильности ввода метража (только числа)
def validate_meters(meters):
    if re.match(r"^\d+$", meters):
        return True
    return False


# Функция для проверки на объект PhotoSize и размер (фото не должно превышать 20 мб)
def validate_photo(photo, max_size_mb = 20):
    if not isinstance(photo, PhotoSize):
        return False

    # Перевод максимального допустимого значения для тг в байты
    max_size_bytes = max_size_mb * 1024 * 1024

    if photo.file_size > max_size_bytes:
        return False

    return photo


# Функция для проверки правильности ввода цены (можно использовать цифры, точку или запятую)
def validate_price(price):
    if re.match(r"^\d+([.,]\d+)?$", price):
        return True
    return False
