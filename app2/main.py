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

        password_hash = pbkdf2_sha256.hash(password)

        cursor.execute("SELECT * FROM flask_app WHERE (username, password) = (%s,%s);", (username,password_hash))
        existing_user = cursor.fetchone()

        if existing_user and pbkdf2_sha256.verify(password, existing_user[2]):
            return render_template('register.html', error='Username already exists.')

        cursor.execute("INSERT INTO flask_app (username, password) VALUES (%s, %s);", (username, password))
        conn.commit()

        return redirect(url_for('login')) 

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hash_password = pbkdf2_sha256.verify(password,user['username'])
        
        cursor.execute("SELECT * FROM flask_app WHERE (username,password) = (%s,%s);", (username,hash_password))
        user = cursor.fetchone()

        if user and pbkdf2_sha256.verify(password, user['username']):
            session['username'] = username
            return redirect(url_for('dashboard'))
        return "Please check your Username and Password"
    return render_template('login.html')


@app.route('/login/reset', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']

        cursor.execute("SELECT * FROM flask_app WHERE username = %s;", (username,))
        user = cursor.fetchone()

        if user and pbkdf2_sha256.hashpw(new_password.encode('utf-8'), user[2].encode('utf-8')):

            cursor.execute("UPDATE flask_app SET password = %s WHERE username = %s;", ( username))
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