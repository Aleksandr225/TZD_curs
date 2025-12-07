import sqlite3
import os
import gostcrypto
import redis

from shifr import *




def get_hash(obj):
    obj = bytes(obj, encoding='utf-8')
    hash_obj = gostcrypto.gosthash.new('streebog256', data=obj)
    result = hash_obj.hexdigest()
    return result

#  добавила функцию подключения к редис 
def get_redis_client():
    return redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        db=0 # вообще это значение по умолчанию, но у тебя в коде ниже было это, поэтому оставила 
    )




# криво рабоатет ==> если вводишь неправильный логин, то запускает 
def check_if_user_exists(id:str,  passwd:str) -> bool:
    try:
        r = get_redis_client()
    except:
        raise ValueError
    
    hash_pass = get_hash(passwd)

    val = r.hmget(id, 'id', 'passwd')
    print(val)
    if val[0] == id and val[1] == passwd:
        return False
    else:
        return True


def register_user(id:str, name:str, passwd:str) -> bool:
    try:
        r = get_redis_client()
    except:
        raise ValueError
    
    hash_pass = get_hash(passwd)
    r.hmset(id, {'id': id, 'name': name, 'passwd' : hash_pass})
    return True




def get_hash_for_file(file_path):
    buffer_size = 128
    hash_obj = gostcrypto.gosthash.new('streebog512')
    with open(file_path, 'rb') as file:
        buffer = file.read(buffer_size)
        while len(buffer) > 0:
            hash_obj.update(buffer) # type: ignore
            buffer = file.read(buffer_size)
    hash_result = hash_obj.hexdigest()
    return hash_result



# print(get_hash_for_file('/Users/a666vg/TZD_curs/main.py'))



































































# import sqlite3
# import gostcrypto





# def sql_check(param:str) -> bool:
#     filter = '-;%,=+/"'''
#     arr = list(set(list(param)))
#     for i in arr:
#         if i in filter:
#             return False
#     return True

# def get_hash(obj):
#     obj = bytes(obj, encoding='utf-8')
#     hash_obj = gostcrypto.gosthash.new('streebog256', data=obj)
#     result = hash_obj.hexdigest()
#     return result




# def check_if_user_exists(id:str,  passwd:str) -> bool:
#     if sql_check(id):
#         if sql_check(passwd):pass
#         else: return False
#     else: return False

#     try:
#         conn = sqlite3.connect('db.db')
#         cursor = conn.cursor()
#     except:
#         raise ValueError
    
#     hash_pass = get_hash(passwd)

#     cursor.execute('''SELECT * FROM user WHERE work_id = ? AND hash_pass = ?''', (id, hash_pass,))
#     rows = cursor.fetchall()
#     if not rows:
#         return False
#     else:
#         return True


# def register_user(id:str, name:str, passwd:str) -> bool:
#     if sql_check(id):
#         if sql_check(passwd):
#             if sql_check(name):
#                 pass
#             else: return False
#         else: return False
#     else: return False

#     try:
#         conn = sqlite3.connect('db.db')
#         cursor = conn.cursor()
#     except:
#         raise ValueError
    
#     hash_pass = get_hash(passwd)
#     cursor.execute('''INSERT INTO user(name, hash_pass, work_id) VALUES (?,?,?)''', (name, hash_pass, id,))
#     conn.commit()
#     return True







# """
# hash_obj = gostcrypto.gosthash.new('streebog256', data=hex)
# result = hash_obj.hexdigest()
# print(result)
# """
