# import os, logging 
from flask import render_template, request, url_for, redirect, send_from_directory
from flask import login_user, logout_user, current_user, login_required
# from werkzeug.exceptions import HTTPException, NotFound, abort
# from jinja2 import TemplateNotFound
from app import app, lm, db, bc
from app.models import Users
from app.forms  import LoginForm, RegisterForm

@lm.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    
    form = RegisterForm(request.form)

    msg     = None
    success = False

    if request.method == 'GET': 

        return render_template( 'register.html', form=form, msg=msg )

    if form.validate_on_submit():

        username = request.form.get('username','', type=str)
        password = request.form.get('password','', type=str) 
        email    = request.form.get('email' ,'', type=str) 

        user = Users.query.filter_by(user=username).first()

        user_by_email = Users.query.filter_by(email=email).first()

        if user or user_by_email:
            msg = 'Error: User exists!'
        
        else:         

            pw_hash = bc.generate_password_hash(password)

            user = Users(username, email, pw_hash)

            user.save()

            msg     = 'User created, please <a href="' + url_for('login') + '">login</a>'     
            success = True

    else:
        msg = 'Input error'     

    return render_template( 'register.html', form=form, msg=msg, success=success )

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    form = LoginForm(request.form)

    msg = None

    if form.validate_on_submit():

        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 

        user = Users.query.filter_by(user=username).first()

        if user:
            
            if bc.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unknown user"

    return render_template( 'login.html', form=form, msg=msg )



