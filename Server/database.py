def main():
    print("""
    A set of predefined operations to create and interact with a sqlite3
    database for storing usernames and passwords.
    """)

def make_database(connection):
    """
    Creates a user_info table (name, password, active, sock)
    Called on startup if the database doesn't already exist

    """
    db_cursor = connection.cursor()
    db_cursor.execute("CREATE TABLE user_info(name TEXT, password TEXT)")


def new_user(connection, username, password):
    """
    Adds a new user to the sqlite3 database
    """
    db_cursor = connection.cursor()
    db_cursor.execute("INSERT INTO user_info VALUES(?, ?)", (username, password))
    connection.commit()


def remove_user(connection, username):
    """
    remove a user from the database, this function is not currently used
    """
    db_cursor = connection.cursor()
    db_cursor.execute("DELETE FROM user_info WHERE name=?", (username,))
    connection.commit()


def username_check(connection, username, password):
    """
    Used to check if the username exists for signup requests, and
    to check if submitted password is correct.
    """
    db_cursor = connection.cursor()
    db_cursor.execute("SELECT * FROM user_info WHERE name=?", (username,))
    user = db_cursor.fetchone()

    if user:
        exists = True  # username exists in the database

        # check if submitted password is equal to the one stored in database
        if user[1] == password:
            correct_password = True
        else:
            correct_password = False

    else:
        exists = False
        correct_password = False

    return exists, correct_password

if __name__ == "__main__":
    main()
