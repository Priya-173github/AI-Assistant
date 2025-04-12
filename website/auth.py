from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, current_user, logout_user

auth = Blueprint('auth',__name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('pwd')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, pwd):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password!', category='error')
        else:
            flash('User does not exist', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required  #makes sure user cannot logout if not logged in
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        pwd = request.form.get('pwd')
        desig = request.form.get('desig')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('User already exists!', category='error')
        else:
            new_user = User(email=email,
                            name=name,
                            desig=desig,
                            password=generate_password_hash(pwd, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created', category='success')
            return redirect(url_for('views.home')) 


    return render_template("signup.html", user=current_user)