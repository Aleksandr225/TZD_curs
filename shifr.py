
import binascii
from copy import copy
from memory_profiler import memory_usage
import struct
from tables import Tables
from utils import bytes2long
from utils import long2bytes
from utils import strxor 
from utils import xrange
import gostcrypto


def pad_size(data_size, blocksize):
    """Calculate required pad size to full up blocksize
    """
    if data_size < blocksize:
        return blocksize - data_size
    if data_size % blocksize == 0:
        return 0
    return blocksize - data_size % blocksize

def pad2(data, blocksize):
   
    return data + b"\x80" + b"\x00" * pad_size(len(data) + 1, blocksize)


class GOST3412_2015:
    tables = None

    def __init__(self):
        self.tables = Tables()

    def start_encrypt(self, message, start_key):
        round_key = [start_key[:16], start_key[16:]]
        round_keys = round_key + self.generate_key(round_key)
        return self.encrypt(message, round_keys)

    def start_decrypt(self, cipher, start_key):
        round_key = [start_key[:16], start_key[16:]]
        round_keys = round_key + self.generate_key(round_key)
        return self.decrypt(cipher, round_keys)

    def generate_key(self, round_key):
        round_keys = []
        for i in range(4):
            for k in range(8):
                round_key = self.feistel(self.tables.c[8 * i + k], round_key)
            round_keys.append(round_key[0])
            round_keys.append(round_key[1])
        return round_keys

    def feistel(self, c, k):
        tmp = self.x_box(c, k[0])
        tmp = self.s_box(tmp)
        tmp = self.L_box(tmp)
        tmp = self.x_box(tmp, k[1])
        return [tmp, k[0]]

    # x_box: k = k xor a
    def x_box(self, k, a):
        # Исправление: конвертируем bytes в list(ints), если нужно
        if isinstance(k, bytes):
            k = list(k)
        if isinstance(a, bytes):
            a = list(a)
        tmp = copy(k)
        for i in range(0, len(k)):
            tmp[i] ^= a[i]
        return tmp

    def s_box(self, a):
        res = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(len(a)):
            res[i] = self.tables.pi[a[i]]
        return res

    def s_box_inv(self, a):
        res = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(len(a)):
            res[i] = self.tables.pi_inv[a[i]]
        return res

    def L_box(self, a):
        for i in range(len(a)):
            a = self.R_box(a)
        return a

    def L_box_inv(self, a):
        for i in range(len(a)):
            a = self.R_box_inv(a)
        return a

    def R_box(self, a):
        return [self.l_box(a)] + a[:-1]

    def R_box_inv(self, a):
        return a[1:] + [self.l_box(a[1:] + [a[0]])]

    # l_box: l(a15..a0) = 148 * a15 + 32 * a14 ... + 1 * a0
    def l_box(self, a):
        coef = [148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1]
        mul_coef = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(0, len(coef)):
            mul_coef[i] = self.tables.mul_table[a[i]][coef[i]]
        res = 0
        for i in mul_coef:
            res ^= i
        return res

    def encrypt(self, message, round_keys):
        tmp = message
        for i in range(9):
            tmp = self.x_box(tmp, round_keys[i])
            tmp = self.s_box(tmp)
            tmp = self.L_box(tmp)
        tmp = self.x_box(tmp, round_keys[9])

        return tmp

    def decrypt(self, cipher, round_keys):
        tmp = cipher
        for i in range(9, 0, -1):
            tmp = self.x_box(tmp, round_keys[i])
            tmp = self.L_box_inv(tmp)
            tmp = self.s_box_inv(tmp)
        tmp = self.x_box(tmp, round_keys[0])
        return tmp
    
    def encrypt_block(self, block):
        if self.key is None:
            raise ValueError("Key not set. Call generate_key first.")
        return self.start_encrypt(bytes(block), bytes(self.key))



    def pad(self, lst, chunk_size):
        result = []
        for i in range(0, len(lst), chunk_size):
            part = lst[i:i + chunk_size]
            result.append(part)
        return result
    

    def _mac_shift(self, bs, data, xor_lsb=0):
        num = (bytes2long(bytes(data)) << 1) ^ xor_lsb
        return list(long2bytes(num, bs)[-bs:])

    def _mac_ks(self, bs, key):
        Rb = 0b10000111 
        _l = self.start_encrypt([0] * bs, key)  
        k1 = self._mac_shift(bs, _l, Rb) if _l[0] & 0x80 else self._mac_shift(bs, _l)
        k2 = self._mac_shift(bs, k1, Rb) if k1[0] & 0x80 else self._mac_shift(bs, k1)
        return k1, k2

    
    def mac(self, data, key):
        bs = 16  
        k1, k2 = self._mac_ks(bs, key)
        if not data:
            return self.start_encrypt(strxor([0] * bs, k2), key)
        
        blocks = self.pad(data, bs)  
        prev = [0] * bs  
        for block in blocks[:-1]:  
            prev = self.start_encrypt(strxor(prev, block), key)

        last_block = blocks[-1] 
        last = self.xor_bytes(last_block, k1)
        
        mac_result = self.start_encrypt(self.xor_bytes(prev, last), key)
        return mac_result
        
    def increment_hex(self, hex_string):
        hex_string = str(binascii.hexlify(bytes(hex_string)).decode())
        
        s1, s2 = hex_string[:16], hex_string[16:]
    
        num = int(s1, 16)
    
        num += 1
        new_hex = hex(num)[2:] + s2
        new_hex = list(binascii.unhexlify(new_hex))
        return new_hex



    def gf_mul(self, a: bytes, b: bytes) -> bytes:
        
        MOD_POLY = 0x100000000000000000000000000000087  #x^128 + x^7 + x^2 + x + 1 (hex)
    
    
        a_int = int.from_bytes(a, 'big')
        b_int = int.from_bytes(b, 'big')
    
    
        result = 0
        for i in range(128):
            if (b_int >> i) & 1:
                result ^= a_int
            a_int <<= 1
            if a_int & (1 << 128):
                a_int ^= MOD_POLY
    
    # Обратно в bytes
        return result.to_bytes(16, 'big')



    def xor_bytes(self, a, b):
        """XOR two byte arrays of same length."""
        return bytes(x ^ y for x, y in zip(a, b))



    def imit_mgm(self, prev, key, A, C):
        prev = str(binascii.hexlify(bytes(prev)).decode())
        s1, s2 = prev[:1], prev[1:]
        num = int(s1, 16)
        num += 8
        new_hex = hex(num)[2:] + s2
        n_prev = list(binascii.unhexlify(new_hex))

        z = n_prev
        z = self.start_encrypt(z, key)
        H = self.start_encrypt(z, key)

        original_C_bytes = C[:-13] 
        original_A_bytes = binascii.unhexlify(A) 
        len_A_bits = len(original_A_bytes) * 8  
        len_C_bits = len(original_C_bytes) * 8  
        len_A_packed = struct.pack('>Q', len_A_bits)  
        len_C_packed = struct.pack('>Q', len_C_bits)
        len_block = len_A_packed + len_C_packed

        A = make_right_len(A)
        A = list(binascii.unhexlify(A))
        
        A_blocks = [A[i:i+16] for i in range(0, len(A), 16)]
        C_blocks = [C[i:i+16] for i in range(0, len(C), 16)]
        all_blocks = A_blocks + C_blocks
        
        for i in range(len(all_blocks)):
            all_blocks[i] = self.gf_mul(H, all_blocks[i])
            z = self.increment_hex(z)
            H = self.start_encrypt(z, key)
        auth_sum = b'\x00' * 16  
        for i, block in enumerate(all_blocks):
            auth_sum = self.xor_bytes(auth_sum, block)
        fin_xor = self.xor_bytes(self.gf_mul(H, len_block), auth_sum)
        mac = self.start_encrypt(fin_xor, key)
        return mac
        

    def mgm(self, data, key, A):
        bs = 16
        enc = []
        blocks = self.pad(data, 16)
        global prev
        prev = blocks[0]
        
        y = prev
        y = self.start_encrypt(y, key)
        y = int.from_bytes(y, 'big') 
        for block in blocks:  
            y_bytes = y.to_bytes(bs, 'big')  
            k_y = self.start_encrypt(y_bytes, key)
            encrypted_block = bytes([b ^ k for b, k in zip(block, k_y)])
            enc.append(encrypted_block)
            y +=1

        
      
        
        
        return b''.join(enc)
        

    def decrypt_mgm(self, C, key, prev):
        
       
        dec = []
        y = prev
        y = self.start_encrypt(y, key)
        y = int.from_bytes(y, 'big') 

        blocks = [C[i:i+16] for i in range(0, len(C), 16)]
    
        for block in blocks:
            y_bytes = y.to_bytes(16, 'big')
            k_y = self.start_encrypt(y_bytes, key)
            decrypted_block = bytes(b ^ k for b, k in zip(block, k_y))  
            dec.append(decrypted_block)
            y += 1  
    
        plaintext = b''.join(dec) 
        return plaintext


prev = ''

import binascii

def make_right_len(data, block_size=16):
    byte_len = len(data) // 2
    padding_bytes = (block_size - (byte_len % block_size)) % block_size
    padding_hex = '00' * padding_bytes
    return data + padding_hex

def make_right_len_str(data):
    while len(data) % 32 != 0:
        data +='0'
    return data


def chifr_file(file_path, key):
    algo = GOST3412_2015()
    with open(file_path, 'rb') as f:
        text = f.read()
    key = key.lower()
    key = list(binascii.unhexlify(key))
    res = algo.mgm(text, key, A='')
    n_file_path = file_path[:-4] + 'enc'
    with open(n_file_path, 'wb') as file:
        file.write(res)
    return n_file_path




def unchifr_file(file_path, key):
    algo = GOST3412_2015()
    with open(file_path, 'rb') as f:
        text = f.read()
    key = key.lower()
    key = list(binascii.unhexlify(key))
    res = algo.decrypt_mgm(text, key, prev)
    output_path = file_path[:-3] + 'docx'
    with open(output_path, 'wb') as file:
        file.write(res)
    return output_path
