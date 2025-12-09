
import redis
from main import get_hash
import os

def get_redis_client() -> None:
    return redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        db=0 # вообще это значение по умолчанию, но у тебя в коде ниже было это, поэтому оставила 
    )


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
    
print(check_if_user_exists('admin', 'adminpa'))


def register_user(id:str, name:str, passwd:str) -> bool:
    try:
        r = get_redis_client()
    except:
        raise ValueError
    
    hash_pass = get_hash(passwd)
    print(hash_pass)
    user = {'id': id, 'name' : name, 'passwd' : hash_pass}
    r.hmset(id, user)
    return True

register_user('admin', 'testdata', 'adminpa')