import redis
import gostcrypto
from shifr import *
r = redis.Redis(
        host='localhost', db=0 )

def get_hash_for_file(data):
    hash_obj = gostcrypto.gosthash.new('streebog512')
    hash_obj.update(data) 
    
    hash_result = hash_obj.hexdigest()
    return hash_result




'''
with open('uploads/Doc1.Docx', 'rb') as f:
    text = f.read()
    r.set('Doc1.Docx', text, 60)
'''
data = r.get('Doc1.Docx')
print(get_hash_for_file(data))