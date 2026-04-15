import os
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
def init_db():
    conn = sqlite3.connect("expenses.db")

    # USERS TABLE
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # EXPENSES TABLE
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            expense_date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()



app.secret_key = "supersecretkey"  # needed for sessions

def get_db():
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---------- AUTH ----------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        hashed_password = generate_password_hash(password)

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
        except:
            return "Username already exists"
        finally:
            conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        else:
            return "Invalid credentials"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------- EXPENSES ----------

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    expenses = conn.execute(
        "SELECT * FROM expenses WHERE user_id = ?",
        (session['user_id'],)
    ).fetchall()
    conn.close()

    return render_template('index.html', expenses=expenses)


@app.route('/add', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    name = request.form.get('name')
    amount = request.form.get('amount')
    category = request.form.get('category')
    expense_date = request.form.get('expense_date')


    conn = get_db()
    conn.execute(
    "INSERT INTO expenses (user_id, name, amount, category, expense_date) VALUES (?, ?, ?, ?, ?)",
    (session['user_id'], name, amount, category, expense_date)
)
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/check')
def check_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()

    total = conn.execute(
        "SELECT SUM(amount) FROM expenses WHERE user_id = ?",
        (session['user_id'],)
    ).fetchone()[0]

    last_date = conn.execute(
        "SELECT MAX(expense_date) FROM expenses WHERE user_id = ?",
        (session['user_id'],)
    ).fetchone()[0]

    conn.close()

    return render_template(
        'check.html',
        total=total,
        last_date=last_date
    )

if __name__ == "__main__":
    app.run()





