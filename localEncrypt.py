from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random
import os.path



# key generation Alisa ГЕНЕРАЦИЯ КЛЮЧЕЙ ДЛЯ ДВУХ ЧЕЛОВЕК
file_path = "D:\SSI project\\1234\\alisaprivatekey.txt"
imporstop = os.path.exists(file_path)
if not imporstop:
    privatekey = RSA.generate(2048)
    f = open('D:\SSI project\\1234\\alisaprivatekey.txt', 'wb')
    f.write(bytes(privatekey.exportKey('PEM')));
    f.close()
    publickey = privatekey.publickey()
    f = open('D:\SSI project\\1234\\alisapublickey.txt', 'wb')
    f.write(bytes(publickey.exportKey('PEM')));
    f.close()
    # key generation Bob
    privatekey = RSA.generate(2048)
    f = open('D:\SSI project\\1234\\bobprivatekey.txt', 'wb')
    f.write(bytes(privatekey.exportKey('PEM')));
    f.close()
    publickey = privatekey.publickey()
    f = open('D:\SSI project\\1234\\bobpublickey.txt', 'wb')
    f.write(bytes(publickey.exportKey('PEM')));
    f.close()


# creation of signature # НАЧАЛО ОТПРАВКИ СООБЩЕНИЯ (ТУТ ОНО ПОДПИСЫВАЕТСЯ)
f = open('D:\SSI project\\1234\plaintext.txt','rb')
plaintext = f.read(); f.close()
privatekey = RSA.importKey(open('D:\SSI project\\1234\\alisaprivatekey.txt','rb').read())
myhash = SHA256.new(plaintext)
signature = PKCS1_v1_5.new(privatekey)
signature = signature.sign(myhash)
print(plaintext)
# signature encrypt #ПОДПИСЬ ШИФРУЕТСЯ ОТКРЫТЫМ КЛЮЧОМ БОБА
publickey = RSA.importKey(open('D:\SSI project\\1234\\bobpublickey.txt','rb').read())
cipherrsa = PKCS1_OAEP.new(publickey)
sig = cipherrsa.encrypt(signature[:128])
sig = sig + cipherrsa.encrypt(signature[128:])
f = open('D:\SSI project\\1234\signature.txt','wb')
f.write(bytes(sig)); f.close()

# creation 256 bit session key #ГЕНЕРИРУЕТ СЕССИОННЫЙ КЛЮЧ
sessionkey = Random.new().read(32) # 256 bit
# encryption AES of the message #ЗАШИФРОВЫВАЕТ ПРИ ПОМОЩИ КЛЮЧА СООБЩЕНИЕ
f = open('D:\SSI project\\1234\plaintext.txt','rb')
plaintext = f.read(); f.close()
iv = Random.new().read(16) # 128 bit
obj = AES.new(sessionkey, AES.MODE_CFB, iv)
ciphertext = iv + obj.encrypt(plaintext)
f = open('D:\SSI project\\1234\plaintext.txt','wb')
f.write(bytes(ciphertext)); f.close()
# encryption RSA of the session key #Сеансовый ключ шифруется открытым ключом Боба
publickey = RSA.importKey(open('D:\SSI project\\1234\\bobpublickey.txt','rb').read())
cipherrsa = PKCS1_OAEP.new(publickey)
sessionkey = cipherrsa.encrypt(sessionkey)
f = open('D:\SSI project\\1234\sessionkey.txt','wb')
f.write(bytes(sessionkey)); f.close()
#Алиса посылает Бобу зашифрованное сообщение, подпись и зашифрованный сеансовый ключ.

#Этап приёма Боб получает зашифрованное сообщение Алисы, подпись и зашифрованный сеансовый ключ.

# decryption session key Боб расшифровывает сеансовый ключ своим закрытым ключом.
privatekey = RSA.importKey(open('D:\SSI project\\1234\\bobprivatekey.txt','rb').read())
cipherrsa = PKCS1_OAEP.new(privatekey)
f = open('D:\SSI project\\1234\sessionkey.txt','rb')
sessionkey = f.read(); f.close()
sessionkey = cipherrsa.decrypt(sessionkey)
# decryption message При помощи полученного, таким образом, сеансового ключа Боб расшифровывает зашифрованное сообщение Алисы.
f = open('D:\SSI project\\1234\plaintext.txt','rb')
ciphertext = f.read(); f.close()
iv = ciphertext[:16]
obj = AES.new(sessionkey, AES.MODE_CFB, iv)
plaintext = obj.decrypt(ciphertext)
plaintext = plaintext[16:]
f = open('D:\SSI project\\1234\plaintext.txt','wb')
f.write(bytes(plaintext)); f.close()


# decryption signature Боб расшифровывает и проверяет подпись Алисы.
f = open('D:\SSI project\\1234\signature.txt','rb')
signature = f.read(); f.close()
privatekey = RSA.importKey(open('D:\SSI project\\1234\\bobprivatekey.txt','rb').read())
cipherrsa = PKCS1_OAEP.new(privatekey)
sig = cipherrsa.decrypt(signature[:256])
sig = sig + cipherrsa.decrypt(signature[256:])
# signature verification
f = open('D:\SSI project\\1234\plaintext.txt','rb')
plaintext = f.read(); f.close()
publickey = RSA.importKey(open('D:\SSI project\\1234\\alisapublickey.txt','rb').read())
myhash = SHA256.new(plaintext)
signature = PKCS1_v1_5.new(publickey)
test = signature.verify(myhash, sig)



