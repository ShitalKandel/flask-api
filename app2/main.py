from flask import Flask, render_template, url_for, request, redirect, session
import psycopg2
import os
from passlib.hash import pbkdf2_sha256
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'in.@123@'

conn = psycopg2.connect(database="flask_app", user="shital", password='123456', host="localhost", port="5432")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS flask_app (
        id SERIAL PRIMARY KEY,
        username VARCHAR,
        password VARCHAR,
        image BYTEA,
        bio VARCHAR
    );
''')
conn.commit()


UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



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


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        
        cursor = conn.cursor()
        username = session['username']
        print(username)
        cursor.execute("SELECT image, bio FROM flask_app WHERE username = %s;", (username,))
        user_data = cursor.fetchone()
        
        cursor.execute("SELECT * FROM flask_app WHERE username = %s;",(username,))
        user_data = cursor.fetchone()
        conn.commit()
        bio = user_data[-1]
        
        
        dlt = delete_bio_route()
        # print(dir(bio))
        # conn.commit()
        # if bio:

        #     return render_template('dashboard.html', username=username, user_data=user_data, bio=bio)

        return render_template('dashboard.html', username=username, user_data=user_data,bio=bio,dlt=dlt)
    else:
        return "Unauthorized Access"


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'username' in session:
            username = session['username']
            if 'profile-image' in request.files:
                file = request.files['profile-image']
                if file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)

                    cursor = conn.cursor()
                    cursor.execute("UPDATE flask_app SET image = %s WHERE username = %s;", (filename, username))
                    conn.commit()
                    return redirect(url_for('dashboard'))
                else:
                    return "Invalid file name"
            else:
                return "No 'profile-image' in the request"
        else:
            return "User not logged in"
    else:
        return "Only POST requests are allowed"


@app.route('/delete_image', methods=['POST'])
def delete_image():
    if 'username' in session:
        username = session['username']
        cursor = conn.cursor()
        cursor.execute("UPDATE flask_app SET image = BYTEA WHERE username = %s;", (username,))
        conn.commit()
        return redirect(url_for('dashboard'))
    else:
        return "User not logged in"
    
def update_bio(username, bio):
    print(cursor)
    cursor.execute("UPDATE flask_app SET bio = %s WHERE username = %s;", (bio, username))
    conn.commit()
    

def delete_bio(username):
    cursor.execute("UPDATE flask_app SET bio = Null WHERE username = %s;", (username))
    conn.commit()
    
    
@app.route('/edit_bio', methods=['POST'])
def edit_bio():
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username, edit_bio=True)
    else:
        return redirect(url_for('dashboard'))

@app.route('/save_bio', methods=['POST'])
def save_bio():
    if 'username' in session:
        username = session['username']
        new_bio = request.form.get('bio')
        update_bio(username, new_bio)
    return redirect(url_for('dashboard'))



@app.route('/delete_bio', methods=['POST'])
def delete_bio_route():
    if 'username' in session:
        username = session['username']
        delete = request.form.get('bio')
        delete_bio(username,delete)

        if delete =='Delete Bio':
            return redirect(url_for('dashboard'))
    
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)