import sqlite3


def new_data(dict, time):
    connection = sqlite3.connect('db.sqlite')
    cursor = connection.cursor()
    cursor.execute("SELECT time FROM rates LIMIT 1")
    check_time = cursor.fetchall()
    print(check_time)
    try:
        check_time = check_time[0][0]
        for name in dict:
            rate = round(dict[name], 2)
            data = (name, rate, time, name)
            connection = sqlite3.connect('db.sqlite')
            cursor = connection.cursor()
            cursor.execute("UPDATE rates SET name = ?, rate = ?, time = ? WHERE name = ?", data)
            connection.commit()
    except IndexError:
        for name in dict:
            rate = round(dict[name], 2)
            data = (name, rate, time)
            connection = sqlite3.connect('db.sqlite')
            cursor = connection.cursor()
            cursor.execute("INSERT INTO rates (name, rate, time) VALUES (?,?,?)", data)
            connection.commit()


def get_time():
    connection = sqlite3.connect('db.sqlite')
    cursor = connection.cursor()
    cursor.execute("SELECT time FROM rates LIMIT 1")
    connection.commit()
    time = cursor.fetchall()
    try:
        time = time[0][0]
    except IndexError:
        return 0
    return time


def get_rates():
    connection = sqlite3.connect('db.sqlite')
    cursor = connection.cursor()
    cursor.execute("SELECT name, rate FROM rates")
    connection.commit()
    rates = cursor.fetchall()
    dict = {}
    for currency in rates:
        dict[currency[0]] = currency[1]
    return dict


def delete_all():
    connection = sqlite3.connect('db.sqlite')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM rates")
    connection.commit()


def get_currency(name):
    connection = sqlite3.connect('db.sqlite')
    cursor = connection.cursor()
    cursor.execute("SELECT rate FROM rates WHERE name=?",(name,))
    connection.commit()
    rate = cursor.fetchall()
    return rate

if __name__ == "__main__":
    connection = sqlite3.connect('db.sqlite')
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE rates (id INTEGER PRIMARY KEY, name TEXT, rate TEXT, time timestamp)""")
    connection.commit()
