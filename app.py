import sqlite3
from flask import Flask, render_template, request

api = Flask(__name__)

con = sqlite3.connect('library.db', check_same_thread=False)
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS books (Name TEXT, Author TEXT, Year INTEGER, Loan TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS clients(Name TEXT, Age INT, City TEXT)")

@api.route('/', methods=['POST', 'GET'])
def hello():
    if request.method == 'POST':
        bName = request.form['bName']
        bAuthor = request.form['bAuthor']
        bYear = request.form['bYear']
        bLoan = request.form['bLoan']

        cur.execute("INSERT INTO books (Name, Author, Year, Loan) VALUES (?, ?, ?, ?)", (bName, bAuthor, bYear, bLoan))
        con.commit()
        print(bName, bAuthor, bYear, bLoan)
    
    res = cur.execute("SELECT ROWID, * FROM books").fetchall()
    return render_template('index.html', data=res)

@api.route('/addClient', methods=['POST', 'GET'])
def add_client():
    if request.method == 'POST':
        cName = request.form['cName']
        cAge = request.form['cAge']
        cCity = request.form['cCity']

        cur.execute("INSERT INTO clients(Name, Age, City) Values (?, ?, ?)", (cName, cAge, cCity))
        con.commit()

    clients = cur.execute("SELECT ROWID, * FROM clients").fetchall()
    return render_template('add_client.html', clients = clients)
if __name__ == '__main__':
    api.run(debug=True)
