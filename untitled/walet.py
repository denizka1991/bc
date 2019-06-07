from random import SystemRandom
from binascii import hexlify
from struct import Struct
import hashlib
import pymysql
import json
from pymysql.cursors import DictCursor
import requests
import re


connection = pymysql.connect(
    host='185.148.82.46',
    user='admin_blockchain',
    password='blockchain',
    db='admin_blockchain',
    charset='utf8mb4',
    cursorclass=DictCursor
)

connection1 = connection

def check_re(mystring):
    CHECK_RE = re.compile('[a-zA-Z0-9_-]+$')
    return CHECK_RE.match(mystring)

def get_public(pubkey):
    sha_pub = hashlib.sha256()
    sha_pub.update(pubkey.encode('utf-8'))
    return sha_pub.hexdigest()

def mkprivkey():
    SYS_RAN = SystemRandom()
    PACKER = Struct('>QQQQ')
    MIN_VAL = 0x1
    MAX_VAL = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
    key = SYS_RAN.randint(MIN_VAL, MAX_VAL)
    key0 = key >> 192
    key1 = (key >> 128) & 0xffffffffffffffff
    key2 = (key >> 64) & 0xffffffffffffffff
    key3 = key & 0xffffffffffffffff

    return hexlify(PACKER.pack(key0, key1, key2, key3))

def create_user(Login, Password):
    pubkey = mkprivkey().decode('utf-8')
    privatkey = get_public(pubkey)
    connection.ping(reconnect=True)
    with connection.cursor() as cursor:
        query = 'SELECT * FROM users WHERE login = %s'
        t = cursor.execute(query, (Login))
        if t == 1:
            print("This login already exists")
        if t == 0:
            query = 'INSERT INTO `users` (`login`, `password`, `privat_key`, `public_key`) VALUES (%s, %s, %s, %s)'
            cursor.execute(query, (Login, Password, pubkey, privatkey))
            connection.commit()
            print("PrivatKey:", pubkey)
            print("PublicKey:", privatkey)
            main()

def check_balance(str):
    connection1.ping(reconnect=True)
    with connection1.cursor() as cursor:
        query = 'SELECT * FROM users WHERE login = %s'
        cursor.execute(query,(str))
        t = cursor.fetchone()
        q = t['public_key']
        query1 = 'SELECT * FROM transaction WHERE public_key = %s'
        cursor.execute(query1, (q))
        t1 = cursor.fetchall()
        sum = 0
        for row in t1:
            sum -= row['amount']
        query2 = 'SELECT * FROM transaction WHERE to_whom_public = %s'
        cursor.execute(query2, (q))
        t2 = cursor.fetchall()
        for row in t2:
            sum += row['to_whom_amount']
        return sum


def last_hash(str):
    r = requests.post("http://localhost:5000/last_hash")
    tmp = json.loads(r.text)
    print("Last hash: ",tmp['hash'])
    wallet(str, 1)

def all_tranaction(str):
    k = my_pv_key(str)
    r = requests.post("http://localhost:5000/all_tranaction", data=k)
    tmp = json.loads(r.text)
    if not tmp:
        print("Wrong key")
    for line in tmp:
        print("\nFrom: {1}, Amount: {2},\nTime: {4}, Previous hash: {0},\nTo whom: {3}, Block hash: {5}\n".format(
            line['prev_hash'], line['public_key'], line['amount'], line['to_whom_public'], line['time_stmp'], line['hash']))
    wallet(str, 1)

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def make_tranaction(str):
    mas = {}
    print("summ for trantaction")
    a = input()
    tmp = isfloat(a)
    if tmp == False:
        print("worng sum")
        make_tranaction(str)
    c = float(a)
    b = check_balance(str)
    b = int(b)
    if c <= b:
        mas['sum'] = a
        print("write your private keys")
        key = input()
        tmpkey = get_public(key)
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            query = 'SELECT * FROM users WHERE public_key = %s AND login = %s'
            t = cursor.execute(query, (tmpkey, str))
            if t == 1:
                print("Key norm")
                mas['public_key'] = tmpkey
                print("Write receiver pub key")
                a = input()
                mas['receiver_key'] = a
                mas['yours_key'] = tmpkey
                tmp = json.dumps(mas)
                r = requests.post("http://localhost:5000/make_tranaction", data={'tmp': tmp})
                if r.text == "0":
                    print("error has not walid chain")
                    wallet(str, 1)
                print("Success")
                last_hash(str)

            if t == 0:
                print("wrong key")
                make_tranaction(str)
    else:
        print("Wrong summ")
        wallet(str, 1)


def block_info(str):
    print("Hash:", end='')
    a = input()
    if not a:
        print("Empty has")
        block_info(str)
    r = requests.post("http://localhost:5000/block_info", data=a)
    tmp = json.loads(r.text)
    if tmp == 0:
        print("Wrong Hash")
        wallet(str, 1)
    print("\nFrom: {1}, Amount: {2},\nTime: {4}, Previous hash: {0},\nTo whom: {3}, Block hash: {5}\n".format(
       tmp['prev_hash'], tmp['public_key'], tmp['amount'], tmp['to_whom_public'], tmp['time_stmp'], tmp['hash']))
    wallet(str, 1)



def my_pv_key(str):
    connection1.ping(reconnect=True)
    with connection1.cursor() as cursor:
        query = 'SELECT * FROM users WHERE login = %s'
        cursor.execute(query,(str))
        t = cursor.fetchone()
        q = t['public_key']
        return q


def wallet(login, i):
    if i == 0:
        sum = check_balance(login)
        print("Your balance: ", sum)
        k = my_pv_key(login)
        print("Your public key: ", k)
    print("1)Check Balance")
    print("2)Last_hash")
    print("3)All Trancaction")
    print("4)Make Trancaction")
    print("5)Block info")
    print("6)Back to main menu")
    a = input()
    if a == '1':
        sum = check_balance(login)
        print("Balance: ", sum)
        wallet(login, 1)
    elif a == '2':
        last_hash(login)
    elif a == '3':
        all_tranaction(login)
    elif a == '4':
        make_tranaction(login)
    elif a == '5':
        block_info(login)
    elif a == '6':
        main()
    else:
        print("Wrong chose")
        wallet(login, 1)

def register():
    print("Login:", end='')
    Login = input()
    t = check_re(Login)
    if t == None:
        print("Incorect login")
        return main()
    print("Password:", end='')
    Password = input()
    t1 = check_re(Password)
    if t1 == None:
        print("Incorect password")
        return main()
    t2 = Password.__len__()
    if t2 < 7:
        print("Small password you need password > 7")
        return main()
    create_user(Login, Password)

def login():
    print("Login:", end='')
    Login = input()
    print("Password:", end='')
    Password = input()
    connection.ping(reconnect=True)
    with connection.cursor() as cursor:
        query = 'SELECT * FROM users WHERE login = %s AND password = %s'
        t = cursor.execute(query, (Login, Password))
        if t == 1:
            wallet(Login, 0)
        if t == 0:
            print("wrong login or password")
            main()

def main():
    print ("DeNis Wallet Coin")
    print ("Chose operation")
    print ("1)Login")
    print ("2)Register")
    print ("3)Exit")
    a = input()
    if a == '1':
        login()
    elif a == '2':
        register()
    elif a == '3':
        exit(0)
    else:
        print("wrong choice")
        main()

main()