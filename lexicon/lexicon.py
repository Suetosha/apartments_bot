

LEXICON = {
    # main
    'start': 'Здравствуйте!\nВас приветствует бот для поиска и сдачи квартир.\nЧто вас интересует?',
    'start_view': 'Начать просмотр',
    'press_for_view': 'Нажмите кнопку для просмотра квартир',
    'edit_filter': 'Редактировать фильтр',
    'filter_not_created': 'Фильтр ещё не создан.',
    'favorite_list': 'Список избранных квартир',
    'published_list': 'Список опубликованных вами квартир',
    'error': 'Что-то пошло не так, попробуйте через несколько минут',
    'apartments_list': 'Список квартир',
    'help':
        'Доступные команды:\n\n'
        '/filter — фильтрация квартир по вашим параметрам.\n'
        '/favorites — просмотр сохраненных квартир.\n'
        '/view_apartments — список доступных квартир.\n'
        '/publish_apartment — публикация объявления о квартире.\n'
        '/view_published_apartments — просмотр ваших объявлений.',

    'other':
        'Этот бот помогает только с подбором квартир и не умеет отвечать на сообщения.\n'
        'Используйте команды, чтобы найти или опубликовать квартиру.\n'
        'Список доступных команд: /help',



    # tenant
    'choose_city_tenant': 'В каком городе ты ищешь квартиру?',
    'choose_meters_tenant': 'Какой метраж тебе нужен?',
    'filter_doesnt_exist': 'Вы не задали фильтры. Укажите город и метры.',
    'apartments_doesnt_exist': 'Нет квартир по заданным параметрам.',
    'error_apartment': 'Ошибка: не найдена текущая квартира.',
    'apartments_sold_out': '🏠 Квартиры закончились! Попробуйте изменить фильтр.',



    # landlord
    'choose_city_landlord': 'В каком городе вы хотите сдавать квартиру?',
    'city_is_not_found': 'К сожалению, город не найден, попробуйте снова',
    'choose_meters_landlord': 'Сколько метров в квартире?',
    'meters_bad_format': 'Метры должны представлены в цифрах, попробуйте снова',
    'choose_price_landlord': 'За сколько вы бы хотели её сдавать?',
    'price_bad_format': 'Цена должна быть представлена в цифрах и может содержать запятую или точку, попробуйте снова',
    'send_photo_landlord': 'Отправьте фотографию квартиры',
    'photo_bad_format': 'Отправьте изображение размером до 20MB, попробуйте снова',
    'choose_title_landlord': 'Напишите заголовок для вашего объявления',
    'choose_description_landlord': 'Напишите описание для вашего объявления',
    'confirmation_landlord': 'Теперь проверьте и подтвердите данные.',
    'apartment_updated': 'Квартира успешно обновлена',
    'apartment_is_not_found': 'Не удалось найти квартиру для обновления',
    'apartment_saved': 'Квартира успешно сохранена',
    'choose_part_for_edit': 'Что нужно изменить?',
    'save_button': '✅ Сохранить',
    'edit_again_button': '🔄 Изменить снова',

}

def get_apartment_info(city, title, price, meters, description, username):
    return (
        f"🏠 {title}\n"
        f"🏙 Город: {city}\n"
        f"💰 Цена: {price} ₽\n"
        f"📏 Метраж: {meters} м²\n"
        f"📝 Описание:\n {description}\n\n"
        f"📩 Контакты: <a href=\"https://t.me/{username}\">Ссылка на профиль</a>"


    )


def get_result_text(city, meters):
    result_text = (
        f"🔹 Город: {city}\n"
        f"🔹 Метры: {meters}"
    )
    return result_text