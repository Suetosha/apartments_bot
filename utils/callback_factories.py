from aiogram.filters.callback_data import CallbackData


class DeleteFavoriteCallbackFactory(CallbackData, prefix='del'):
    user_id: int
    apartment_id: int
    message_id: int

class DeletePublishedCallbackFactory(CallbackData, prefix='del'):
    apartment_id: int
    message_id: int


class GetApartmentCallbackFactory(CallbackData, prefix='get'):
    user_id: int
    apartment_id: int
    message_id: int


class GetPublishedApartmentCallbackFactory(CallbackData, prefix='get'):
    apartment_id: int
    message_id: int


class EditPublishedApartmentCallbackFactory(CallbackData, prefix='edit'):
    user_id: int
    apartment_id: int
    message_id: int