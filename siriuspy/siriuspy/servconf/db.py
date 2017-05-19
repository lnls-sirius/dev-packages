import pymysql

_connection = None

def get_connection():
    global _connection
    if not _connection:
        _connection = pymysql.connect( host='localhost',
                                            user='root',
                                            password='Ahfae9nobaehohVahzaivu5aeThasohx',
                                            db='sirius',
                                            charset='utf8mb4',
                                            cursorclass=pymysql.cursors.DictCursor)
    return _connection
