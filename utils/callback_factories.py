from aiogram.filters.callback_data import CallbackData


class DeleteFavoriteCallbackFactory(CallbackData, prefix='del'):
    user_id: int
    apartment_id: int
    message_id: int


class GetApartmentCallbackFactory(CallbackData, prefix='get'):
    user_id: int
    apartment_id: int
    message_id: int