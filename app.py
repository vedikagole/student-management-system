from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create students table if not exists
with get_db_connection() as conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll TEXT NOT NULL,
            marks INTEGER NOT NULL
        )
    ''')

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "vedika" and password == "vedu@1234":
            session['user'] = username
            return redirect('/home')
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

# Home route
@app.route('/home')
def index():
    if 'user' not in session:
        return redirect('/')

    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('index.html', students=students)

# Add student route
@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        marks = request.form['marks']

        # Validate marks input
        try:
            marks = int(marks)
        except ValueError:
            return render_template('add.html', error="Marks must be a number")

        conn = get_db_connection()
        conn.execute("INSERT INTO students (name, roll, marks) VALUES (?, ?, ?)",
                     (name, roll, marks))
        conn.commit()
        conn.close()
        return redirect('/home')

    return render_template('add.html')

# Delete student route
@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect('/')

    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/home')

# Edit student route
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user' not in session:
        return redirect('/')

    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()

    if not student:
        conn.close()
        return redirect('/home')

    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        marks = request.form['marks']

        try:
            marks = int(marks)
        except ValueError:
            return render_template('edit.html', student=student, error="Marks must be a number")

        conn.execute("UPDATE students SET name = ?, roll = ?, marks = ? WHERE id = ?",
                     (name, roll, marks, id))
        conn.commit()
        conn.close()
        return redirect('/home')

    conn.close()
    return render_template('edit.html', student=student)

# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True,port=5000)