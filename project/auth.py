from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from . import db
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    
    session.clear()
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details or sign up first.')
        return redirect(url_for('auth.login')) 
    
    login_user(user, remember=remember)
    session['id'] = user.id
    return redirect(url_for('main.start', name=user))


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
   
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    
    if not email:
        flash('Please add a valid email')
        return redirect(url_for('auth.signup'))
    if not name:
        flash('Please add a name')
        return redirect(url_for('auth.signup'))
    if not password:
        flash('Please add a password')
        return redirect(url_for('auth.signup'))

    user = User.query.filter_by(email=email).first() 

    if user: 
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()
    flash('Account created! Please Login')
    return redirect(url_for('auth.login'))


@auth.route('/reset', methods=['POST', 'GET'])
def reset():
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
    
        if user:
            return render_template('resetpassword.html', email=email)
        else:
            flash('Please enter valid email or sign up!')
            return render_template('reset.html')
    else:
        return render_template('reset.html')
    

@auth.route('/resetpassword/<email>', methods=['POST','GET'])
def resetpassword(email):
    if request.method == 'POST':
        new_password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        user.password = generate_password_hash(new_password, method='sha256')
        db.session.commit()
        flash('Password reset! Please Login')
        return render_template('login.html')
    else:
        user = User.query.filter_by(email=email).first()
        return render_template('resetpassword.html', email=email)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.start'))