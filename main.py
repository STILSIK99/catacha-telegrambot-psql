from telebot import TeleBot
import random
from vars import *
from database import get_database
from mytoken import API_TOKEN



bot = TeleBot(API_TOKEN)

db = get_database()


# Handle '/start' and '/help'
@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    if not db.check_reg(message.from_user.id):
        bot.send_message(message.chat.id, "Привет, уважаемый гость.", reply_markup=[start_buttons])
    else:
        bot.send_message(message.chat.id, f"Давно не виделись, {db.get_name(message.from_user.id)}. Давай играть :)")
        route_user(message)


@bot.message_handler(commands=['test'])
def test(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Как меня зовут?")
    btn2 = types.KeyboardButton("Что я могу?")
    back = types.KeyboardButton("Вернуться в главное меню")
    markup.add(btn1, btn2, back)
    bot.send_message(message.chat.id, text="Задай мне вопрос", reply_markup=[markup])

def route_user(message):
    """
    Проверка, зарегистрирован ли пользователь, чтобы выбрать на какой этап его отправить
    """
    if not db.check_reg(message.from_user.id):
        # на регистрацию
        bot.send_message(message.chat.id, "Зарегистрируйся, уважаемый гость.", reply_markup=[start_buttons])
    else:
        room = db.check_game(message.from_user.id)
        if room is None:
            # в менюшку
            bot.send_message(message.chat.id, "Приступим к веселью?", reply_markup=[init_buttons])
        else:
            # в игру
            status = db.get_room_status(room)
            if status == "Wait":
                if db.is_room_admin(message.from_user.id):
                    bot.send_message(message.chat.id, f"Вы вернулись в комнату №{ room }", reply_markup=[room_admin_buttons])
                else:
                    bot.send_message(message.chat.id, f"Вы вернулись в комнату №{room}", reply_markup=[room_buttons])
                bot.register_next_step_handler(message, room_active)
            elif status == "Active":
                bot.send_message(message.chat.id, f"Игра №{ room } уже идёт", reply_markup=[game_buttons])
                bot.register_next_step_handler(message, game_active)
            elif status == "Finished":
                bot.send_message(message.chat.id, f"Приступим к веселью?", reply_markup=[init_buttons])
                bot.register_next_step_handler(message, initial_active)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def initial_active(message: types.Message):
    if message.text in ["Регистрация", "Изменить профиль"]:
        if not db.check_reg(message.from_user.id):
            bot.send_message(message.chat.id, "Напиши имя, которое будет известно другим участникам.", reply_markup=[no_buttons])
            bot.register_next_step_handler(message, sign_up)
        else:
            bot.send_message(message.chat.id, "Хочешь изменить имя? " + db.get_name(message.from_user.id), reply_markup=[rename_buttons])
            bot.register_next_step_handler(message, change_profile)

    elif message.text == "Правила":
        bot.send_message(message.chat.id, rules)
    elif message.text == "Создать комнату":
        id = db.create_room(message.from_user.id)
        if id is not None:
            bot.send_message(message.chat.id, f"Создана комната №{ id }\n"
                                              "Поделись этим номером с друзьями,\nчтобы они могли присоединиться.", reply_markup=[room_admin_buttons])
            bot.register_next_step_handler(message, room_active)
        else:
            bot.send_message(message.chat.id, "Не удалось создать комнату.", reply_markup=[init_buttons])

    elif message.text == "Присоединиться":
        bot.send_message(message.chat.id, "Напиши номер комнаты:")
        bot.register_next_step_handler(message, wait_get_room_number)

    else:
        bot.send_message(message.chat.id, "Напишите /start . Это должно помочь.")


def sign_up(message):
    if message.text in ["Отмена", "Назад", ]:
        bot.send_message(message.chat.id, "Действие отменено", reply_markup=[init_buttons])
        route_user(message)
    elif check_name(message.text):
        db.set_username(message.from_user.id, message.text)
        bot.send_message(message.chat.id, "Тебя будут видеть под именем: " + message.text, reply_markup=[init_buttons])
        route_user(message)
    else:
        bot.send_message(message.chat.id, "Не прошел цензуру, попробуй еще раз " + message.text, reply_markup=[no_buttons])
        bot.register_next_step_handler(message, wait_get_name)

def finish_game_active(message):
    pass


def game_active(message):
    if message.text in ["Создать комнату", "Присоединиться", "Правила", "Изменить профиль"]:
        if db.check_game(message.from_user.id) is None:
            bot.register_next_step_handler(message, initial_active)
            initial_active(message)
            return

    if message.text not in ["Выбыл", "Правила", "Моя цель", "Осталось"]:
        bot.send_message(message.chat.id, "Неизвестная команда")
    elif message.text == "Выбыл":
        other = db.leave_from_game(message.from_user.id)
        bot.send_message(message.chat.id, "В следующий раз победишь :)", reply_markup=[finish_game_buttons])
        if other <= 2:
            info = "Победители:\n"
            players = db.get_current_targets(message.from_user.id)
            for player in players:
                info += f"   {player}\n"
            info += "_"*40 + "\n"*4
            info += "Рейтинг:\n"
            stats = db.get_stats(message.from_user.id)
            for ind, player in enumerate(stats):
                info += f"{ind + 1}. {player[0]} - счёт: {player[1]}\nПоймал: {player[2]}\n\n"

            for player in db.get_list_players(message.from_user.id):
                bot.send_message(player, info, reply_markup=[init_buttons])
            db.finish_game(message.from_user.id)
        bot.register_next_step_handler(message, finish_game_active)
        return

    elif message.text == "Моя цель":
        bot.send_message(message.chat.id, "Твоя цель - " + db.get_my_target_name(message.chat.id))

    elif message.text == "Осталось":
        players = db.get_current_targets(message.from_user.id)
        info = "Осталось действующих участников - " + str(len(players)) + "\n" + '_' * 40 + "\n"
        for ind, player in enumerate(players):
            info += f"{ ind + 1 }. { player }\n"
        bot.send_message(message.chat.id, info)

    elif message.text == "Правила":
        bot.send_message(message.chat.id, rules)

    bot.register_next_step_handler(message, game_active)

def room_active(message):
    if message.text not in ["Правила", "Начать", "Участники", "Покинуть комнату", "Инфо", "Выбыл", "Правила", "Моя цель", "Осталось"]:
        if db.check_game(message.chat.id) is None:
            bot.send_message(message.chat.id, "Комната была удалена.", reply_markup=[init_buttons])
            route_user(message)
            bot.register_next_step_handler(message, initial_active)
        else:
            bot.send_message(message.chat.id, "Неизвестная команда")
            bot.register_next_step_handler(message, room_active)
        return
    elif message.text in ["Выбыл", "Моя цель", "Осталось"]:
        game_active(message)
        bot.register_next_step_handler(message, game_active)

    elif message.text == "Участники":
        info = "Список участников:\n"
        for index, username in enumerate(db.get_list_players_names(message.from_user.id)):
            info += f"{index + 1}. {username}\n"
        bot.send_message(message.chat.id, info)

    elif message.text == "Правила":
        bot.send_message(message.chat.id, rules)

    elif message.text == "Начать":
        if not db.is_room_admin(message.chat.id):
            bot.send_message(message.chat.id, "Не хакерок ли ты случайно?\nНе шали, здесь красть нечего.")
            return
        players = db.get_list_players(message.chat.id)
        # if len(players) <= 2:
        #     bot.send_message(message.chat.id, "А скучно вам не будет? Ждите ещё.")
        #     bot.register_next_step_handler(message, room_active)
        #     return
        random.shuffle(players)
        db.set_targets(players)
        db.start_game(message.from_user.id)

        for player in players:
            bot.send_message(player, "Игра началась, развлекайтесь", reply_markup=[game_buttons])

    elif message.text == "Инфо":
        info = "Список участников:\n"
        for index, username in enumerate(db.get_list_players_names(message.from_user.id)):
            info += f"{index + 1}. {username}\n"
        owner = "Владелец комнаты - " + db.get_room_info(message.from_user.id) + "\n"
        bot.send_message(message.chat.id,  owner + "_"*40 + "\n" + info)

    elif message.text == "Покинуть комнату":
        players_in_room = db.leave_room(message.from_user.id)
        if players_in_room is None:
            bot.send_message(message.chat.id, "Ты покинул комнату.", reply_markup=[init_buttons])
        else:
            for player in players_in_room:
                if player != message.chat.id:
                    bot.send_message(player, "Ты покинул комнату. Напиши /start", reply_markup=[init_buttons])
                else:
                    bot.send_message(player, "Ты покинул комнату.", reply_markup=[init_buttons])
        bot.register_next_step_handler(message, initial_active)
    bot.register_next_step_handler(message, room_active)

def change_profile(message):
    if message.text == "Да":
        bot.send_message(message.chat.id, "Напиши имя, которое будет известно другим участникам", reply_markup=[no_buttons])
        bot.register_next_step_handler(message, wait_get_name)
    elif "Нет":
        route_user(message)

def wait_get_room_number(message):
    if message.text[0] == '/':
        initial_active(message)
    if message.text in ["Отмена", "Назад", ]:
        bot.send_message(message.chat.id, "Действие отменено", reply_markup=[init_buttons])
        route_user(message)
    else:
        try:
            room_id = int(message.text)
            if db.room_exist(room_id):
                db.come_room(room_id, message.from_user.id)
                bot.send_message(message.chat.id, f"Ты успешно присоединился к комнате №{room_id}",
                                 reply_markup=[room_buttons])
                players = db.get_list_players(message.chat.id)
                name = db.get_name(message.from_user.id)
                if players is not None:
                    for player in players:
                        if player != message.from_user.id:
                            bot.send_message(player, f"К вам присоединился {name}.")
                bot.register_next_step_handler(message, room_active)
                return
            else:
                bot.send_message(message.chat.id, "Не получилось присоединиться. " + message.text,
                                 reply_markup=[init_buttons])

        except:
            bot.send_message(message.chat.id, "Не получилось найти комнату. Попробуй ещё.", reply_markup=[init_buttons])

    bot.register_next_step_handler(message, initial_active)


def wait_get_name(message):
    if message.text[0] == '/':
        initial_active(message)
    if message.text in ["Отмена", "Назад", ]:
        bot.send_message(message.chat.id, "Действие отменено", reply_markup=[init_buttons])
        route_user(message)
    if check_name(message.text):
        db.set_username(message.from_user.id,
                        message.text)
        bot.send_message(message.chat.id, "Твоё имя в игре: " + message.text, reply_markup=[init_buttons])
        route_user(message)
    else:
        bot.send_message(message.chat.id, "Не прошел цензуру, попробуй еще раз " + message.text, reply_markup=[no_buttons])
        bot.register_next_step_handler(message, wait_get_name)


bot.infinity_polling()