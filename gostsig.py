
import math
import gostcrypto
import random

def get_hash_for_sig(file_path):
    buffer_size: int = 128
    hash_obj = gostcrypto.gosthash.new('streebog256')
    with open(file_path, 'rb') as file:
        buffer = file.read(buffer_size)
        while len(buffer) > 0:
            hash_obj.update(buffer) 
            buffer = file.read(buffer_size)
    hash_result = hash_obj.digest()
    return hash_result

def is_prime(n):  
    if n <= 1:  
        return False  
    for i in range(2, int(n**0.5) + 1):  
        if n % i == 0:  
            return False  
    return True  

def is_coprime(x, y):
    return math.gcd(x, y) == 1

def get_a(P, Q):
    arr = []
    for i in range(P):
        if i**Q%P == 1 and i < P-1:
            arr.append(i)
            print(arr)
    return arr


def get_q(P):
    qarr = []
    for i in range(1,P):
        if ((P-1) % i == 0) and (is_prime(i) == True):
            qarr.append(i)
            print(qarr)

    return qarr


import sys
sys.set_int_max_str_digits(100000)

def gost(file_path):
    P = 7369

    Q = 307
    

    a = 6937

    while True:
        x = random.randint(0, Q)
        if x > Q:
            print(f"Число должно быть меньше {Q}")
            continue
        else:
            break

    while True:
        k = random.randint(0, P)
        if x > P:
            print(f"Число должно быть меньше {P}")
            continue
        else:
            break
    




    y = a**x%P
    
    m = get_hash_for_sig(file_path=file_path)
    m = int.from_bytes(m)
    r = (a**k % P) % Q
    s = (x*r+k*m) % Q

    print(f"Число y: {y}")
    print(f"Число k: {k}")
    print(f"Число m: {m}")
    print(f"подпись r, s: {r, s}")
    

    v = m**(Q-2)
    z1 = (s*v) % Q
    z2 = ((Q-r)*v) % Q
    u = (((a**z1*y**z2)% P) % Q)


    print(f"Число v: {v}")
    print(f"Число z1: {z1}")
    print(f"Число z2: {z2}")


    print(f"Число r: {r} Число u: {u}")

gost('requirements.txt')

