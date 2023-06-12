from sqlalchemy import create_engine
from sqlalchemy import  Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Session
from models import *

class DB:
    """
    Класс для работы с базой данных
    """

    def __init__(self):
        """
        postgresql://user:password@localhost/database
        """
        self.engine = create_engine('postgresql://catacha_user:d8hXR2wPoMCGWtqZ@localhost:5432/catacha', echo=False)
        Base.metadata.create_all(bind=self.engine)


    def __del__(self):
        pass


    def check_reg(self, tg_id):
        with Session (autoflush=False, bind=self.engine) as db:
            user = db.query(Person).filter(Person.id == tg_id).first()
            if user is None:
                db.add(Person(id=tg_id))
                db.commit()
                return False
            else:
                if user.username == "":
                    return False
        return True

    def check_game(self, tg_id):
        with Session(autoflush=False, bind=self.engine) as db:
            room = db.query(Players).filter(Players.id_user == tg_id).first()
        if room is None:
            return None
        return room.id_room

    def create_room(self, tg_id):
        #Получаем id владельца комнаты
        with Session(autoflush=False, bind=self.engine) as db:
            new_room = Room(id_admin=tg_id)
            new_room.players_in_room.append(Players(id_user=tg_id))
            db.add(new_room)
            db.commit()
            _new_room = db.query(Room).filter(Room.id_admin == tg_id).first()
            if _new_room is None:
                return None
        return _new_room.id

    def register(self, tg_id):
        with Session(autoflush=False, bind=self.engine) as db:
            user = Person(id=tg_id)
            db.commit()
            return True
        return False

    def get_name(self, tg_id):
        with Session(autoflush=False, bind=self.engine) as db:
            user = db.query(Person).filter(Person.id == tg_id).first()
        if user is None:
            return None
        return user.username


    def set_username(self, tg_id, name):
        with Session(autoflush=False, bind=self.engine) as db:
            user = db.query(Person).filter(Person.id == tg_id).first()
            user.username = name
            db.commit()

    def get_list_person(self):
        with Session(autoflush=False, bind=self.engine) as db:
            list_person = db.query(Person).all()
        return list_person

    def create_person(self, tg_id, name):
        with Session(autoflush=False, bind=self.engine) as db:
            db.add(Person(id=tg_id, username=name))
            db.commit()
    # def set_photo(self):

    def delete_persons(self):
        with Session(autoflush=False, bind=self.engine) as db:
            db.query(Person).delete()
            db.commit()

    def delete_rooms(self):
        with Session(autoflush=False, bind=self.engine) as db:
            db.query(Room).delete()
            db.commit()

    def delete_players(self):
        with Session(autoflush=False, bind=self.engine) as db:
            db.query(Players).delete()
            db.commit()


    def get_list_room(self):
        with Session(autoflush=False, bind=self.engine) as db:
            list_room = db.query(Room).all()
        return list_room

    def get_room_status(self, room_id):
        with Session(autoflush=False, bind=self.engine) as db:
            room = db.query(Room).get(room_id)
        if room is not None:
            return room.status
        return None

    def get_list_players_names(self, id_player):
        room = self.get_list_players(id_player)
        with Session(autoflush=False, bind=self.engine) as db:
            return [db.query(Person).get(player).username for player in room]
        return None

    def set_targets(self, targets):
        with Session(autoflush=False, bind=self.engine) as db:
            room_id = self.check_game(targets[0])
            for index in range(len(targets)):
                db.add(Targets(id_room=room_id, target_user=targets[index - 1], id_user=targets[index]))
            db.commit()

    def leave_from_game(self, tg_id):
        #удаляем из списка таргетов
        #обновляем статистику
        #возвращаем кол-во живых
        with Session(autoflush=False, bind=self.engine) as db:
            room_id = self.check_game(tg_id)
            next_target = db.query(Targets).filter(Targets.id_user == tg_id and Targets.id_room == room_id)
            prev_target = db.query(Targets).filter(Targets.target_user == tg_id and Targets.id_room == room_id).first()
            prev_target.target_user = next_target.first().target_user
            next_target.delete()
            prev_player = db.query(Players).filter(Players.id_user == prev_target.id_user).first()
            if prev_player is not None:
                if prev_player.score is None:
                    prev_player.score = 0
                prev_player.score += 1
                leaver = db.query(Players).filter(Players.id_user == prev_target.target_user).first()
                if leaver is not None:
                    if prev_player.target_list is None:
                        prev_player.target_list = ""
                    prev_player.target_list += self.get_name(leaver.id_user)
                    prev_player.target_list += ", "

            count = db.query(Targets).filter(Targets.id_room == room_id).count()
            db.commit()
        return count

    def finish_game(self, tg_id):
        with Session(autoflush=False, bind=self.engine) as db:
            room_id = self.check_game(tg_id)
            room = db.query(Room).get(room_id)
            if room is not None:
                room.status = "Finished"
            db.query(Targets).filter(Targets.id_room == room_id).delete()
            db.query(Players).filter(Players.id_room == room_id).delete()
            db.query(Room).filter(Room.id == room_id).delete()
            db.commit()

    def get_current_targets(self, tg_id):
        with Session(autoflush=False, bind=self.engine) as db:
            room_id = self.check_game(tg_id)
            target_list = db.query(Targets).filter(Targets.id_room == room_id).all()
            names = []
            for target in target_list:
                names.append(self.get_name(target.id_user))
            return names

    def start_game(self, tg_id):
        with Session(autoflush=False, bind=self.engine) as db:
            room = db.query(Room).filter(Room.id_admin == tg_id).first()
            if room is not None:
                room.status = "Active"
                db.commit()

    def get_my_target(self, tg_id):
        with Session(autoflush=False, bind=self.engine) as db:
            room_id = self.check_game(tg_id)
            target = db.query(Targets).filter(Targets.id_user == tg_id and Targets.id_room == room_id).first()

        return target.target_user

    def get_my_target_name(self, tg_id):
        return self.get_name(self.get_my_target(tg_id))

    def get_list_players(self, id_player):
        with Session(autoflush=False, bind=self.engine) as db:
            room_player = db.query(Players).filter(Players.id_user == id_player).first()
            if room_player is not None:
                room = db.query(Room).get(room_player.id_room)
                return [player.id_user for player in room.players_in_room]
        return None

    def is_room_admin(self, id_player):
        with Session(autoflush=False, bind=self.engine) as db:
            room = db.query(Room).filter(Room.id_admin == id_player).first()
            if room is None:
                return False
            return True

    def leave_room(self, tg_id):
        with Session(autoflush=False, bind=self.engine) as db:
            if self.is_room_admin(tg_id):
                #удалить комнату и сделать рассылку всем пользователям
                players = self.get_list_players(tg_id)
                room_id = self.check_game(tg_id)
                db.query(Players).filter(Players.id_room == room_id).delete()
                db.query(Room).filter(Room.id == room_id).delete()
                db.commit()
                return players
            else:
                #удалить себя из комнаты
                room = self.check_game(tg_id)
                db.query(Players).filter(Players.id_user == tg_id).delete()
                db.commit()
        return None

    def get_stats(self, tg_id):
        with Session(autoflush=False, bind=self.engine) as db:
            room_id = self.check_game(tg_id)
            players = self.get_list_players(tg_id)
            rating = db.query(Players).filter(Players.id_room == room_id and Players.id_user in players)
            arr = sorted(rating, key=lambda obj: obj.score * (-1))
            return [[self.get_name(player.id_user),
                     player.score, player.target_list[:-2]]
                    for player in arr]

    def room_exist(self, room_id):
        with Session(autoflush=False, bind=self.engine) as db:
            room = db.query(Room).get(room_id)
            if room is None:
                return False
            if room.status == "Wait":
                return True
        return False

    def come_room(self, room_id, tg_id):
        with Session(autoflush=False, bind=self.engine) as db:
            db.add(Players(id_room=room_id, id_user=tg_id))
            db.commit()

    def get_room_info(self, tg_id):
        room_id = self.check_game(tg_id)
        if room_id is None:
            return ""
        with Session(autoflush=False, bind=self.engine) as db:
            room = db.query(Room).get(room_id)
            if room is None:
                return ""
            admin = db.query(Person).filter(Person.id == room.id_admin).first()
            return admin.username


def get_database():
    db = DB()
    return db