import sqlite3
import gostcrypto





def sql_check(param:str) -> bool:
    filter = '-;%,=+/"'''
    arr = list(set(list(param)))
    for i in arr:
        if i in filter:
            return False
    return True

def get_hash(obj):
    obj = bytes(obj, encoding='utf-8')
    hash_obj = gostcrypto.gosthash.new('streebog256', data=obj)
    result = hash_obj.hexdigest()
    return result




def check_if_user_exists(id:str,  passwd:str) -> bool:
    if sql_check(id):
        if sql_check(passwd):pass
        else: return False
    else: return False

    try:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
    except:
        raise ValueError
    
    hash_pass = get_hash(passwd)

    cursor.execute('''SELECT * FROM user WHERE work_id = ? AND hash_pass = ?''', (id, hash_pass,))
    rows = cursor.fetchall()
    if not rows:
        return False
    else:
        return True


def register_user(id:str, name:str, passwd:str) -> bool:
    if sql_check(id):
        if sql_check(passwd):
            if sql_check(name):
                pass
            else: return False
        else: return False
    else: return False

    try:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
    except:
        raise ValueError
    
    hash_pass = get_hash(passwd)
    cursor.execute('''INSERT INTO user(name, hash_pass, work_id) VALUES (?,?,?)''', (name, hash_pass, id,))
    conn.commit()
    return True







"""
hash_obj = gostcrypto.gosthash.new('streebog256', data=hex)
result = hash_obj.hexdigest()
print(result)
"""
