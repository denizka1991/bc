from flask import Flask
from flask import render_template
from flask import request




app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        lender = request.form['lender']
        summ = request.form['summ']
        sender = request.form['sender']
        print(lender, " ", summ, " ", sender)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
