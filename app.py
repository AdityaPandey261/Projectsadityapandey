from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flash messages and session management

DATABASE = 'expenses.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
        ''')
        conn.execute('''
            CREATE TABLE expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT
            );
        ''')
        conn.execute('''
            CREATE TABLE income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL
            );
        ''')
        conn.commit()
        conn.close()

def login_required(func):
    # Decorator to ensure a user is logged in for protected routes
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_view

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm = request.form['confirm']

        if not username:
            flash('Username is required.')
            return redirect(url_for('signup'))
        if not password:
            flash('Password is required.')
            return redirect(url_for('signup'))
        if password != confirm:
            flash('Passwords do not match.')
            return redirect(url_for('signup'))

        conn = get_db_connection()
        existing_user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()

        if existing_user:
            flash('Username already exists.')
            conn.close()
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        flash('Signup successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if not username or not password:
            flash('Username and password are required.')
            return redirect(url_for('login'))

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user is None or not check_password_hash(user['password'], password):
            flash('Incorrect username or password.')
            return redirect(url_for('login'))

        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash('Login successful!')
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/set_income', methods=('GET', 'POST'))
@login_required
def set_income():
    if request.method == 'POST':
        amount_raw = request.form['amount']
        try:
            amount = float(amount_raw)
            if amount < 0:
                flash('Income must be a positive number!')
                return redirect(url_for('set_income'))
        except ValueError:
            flash('Invalid amount! Must be a number.')
            return redirect(url_for('set_income'))

        conn = get_db_connection()
        conn.execute('INSERT INTO income (amount) VALUES (?)', (amount,))
        conn.commit()
        conn.close()
        flash('Income set successfully!')
        return redirect(url_for('index'))

    return render_template('set_income.html')

@app.route('/monthly_expenses')
@login_required
def monthly_expenses():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses WHERE strftime("%Y-%m", date) = strftime("%Y-%m", "now") ORDER BY date DESC').fetchall()
    total_expense = sum(expense['amount'] for expense in expenses)
    conn.close()
    return render_template('monthly_expenses.html', expenses=expenses, total_expense=total_expense)

@app.route('/weekly_expenses')
@login_required
def weekly_expenses():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses WHERE date >= date("now", "-7 days") ORDER BY date DESC').fetchall()
    total_expense = sum(expense['amount'] for expense in expenses)
    conn.close()
    return render_template('weekly_expenses.html', expenses=expenses, total_expense=total_expense)

@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()
    categories = conn.execute('SELECT category, SUM(amount) as total FROM expenses GROUP BY category').fetchall()
    total_expense = conn.execute('SELECT SUM(amount) as total FROM expenses').fetchone()['total'] or 0.0
    income = conn.execute('SELECT SUM(amount) as total FROM income').fetchone()['total'] or 0.0
    conn.close()
    return render_template('index.html', expenses=expenses, categories=categories, total_expense=total_expense, income=income)

@app.route('/add', methods=('GET', 'POST'))
@login_required
def add_expense():
    if request.method == 'POST':
        date_raw = request.form['date']
        amount_raw = request.form['amount']
        category = request.form['category'].strip()
        description = request.form['description'].strip()

        if not date_raw:
            flash('Date is required!')
            return redirect(url_for('add_expense'))
        if not amount_raw:
            flash('Amount is required!')
            return redirect(url_for('add_expense'))
        if not category:
            flash('Category is required!')
            return redirect(url_for('add_expense'))

        # Validate date format
        try:
            date_obj = datetime.strptime(date_raw, '%Y-%m-%d')
            date = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            flash('Invalid date format! Use YYYY-MM-DD.')
            return redirect(url_for('add_expense'))
        
        # Validate amount
        try:
            amount = float(amount_raw)
            if amount <= 0:
                flash('Amount must be positive number!')
                return redirect(url_for('add_expense'))
        except ValueError:
            flash('Invalid amount! Must be a number.')
            return redirect(url_for('add_expense'))

        conn = get_db_connection()
        conn.execute('INSERT INTO expenses (date, amount, category, description) VALUES (?, ?, ?, ?)',
                     (date, amount, category, description))
        conn.commit()
        conn.close()
        flash('Expense added successfully!')
        return redirect(url_for('index'))

    return render_template('add_expense.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit_expense(id):
    conn = get_db_connection()
    expense = conn.execute('SELECT * FROM expenses WHERE id = ?', (id,)).fetchone()

    if expense is None:
        flash('Expense not found!')
        conn.close()
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        date_raw = request.form['date']
        amount_raw = request.form['amount']
        category = request.form['category'].strip()
        description = request.form['description'].strip()

        if not date_raw:
            flash('Date is required!')
            return redirect(url_for('edit_expense', id=id))
        if not amount_raw:
            flash('Amount is required!')
            return redirect(url_for('edit_expense', id=id))
        if not category:
            flash('Category is required!')
            return redirect(url_for('edit_expense', id=id))

        # Validate date format
        try:
            date_obj = datetime.strptime(date_raw, '%Y-%m-%d')
            date = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            flash('Invalid date format! Use YYYY-MM-DD.')
            return redirect(url_for('edit_expense', id=id))
        
        # Validate amount
        try:
            amount = float(amount_raw)
            if amount <= 0:
                flash('Amount must be positive number!')
                return redirect(url_for('edit_expense', id=id))
        except ValueError:
            flash('Invalid amount! Must be a number.')
            return redirect(url_for('edit_expense', id=id))

        conn.execute('UPDATE expenses SET date = ?, amount = ?, category = ?, description = ? WHERE id = ?',
                     (date, amount, category, description, id))
        conn.commit()
        conn.close()
        flash('Expense updated successfully!')
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit_expense.html', expense=expense)

@app.route('/delete/<int:id>', methods=('POST',))
@login_required
def delete_expense(id):
    conn = get_db_connection()
    expense = conn.execute('SELECT * FROM expenses WHERE id = ?', (id,)).fetchone()
    if expense:
        conn.execute('DELETE FROM expenses WHERE id = ?', (id,))
        conn.commit()
        flash('Expense deleted successfully!')
    else:
        flash('Expense not found!')
    conn.close()
    return redirect(url_for('index'))

@app.route('/analyze')
@login_required
def analyze():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses').fetchall()
    total_expense = sum(expense['amount'] for expense in expenses)
    
    # Group expenses by category for analysis
    categories = conn.execute('SELECT category, SUM(amount) as total FROM expenses GROUP BY category').fetchall()
    
    # Convert categories to a list of dictionaries
    categories_list = [{'category': category['category'], 'total': category['total']} for category in categories]
    
    conn.close()
    
    return render_template('analyze.html', total_expense=total_expense, categories=categories_list)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
