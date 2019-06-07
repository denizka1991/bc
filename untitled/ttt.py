from flask import Flask
from flask import request
import json
import pymysql
from pymysql.cursors import DictCursor
import time
import hashlib

app = Flask(__name__)

connection = pymysql.connect(
    host='185.148.82.46',
    user='admin_blockchain',
    password='blockchain',
    db='admin_blockchain',
    charset='utf8mb4',
    cursorclass=DictCursor
)


def generate_hash(prev_hash, public_key, amount, to_whom_public, time):
    hash = hashlib.sha256()
    hash.update(prev_hash.encode('utf-8'))
    hash.update(public_key.encode('utf-8'))
    hash.update(amount.encode('utf-8'))
    hash.update(to_whom_public.encode('utf-8'))
    hash.update(time.encode('utf-8'))
    return hash.hexdigest()

def cl():
    connection.ping(reconnect=True)
    with connection.cursor() as cursor:
        query = 'SELECT * FROM `transaction`'
        cursor.execute(query)
        t = cursor.fetchall()
        c = t[0]['hash']
        for row1 in t:
            tmp = row1['prev_hash']
            if c == tmp or c == "NULL":
                return 1

def chain():
    connection.ping(reconnect=True)
    with connection.cursor() as cursor:
        query = 'SELECT * FROM `transaction`'
        cursor.execute(query)
        t = cursor.fetchall()
        for row in t:
            t = generate_hash(row['prev_hash'], row['public_key'], str(float(row['amount'])),row['to_whom_public'], str(int(row['time_stmp'])))
            c = row['hash']
            print(t, '\t', c)
            if t != c:
                print ("error")
                return 0


@app.route('/all_tranaction', methods=['GET', 'POST'])
def myfun():
    if request.method == 'POST':
        a = request.get_data()
        connection.ping(reconnect=True)
        str = a.decode('utf-8')
        print(str)
        with connection.cursor() as cursor:
            query = 'SELECT * FROM transaction WHERE public_key = %s'
            cursor.execute(query, (str))
            tmp1 = cursor.fetchall()
            query = 'SELECT * FROM transaction WHERE to_whom_public = %s'
            cursor.execute(query, (str))
            tmp2 = cursor.fetchall()
            if not tmp1:
                return json.dumps(tmp2)
            elif not tmp2:
                return json.dumps(tmp1)
            elif not tmp1 and not tmp2:
                return 0
        return json.dumps(tmp1 + tmp2)
    else:
        return 'this route supports only post'

@app.route('/last_hash', methods=['GET', 'POST'])
def last_hash():
    if request.method == 'POST':
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            query = 'SELECT `hash` FROM `transaction` ORDER BY id DESC LIMIT 1'
            cursor.execute(query)
            tmp = cursor.fetchone()
            tmp = json.dumps(tmp)
            return tmp
    else:
        return 'this route supports only post'

@app.route('/block_info', methods=['GET', 'POST'])
def block_info():
    if request.method == 'POST':
        a = request.get_data()
        str = a.decode('utf-8')
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            query = 'SELECT * FROM `transaction` WHERE `hash` = %s'
            t = cursor.execute(query, (str))
            if t == 1:
                return json.dumps(cursor.fetchone())
            if t == 0:
                return json.dumps(0)
    else:
        return 'this route supports only post'






@app.route('/make_tranaction', methods=['POST'])
def make_tranaction():
    a = request.form.get('tmp')
    t = json.loads(a)
    timestamp = str(int(time.time()))
    tmp = 1
    tmp = chain()
    tmp1 = 0
    tmp1 = cl()
    print (tmp1)
    if tmp == 0 or tmp1 == 0:
        print("error has not walid chain")
        return "0"
    connection.ping(reconnect=True)
    with connection.cursor() as cursor:
        transaction = generate_hash(json.loads(last_hash())['hash'], t['public_key'], str(float(t['sum'])), t['receiver_key'],
                               timestamp)
        cursor.execute('INSERT INTO transaction (`prev_hash`, public_key, amount, to_whom_public, to_whom_amount, time_stmp, `hash`) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (json.loads(last_hash())['hash'], t['public_key'], str(float(t['sum'])), t['receiver_key'], str(float(t['sum'])), timestamp, transaction))
        connection.commit()
    return a



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



