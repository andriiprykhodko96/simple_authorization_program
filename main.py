import pymysql
import uuid
import hashlib
from re import match

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='my_first',
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Connected to db")
except Exception as ex:
    print('Something went wrong...')
    print(ex)
    exit()


def start_panel():
    while True:
        print("\n1 - register\n"
              "2 - log in\n"
              "3 - help\n"
              "4 - exit\n")
        command = int(input("Enter what to do: "))
        if command == 1:
            register()
        if command == 2:
            authorize()
        if command == 3:
            help_page()
        if command == 4:
            exit()


def admin_panel():
    while True:
        print("\n1 - change ADMIN password\n"
              "2 - view list of users\n"
              "3 - add user with blank password\n"
              "4 - ban user\n"
              "5 - turn on/off restriction\n"
              "6 - exit\n")
        command = int(input("Enter what to do: "))
        if command == 1:
            change_admin_pass()
        if command == 2:
            user_list()
        if command == 3:
            add_user_by_admin()
        if command == 4:
            ban()
        if command == 5:
            turn_on_off_restriction()
        if command == 6:
            start_panel()


def user_panel():
    while True:
        print('\n1 - change password\n'
              '2 - exit\n')
        command = int(input("Enter what to do: "))
        if command == 1:
            change_password()
        if command == 2:
            start_panel()


def create_table_users():
    try:
        with connection.cursor() as cursor:
            create_table_query = "CREATE TABLE `users`(" \
                                 " name varchar(32)," \
                                 " password varchar(256)," \
                                 " ban BOOLEAN," \
                                 " restriction BOOLEAN," \
                                 " PRIMARY KEY (name));"
            cursor.execute(create_table_query)
            print("Table was created")
            query = "INSERT INTO `users` (name,password,ban,restriction)" \
                    "VALUES(%s,%s,%s,%s)"
            password = hash_password('admin')
            cursor.execute(query, ("admin", password, 0, 0))
            connection.commit()
            print("ADMIN was created")
    except Exception as ex:
        print(ex)


def drop_table_users():
    try:
        with connection.cursor() as cursor:
            drop_table_query = "DROP TABLE `users`;"
            cursor.execute(drop_table_query)
            print("Table was deleted")
    except Exception as ex:
        print(ex)


def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


def register():
    print("REGISTRATION")
    name = str(input("Enter username >>"))
    password = str(input("Enter password >> "))
    password = hash_password(password)
    try:
        with connection.cursor() as cursor:
            query = "INSERT INTO `users` (name,password,ban,restriction)" \
                    "VALUES(%s,%s,%s,%s)"
            cursor.execute(query, (name, password, 0, 0))
            connection.commit()
            print("User {0} was registered".format(name))
    except Exception as ex:
        print('Something went wrong...')
        print(ex)


def exist_check(name):
    try:
        with connection.cursor() as cursor:
            query = "SELECT count(*) FROM `users` WHERE name = %s"
            cursor.execute(query, name)
            res = cursor.fetchall()
            if res[0]['count(*)'] > 0:
                return True
            else:
                return False
    except Exception as ex:
        print(ex)


def is_banned(name):
    try:
        with connection.cursor() as cursor:
            query = "SELECT ban FROM `users` WHERE name = %s"
            cursor.execute(query, name)
            res = cursor.fetchall()
            if res[0]['ban'] == 1:
                return True
            else:
                return False
    except Exception as ex:
        print(ex)


def change_password():
    print("CHANGE PASSWORD")
    name = str(input("Enter your name >>"))
    password = str(input("Enter your OLD password >>"))
    if exist_check(name):
        try:
            with connection.cursor() as cursor:
                query = 'SELECT `password` FROM `users`' \
                        'WHERE name=%s'
                cursor.execute(query, name)
                db_old_pass = cursor.fetchall()
                db_old_pass = db_old_pass[0]['password']
                if check_password(db_old_pass, password):
                    new_password1 = str(input("Enter your NEW password >>"))
                    new_password2 = str(input("Enter your NEW password again >>"))
                    if new_password1 == new_password2:
                        query = "UPDATE `users`" \
                                "SET password=%s" \
                                "WHERE name= %s"
                        cursor.execute(query, (hash_password(new_password1), name))
                        connection.commit()
                    else:
                        print('Your passwords does not matches')
                else:
                    print("Old password is incorrect")
        except Exception as ex:
            print('Something went wrong...')
            print(ex)
    else:
        print("No user")


def is_rest(name):
    try:
        with connection.cursor() as cursor:
            query = "SELECT restriction FROM `users` WHERE name = %s"
            cursor.execute(query, name)
            res = cursor.fetchall()
            if res[0]['restriction'] == 1:
                return True
            else:
                return False
    except Exception as ex:
        print(ex)


def check_password_rest(password):
    return match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[\W^ ])', password)


def authorize():
    print("AUTHORIZATION")
    name = str(input("Enter your name >>"))
    password = str(input("Enter your password >>"))
    if exist_check(name):
        try:
            with connection.cursor() as cursor:
                query = "SELECT password FROM `users` WHERE name = %s"
                cursor.execute(query, name)
                db_pass = cursor.fetchall()
                db_pass = db_pass[0]['password']
                if check_password(db_pass, password):
                    if is_banned(name):
                        print("OH! Your were banned")
                    else:
                        if is_rest(name):
                            if check_password_rest(password):
                                print("Success!")
                            else:
                                print("Please change your password")
                                change_password()
                        else:
                            if name == "admin":
                                print("Success!")
                                admin_panel()
                            else:
                                print("Success!")
                                user_panel()
                else:
                    i = 0
                    while True:
                        print("Your passwords doesnt matches.Enter again")
                        password = str(input("Enter your password >>"))
                        if check_password(db_pass, password):
                            print("Success!")
                            if name == 'admin':
                                admin_panel()
                            else:
                                user_panel()
                            return False
                        i+=1
                        if i > 1:
                            print("Goodbye(")
                            exit()
        except Exception as ex:
            print(ex)
    else:
        print("There is no user with such name")


def ban():
    print("BAN panel")
    name = str(input("Enter name to ban >>"))
    if exist_check(name):
        try:
            with connection.cursor() as cursor:
                query = "UPDATE `users` SET ban = 1 WHERE name = %s"
                cursor.execute(query, name)
                connection.commit()
                print("User {0} was banned!".format(name))
        except Exception as ex:
            print(ex)
    else:
        print("There is no user with such name")


def user_list():
    print("USER LIST")
    try:
        with connection.cursor() as cursor:
            query = "SELECT * from `users`"
            cursor.execute(query)
            out = cursor.fetchall()
            for user in out:
                print(user)
    except Exception as ex:
        print(ex)


def change_admin_pass():
    old_pass = str(input("Enter OLD password>> "))
    try:
        with connection.cursor() as cursor:
            query = 'SELECT `password` FROM `users`' \
                    'WHERE name=%s'
            cursor.execute(query, 'admin')
            db_old_pass = cursor.fetchall()
            db_old_pass = db_old_pass[0]['password']
            if check_password(db_old_pass, old_pass):
                new_password1 = str(input("Enter your NEW password >>"))
                new_password2 = str(input("Enter your NEW password again >>"))
                if new_password1 == new_password2:
                    query = "UPDATE `users`" \
                            "SET password=%s" \
                            "WHERE name= %s"
                    cursor.execute(query, (hash_password(new_password1), "admin"))
                    connection.commit()
                else:
                    print("Passwords do not match.Try again")
            else:
                print("Wrong password. Try again")
    except Exception as ex:
        print(ex)


def add_user_by_admin():
    name = str(input("Enter name >>"))
    if exist_check(name):
        print('user with name {0} already exists')
    else:
        try:
            with connection.cursor() as cursor:
                query = "INSERT INTO `users` (name,password,ban,restriction)" \
                        "VALUES(%s,%s,%s,%s)"
                cursor.execute(query, (name, '', 0, 0))
                connection.commit()

        except Exception as ex:
            print(ex)


def turn_on_off_restriction():
    name = str(input('Enter name>> '))
    if exist_check(name):
        rest = input("Enter 1 to turn on or 0 to turn off >> ")
        try:
            with connection.cursor() as cursor:
                query = "UPDATE `users` SET restriction = %s WHERE name = %s"
                cursor.execute(query, (rest, name))
                connection.commit()
                print("Restriction was changed")
        except Exception as ex:
            print(ex)
    else:
        print("There is no user")


def help_page():
    print(
        "\nAbout\n"
        "Наявність рядкових і прописних букв, а також розділових знаків\n"
        "Andrii Prykhodko FB-93\n"
    )


if __name__ == '__main__':
    drop_table_users()
    create_table_users()
    start_panel()
