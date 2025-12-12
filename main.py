import sqlite3
import os
import gostcrypto
import redis





def get_hash(obj) -> str:
    obj = bytes(obj, encoding='utf-8')
    hash_obj = gostcrypto.gosthash.new('streebog256', data=obj)
    result = hash_obj.hexdigest()
    return result

#  добавила функцию подключения к редис 
def get_redis_client() -> None:
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
    if val[0] == id and val[1] == hash_pass:
        return True
    else:
        return False


def register_user(id:str, name:str, passwd:str) -> bool:
    try:
        r = get_redis_client()
    except:
        raise ValueError
    
    hash_pass = get_hash(passwd)
    r.hmset(id, {'id': id, 'name': name, 'passwd' : hash_pass})
    return True


def check_data_in_redis(key) -> bool:
    r = get_redis_client()
    data = r.get(key)
    return True if data is not None else False


def add_data_to_redis(key, data, mode) -> None:
    r = get_redis_client()
    r.set(f'{key}:{mode}', data, 300)
    


def get_data_from_redis(key) -> bytes:
    r = get_redis_client()
    return r.get(key)



def get_hash_for_file(file_path) -> str: 
    if check_data_in_redis(f'{file_path[8:]}:hash') is True:
        os.remove(file_path)
        return get_data_from_redis(f'{file_path[8:]}:hash')

    else:
        buffer_size: int = 128
        hash_obj = gostcrypto.gosthash.new('streebog512')
        with open(file_path, 'rb') as file:
            buffer = file.read(buffer_size)
            while len(buffer) > 0:
                hash_obj.update(buffer) 
                buffer = file.read(buffer_size)
        hash_result = hash_obj.hexdigest()
        add_data_to_redis(file_path[8:], hash_result, 'hash')
        os.remove(file_path)
    return hash_result





import random

def generate_key() -> str:
    key_gen_alph: str = "0123456789ABCDEF"
    key: str = ''
    items = os.listdir('uploads')
    for i in items:
        os.remove(f'uploads/{i}')
    for _ in range(64): key += key_gen_alph[random.randint(0,15)]

    return key
