from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import  hashlib

class CryptoEncrypt:




    def info(self):
        print('''当前类是一个集各种加密工具方法集合的工具类，你可以利用此工具实现各种加密算法如MD5,AES....''')
    #MD5加密
    @staticmethod
    def md5(value):
        # 创建md5对象
        md5 = hashlib.md5()
        # 更新md5对象
        md5.update(value.encode('utf8'))
        return md5.hexdigest()
    #SHA1加密
    @staticmethod
    def sha1(value):
        # 创建sha1对象
        sha1 = hashlib.sha1()
        # 更新sha1对象
        sha1.update(value.encode('utf8'))
        return sha1.hexdigest()
    #SHA256加密
    @staticmethod
    def sha256(value):
        # 创建sha256对象
        sha256 = hashlib.sha256()
        # 更新sha256对象
        sha256.update(value.encode('utf8'))
        return sha256.hexdigest()
    #SHA512加密
    @staticmethod
    def sha512(value):
        # 创建sha512对象
        sha512 = hashlib.sha512()
        # 更新sha512对象
        sha512.update(value.encode('utf8'))
        return sha512.hexdigest()
    #sha384加密
    @staticmethod
    def sha384(value):
        # 创建sha384对象
        sha384 = hashlib.sha384()
        # 更新sha384对象
        sha384.update(value.encode('utf8'))
        return sha384.hexdigest()
    #sha224加密
    @staticmethod
    def sha224(value):
        # 创建sha224对象
        sha224 = hashlib.sha224()
        # 更新sha224对象
        sha224.update(value.encode('utf8'))
        return sha224.hexdigest()
    @staticmethod
    def ripemd(value):
        # 创建sha3对象
        ripemd = hashlib.new('ripemd160')
        # 更新sha3对象
        ripemd.update(value.encode('utf8'))
        return ripemd.hexdigest()

    #base64加密
    @staticmethod
    def base64Encrypt(value):
        bytes_string = value.encode('utf8')
        return base64.b64encode(bytes_string).decode('utf8')

    #base64解密
    @staticmethod
    def base64Decrypt(value):
        bytes_string = value.encode('utf8')
        return base64.b64decode(bytes_string).decode('utf8')
