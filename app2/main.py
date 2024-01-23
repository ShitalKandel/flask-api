from flask import Flask, render_template, url_for, request, redirect, session
import psycopg2
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.secret_key = 'in.@123@'

conn = psycopg2.connect(database="flask_app", user="shital", password='123456', host="localhost", port="5432")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS flask_app (
        id SERIAL PRIMARY KEY,
        username VARCHAR,
        password VARCHAR
    );
''')
conn.commit()



@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            return render_template('register.html', error='Passwords do not match.')

        hashed_password = pbkdf2_sha256.hash(password)

        cursor.execute("SELECT * FROM flask_app WHERE username = %s;", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template('register.html', error='Username already exists.')

        cursor.execute("INSERT INTO flask_app (username, password) VALUES (%s, %s);", (username, hashed_password))
        conn.commit()

        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM flask_app WHERE username = %s;", (username,))
        user = cursor.fetchone()

        if user and pbkdf2_sha256.verify(password, user[2]): 
            session['username'] = username
            return redirect(url_for('dashboard'))

        return "Please check your Username and Password"
    
    return render_template('login.html')


@app.route('/login/reset', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        cursor.execute("SELECT * FROM flask_app WHERE username = %s;", (username,))
        user = cursor.fetchone()

        if user and new_password == confirm_password:
            hashed_password = pbkdf2_sha256.hash(new_password)

            cursor.execute("UPDATE flask_app SET password = %s WHERE username = %s;", (hashed_password, username))
            conn.commit()

            return redirect(url_for('login'))
        else:
            return render_template('reset_password.html', error='Invalid username or password.')

    return render_template('reset_password.html')



@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))
    
    

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)