import re

from aiogram.types import PhotoSize
from geopy import Nominatim


def validate_city_name(city):
    """Проверяет, существует ли такой город с помощью Nominatim API"""
    geolocator = Nominatim(user_agent="apartments_tg_bot")
    try:
        location = geolocator.geocode(city, exactly_one=True)
        if location and len(city) > 1:
            return location.raw.get("display_name").split(",")[0]
    except Exception as e:
        print(f"Ошибка при запросе к Nominatim API: {e}")


def validate_meters(meters):
    """Функция для проверки правильности ввода метража (только числа)"""
    if re.match(r"^\d+$", meters):
        return True
    return False


def validate_photo(photo, max_size_mb: int = 20):
    if not isinstance(photo, PhotoSize):
        return False
    max_size_bytes = max_size_mb * 1024 * 1024

    if photo.file_size > max_size_bytes:
        return False

    return photo



def validate_price(price):
    """Функция для проверки правильности ввода цены (можно использовать цифры, точку или запятую)"""
    if re.match(r"^\d+([.,]\d+)?$", price):
        return True
    return False

