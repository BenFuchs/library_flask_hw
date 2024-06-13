import sqlite3
from flask import Flask, redirect, render_template, request, url_for

api = Flask(__name__)

con = sqlite3.connect('library.db', check_same_thread=False)
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS books (Name TEXT, Author TEXT, Year INTEGER, Loan TEXT, Active INT)")
cur.execute("CREATE TABLE IF NOT EXISTS clients(Name TEXT, Age INT, City TEXT, Logged_in INT)")
cur.execute("CREATE TABLE IF NOT EXISTS loans(BookID INT, ClientID INT, LoanDate, Active INT)")

@api.route('/addBook', methods=['POST', 'GET'])
def addBook():
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
        # logged_user => currently logged in user. use for loaning
        logged_user_result = cur.execute("SELECT ROWID FROM clients WHERE Logged_in = 1").fetchone()
        logged_user = logged_user_result[0] if logged_user_result else None
        print(logged_user)
        cur.execute("UPDATE books SET Active = 0 WHERE ROWID = ?", (id,))
        cur.execute("""
                    SELECT books.ROWID, loans.BookID 
                    FROM books
                    INNER JOIN loans ON books.ROWID = loans.BookID 
                    """)
        cur.execute("""
                    SELECT clients.ROWID, loans.ClientID
                    FROM clients
                    INNER JOIN loans on clients.ROWID = loans.ClientID
                    """)
        cur.execute("INSERT INTO loans Values(?, ?, ?, ?)", (id, logged_user, 1, 1))
        con.commit()
        return redirect(url_for('loanBook', id=id))
    
    books = cur.execute("SELECT ROWID, * FROM books WHERE Active = 0").fetchall()
    print("Loan", id)
    return render_template('loan_book.html', books=books)

@api.route('/returnBook/<int:id>', methods=['GET', 'POST'])
def returnBook(id):
    if request.method == 'POST':
        cur.execute("UPDATE books SET Active == 1 WHERE ROWID = ?", (id,))
        cur.execute("UPDATE loans SET Active == 0 WHERE BookID = ?", (id,))
        con.commit()
        books = cur.execute("SELECT ROWID, * FROM books WHERE Active = 0").fetchall()
        return render_template('loan_book.html', books=books)
    
    books = cur.execute("SELECT ROWID, * FROM books WHERE Active = 0").fetchall()
    return render_template('loan_book.html', books=books)

@api.route('/', methods=['POST', 'GET'])
def log_in():
    if request.method == 'POST':
        user_name = request.form.get('user')
        print("Form data:", request.form)  # Debugging line
        try:
            cur.execute("SELECT * FROM clients WHERE Name = ?", (user_name,))
            client = cur.fetchone()
            print("Client fetched:", client)  # Debugging line
            if client:
                cur.execute("UPDATE clients SET Logged_in = 1 WHERE Name = ?", (user_name,))
                con.commit()
                return redirect(url_for('addBook'))
            else:
                return render_template('login_page.html', message="User not found")
        except Exception as e:
            print("Error:", e)
            return render_template('login_page.html', message="An error occurred")
    return render_template('login_page.html')

@api.route('/logout')
def logout():
    try:
        cur.execute("UPDATE clients SET Logged_in = 0")
        con.commit()
    except Exception as e:
        print("Error:", e)
    return redirect(url_for('log_in'))

if __name__ == '__main__':
    api.run(debug=True)
