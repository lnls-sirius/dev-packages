import pymysql

_connection = None

def get_connection():
    global _connection
    if not _connection:
        _connection = pymysql.connect(host='10.0.21.65',
                                      user='root',
                                      password='root',
                                      db='sirius',
                                      charset='utf8mb4',
                                      cursorclass=pymysql.cursors.DictCursor)
    return _connection
