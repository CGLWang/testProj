import pymysql
from configuration import get_config_values

PORT = int(get_config_values('mysql', 'port'))
HOST = get_config_values('mysql', 'host')
USER = get_config_values('mysql', 'user')
PASW = get_config_values('mysql', 'password')
DATB = get_config_values('mysql', 'database')


def get_list(sql,args=None):
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASW,db=DATB, charset='utf8')
    cursor = conn.cursor()
    try:
        cursor.execute(sql,args)
        result = cursor.fetchall()
    except Exception as e:
        print(e)
    cursor.close()
    conn.close()
    return result

def get_list_dict(sql,args=None):
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASW,db=DATB, charset='utf8')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cursor.execute(sql,args)
        result = cursor.fetchall()
    except Exception as e:
        print(e)
    cursor.close()
    conn.close()
    return result

def get_one(sql,args=None):
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASW,db=DATB, charset='utf8')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql, args)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def execute(sql,args=None):
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASW,db=DATB, charset='utf8')
    cursor = conn.cursor()
    cursor.execute(sql,args)
    conn.commit()
    cursor.close()
    conn.close()

def insert_many(sql,args=None):
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASW,db=DATB, charset='utf8')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.executemany(sql,args)
    conn.commit()
    cursor.close()
    conn.close()

def execute_many_sql(sqls):
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASW,db=DATB, charset='utf8')
    cursor = conn.cursor()
    for item in sqls:
        cursor.execute(item)
    # cursor.execute('''SET FOREIGN_KEY_CHECKS=0''')
    # cursor.execute('''TRUNCATE TABLE repeatcheck_cache''')
    # cursor.execute('''SET FOREIGN_KEY_CHECKS=1''')
    conn.commit()
    cursor.close()
    conn.close()