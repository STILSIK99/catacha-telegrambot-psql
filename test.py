from database import get_database

db = get_database()


# db.delete_players()
# db.delete_rooms()


arr = db.get_list_person()
arr = sorted(arr, key=lambda obj: obj.id)
for el in arr:
    print(el)