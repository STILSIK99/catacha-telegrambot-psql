#set KeyboardButtons

from aiogram import types

no_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
no_buttons.add(
    types.KeyboardButton(text="Отмена")
)

start_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_buttons.add(
    types.KeyboardButton(text="Регистрация"),
    types.KeyboardButton(text="Правила")
)


init_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
init_buttons.add(
    types.KeyboardButton(text="Присоединиться"),
    types.KeyboardButton(text="Создать комнату"),
    types.KeyboardButton(text="Изменить профиль"),
    types.KeyboardButton(text="Правила")
)

room_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
room_buttons.add(
    types.KeyboardButton(text="Правила"),
    types.KeyboardButton(text="Инфо"),
    types.KeyboardButton(text="Покинуть комнату")
)

room_admin_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
room_admin_buttons.add(
    types.KeyboardButton(text="Начать"),
    types.KeyboardButton(text="Правила"),
    types.KeyboardButton(text="Участники"),
    types.KeyboardButton(text="Покинуть комнату")
)

game_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
game_buttons.add(
    types.KeyboardButton(text="Осталось"),
    types.KeyboardButton(text="Моя цель"),
    types.KeyboardButton(text="Правила"),
    types.KeyboardButton(text="Выбыл")
)

rename_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
rename_buttons.add(
        types.KeyboardButton(text="Да"),
        types.KeyboardButton(text="Нет")
)

finish_game_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
finish_game_buttons.add(
        types.KeyboardButton(text="Инфо"),
        types.KeyboardButton(text="Рейтинг"),
        types.KeyboardButton(text="Покинуть комнату")
)



def check_name(name):
    if name == "" and name[0] == '/':
        return False
    if name.find(',') != -1:
        return False
    if name in [
                    "Правила", "Начать", "Участники", "Покинуть комнату",
                    "Инфо", "Выбыл", "Правила", "Моя цель", "Осталось",
                    "Отмена", "Назад", "Регистрация", "Изменить профиль",
                    "Создать комнату", "Присоединиться"
                ]:
        return False
    return True



rules = """
Данная игра предназначена для большой
активной компании, которая любит движ.

Всё просто, ты разберешься.
1. Побеждает тот, кто остался живым
или набрал больше очков.
2. Чтобы набирать очки, необходимо 
застать цель 1 на 1, прикоснуться и
сказать: 'Ты пойман'.
3. Если были свидетели, тогда не 
считается
4. Игра заканчивается, когда остается
двое участников.

Для участия необходимо создать комнату
или присоединиться к существующей.

Для исправления любых непредвиденных 
поведений бота напиши /start

Ну вот и всё. Развлекайся.

"""


