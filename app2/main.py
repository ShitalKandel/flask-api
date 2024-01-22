from flask import Flask, render_template, url_for, request, redirect, session
import psycopg2
import bcrypt


app = Flask(__name__)
app.secret_key = 'in.@123@'


conn = psycopg2.connect(database="flask_app", user="shital", password='123456', host="localhost", port="5432")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS flask_app (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100),
        password VARCHAR(100)
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

        cursor.execute("SELECT * FROM flask_app WHERE username = %s;", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
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

        cursor.execute("SELECT * FROM flask_app WHERE username = %s AND password = %s;", (username,
                                                                                          password))
        user = cursor.fetchone()

        if user:
            session['username'] = username
            if user and not bcrypt.hashpw(user[2], password):
                reset = reset_password()
                return reset ,redirect(url_for('reset_password'))

        return "Please check your Username and Password"

    return render_template('login.html')


@app.route('/login/reset', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        cursor.execute("SELECT * FROM flask_app WHERE username = %s;", (username,))
        user = cursor.fetchone()

        if user and bcrypt.hashpw(user[2], old_password):
            hashed_password = bcrypt.checkpw(new_password).decode('utf-8')

            cursor.execute("UPDATE flask_app SET password = %s WHERE username = %s;", (hashed_password, username))
            conn.commit()

            return redirect(url_for('login'))
        else:
            return render_template('reset_password.html', error='Invalid username or old password.')

    return render_template('reset_password.html')


@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))
    
    

@app.route('/logout')
def logout():
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)