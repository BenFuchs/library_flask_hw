import sqlite3
from flask import Flask, redirect, render_template, request, url_for

api = Flask(__name__)

con = sqlite3.connect('library.db', check_same_thread=False)
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS books (Name TEXT, Author TEXT, Year INTEGER, Loan TEXT, Active INT)")
cur.execute("CREATE TABLE IF NOT EXISTS clients(Name TEXT, Age INT, City TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS loans(BookID INT, ClientID INT, LoanDate, Active INT)")

@api.route('/', methods=['POST', 'GET'])
def hello():
    if request.method == 'POST':
        bName = request.form['bName']
        bAuthor = request.form['bAuthor']
        bYear = request.form['bYear']
        bLoan = request.form['bLoan']
        if len(bLoan) >= 1:
            cur.execute("INSERT INTO books (Name, Author, Year, Loan, Active) VALUES (?, ?, ?, ?, ?)", (bName, bAuthor, bYear, bLoan, 1))
            con.commit()
        print(bName, bAuthor, bYear, bLoan)
    
    res = cur.execute("SELECT ROWID, * FROM books WHERE Active = 1").fetchall()
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

@api.route('/delBook<int:id>', methods=['DELETE'])
def del_book(id):
    print("delete", id)
    cur.execute(f"UPDATE books SET Active = 0 WHERE ROWID = {id}")
    con.commit()
    return "delete successful"

@api.route('/delUser<int:id>', methods=['DELETE'])
def del_user(id):
    print("delete", id)
    cur.execute(f"DELETE FROM clients WHERE ROWID = {id}")
    con.commit()
    return "delete successful"

@api.route('/loanBook/<int:id>', methods=['GET', 'POST'])
def loanBook(id):
    if request.method == 'POST':
        cur.execute("UPDATE books SET Active = 0 WHERE ROWID = ?", (id,))
        cur.execute("INSERT INTO loans Values(?, ?, ?, ?)", (x, x, x, 1))
        con.commit()
        return redirect(url_for('loanBook', id=id))
    
    books = cur.execute("SELECT ROWID, * FROM books WHERE Active = 1").fetchall()
    print("Loan", id)
    return render_template('loan_book.html', books=books)

if __name__ == '__main__':
    api.run(debug=True)
