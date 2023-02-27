import pymysql
from logmanager import log
def conn():
    # 資料庫設定
    # db_settings = {
    #     "host": "144.48.141.3",
    #     "port": 3306,
    #     "user": "recmwutu_tester",
    #     "password": "(u~YzXV,_YXB",
    #     "db": "recmwutu_thepbooks_test",
    #     "charset": "utf8"
    # }
    db_settings = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "",
        "db": "thepbooks",
        "charset": "utf8"
    }
    try:
        # 建立Connection物件
        c = pymysql.connect(**db_settings)
        return c
            
    except Exception as ex:
        log.err_log(ex)

def insert(sql:str):
    c = conn()
    try:
       
        # 建立Cursor物件
        with c.cursor() as cursor: 
            cursor.execute(sql)
            c.commit()
        return True
    except Exception as ex:
        
        log.err_log(ex)
        return False

def update(sql:str):
    c = conn()
    try:
       
        # 建立Cursor物件
        with c.cursor() as cursor: 
            cursor.execute(sql)
            c.commit()
        return True
    except Exception as ex:
        
        log.err_log(ex)
        return False
        
def query(sql:str):
    
    c = conn()
   
    try:
       
        # 建立Cursor物件
        with c.cursor(pymysql.cursors.DictCursor) as cursor:

            # 執行指令
            cursor.execute(sql)
            # 取得所有資料
            result = cursor.fetchall()
            return result
    except Exception as ex:
        log.err_log(ex)
        return False
    

