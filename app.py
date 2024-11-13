from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# データベース接続関数
def get_db_connection():
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

# ホームページ（合計を表示）
@app.route('/')
def index():
    conn = get_db_connection()
    query = '''
    SELECT category, strftime('%Y-%m', time_added) AS month, SUM(price) AS total
    FROM expenses
    GROUP BY category, month
    '''
    expenses = conn.execute(query).fetchall()
    conn.close()
    return render_template('index.html', expenses=expenses)

# カテゴリ詳細ページ
@app.route('/category/<string:category>')
def category_detail(category):
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses WHERE category = ?', (category,)).fetchall()
    conn.close()
    return render_template('category_detail.html', category=category, expenses=expenses)

# 経費の追加
@app.route('/add', methods=('GET', 'POST'))
def add_expense():
    if request.method == 'POST':
        category = request.form['category']
        item_name = request.form['item_name']
        price = int(request.form['price'])
        memo = request.form['memo']
        time_added = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = get_db_connection()
        conn.execute('INSERT INTO expenses (category, item_name, price, time_added, memo) VALUES (?, ?, ?, ?, ?)',
                     (category, item_name, price, time_added, memo))
        conn.commit()
        conn.close()
        flash('経費が追加されました！')
        return redirect(url_for('index'))

    return render_template('add_expense.html')

# 経費の編集
@app.route('/edit/<int:expense_id>', methods=('GET', 'POST'))
def edit_expense(expense_id):
    conn = get_db_connection()
    expense = conn.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,)).fetchone()

    if request.method == 'POST':
        category = request.form['category']
        item_name = request.form['item_name']
        price = int(request.form['price'])
        memo = request.form['memo']

        conn.execute('UPDATE expenses SET category = ?, item_name = ?, price = ?, memo = ? WHERE id = ?',
                     (category, item_name, price, memo, expense_id))
        conn.commit()
        conn.close()
        flash('経費が更新されました！')
        return redirect(url_for('category_detail', category=category))

    conn.close()
    return render_template('edit_expense.html', expense=expense)

if __name__ == '__main__':
    app.run(debug=True)


conn = sqlite3.connect('expenses.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    item_name TEXT NOT NULL,
    price INTEGER NOT NULL,
    time_added TEXT NOT NULL,
    memo TEXT
)
''')

conn.commit()
conn.close()




###   時間も編集したい。動きをもっとつけたい。経費を追加がなんか2つある。。